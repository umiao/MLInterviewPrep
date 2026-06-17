"""Rewrite company_documents id=52 'Google DNN / Key Papers Gist' to Chinese-prose.

Per T-P1-531 [T-GOOG-CN-52]. Source doc was 0% Chinese (pure English), violating
the project's content_style convention (Chinese narration + English technical terms,
target CJK ratio >= 60%).

Writing discipline (feedback_content_style_cn_en memory):
- Prose narration in Chinese by default
- English technical terms preserved on first occurrence with format
  `**English full name** (acronym, 中文译名)` per section
- Subsequent mentions of the acronym alone are fine
- Math formulas, variable names, complexity notation, and paper citations
  stay in English verbatim
- Structure preserved: 10 papers, each with What / Why-mattered / Architecture
  / Gotcha bullets; cross-cutting talking-points section at end

Idempotent: sentinel `<!-- CN_REWRITE_20260419 -->` near the top. If already
present in stored content, the seeder prints [UNCHANGED] and skips.

Title column NOT changed -- the English title 'Google DNN / Key Papers Gist'
stays as the display title; only content body is rewritten.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- CN_REWRITE_20260419 -->"
DOC_ID = 52


DOC_52 = SENTINEL + """
# Google DNN / Recs & Search Papers — One-Page Gist

这是 Google SWE III / ML 面试的口述素材清单。每篇论文给出四段式纲要——**What · Why-mattered · Architecture · Gotcha**，不是逐字深读，而是能在一两句话里体现熟悉度的"钩子"；面试官追问时再顺势展开到细节。十篇论文按时间与主题编排，从召回层的起源一直走到多任务排序与自监督对比学习，覆盖 Google / YouTube / Pinterest / Airbnb 四条工业推荐主线。

---

## 1. YouTube DNN (Covington et al., 2016)

- **What**：面向 YouTube 视频推荐的两阶段架构，候选生成 **Deep Neural Network** (DNN, 深度神经网络) 叠加排序 DNN。候选生成负责从百万量级物料里粗筛出几百个候选，排序侧再做精细打分，两个模型各有不同的训练目标与特征口径。
- **Why mattered**：这是工业界第一篇把推荐显式拆成两座深度网络塔的大规模论文，彻底取代了传统的矩阵分解基线；"先召回再排序"的 retrieve-then-rank 范式至今仍是工业推荐的默认骨架。任何面试里讲到推荐系统的分层结构，这篇都是绕不过去的起点。
- **Architecture**：候选生成侧把观看向量、搜索向量、人口统计学特征拼接后送入多层感知器，最后对数百万视频做 sampled softmax（负采样 softmax）；线上通过 **Approximate Nearest Neighbor** (ANN, 近似最近邻) 检索用户向量召回候选。排序侧则用更丰富的特征（曝光上下文、新鲜度、视频被观看时的年龄）去预测期望观看时长，头部接一个加权逻辑回归的回归头。两侧共享底层 embedding 但各自独立训练与调参。
- **Gotcha**：**example age** 这个特征（视频上传以来经过的时间）至关重要——去掉它模型会系统性过度推荐老的爆款视频，因为训练样本天然偏向"存活足够久的老视频"。此外，训练目标是预期观看时长而非 **Click-Through Rate** (CTR, 点击率)，就是为了规避标题党刷 CTR 的劣化；这个选型背后是一次用户体验对齐的深思熟虑，面试时值得展开讲。

## 2. DSSM / Two-Tower (Huang et al., 2013; Yi et al., Google, 2019)

