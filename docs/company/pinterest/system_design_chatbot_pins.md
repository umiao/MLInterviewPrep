# Pinterest ML System Design: Personalized Chat Bot Recommending Pins

> Pinterest SD 2025-11 onsite 题目: "Design a personalized conversational assistant that chats with users and recommends relevant Pins in-line"
> Scope: 对话理解 → 意图分类 → RAG pin 检索 → grounding → safety → 评估
> Format: 45-min SD loop (clarify 5m, objective 5m, 架构 8m, 模型 10m, serving 8m, safety/eval 6m, follow-up 3m)

---

## 0. Clarifying Questions (前 5 分钟必问)

"Design a chat bot that recommends pins" 歧义极大, 必须先对齐:

| 维度 | 问题 | 为什么重要 |
|------|------|----------|
| 产品形态 | 独立 chat tab? home feed 里的 inline assistant? 还是 search 页的 AI refine? | 决定 UI 约束 + latency SLA + turn 长度 |
| 输入模态 | 纯文本? 允许图片上传 (visual search)? 语音? | 多模态决定 encoder; 图片 ⇒ CLIP / unified embedding |
| 输出模态 | 纯 pin grid? 文本 + pin 混排? 有 "reasoning" 文字解释吗? | 混排需要 LLM 做 grounded generation, 不仅仅 retrieval |
| 个性化深度 | 用 user 历史 repin/board 吗? cross-session 记忆? 还是单 session 隐私隔离? | 决定是否拉 user embedding / long-term profile |
| 会话长度 | 平均 turn 数? 上下文窗口多大? | 多轮 ⇒ dialog state tracking; 单轮 ⇒ 退化为 search |
| Pin corpus | 全 5B pins? 只 shopping / recipe? 可包含 ads? | 决定 retrieval index 大小 + 商业化策略 |
| Latency | first-token / full-response P99? | 纯 chat <2s first-token; 带 pin grid <3s full |
| Scale | DAU chat 用户? QPS? | 估 10M DAU × 5 turn ⇒ 600 QPS peak |
| Safety | 成人/暴力/自残 topic 如何处理? ads 披露? | safety layer 必须在 LLM 前后双向拦截 |

**本设计假设**:
- 独立 chat surface (Pinterest app "Ask Pinterest" tab), 文本 + 图片输入, 文本 + pin grid 混排输出
- 多轮对话 (平均 4 turn, 上下文窗口 8K tokens)
- 个性化: 使用 user long-term embedding + 最近 session 的 repin/hide
- Pin corpus: 全量 5B pins, ads 可混入但需 disclosure
- Latency: first-token <1.5s, pin grid <3s (P99)
- Scale: 10M DAU, peak 2K QPS

---

## 1. High-Level Architecture

```
  user turn (text + optional img)
           │
           ▼
  ┌─────────────────────┐
  │ 1. Input Safety      │  (PII redact, toxicity, self-harm → escalate)
  └─────────┬───────────┘
            ▼
  ┌─────────────────────┐
  │ 2. Dialog State Mgr  │  (merge history + user profile → compact state)
  └─────────┬───────────┘
            ▼
  ┌─────────────────────┐
  │ 3. Intent Classifier │  (chit-chat / ask-pins / refine / compare / off-topic)
  └─────┬──────┬────────┘
        │      │
   chit-chat   ask-pins / refine
        │      │
        │      ▼
        │  ┌────────────────────────┐
        │  │ 4. Query Rewriter (LLM)│  (expand to search query + facets)
        │  └──────────┬─────────────┘
        │             ▼
        │  ┌────────────────────────┐
        │  │ 5. Retrieval (RAG)     │
        │  │  - ANN on pin embed    │
        │  │  - BM25 text           │
        │  │  - personalization re- │
        │  │    rank w/ user embed  │
        │  └──────────┬─────────────┘
        │             ▼
        │  ┌────────────────────────┐
        │  │ 6. Grounded Generation │  (LLM w/ pin metadata as context)
        │  │  - rationale           │
        │  │  - citation (pin_id)   │
        │  └──────────┬─────────────┘
        │             ▼
        └──► ┌─────────────────────┐
             │ 7. Output Safety     │  (dedup, policy filter, ad disclosure)
             └─────────┬───────────┘
                       ▼
                 streaming response
                 (text tokens + pin_ids)
                       │
                       ▼
                 engagement log → feedback
```

