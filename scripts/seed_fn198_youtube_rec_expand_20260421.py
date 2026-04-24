"""Seed SD-YT-02: Expand framework_nodes id=198 (Real-Time Recommendation).

Adds YouTube-specific ML content into the existing 4a/4b deep dives and
appends a NEW 4e frontier subsection (LRM + Semantic IDs + RQ-VAE). Additive
only: preserves all existing 19 headers and existing numbered lists.

Three insertion blocks (each anchor appears exactly once in pre-state):

  Block A (4a Two-Tower additions): Covington 2016 DNN recall tricks
    (user-vector = last-hidden-layer, item_emb = softmax input weights,
    example age feature, next-watch target, extreme multiclass) + multi-
    source retrieval (7 parallel recall paths + source_score as ranker
    feature) + frequency features (historical impression frequency to
    prevent sequential sameness). Inserted at end of 4a.

  Block B (4b Ranking additions): Zhao 2019 MMoE specifics (share-bottom
    -> MMoE, engagement vs satisfaction negative transfer) + watch-time
    weighted LR output + shallow tower for position/device bias (Daiwk) +
    training-sample policy (all surfaces, per-user equal weighting) +
    query vs impression features distinction. Inserted after MMoE formula
    explanation and before 多目标融合打分 block.

  Block C (NEW 4e LRM subsection): Large Recommender Models background,
    Semantic IDs via RQ-VAE + continued pre-training + generative
    retrieval + cold-start advantage + serving-cost reality + YouTube
    scale numbers + cross-link to id=21 Content-to-Feature Bridge +
    3 interview probes. Inserted between 4d wrap-up and section 5.

Idempotent:
  - Detects post-expansion state via three characteristic markers
    ("Covington", "shallow tower", "LRM"). If all three present -> [SKIP].
  - Partial state (some but not all markers) -> [FAIL] for manual review.

DB-backup-guarded:
  Before any write, copies the target DB file to
  <db>.bak.<timestamp>_pre_expand_fn198. Skip via --no-backup.

AC grep checks (post-expansion, applied to final description):
  Covington>=1, Zhao>=1, 'watch-time'>=2, 'Semantic ID'>=2,
  LRM>=3, RQ-VAE>=1, 'shallow tower'>=1, 'example age'>=1.

  All 19 existing section headers must still be present.

Target length: 32000-36000 chars (net +4000-8000).

Usage:
    python scripts/seed_fn198_youtube_rec_expand_20260421.py [--no-backup]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.backend.database import SessionLocal, get_engine, init_db  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402

TARGET_ID = 198

# Idempotency markers: all three must be present to count as already-applied.
MARKERS = ("Covington", "shallow tower", "LRM")

# Existing section headers (must all survive the expansion).
EXISTING_HEADERS = [
    "# Real-Time Recommendation System (L5 Design)",
    "## Prerequisites",
    "## 1. Requirements Clarification",
    "## 2. Capacity Estimation",
    "### 请求链与召回扇出",
    "### Embedding 与物品库",
    "### Feature Store 分层",
    "### Event Log 与带宽",
    "## 3. High-Level Architecture",
    "## 4. Deep Dives",
    "### 4a. Two-Tower Retrieval + ANN",
    "### 4b. Ranking: Deep Models + Multi-Task Learning",
    "### 4c. Re-Ranking",
    "### 4d. Cold Start & Exploration",
    "## 5. Reliability & Monitoring",
    "## 6. Summary & Tradeoffs",
    "## Interview Q&A",
    "## Self-Check",
    "## L5 Tradeoff Matrix",
]

# ---------------------------------------------------------------------------
# Block A: 4a Two-Tower additions (Covington + multi-source + frequency).
# Anchor = end of existing 4a paragraph, before "### 4b." header.
# ---------------------------------------------------------------------------

BLOCK_A_ANCHOR = (
    "ANN 扩容路径按 item_id hash 分 32 shards、每 shard 8GB 内存、"
    "检索 fan-out 32 × top-50 → 合并精确 rerank top-500；"
    "边缘场景上新物品走 incremental HNSW、日级全量 rebuild 兜底、"
    "shard 失效时用其他 31 shards 降级召回保持主流程不中断。\n"
    "\n"
    "### 4b. Ranking: Deep Models + Multi-Task Learning (精排)"
)

BLOCK_A_INSERT = (
    "ANN 扩容路径按 item_id hash 分 32 shards、每 shard 8GB 内存、"
    "检索 fan-out 32 × top-50 → 合并精确 rerank top-500；"
    "边缘场景上新物品走 incremental HNSW、日级全量 rebuild 兜底、"
    "shard 失效时用其他 31 shards 降级召回保持主流程不中断。\n"
    "\n"
    "**YouTube 实战细节 (Covington 2016 DNN recall 论文)** 有四个让线上"
    "召回大幅提升的 trick 必须同框记住：(a) **user vector 从 last-layer "
    "activation 取**——不是输入特征的平均、而是 MLP 最后隐层的输出作为"
    "用户侧 embedding；**item embedding 直接复用 softmax 输入权重**，"
    "这样 $u \\cdot v$ 内积是模型在训练期间就显式学习的相似度指标、"
    "不是后期硬拼的内积。(b) **example age 特征 (视频从上传到当前样本"
    "的相对时间) 训练时灌、serving 时置零**——原始点击数据天然对老视频"
    "偏好 (老视频累计曝光多)；把 example age 作为显式特征训练、"
    "推理时固定为 0 或未来的预测 horizon，可以抵消 ML bias toward old "
    "viral content 的倾向、让模型预测 \"如果这个视频是新的会有多吸引人\"。"
    "(c) **target 选 next-watch 而非随机 held-out**——如果从用户全部"
    "观看历史里随机留一个做 label 会泄漏后续 session 的信息造成 "
    "sequential episode leak；用 \"下一条将要看的视频\" 做 label 更贴近"
    "线上 serving 场景。(d) **extreme multiclass + sampled softmax**——"
    "把召回建模为 500M 类的多分类问题、用 sampled softmax + log-Q "
    "correction (前面已讲) 让训练可行。这四个 trick 在后来的工业推荐 "
    "(TikTok / Meta Reels / Netflix) 都被沿用、是 two-tower 工业实现的"
    "必读手册。\n"
    "\n"
    "**多路召回 (multi-source retrieval)** 是 YouTube / TikTok 线上工业"
    "系统的默认形态、不是只跑 one two-tower：并行召回源通常包括 (1) "
    "**collaborative filter 路**——item-CF co-visit 矩阵、召回 \"和你"
    "看过类似的人也看过\"；(2) **two-tower 语义召回路**——上面讲的"
    "主干；(3) **subscription / 关注路**——用户订阅/关注作者的新发布"
    "视频强制进入召回池；(4) **search history 路**——最近搜索词语义"
    "检索相关视频；(5) **topic-trending 路**——当前热点话题 + 用户兴趣"
    "交集；(6) **item-item related 路**——从用户刚看过的视频出 related "
    "list；(7) **fresh upload 路**——新上传冷启专用池。Ranker 不仅接收"
    "候选 item、还接收 **哪一路 nominated + 该路的 source_score** "
    "作为 ranking 特征，让精排自己学会 \"CF 路的高分可信度\" 与 "
    "\"fresh upload 路需 discount\" 的差异化融合。单塔式纯 two-tower "
    "只是教科书架构，真实线上必须多路兜底。\n"
    "\n"
    "**Frequency features (历史曝光频率特征)** 在 YouTube 2019 Rangadurai "
    "等的论文中被单独强调：每个 (user, item) 对都记录历史 impression "
    "频率 (当前 session 内 + 过去 24h + 过去 7d 三个窗口)，作为精排特征"
    "输入。作用是**防止 sequential requests 返回相同列表**——如果某视频"
    "被连续曝光 3 次未点击、它的 frequency 特征会抑制它再次排到 top；"
    "没有这个特征、两塔 + MMoE 会在用户侧 embedding 变化前反复推同一"
    "视频造成用户疲劳。这是工业 recommender 与玩具 recommender 的典型"
    "区别：公开 benchmark 数据集没有 \"前 3 次曝光\" 的语境、学术模型"
    "从来不加这个特征、但线上系统缺了它 CTR 会直接掉 3-5%。\n"
    "\n"
    "### 4b. Ranking: Deep Models + Multi-Task Learning (精排)"
)


# ---------------------------------------------------------------------------
# Block B: 4b Ranking additions (Zhao + watch-time + shallow tower + policy).
# Anchor = MMoE formula explanation ending, before "多目标融合打分".
# ---------------------------------------------------------------------------

BLOCK_B_ANCHOR = (
    "其中 $g_k$ 是任务 $k$ 的 gate 网络 (softmax 输出 n 维权重)、"
    "$E_j$ 是第 $j$ 个共享专家、$h_k$ 是任务特定输出层；"
    "不同任务通过独立 gate 选择不同的专家组合缓解负迁移。\n"
    "\n"
    "多目标融合打分 (DoorDash Universal Ranker 风格)："
)

BLOCK_B_INSERT = (
    "其中 $g_k$ 是任务 $k$ 的 gate 网络 (softmax 输出 n 维权重)、"
    "$E_j$ 是第 $j$ 个共享专家、$h_k$ 是任务特定输出层；"
    "不同任务通过独立 gate 选择不同的专家组合缓解负迁移。\n"
    "\n"
    "**Zhao 2019 MMoE YouTube 应用细节**: 原始 YouTube ranker 是 "
    "share-bottom 架构 (所有任务共享底部 MLP、只在最后一层分 task head)；"
    "替换为 MMoE 后、引入 $n$ 个共享 expert 网络 + 每任务独立 gate 网络、"
    "让 **engagement 类任务** (click、watch-time) 与 **satisfaction 类"
    "任务** (like、dismiss、rating) 各自学到更合适的 expert 权重分布、"
    "显式缓解了 share-bottom 下两类任务互拉梯度的 negative transfer "
    "问题。论文报告 watch-time 与满意度联合指标均正向、不存在单指标"
    "换另一指标的 tradeoff。这是 Zhao et al. RecSys 2019 的主贡献。\n"
    "\n"
    "**Watch-time weighted LR (watch-time 加权逻辑回归)** 是 YouTube "
    "排序的核心目标函数改动：输出层不直接预测 click 概率、而是用 "
    "**weighted logistic regression**、每个正样本 (click) 的 loss 权重 "
    "= 观察到的 watch-time (秒数)、负样本权重为 1。数学上相当于把"
    "点击事件按 watch-time 复制多次作为正样本、训练时直接优化**期望 "
    "watch duration**、规避 clickbait 陷阱里 \"高 CTR 但 0 秒退出\" 的"
    "假点击。线上效果是 watch-time 总时长提升的同时 early-drop "
    "(< 5 秒退出) 比例显著下降。类比到电商场景等价于把 pCVR 换成 "
    "GMV-weighted 样本、任何 \"点击后质量指标\" 都可以通过这种 "
    "sample-weighting 直接进入 LR 的目标函数。\n"
    "\n"
    "**Shallow tower for bias correction (浅塔偏置校正)** 是叠在 MMoE 之上"
    "的专门结构、用来显式学习 **position bias** (曝光位置的固有点击衰减)"
    "和 **device bias** (手机 / 平板 / TV 不同 UI 下点击模式差异)——把"
    "position feature (训练时是真实曝光位置、serving 时固定为某个中位值"
    "如 5) 和 device feature 喂给一个 1-2 层的浅 MLP、它的输出在 MMoE "
    "logits 之上做 **linear bias correction** (logit 空间相加)；"
    "serving 时 position 置为 fixed constant、device 按当前请求。这样 "
    "MMoE 主塔学的是 \"用户-物品\" 真实匹配分数、shallow tower 吸走"
    "位置 / 设备的解释力，避免主塔学到 \"排在位置 1 更受欢迎\" 这种"
    "反向因果。Daiwk 2020 在 YouTube 上线验证显著减少了 list 顶部过度"
    "利用。\n"
    "\n"
    "**Training-sample policy (训练样本策略)** 有两条 YouTube 明确的工程"
    "约定：(1) **样本来自所有 YouTube 场景**——不仅仅是 recommender "
    "自己推出去的结果、也包括搜索、订阅、首页之外的各种入口。"
    "如果只用 recommender 自己的曝光训练会形成 model-induced selection "
    "bias、模型越推什么越学到什么、候选空间逐渐收窄、长尾永远摸不到"
    "训练梯度。(2) **每用户等权 (equal-per-user weighting)**——重度"
    "用户可能一天贡献 100+ 样本、轻度用户只有 1-2 条；不做 per-user "
    "归一化会让 loss 被重度用户主导、模型偏向头部活跃用户偏好、"
    "尾部用户体验退化。这两条都是 L5 信号、在面试中被问到训练偏差的"
    "时候点出来立刻加分。\n"
    "\n"
    "**Query features vs impression features 分离**：YouTube ranker "
    "明确把特征分成两类，**query features** (用户侧 + 上下文、如 "
    "user_id、last-watch、country、device、time-of-day) 每次请求计算"
    "一次、所有候选共享；**impression features** (候选 item 侧、如 "
    "video_id、author、topic、CTR prior、historical frequency) "
    "每候选计算一次。这个工程切分让精排 GPU 批推时 query features "
    "**broadcast**、impression features **stack**、计算与内存复用"
    "显著——同一个 user 塔 forward 只跑一次、不是 300 个候选各跑一次。"
    "MLSys 层面直接决定 350K invocations/s 的吞吐能不能达到、不是"
    "\"优化无关的小事\"。\n"
    "\n"
    "多目标融合打分 (DoorDash Universal Ranker 风格)："
)


# ---------------------------------------------------------------------------
# Block C: NEW 4e subsection (LRM + Semantic IDs + RQ-VAE + serving cost).
# Anchor = 4d wrap-up line, before "## 5. Reliability" header.
# ---------------------------------------------------------------------------

BLOCK_C_ANCHOR = (
    "四个 deep dive 共同组成精排漏斗的骨架：two-tower 负责宽召回、"
    "DCN-v2+MMoE 负责精排多目标、MMR 负责重排多样性、"
    "硬配额+content pretrain 负责冷启防埋没，四段一起回到 §2 的"
    "延迟预算数字上形成闭环。\n"
    "\n"
    "## 5. Reliability & Monitoring (5m)"
)

BLOCK_C_INSERT = (
    "四个 deep dive 共同组成精排漏斗的骨架：two-tower 负责宽召回、"
    "DCN-v2+MMoE 负责精排多目标、MMR 负责重排多样性、"
    "硬配额+content pretrain 负责冷启防埋没，四段一起回到 §2 的"
    "延迟预算数字上形成闭环。下面 §4e 单独讨论 2024-2025 的生成式"
    "推荐前沿、作为对主干漏斗的展望补充。\n"
    "\n"
    "### 4e. Large Recommender Models (LRM) + Semantic IDs (2024-2025 frontier)\n"
    "\n"
    "2024 年之后的 recommendation 前沿是把**生成式大模型**的 recipe "
    "搬进推荐召回。YouTube / Meta / TikTok 都在研究 **Large Recommender "
    "Models (LRM)**——基于 Gemini / LLaMA 架构的生成式推荐模型、"
    "原生处理视频 / 商品作为 token 序列。主推动力是传统 two-tower + "
    "MMoE 在**冷启与长尾物品**上天花板明显：content-based features "
    "(textual、visual) 在两塔架构里只能从 item tower 侧注入、表达力"
    "弱于 LLM 的海量预训练带来的世界知识。\n"
    "\n"
    "LRM 的关键技术路径有三层：\n"
    "\n"
    "**第一层：Semantic IDs via RQ-VAE (语义 ID 量化)**——传统推荐用"
    "整数 item_id、每 item 独立学一个 embedding、500M items 要 500M × "
    "128d 的 embedding table。Semantic ID 做法是先用 **Video-BERT** "
    "风格的 Transformer encoder 把 item 的文本 + 视觉 + 音频输入编码成"
    "稠密 embedding、再用 **Residual Quantization Variational "
    "AutoEncoder (RQ-VAE, 残差量化变分自编码器)** 把这个稠密 embedding "
    "压缩成 4-8 个离散 token 序列 (每个 token 来自 K=256 / 512 的 "
    "codebook)。这样每个视频变成一个短 token 序列、共享 codebook 极大"
    "减少 embedding 参数量、且语义相近的视频 token 前缀相同 "
    "(比如所有 \"烹饪 / 意大利面\" 类视频前 2 个 token 一致)、天然"
    "支持 prefix-based category retrieval。Semantic ID 也是后续 LRM "
    "把视频当语言 token 处理的技术前提、没有它 LLM 词表爆炸 (500M "
    "整数 id 做词表完全不可能)。\n"
    "\n"
    "**第二层：Continued pre-training (\"YouTube 语言\")**——在 Gemini "
    "的通用文本预训练之上、用 YouTube 平台日志 (watch sequences、"
    "comments、captions、related lists) 做第二轮 pre-training、让模型"
    "**同时学习英语 + YouTube 视频语言**。这一步让 LRM 具备**跨模态"
    "的下一视频预测能力**——输入 \"用户看了 [sem_id_1][sem_id_2]"
    "[sem_id_3]、下一条看什么\" 可以直接 autoregressive 生成 "
    "[sem_id_4]。\n"
    "\n"
    "**第三层：生成式召回 (generative retrieval)**——推理时 LRM 以用户"
    "历史 (转成 sem_id 序列) 为 context、autoregressive 生成候选 "
    "sem_id；把生成的 sem_id 映射回物品即是召回结果。相比 two-tower 的"
    "\"编码 + ANN 检索\" 两步、生成式召回直接 \"一步出候选\"、天然"
    "规避 ANN 索引维护成本 (无需 HNSW 图重建、无需 fan-out 32 shards)。\n"
    "\n"
    "**冷启优势**是 LRM 相对传统 recommender 最明显的胜点：新上传视频"
    "没有任何交互信号、两塔只能 fallback 到 content tower；而 LRM 通过"
    "sem_id 的 prefix 共享可以从语义相近的老视频迁移强先验、long-tail "
    "与 fresh content 的 CTR 提升实测 +2-5%、比 content pretrain + "
    "硬配额兜底更强。这是把 LRM 推进工业线上的第一个商业化 case。\n"
    "\n"
    "**serving 成本现实**：生成式 LRM 单次推理比两塔昂贵 100-1000×，"
    "直接替换线上 pipeline 在 YouTube 规模 (350K invocations/s) 完全"
    "不可行。现阶段的工业落地范式是 **hybrid**：(a) **LRM 作为辅助"
    "召回源**注入到多路召回体系 (§4a 讲的 7 路之外新增 1 路)、每请求"
    "只取 top 10-50 生成候选、对精排吞吐压力有限；(b) **LRM 离线打标**"
    "——夜间 batch 跑 LRM 对全量新视频生成 content embedding + 语义 "
    "tag、写入 feature store、线上精排只查 embedding 不做 LRM "
    "inference；(c) **95%+ cost reduction** 成为必备工程目标——Google "
    "内部报告提到通过 KV cache 复用、quantization-aware training、"
    "speculative decoding 等优化把 LRM serving cost 压下来是 2025 年的"
    "关键基础设施投入。结论：**LRM 是 auxiliary retrieval + offline "
    "tagging**、现阶段 NOT replacing 线上 two-tower + MMoE 主 pipeline**、"
    "面试中把这个 hybrid 范式讲清楚比吹 LRM 银弹更有信号。\n"
    "\n"
    "**YouTube 平台量级参考**: 日上传视频 **500h+**、月 DAU **2B+**、"
    "watch QPS 峰值 **70K+**、总 watch-time **10 亿+ 小时 / 日**——"
    "这些数字让 \"把整条 pipeline 换成 LRM\" 的成本现实立刻落地、"
    "也是 §1 requirements clarification 里 DAU 100M 这个通用锚点在真实"
    "YouTube 场景下的放大版 (2B vs 100M 差 20×)。L5 答题的核心是"
    "**承认 LRM 是未来方向、同时给出当前 hybrid 落地路径**、不要把它"
    "当成银弹。\n"
    "\n"
    "**与 id=21 Video Streaming 的桥接**: 视频流媒体的 **content-"
    "understanding pipeline** (frame embedding / ASR / OCR / 音频 "
    "fingerprint / topic classifier / thumbnail CTR) 同时为 search "
    "索引、Content ID 反盗版、和此处的 recommendation 提供 multimodal "
    "features；这条 pipeline 在 id=21 §7 Content-to-Feature Bridge "
    "有完整描述。Recommendation 侧消费的是 pipeline 下游的 item "
    "embedding + 语义 tag、不重复投入视频解码与特征提取的基础设施。"
    "这是 L5 的 platform-thinking signal——把两个 system design 题"
    "(视频存储 + 推荐) 用一条 content pipeline 打通、证明你理解平台级"
    "基础设施共用、而不是把每个 feature 都当成独立项目从零搭。\n"
    "\n"
    "> **常见追问**:\n"
    "> 1. \"LRM 是不是会替换掉 MMoE？\" —— 中期内不会。精排仍需多目标融合"
    " (CTR / watch-time / like / 满意度)、MMoE 的 per-task gate + "
    "calibration 栈在 LRM 之上仍有独立价值；LRM 的位置是召回 + content "
    "understanding 的新一层、不是精排替换。\n"
    "> 2. \"Semantic ID 的 codebook 怎么维护？\" —— 离线训练一次 "
    "codebook 固定 6-12 月、新视频只做 encode 不改 codebook；年度或"
    "半年级别用新视频数据重新训 codebook 时做一次全库 re-encoding "
    "批作业、下线 serving 侧需要 dual-read 过渡 1-2 周。\n"
    "> 3. \"生成式召回的 diversity 怎么保证？\" —— autoregressive 采样"
    "时加 temperature + top-K sampling、不是 greedy decoding；且 LRM "
    "只作为多路召回之一、最终多样性仍由 4c MMR / DPP 兜底、不依赖 LRM "
    "采样本身的多样性。\n"
    "\n"
    "## 5. Reliability & Monitoring (5m)"
)


# ---------------------------------------------------------------------------
# DB-file backup
# ---------------------------------------------------------------------------


def _backup_db(db_path: Path) -> Path | None:
    """Copy the DB file to a timestamped .bak before mutating.

    Args:
        db_path: Absolute path to the SQLite DB file.

    Returns:
        Path to the backup file, or None if the source does not exist.
    """
    if not db_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.name}.bak.{ts}_pre_expand_fn198")
    shutil.copy2(db_path, backup)
    return backup


def _resolve_db_file() -> Path | None:
    """Return the SQLite DB file path bound to the engine, or None.

    Returns:
        Resolved DB file path, or None if engine is not file-backed SQLite.
    """
    engine = get_engine()
    url = engine.url
    if url.drivername != "sqlite":
        return None
    if url.database in (None, "", ":memory:"):
        return None
    return Path(url.database).resolve()


# ---------------------------------------------------------------------------
# Insertion helpers
# ---------------------------------------------------------------------------


def _apply_insert(
    description: str,
    anchor: str,
    replacement: str,
    label: str,
) -> str:
    """Replace a single anchor occurrence, asserting exactly one match.

    Args:
        description: Full framework_node description body.
        anchor: Anchor substring to locate (must appear exactly once).
        replacement: Replacement string (anchor + new content).
        label: Label for error messages.

    Returns:
        Updated description text.

    Raises:
        RuntimeError: If anchor missing or appears more than once.
    """
    count = description.count(anchor)
    if count == 0:
        raise RuntimeError(
            f"[{label}] anchor not found in description. "
            "Upstream content may have drifted; re-verify anchor strings."
        )
    if count > 1:
        raise RuntimeError(
            f"[{label}] anchor matched {count}x (expected 1). "
            "Pick a more specific anchor."
        )
    return description.replace(anchor, replacement, 1)


def _check_markers(description: str) -> tuple[bool, bool, bool]:
    """Return per-marker presence flags.

    Args:
        description: Framework node description text.

    Returns:
        Tuple of three booleans, one per entry in MARKERS, True iff present.
    """
    return tuple(marker in description for marker in MARKERS)  # type: ignore[return-value]


def _grep_ac_checks(description: str) -> dict[str, int]:
    """Compute AC grep counts on the post-expansion description.

    Args:
        description: Expanded description body.

    Returns:
        Mapping from grep key to case-aware count.
    """
    lower = description.lower()
    return {
        "Covington": description.count("Covington"),
        "Zhao": description.count("Zhao"),
        "watch-time": lower.count("watch-time"),
        "Semantic ID": description.count("Semantic ID"),
        "LRM": description.count("LRM"),
        "RQ-VAE": description.count("RQ-VAE"),
        "shallow tower": lower.count("shallow tower"),
        "example age": lower.count("example age"),
    }


AC_MIN_COUNTS = {
    "Covington": 1,
    "Zhao": 1,
    "watch-time": 2,
    "Semantic ID": 2,
    "LRM": 3,
    "RQ-VAE": 1,
    "shallow tower": 1,
    "example age": 1,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Apply the expansion.

    Returns:
        0 on success or [SKIP]; 1 on failure or partial prior state.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip the DB-file backup step (not recommended).",
    )
    args = parser.parse_args()

    init_db()
    db_file = _resolve_db_file()
    if db_file is not None and not args.no_backup:
        backup = _backup_db(db_file)
        if backup is not None:
            print(f"[BACKUP] {backup.name}")

    db = SessionLocal()
    try:
        row = db.get(FrameworkNode, TARGET_ID)
        if row is None:
            print(f"[FAIL] framework_nodes id={TARGET_ID} not found")
            return 1

        orig = row.description or ""
        print(f"[BEFORE] fn198 description: {len(orig)} chars")

        # Idempotency gate: all three markers present -> already applied.
        flags = _check_markers(orig)
        if all(flags):
            print(
                "[SKIP] fn198 already expanded "
                f"(markers {MARKERS} all present)"
            )
            return 0
        if any(flags):
            # Partial prior run -- refuse to half-apply.
            present = [m for m, f in zip(MARKERS, flags) if f]
            missing = [m for m, f in zip(MARKERS, flags) if not f]
            print(
                f"[FAIL] partial expansion detected. "
                f"Present: {present}. Missing: {missing}. "
                f"Manual inspection required."
            )
            return 1

        # Apply three insertion blocks sequentially.
        new = _apply_insert(orig, BLOCK_A_ANCHOR, BLOCK_A_INSERT, "block_a")
        new = _apply_insert(new, BLOCK_B_ANCHOR, BLOCK_B_INSERT, "block_b")
        new = _apply_insert(new, BLOCK_C_ANCHOR, BLOCK_C_INSERT, "block_c")

        # Invariant: all 19 existing headers must still be present.
        for header in EXISTING_HEADERS:
            if header not in new:
                print(f"[FAIL] expansion deleted existing header: {header!r}")
                return 1

        # AC grep assertions.
        counts = _grep_ac_checks(new)
        failed = [
            (k, v, AC_MIN_COUNTS[k])
            for k, v in counts.items()
            if v < AC_MIN_COUNTS[k]
        ]
        if failed:
            for name, actual, needed in failed:
                print(
                    f"[FAIL] AC grep check: '{name}' {actual}x "
                    f"(need >= {needed})"
                )
            return 1
        for name, actual in counts.items():
            print(f"  [GREP] '{name}' -> {actual}x")

        row.description = new
        db.commit()
        # Also update last_studied_at timestamp if schema has it -- no-op here
        # since timestamp fields are student-progress, not content-version.

        print(
            f"[WRITE] fn198 expanded: "
            f"{len(orig)} -> {len(new)} chars "
            f"(+{len(new) - len(orig)})"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