- **What**：**Deep Structured Semantic Model** (DSSM, 深度语义模型) / 双塔架构——一个查询塔、一个物品塔各自独立输出向量，内积即相关性，训练端用 in-batch sampled softmax。查询塔处理用户上下文、物品塔处理物品侧特征，两塔彻底解耦是整套设计的灵魂。
- **Why mattered**：双塔解耦使物品向量可以**离线预计算**并通过 ANN 索引（例如 Google 的 ScaNN 或开源的 Faiss）在线召回；这正是 Google、YouTube、Pinterest 等一线推荐系统召回层的事实标准，也是当代 semantic search 的基础结构。如果面试被问"召回层怎么设计"，几乎必然落到双塔上。
- **Architecture**：查询塔与物品塔各自独立做多层感知器或 Transformer 编码，输出先做 L2 归一化再求内积或余弦相似度。训练目标是在 batch 内把正样本从其他 batch 内物品里区分出来，并用 `-log Q(i)` 这一项对采样概率做**偏差修正**（Yi et al. 2019 的 sampling bias correction），以还原全量 softmax 的统计意义。
- **Gotcha**：in-batch 负样本天然偏向热门物品——它们更频繁地出现在 batch 里，因此被当作负样本的概率也更高。不做 `-log Q(i)` 修正会让模型系统性低召回头部物品；而要做修正，就得在线持续估计每个物品的出现频率，工程上并不免费。另一个硬约束是：双塔**无法**直接建模 query-item 的交叉特征（例如"这个 query 含这个词而且 item 属于这个类目"），所有此类交叉只能留给排序层去吃。

## 3. Wide & Deep (Cheng et al., Google, 2016)

- **What**：**Wide & Deep** (W&D, 宽深模型) 把带手工交叉特征的线性模型（宽部分）与一个对 embedding 做多层感知器的深度模型（深部分）**联合训练**，最早部署在 Google Play 商店的 App 推荐里。两部分共享标签但各自算 logit，再加和过 sigmoid。
- **Why mattered**：这是"memorization vs generalization"（记忆 vs 泛化）问题的经典回答——宽部分负责记住"装了这个 app 的用户也装了那个 app"等**稀疏特例**，深部分负责通过 embedding 泛化到组合没见过的场景。由此催生了整个混合架构家族（DeepFM / DCN / xDeepFM），成为工业推荐里几乎所有 CTR 模型的思路源头。
- **Architecture**：宽端是在人工交叉特征上跑逻辑回归，用 FTRL（一种在线学习优化器）更新参数；深端是 embedding lookup 之后接多层感知器，用 AdaGrad 更新；两端的 logit 求和之后再过 sigmoid，端到端做联合随机梯度下降。同一批样本同时更新两端，但用不同优化器是论文的工程细节。
- **Gotcha**：宽部分**仍然要人工做特征交叉**——这恰恰是后续 DeepFM / DCN 想要干掉的痛点。两端用不同优化器也意味着线上训练基础设施要多维护一条链路；后来很多团队干脆用 DCN / xDeepFM 替换掉宽部分，彻底摆脱人工交叉的维护负担。如果面试问"今天你还会用 Wide & Deep 吗"，答案通常是否定的，但其思路仍是所有后继者的参考点。

## 4. DeepFM (Guo et al., 2017)

- **What**：深度分解机把 **Factorization Machine** (FM, 分解机) 和 DNN **共享同一层 embedding**——FM 捕获二阶交互，DNN 捕获高阶非线性交互，端到端一起学。相比 W&D 无需手工交叉，所有交互都在模型里自动组合出来。
- **Why mattered**：它解决了 W&D 里"还要人工做交叉"的痛点，成为 CTR 预估任务里长期霸榜的基线。只要有人说"我们做了个 CTR 预估模型"，工业界的第一反应就是跟 DeepFM 比；在竞赛社区也是前几年的常青树。
- **Architecture**：每个字段（field）共享同一个 embedding 向量 $e_i$；FM 部分是所有 pair 的 $\\langle e_i, e_j \\rangle$ 之和，DNN 部分是 concat 所有 embedding 后过多层感知器，最后 sigmoid(FM + DNN + 一阶线性项) 输出点击概率。训练是标准的交叉熵 + 反向传播，一次 forward 同时更新三条分支。
- **Gotcha**：FM 只能捕获二阶交互——如果信号深度非线性，DNN 就会独自扛大旗，FM 项退化成装饰；此时 DeepFM 与 pure DNN 的差距会压得很小。另外每个高基数字段都需要一套自己的 embedding 表，稀疏字段一多内存会爆炸——这也是 DCN-V2 转而用低秩结构去缓解参数量问题的原因。