4 个关键子系统: 对话理解 (2+3), 检索 (4+5), 生成 (6), 安全评估 (1+7+监控).

---

## 2. Conversation Understanding (对话理解)

### 2.1 Dialog State Tracking
不使用传统 slot-filling (过于 rigid). 改用 **LLM-compiled state**:

- 每 turn 结束, 由一个轻量 LLM (Llama-3-8B fine-tune) 产出结构化 state:
  ```json
  {
    "active_topic": "home office desk setup",
    "constraints": {"style": "minimalist", "color": "white/wood", "budget_usd": 500},
    "negative": ["no industrial", "no black metal"],
    "already_shown_pin_ids": [...],
    "liked_pin_ids": [...],
    "user_persona": "first-time remote worker"
  }
  ```
- State 用于下一 turn 的 retrieval + generation, 避免把整段 history 塞进上下文.
- Long-term user profile (board 标题, top categories, 风格 embedding) 作为 **persistent state**, 与 session state 合并.

### 2.2 Context Compression
- Window 8K tokens, 接近饱和时用 **summarization** (同一个轻量 LLM), 保留 active_topic + constraints + negative + 最近 2 turn 原文.
- 图片输入: CLIP ViT-L/14 抽 image embedding, 存入 state (而非 raw pixels), 减少后续 turn cost.

### 2.3 Coreference & Follow-up
用户说 "show me more like the third one" ⇒ 需要把 pin grid index 映射回 pin_id. 前端把最近一次展示的 pin_ids + 序号塞回 state, LLM 做 coref resolution.

---

## 3. Intent Classification

### 3.1 Taxonomy
5 类 (MECE, 覆盖 >98% 实际 query):

| 意图 | 示例 | 下游 action |
|------|------|-----------|
| **ask-pins** | "show me cozy bedroom ideas" | 触发 retrieval + pin grid |
| **refine** | "more boho, less beige" | 基于上轮 state 调整 query, 重检索 |
| **compare** | "which of these would fit a small room?" | LLM reasoning over last grid, 无检索 |
| **chit-chat** | "hi", "thanks!", "are you real?" | 纯 LLM 生成, 不检索 |
| **off-topic / unsafe** | 医疗建议, 政治, 成人 | 礼貌 decline + safe fallback |

### 3.2 Model Choice
- **首选**: 让生成 LLM 自己输出 `intent` 字段 (structured decoding). 省一次调用.
- **兜底**: 独立 DistilBERT classifier (6-layer, 256 dim) 做 guardrail, 只在生成 LLM 给出低置信度时介入.
- 训练数据: 100K 人工标注 + 1M weak-label (用 GPT-4 在历史 chat 上打标).

### 3.3 为什么不用 pure zero-shot LLM
- 成本 + latency: 每 turn 多一次 LLM 调用 = +400ms.
- Calibration: 细分类 LLM confidence 不稳, 需要 temperature scaling; 小模型 classifier 做兜底更稳.

---

## 4. Retrieval-Augmented Pin Recommendation

### 4.1 Query Rewriting
LLM 把对话 state 改写成 **多路查询**:
- `text_query`: 自然语言 (喂 BM25 + text tower)
- `facets`: `{style: minimalist, color: white/wood, budget_usd: <500}` (结构化过滤)
- `negative_terms`: ["industrial", "black metal"]
- `image_embed`: 若有图片输入, 直接 reuse

### 4.2 Multi-Retriever Fusion
三路并行检索, top-200 each:

