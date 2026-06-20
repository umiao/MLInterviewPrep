## 速查表 (Cheat Sheet) -- Yelp Restaurant Recommendation

```text
User Request (user_id + geo + time + query)
  |
  v
Hard Eligibility Filter (geo radius + open-now) [Twist 4]
  |
  v
Aspect-Overlap Retrieval (50-dim sparse cosine)
  |
  v
Candidate Set (~hundreds)
  |
  v
Multi-Task Ranking (p_visit, p_positive_postvisit, p_dwell)
  |
  +-------- Freshness Multiplier (photo + recent visit) [Twist 3]
  |
  v
Page Re-rank (blend aspect match + proximity + recency)
  |
  v
Ordered List (~10-25 restaurants)
```

**核心**: 所有阶段共享同一个 **Aspect Taxonomy** (LLM teacher离线抽取, 周更蒸馏student, >20新review触发再抽)。用户侧偏好 (Twist 2) 同样映射到这个taxonomy, 实现双侧桥接。

---

**关键词块 (Industry Jargon)**  
- **LLM (Large Language Model) extracted aspect graph**: 用大模型从review文本中抽取~50维的细粒度aspect向量 (cuisine/vibe/dietary/group-size/occasion), 取代传统rating-CF。  
- **Self-referential user profile**: 用户偏好权重从用户自己写的review推断, 而非显式设置或点击信号。写过多次"loved the quiet patio" -> 推断`quiet`, `outdoor`偏好。  
- **Freshness multiplier (乘性)**: 近期photo信号 + visit dwell-time作为乘性因子修正历史aspect prior, 抵抗餐厅质量漂移。  
- **Hard eligibility (geo + open-now)**: 必须在候选生成阶段硬过滤, 不能作为soft ranking feature。closed且完美aspect match -> 评分0。  
- **Post-visit-positive objective**: 优化目标不是listing click, 而是visit后的正向信号 (回访 / positive review / dwell > 30s)。  
- **Multi-task ranking**: 同时预估visit概率、post-visit正向概率和listing dwell概率, 最终融合以对齐上述目标。  
- **IPS (Inverse Propensity Score) counterfactual replay**: 离线评估修正长尾曝光偏差, 用于strategy的可靠对比。  
- **SLO (Service Level Objective)**: 200ms p99延迟预算, 10M餐厅规模下地理预过滤后进入精排。

---

**Senior 信号表**

| 维度 | 不及格答法 | Staff Golden 答法 |
|------|-----------|------------------|
| Framing | 当成 rating-CF 题, lift来源仅靠rating微调 | 明确指出 aspect-level matching 从review text来, LLM aspect graph 是压舱石, rating-CF有硬天花板 |
| Retrieval | 用 two-tower user embedding, 将aspect当作普通feature输入 | 共享 aspect taxonomy, 用 sparse cosine 进行 aspect overlap retrieval, 候选集 interpretability 强 |
| Ranking | 将 geo/open-now 作为 soft loss feature; 将 freshness 当作一个普通特征输入模型 | 硬 eligibility 在 retrieval 前单独过滤; freshness 作为乘性 multiplier 修正 prior, 并配套 authority weighting 防 photo-bomb |
| Eval | A/B 只看 click lift | 切片评估 (aspect x review-count bucket) + IPS counterfactual replay + A/B 用 post-visit-positive lift |
| Bias | 认为所有用户 profile 都能充分个性化 | 承认低写评用户 profile 欠定, 设计 cohort prior + 平滑 blending, 并监控冷启颠簸 |

---

**Mini 术语表**

| 术语 | 一句话 |
|------|--------|
| LLM (Large Language Model) | 大语言模型, 用于从review文本中提取结构化的aspect graph |
| CF (Collaborative Filtering) | 协同过滤, 传统基于用户-物品交互的方法, 本题中天花板明显 |
| IPS (Inverse Propensity Score) | 反向倾向分数, 用于离线策略评估时修正曝光偏差 |
| SLO (Service Level Objective) | 服务水平目标, 本题中为 200ms p99 延迟 |
| MAU (Monthly Active Users) | 月活跃用户数, 本题规模 ~30M |
| Aspect Taxonomy | 细粒度的餐厅属性分类体系 (~50维), 是检索和排序的共享桥梁 |
| Freshness Multiplier | 基于近期photo和visit的乘性修正因子, 反映餐厅质量漂移 |