## 5. DCN / DCN-V2 (Wang et al., Google, 2017 / 2020)

- **What**：**Deep & Cross Network** (DCN, 深度交叉网络) 用显式的交叉层 $x_{l+1} = x_0 \\cdot (w^T x_l) + b + x_l$ 堆叠出有界阶数的高阶交互，与普通 DNN 并联；DCN-V2 把向量 $w$ 升级为低秩矩阵，大幅提升表达力。
- **Why mattered**：DCN 在参数效率与交叉阶数可控性之间找到了折中；DCN-V2 让交叉层真正在 Google 广告、YouTube 这种超大流量上跑通生产。这是面试里被追问"除了 DeepFM 还有什么更强的交叉结构"时的标准答案。
- **Architecture**：交叉网络每一层产生输入的 $L$ 阶多项式交互，通常与 DNN 塔并联或串联，最后 concat 过 sigmoid；DCN-V2 里 $w^T x_l$ 这个标量权重被替换为 $W x_l$ 的低秩投影，因此每一层能学到更丰富的 pair 耦合。整体仍保持端到端可导，部署难度没明显上升。
- **Gotcha**：原版 DCN 的秩 1 交叉对每个 pair 只分配一个标量权重，实际上表达力太受限，工业界基本只用 DCN-V2。更隐蔽的坑是：交叉层对输入尺度极其敏感——如果不先做归一化或批归一化，训练会直接发散，是踩过坑的人才会记得的细节。

## 6. SASRec / BERT4Rec (Kang & McAuley 2018 / Sun et al. 2019)

- **What**：**Self-Attentive Sequential Recommendation** (SASRec, 自注意力序列推荐) 与 BERT4Rec 把用户历史交互序列当作 next-item 预测任务；SASRec 用单向（causal）自注意力，BERT4Rec 用双向加 masked-item 的 BERT 风格目标。两者都把 Transformer 的序列建模能力带入了推荐。
- **Why mattered**：它把 Transformer 从 **Natural Language Processing** (NLP, 自然语言处理) 迁移到推荐，效果显著超越 GRU4Rec 和 Caser 等 RNN/CNN 序列模型，成为 YouTube、TikTok、电商等场景下基于会话 (session-based) 和序列召回的主流范式。面试被问"序列推荐怎么做"时几乎不可能绕过这两篇。
- **Architecture**：物品 ID embedding 加上位置 embedding，堆若干层自注意力块，最后把序列末端的向量与整个物品 embedding 矩阵做内积，预测下一个物品。BERT4Rec 在训练时用 masked-item 任务替代单向预测，使得上下文双向可见但推理时要单独准备一种 masking 策略。
- **Gotcha**：物品词表极大，直接做 softmax 会爆炸——必须用 sampled softmax 或 in-batch 负样本兜底。序列长度一般被砍到最近 50 个物品，活跃用户被截断、长尾用户被 padding，两头都伤质量；冷启动物品没 embedding，得靠侧信息（内容、图像）融合来救。

## 7. PinSAGE (Ying et al., Pinterest × Stanford, 2018)