1. **Dense ANN on pin embedding** (复用 T-P1-409 的 256-dim pin embedding, ScaNN + PQ). Query 向量 = LLM encoder 抽的 query embedding (用对比学习 align 到 pin 空间).
2. **Sparse BM25** on pin title + board + OCR text. 补语义漏召回 (长尾精确词, 品牌名, 产品型号).
3. **Personalized** = user embedding · pin embedding, 从 user top-K recent-interest clusters 里各召 top-50.

Fusion: **RRF** (reciprocal rank fusion, k=60), 得 top-400 候选.

### 4.3 Re-ranking
- **Stage-1 ranker**: LightGBM, 特征 = [RRF rank, BM25 score, dense sim, personalized score, freshness, pin quality, engagement rate, repetition penalty w/ `already_shown`]. 输出 top-50.
- **Stage-2 LLM reranker** (可选): 只在 compare / refine 意图时启用. 把 top-20 pin metadata 塞进 LLM, 让它按语义匹配 re-rank. 成本高, 默认关闭.

### 4.4 Diversity & Anti-Repetition
- MMR (λ=0.3) on pin embedding, 避免同一 board 刷屏.
- Filter `already_shown_pin_ids` from state.
- Category balance: 确保 top-12 里最多 6 个来自同一 L2 category.

---

## 5. Grounded Generation

### 5.1 为什么需要 grounding
纯生成 LLM 会 hallucinate pin_id / 假装引用不存在的 pin. Grounding = 让 LLM 只能从 retrieval 返回的 top-50 pins 里挑, 且必须引用 pin_id.

### 5.2 Prompt 结构
```
[system] You are Pinterest Assistant. Only cite pins from the provided list.
Output JSON: {"reply": "...", "pin_ids": ["p_123", ...], "intent": "ask-pins"}.
[user profile] persona=first-time remote worker, style_affinity=[scandi, japandi]
[dialog state] active_topic=..., constraints=..., negative=...
[candidate pins]
  p_123: title="Walnut floating desk", colors=[wood, white], board="WFH 2025"
  p_456: ...
  (top-50 with 1-line summary each)
[user turn] "show me desks under $500"
```

### 5.3 模型选择
- **生成 LLM**: 7B instruction-tuned (Llama-3 / Mistral fine-tune on Pinterest conv data). INT8 quantized, vLLM serving, ~80 tok/s per GPU.
- 为什么不用 70B: latency (first-token 预算 1.5s) + cost. 7B fine-tune on domain data 在相关性评测上比 70B zero-shot 高 6%.
- **Structured decoding**: 用 outlines / xgrammar 强制 JSON schema, 杜绝 pin_id 格式错误.

### 5.4 Citation Enforcement
后处理: 解析 `pin_ids`, 丢弃任何不在 retrieved top-50 的 id (防 hallucination). 若 <3 个合法 pin, fallback 到 stage-1 ranker 的 top-12.

### 5.5 Streaming
- Text tokens 先流式返回 (first-token 800ms typical), pin grid 在生成结束一次性 render (避免闪烁).
- 前端 WebSocket, 后端 SSE.

---

## 6. Safety & Moderation

双向 (输入 + 输出) 分层防御:

### 6.1 Input-side
| 层 | 检测内容 | Action |
|----|---------|--------|
| PII detector | 电话, 地址, 身份证 | Redact before LLM |
| Toxicity classifier (Perspective-style) | 辱骂/仇恨 | Soft warning or decline |
| Self-harm / medical crisis | "I want to hurt myself" | **Hard override**: show crisis hotline, skip retrieval |
| Jailbreak detector | prompt injection ("ignore previous…") | Strip injection, log to security |

### 6.2 Retrieval-side
- Pin-level safety score (从 Trust & Safety pipeline 继承) 作为 hard filter: block adult, graphic, misinfo.
- Age-gate: under-18 用户使用更严格阈值.
- Ads disclosure: 若 top-12 含 promoted pin, reply 里必须带 `"(sponsored)"` 标签, 由后处理强制插入.