- **What**：把 GraphSAGE 的思想应用到 Pinterest 30 亿节点的 pin-board 异构图上，学习用于召回的 pin embedding。相比传统的协同过滤，PinSAGE 同时融合了图结构与节点内容特征。
- **Why mattered**：这是第一次有人证明 **Graph Neural Network** (GNN, 图神经网络) 能扩展到 web-scale 规模——关键是用**随机游走**代替均匀邻居采样，并用 MapReduce 做离线全量推断；训练出来的 embedding 直接服务 Related Pins 与 Home Feed 等多个核心场景。这是面试里回答"GNN 能不能做工业推荐"的标准案例。
- **Architecture**：对每个 pin 先用短随机游走定义邻域，再把邻居特征按访问频次加权，依次过 $K$ 层 GraphSAGE 聚合得到 pin embedding；训练目标是对 hard negative 的 max-margin 损失，让正样本比难负样本至少领先一个 margin。
- **Gotcha**：随机游走采样是工程上**最关键的 trick**——均匀邻居采样既不能扩展也会导致聚合噪声过大；hard-negative mining（从"有点相关但不完全对"的物品里挖负样本）是效果突破的关键，全用随机负样本训练目标会塌缩，召回质量上不去。这两点是后续 GNN 推荐论文共同的设计范式。

## 8. Item2Vec / Airbnb Embeddings (Barkan 2016 / Grbovic & Cheng 2018)

- **What**：Item2Vec 把 Word2Vec 的 skip-gram 迁移到物品序列——共现的 pin、房源预订流、歌单等都可以当作"句子"；Airbnb 在此基础上针对房源预订场景做了深度领域适配，学出带业务语义的 embedding。
- **Why mattered**：这是物品相似度最便宜、最强的基线之一；Airbnb 2018 年那篇论文把"把被预订的房源作为 global context 加到每个窗口"这种领域 trick 做成了经典案例，几乎所有推荐讲义里都会拿它作为 item embedding 的示范。
- **Architecture**：把用户会话当作"句子"、物品当作"单词"，用 skip-gram + negative sampling 训练。Airbnb 的额外改造有两处：一是把用户最终预订的房源作为 **global context** 加入每一个滑动窗口，让模型偏向预测"最终会被预订"的信号；二是**市场级负采样**——负样本从同一市场内采，避免模型退化为"分辨所在市场"的简单分类器。
- **Gotcha**：冷启动靠**类型 + 位置 embedding 求平均**来兜底——表面上是个 hack，但实测相当有效；纯粹共现的 embedding 抓不到内容信号，对新物品必须再融合图像、文本等内容侧信息。这个"简单方法扛大梁"的故事是 Airbnb 工程文化的典型体现。

## 9. MoE Ranking / Multi-Gate MoE (Ma et al., Google, 2018)

- **What**：**Multi-gate Mixture-of-Experts** (MMoE, 多门控专家混合) 是多任务学习里共享专家子网络、但按任务独立做 gating 加权的架构——每个任务自己选一组专家权重，互不干扰。
- **Why mattered**：MMoE 在 YouTube 排序（同时优化 engagement 与 satisfaction）和广告里被部署得最多，直接缓解了"多任务跷跷板"问题——加一个任务原本会让另一个任务退化，MMoE 让这种相互挤压显著减轻。对于任何需要多目标排序的业务，它几乎是现代起点。
- **Architecture**：共享输入先过 $N$ 个专家多层感知器；每个任务配一个 gate（对专家做 softmax），得到任务专属的加权专家组合，再进各自的任务塔算损失；总损失等于各任务损失的加权和。多任务的耦合由 gate 的学习动态决定。
- **Gotcha**：当任务高度相关时 gate 会**塌缩**——某个专家主导所有任务、其余专家闲置；对策是加 gate 熵正则，或者改用 **Progressive Layered Extraction** (PLE, 渐进分层抽取) 显式分离任务私有专家与共享专家。任务损失权重是第一大超参，不确定性加权损失（Kendall 2018）是较标准的解法，但在实际业务里仍常需要手动调。

## 10. Contrastive Pretraining for Recs (CLIP-style / SimCSE / SSL4Rec)