### 6.3 Output-side
- LLM 输出再过一次 toxicity / policy classifier.
- Regex + classifier 检测 medical / legal / financial 建议 ⇒ 附加 disclaimer 或 decline.
- Pin grid 二次 safety scan (catch 新上线、尚未被离线管线扫描的 pin).

### 6.4 Kill Switch
每个模块 (retrieval / LLM / reranker) 都有独立 feature flag, 可单独降级为: `retrieval-only` (无 LLM 文字) 或 `pure-LLM` (无 pin). 用于事故快速止血.

---

## 7. Training & Data Pipeline

### 7.1 Label 来源
- **Conversation quality**: human rater 对 (reply, pin grid) 打 5 分 (relevance / helpfulness / safety). 每日 5K 样本.
- **Implicit engagement**: 用户在 chat 内对 pin 的 click / repin / long-press / hide. 作为 RL 信号.
- **Refine → success**: 若 refine turn 后用户有 repin, 视为 positive.

### 7.2 Stage-wise 训练
1. **SFT**: 100K 高质量人写 conversation (Pinterest 内部 annotator), 学 pin citation 格式 + 风格.
2. **RLHF / DPO**: 用 human preference 对 (reply_A, reply_B), DPO 比 PPO 更稳定, 用 50K pair.
3. **Retrieval alignment**: 用对比学习把 LLM query encoder 对齐到 pin embedding 空间 (in-batch negatives + hard negatives from BM25 mismatches).
4. **Intent classifier**: 独立训练, 每周增量.

### 7.3 Online Learning
- User-level: 最近 session 的 hide/repin 实时更新 user embedding (15-min streaming, 复用 embedding 管线).
- Model-level: 每周 SFT 增量 (新 annotator 数据) + 每月 DPO 重训.

---

## 8. Serving Architecture

| 组件 | 硬件 | Latency budget | Scale |
|------|------|---------------|-------|
| Input safety | CPU classifier | 20ms | 2K QPS |
| Intent (built-in) | 与生成 LLM 合并 | 0ms | - |
| Query rewriter | 轻 LLM (3B, on same GPU pool) | 150ms | 2K QPS |
| ANN retrieval | ScaNN shard × 32 | 30ms | - |
| BM25 | Elasticsearch | 40ms | - |
| Personal re-rank | CPU (dot product) | 10ms | - |
| Stage-1 LGBM ranker | CPU | 15ms | - |
| Generation LLM (7B) | A100 × N, vLLM, INT8 | first-token 800ms, total 2s | 2K QPS, ~200 replicas |
| Output safety | CPU | 30ms | - |

**End-to-end P99**: first-token ~1.3s, full response (text + grid) ~2.8s.

**Caching**:
- Query-level cache (hash of `compact_state + last_user_turn`) 对重复热问 hit 率 ~15%.
- User embedding cache (Redis, 15-min TTL).
- Pin metadata cache (per pin_id, 1h TTL, 5B entries ⇒ 分片 memcached).

---

## 9. Monitoring & Evaluation

### 9.1 Offline
| 指标 | 方法 | 目标 |
|------|------|------|
| Retrieval Recall@50 | 人工标注 query→relevant pin set | >0.75 |
| Grounding faithfulness | citation pin 是否真匹配 reply (LLM-as-judge) | >0.95 |
| Intent F1 | held-out test | >0.90 |
| DPO win-rate vs baseline | pairwise human eval | >55% |
| Safety leakage | red-team prompt 通过率 | <0.5% |

### 9.2 Online
- **Conversational NDCG**: 按 turn 内 pin click/repin 加权.
- **Turn→repin rate**: 一个 turn 里至少一个 pin 被 repin 的比例.
- **Session length**: 健康对话通常 3-6 turn, 过短/过长都异常.
- **Refine rate**: 用户连续 refine 说明首轮不准; refine>2 视为 retrieval 失败.
- **Safety incident rate**: 每 1M turn 的 human-reported violation.
- **Latency**: first-token P50/P99, full P50/P99.

### 9.3 A/B
- 主指标: **weekly active chat users × avg repin/session**.
- 护栏: 整体 home feed DAU 不下降 (cannibalization check), safety incident 不上升.

---

## 10. 常见 Follow-ups (面试官必追)

1. **Q: 如何避免 LLM hallucinate 不存在的 pin?**
   A: (a) structured decoding 强制 JSON; (b) 后处理把 retrieved set 外的 pin_id 全部丢弃; (c) fallback 到 stage-1 ranker top-12; (d) 离线 grounding faithfulness 监控 <0.95 触发告警.

2. **Q: 冷启用户 (无历史) 怎么办?**
   A: 降级为纯内容检索 (BM25 + dense, 无 personalization re-rank), query rewrite 主动问 persona clarify ("what's the room size / style?"), 首轮后立刻累积 session-level state.

3. **Q: 多轮 context 爆炸如何压缩?**
   A: compact state JSON 替代 raw history, 超过阈值触发 summarization LLM 保留 active_topic + constraints + 最近 2 turn 原文. 图片用 CLIP embedding 代替 raw.

4. **Q: 怎么平衡 latency 和质量?**
   A: 分层: chit-chat 用 3B 模型 (200ms), ask-pins 用 7B, compare 才启用 stage-2 LLM reranker. 流式输出让用户感知 first-token, 检索并行.

5. **Q: 个性化 vs 探索如何权衡?**
   A: Personal re-rank 权重随 session 长度衰减 (首轮重 personalization, 后续重 query match); ε-greedy 保留 10% 探索 slot; refine 意图触发时降低 personalization 权重 (用户主动纠偏).

6. **Q: Safety 被绕过 (jailbreak) 怎么办?**
   A: 多层独立防御 (input + retrieval filter + output), 任一命中即 decline. 专门 jailbreak detector (fine-tune on adversarial prompts), red-team 数据每周更新. 出事走 kill switch 降级 retrieval-only 模式.

7. **Q: 如何做离线评估?**
   A: 固定 eval set (5K 多轮 conversation, 人工标 reply 参考 + 相关 pin set). 指标: Recall@50, grounding faithfulness (LLM-as-judge + 人工抽查), DPO win-rate, safety red-team 通过率. 发版前必须全部通过阈值.

8. **Q: 商业化 (ads) 怎么接?**
   A: Ads 作为独立 retriever 召 top-20, 与 organic 融合前先过 pacing / budget 模型, 限制 per-grid 最多 2 个 sponsored, 强制 `(sponsored)` disclosure. CTR model 仍用现有 ads stack, 仅变更展示 surface.

9. **Q: 如何防止 reply 泄露 user PII 到 LLM 日志?**
   A: Input PII redactor 在 LLM 调用前执行, 日志只存 redacted token. 生成端再扫一次输出. Long-term state 存用户 profile 只保留 aggregate (top category, style), 不存 raw text.

10. **Q: 假如 7B 模型推理 GPU 不够如何降级?**
    A: (a) 缓存热问 reply (15% hit); (b) chit-chat/intent 合并路由到 3B; (c) 非首页 surface 降级为 retrieval-only + 模板化文案; (d) 末端 kill switch 关闭生成, 只返回 pin grid.

---

## 11. 可选深入方向 (面试官问 "还有什么?")

- **Multimodal**: 用户直接发图 "找类似的沙发" ⇒ CLIP image embedding 直接当 query 向量.
- **Tool use**: LLM 调用 `search_shopping_pins(budget, category)` 等工具, 结构化查询比自由文本更精确.
- **Long-term memory**: 跨 session 保留用户兴趣档案 (opt-in), 用 summary + embedding 双存.
- **Agentic refine**: bot 主动问 clarify question ("什么风格?") 而非被动等用户 refine.
- **Evaluation harness**: 自动化 adversarial test suite + LLM-as-judge 持续回归.
- **On-device small model**: 极低延迟 chit-chat 可跑在端侧 phi-3-mini, 仅 ask-pins 调云端.