- **What**：**Contrastive Learning** (对比学习) 在推荐里的形态包括图文对比（CLIP 把图像和文本对齐到同一向量空间）、或对序列做数据增强得到两个视图（SimCSE / SSL4Rec），在监督微调前先做自监督预训练。这是一类打通"无标签海量内容 → 下游推荐任务"的通用手段。
- **Why mattered**：它缓解了冷启动和长尾物品问题——自监督学出来的内容 embedding 不依赖交互数据；CLIP 风格的双编码器更是当代多模态搜索（Google Search、Pinterest Lens 等）的底层基础。面试问到"冷启动怎么办"，除了传统的侧信息融合之外，对比预训练是近三年最常被提到的答案。
- **Architecture**：双编码器（图像 + 文本，或 sequence-aug-A + sequence-aug-B）→ **InfoNCE** 对比损失在 batch 内负样本上拉近正对、推远负对；预训练权重接着进监督推荐任务的微调阶段。核心等式是 $\\mathcal{L} = -\\log \\frac{\\exp(\\text{sim}(z_i, z_j)/\\tau)}{\\sum_k \\exp(\\text{sim}(z_i, z_k)/\\tau)}$。
- **Gotcha**：预训练目标必须和下游对齐——在"图文对齐"上预训练然后去 fine-tune 点击预测，有时根本迁移不过去（分布偏移）。InfoNCE 的温度 $\\tau$ 是 load-bearing 超参，取错了要么梯度消失要么爆炸；实操里通常先粗扫一遍温度才能定其它参数。

---

## Quick Cross-Cutting Talking Points（口述小抄）

- **Retrieval 与 ranking 的分层**：YouTube DNN 定义了这种分层。召回层等于双塔加 ANN——不能直接用 query-item 交叉特征；排序层则是全量交叉特征加 MMoE 多头，承担所有精细打分。这一层级划分几乎是所有现代工业推荐的标准答案。
- **Feature cross 的演化史**：从人工交叉 (Wide & Deep) 到 FM 学交叉 (DeepFM)，再到显式多项式交叉 (DCN-V2)，最后演进到 attention 学交叉 (AutoInt、Transformer)。这条演化主线就是"怎样把人工特征工程越挤越少"的历史。
- **冷启动 playbook**：内容 embedding (PinSAGE、CLIP)、侧信息融合 (Airbnb 的类型与位置 embedding)、元学习 (MeLU, Meta-Learning for User Cold-Start Recommendation)、或者直接退化到分段流行度兜底。这四条路径大致覆盖了所有工业冷启动的通用组合。
- **Negative sampling**：从 in-batch（便宜但有偏，需要 `-log Q(i)` 修正）到 hard negative (PinSAGE)，再到 mixed（随机与 hard 按比例混合）——这是召回质量里最灵的杠杆之一。离线指标拉不上来，第一反应通常是调负样本策略。
- **多任务**：从 shared-bottom 到 MMoE，再到 PLE 这条主线。gate 正则与任务损失权重是工程上最痛的两个旋钮，选错了所有任务都一起退化。面试被问"多目标怎么调"，这两个关键词基本能拿全分。

---

## 面试追问预测（按论文编号对应）

| # | 常见追问 | 建议回答切入点 |
|---|---------|---------------|
| 1 | 为什么用 expected watch time 而不是 CTR？ | 引入 clickbait / 用户长期留存，点到"业务目标与训练目标不一致"这个通用框架 |
| 1 | example age 去掉了会怎样？ | 训练分布偏老，预测时近似 prior，新视频被系统性压低 |
| 2 | in-batch 负样本为什么有偏？ | 热门物品出现在更多 batch 里，采样频率与物品频率成正比，需要 `-log Q` 修正 |
| 2 | 双塔怎么加入用户实时行为？ | query 塔动态侧加 sequence feature，serving 端重算；item 塔仍可离线预计算 |
| 3 | 今天你还会用 Wide & Deep 吗？ | 大概率会直接上 DCN-V2 + DNN，但思路是 W&D 的延续 |
| 4 | FM 只能二阶，怎么办？ | 堆 xDeepFM 的 CIN 层或直接换 DCN-V2；或承认 DNN 已经主导 |
| 5 | DCN 跟 DeepFM 的核心差异？ | DCN 显式构造多项式交互、阶数可控；DeepFM 靠 FM 学隐式交叉 |
| 6 | SASRec 的长度上限怎么定？ | 结合 attention 复杂度 $O(L^2)$、线上 latency 预算、以及业务上 P95 活跃序列长度 |
| 7 | PinSAGE 推断阶段怎么跑全量？ | MapReduce 按层聚合，每轮广播邻居特征；这是工程上真正难的部分 |
| 8 | Airbnb 为什么做 market-level 负采样？ | 避免模型学成"判别所在市场"的捷径，而是逼它学市场内的细粒度偏好 |
| 9 | gate 塌缩怎么缓解？ | gate entropy 正则、PLE 分离任务私有专家、甚至冷启动 gate 做 warmup |
| 10 | InfoNCE 温度 $\\tau$ 怎么选？ | 先粗扫 0.01 / 0.05 / 0.1 / 0.5，看对正负对相似度分布的压缩情况，再精调 |

## 30 秒自我测试

读完这份清单后，挑一篇随机论文，试着用下面这套节奏口述：
1. **一句话起手**：什么任务、什么突破。
2. **一个关键结构**：两塔？交叉层？gate？
3. **一个 gotcha**：如果面试官追问"最容易踩的坑"，你能秒答。

如果做不到，就回去补那一条——这比把十篇都读一遍更高效。十篇全部过一次的时间应控制在 **20 分钟**以内；超时说明还没到能口述的熟练度，而不是材料不够。

## 关键缩写速查（面试常用）

| 缩写 | 全称 | 中文 |
|------|------|------|
| DNN | Deep Neural Network | 深度神经网络 |
| ANN | Approximate Nearest Neighbor | 近似最近邻 |
| DSSM | Deep Structured Semantic Model | 深度语义模型 |
| W&D | Wide & Deep | 宽深模型 |
| FM | Factorization Machine | 分解机 |
| DCN | Deep & Cross Network | 深度交叉网络 |
| GNN | Graph Neural Network | 图神经网络 |
| MMoE | Multi-gate Mixture-of-Experts | 多门控专家混合 |
| PLE | Progressive Layered Extraction | 渐进分层抽取 |
| CTR | Click-Through Rate | 点击率 |
| SASRec | Self-Attentive Sequential Rec | 自注意力序列推荐 |

如果被问到任何一个缩写却卡在全称上，直接掉分——面试官默认"能讲出全称"是专业度的底线。这份表建议在面试前 30 分钟再过一遍。
"""


def main() -> int:
    """Apply CN rewrite to doc 52 idempotently."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT title, content FROM company_documents WHERE id = ?",
            (DOC_ID,),
        ).fetchone()
        if row is None:
            print(f"[ERROR] doc {DOC_ID} not found")
            return 1
        cur_title, cur_content = row
        if SENTINEL in cur_content:
            print(f"[UNCHANGED] doc {DOC_ID} ({cur_title}) -- sentinel present")
            return 0

        new_hash = hashlib.sha256(DOC_52.encode("utf-8")).hexdigest()
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        cur = conn.execute(
            "UPDATE company_documents "
            "SET content = ?, content_hash = ?, updated_at = ? "
            "WHERE id = ?",
            (DOC_52, new_hash, now, DOC_ID),
        )
        conn.commit()
        old_len = len(cur_content)
        new_len = len(DOC_52)
        print(
            f"[UPDATE] doc {DOC_ID} rows={cur.rowcount} "
            f"old_len={old_len} new_len={new_len} delta={new_len - old_len:+d}"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
