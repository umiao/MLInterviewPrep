# 推荐系统核心模型复习笔记

涵盖 CTR/CVR 预测、特征交叉、序列建模、生成式推荐几条主线的关键工作。每节按"核心想法 → 关键实现 → 为什么这样设计 → 局限/后续"组织。

---

## 1. DCN v1 / v2 (Deep & Cross Network) — 显式特征交叉的 Cross Network 路线

**核心想法**:用一个专门的 Cross 子网络显式建模有界阶数的多项式特征交叉,替代 MLP 的隐式黑箱。

**v1 (Wang et al., 2017)**

把所有 sparse embedding + dense feature 拼接成 $x_0 \in \mathbb{R}^d$,然后递归:

$$x_{l+1} = x_0\, x_l^\top w_l + b_l + x_l$$

每层做的事:**特征拼接 → 用 $w_l$ 做一次 linear mapping 得到一个标量 → 用这个标量去缩放 $x_0$ → 加残差**。展开第一层就能看到 $a^2, ab, b^2$ 这些二阶项被生成出来;递归 $N$ 层就得到 order ≤ $N+1$ 的所有多项式交叉。每层参数只有 $2d$,极轻量。

**局限**:$w_l$ 是向量,使得 $ab$ 这种交叉项的系数与 $a^2, b^2$ 锁死,等价于 rank-1 双线性,表达力受限。

**v2 (Wang et al., 2020)**

把向量 $w_l$ 升级为矩阵 $W_l$,每个参数获得独立自由度:

$$x_{l+1} = x_0 \odot (W_l x_l + b_l) + x_l$$

($\odot$ 是 Hadamard product,**逐元素乘**,不是矩阵乘——分工是 $W_l x_l$ 做线性变换重新组合特征,$\odot x_0$ 才制造**乘性交互**;拿掉 $\odot x_0$ 就只剩线性组合,永远造不出 $x_i x_j$ 交叉项。)现在每个二阶交叉 $x_i x_j$ 都有独立系数 $W_{ij}$,full-rank 双线性。

**工业级优化**:$d$ 通常上千,$d^2$ 参数爆炸,所以做 low-rank 分解 $W_l = U_l V_l^\top$,$U_l, V_l \in \mathbb{R}^{d \times r}$,参数从 $d^2$ 降到 $2dr$。意外发现:low-rank 不只是省参,效果常常更好(隐式正则)。进一步在 low-rank cross 上叠 MoE,多个 $(U, V)$ 专家分工不同的特征子空间。

**Parallel vs Stacked**:v2 论文明确对比两种组合 Cross 和 Deep 的方式:

- Parallel:embedding 同时进入 Cross 和 Deep,输出拼接 → logit。这是 v1 默认。
- Stacked:embedding 先过 Cross,再喂给 Deep,串行。

没有绝对赢家,跨数据集表现不一致。直觉上 stacked 在 Cross 已经给出的显式交叉之上再做一层抽象,更"层次化";parallel 让两条通路独立,融合更晚。

**核心 takeaway**:DCN 系列把"做特征工程"这件事变成"端到端学一个有界阶数的多项式"。v2 把表达力卡口从 rank-1 解开,low-rank 让它能上工业 scale。

---

## 2. DLRM (Deep Learning Recommendation Model) — Meta 2019 工业级 CTR 基线

**核心想法**:稀疏 + 稠密特征分别处理,然后用 dot product 做显式二阶交互,再过 top MLP 出分数。是 **FM**(Factorization Machine, 因子分解机)思想的深度学习扩展。

**架构 flow**(Naumov et al., 2019):

1. 每个 categorical feature 单独一张 embedding table,lookup 得到一个向量 $e_i$
2. 所有连续特征拼起来过一个 bottom MLP,得到 $b$
3. **Feature interaction**:把 $\{e_1, ..., e_k, b\}$ 这一组向量两两做 dot product,得到 $\binom{k+1}{2}$ 个标量
4. 这些标量和原始 $b$ 拼接,送入 top MLP
5. Sigmoid 出 CTR

**为什么这样设计**:dot product 直接对标 FM 的二阶 $\langle v_i, v_j \rangle x_i x_j$,但相比 FM 有三处结构升级——(1) dense 特征专门走 bottom MLP 而不是被忽略;(2) 两两 dot product 的结果**保留为标量并拼成向量**喂给 top MLP,而不是像 FM 那样 sum 成一个数让信息坍缩;(3) 顶部是 MLP 非线性而不是线性加权。其中第 (2) 点是真正核心——FM 把交互 sum 掉信息就丢了,DLRM 保留每个 pair 作为 element 让上层 MLP 进一步学。比纯 MLP 暴力混合更结构化,比 DCN 那种 N 阶多项式简单(只到二阶)。

**系统层面**(这才是 DLRM 在 ML Sys 课上被反复讨论的原因):

- **Hybrid parallelism**:embedding table 巨大(TB 级,因为 categorical 词表上亿)→ model-parallel,各 GPU 持有部分 table;MLP 计算量大但参数小 → data-parallel
- 训练时一次 minibatch 需要先做 all-to-all(把 lookup 结果按 sample 重新分发),再做 all-reduce(MLP 梯度同步)。通信成为瓶颈
- 开源后成了 MLPerf 推荐 benchmark 标杆

**局限**:特征工程不可避免(几百个手工 feature field),scale 起来收益递减——这是后来 **HSTU**(Hierarchical Sequential Transduction Units,Meta 2024)提出 "DLRM doesn't scale with compute" 的批评。

**轴的澄清**(一个常见误用):学习目标轴(pointwise / pairwise / listwise)与打分函数输入轴(user-independent / personalized)**正交**,不是同一件事。DLRM 本身就是 personalized + pointwise:$\text{score} = f(\text{user\_feat}, \text{item\_feat}, \text{context})$,逐 item 打分但是 user-conditioned。现场如果说"这题不适用 pointwise"是错的,正确表述应该是"user-independent ranking(PageRank / global quality score / CTR-rank)不适用"。真正决定 architecture 的是 **user side 是否参与打分**,不是 pointwise/pairwise/listwise 的选择。

---

## 3. Collaborative Filtering 主流方法和策略

**核心问题**:从 user × item 交互矩阵里学每个 user/item 的表示,使得相似 user 喜欢相似 item。

**三大流派**:

**(a) Memory-based / Neighborhood**

- User-based CF:找和你最像的 K 个用户,推他们喜欢的
- Item-based CF:推和你历史交互过的 item 相似的 item("买了这个的人还买了")。Amazon 经典做法
- 相似度用 cosine / Pearson;不需要训练,但可扩展性差,稀疏矩阵下 cold start 严重

**(b) Latent factor / Matrix Factorization**

把交互矩阵 $R \approx U V^\top$,$U \in \mathbb{R}^{n \times k}$ 是 user latent,$V \in \mathbb{R}^{m \times k}$ 是 item latent

- **Explicit feedback**(评分):SVD / FunkSVD,最小化 $\sum (r_{ui} - u_u^\top v_i)^2$
- **Implicit feedback**(点击/观看):
  - **ALS-WR** (Alternating Least Squares with Weighted Regularization):把没观察到的当负样本,但加置信权重,交替优化 user/item 矩阵
  - **BPR** (Bayesian Personalized Ranking):pairwise loss $\sigma(u^\top v_+ - u^\top v_-)$,直接优化排序

**(c) Neural / Deep CF**

- **NCF** (Neural Collaborative Filtering, He et al., 2017):用 MLP 替代 inner product 做 user-item 匹配。后来 Rendle 那篇 "Neural CF vs. dot product" 又指出 dot product 调好其实更强
- **Two-tower / dual encoder**:user tower 和 item tower 各自学 embedding,inner product 打分。**工业界 retrieval 阶段事实标准**——item embedding 离线算好建 ANN 索引,user embedding 在线 forward,做最近邻召回
- **Graph-based**:PinSage(Pinterest)、LightGCN,把交互建成 bipartite graph 做 GNN 传播
- **Sequential**:SASRec, BERT4Rec,把用户历史当序列做 self-attention,后面演化到 HSTU

**实际工业 stack**:Retrieval 用双塔多路召回 → 粗排小模型 → 精排 DLRM-style → 重排多目标 trade-off。每一阶段候选规模差几个数量级,模型复杂度也相应递增。

**CF 与 2-tower 的关系**:能力上看,纯 CF(user_id × item_id MF)就是 2-tower 的退化版(只有 ID embedding + 内积)。加上 content / 行为特征后才是完整双塔。但故事里仍要讲 CF——它解释了「为什么做内积、user/item 为什么对称」的直觉根源,cold start 痛点驱动了 CF → content-based → hybrid → 2-tower 的演进路径,而且工业纯 ID 召回通道至今仍存在。

---

## 4. 多模态 Embedding 怎么 Unify / Fuse

**问题本质**:图像 ViT 出来 512 维、文本 BERT 出来 768 维、ID embedding 出来 64 维,scale 和语义空间都不同,怎么塞进同一个模型?

**几种思路,按耦合度从低到高**:

**(a) Late fusion**:每个模态走独立 tower,在 logit 层加权求和。简单、各模态 decouple,但模态间交互缺失。

**(b) Feature-level fusion**(也常被笼统称作 early fusion,但严格说真正的 early fusion 是 raw input 级别——比如把 image patch token 和 text token 拼起来直接喂同一个 Transformer):projector 把每个模态投到统一维度后直接拼接 + MLP。最常用,但隐式假设 MLP 能学好异构特征的交互——RankMixer 论文恰好质疑这一点。同层级的几种变体:**sum**(同维相加,丢 modality 区分,简单 baseline)、**gated fusion**(学每个模态的标量权重 $\sum_m g_m \cdot e_m$)、**bilinear / Hadamard**($e_{\text{vis}} \odot e_{\text{text}}$ 显式制造模态间乘性交互)。

**(c) Cross-attention fusion**:让一个模态做 query 去 attend 另一个模态。例如 item 的图像 token 做 K/V,文本/ID 做 Q。BLIP-2 的 Q-Former 是这条路的精华:用一小撮 learnable query 从冻结的大视觉编码器抽信息,统一成固定数量的 query token,后面接 LLM。

**(d) Contrastive alignment**:CLIP-style,用对比损失把不同模态的语义对齐到同一空间,再下游 fuse。Pinterest、阿里都有把 item 多模态做 CLIP 对齐当上游预训练再喂下游 CTR 模型的做法。

**(e) MoE over modalities**:每个 expert 专门处理一种模态/子空间,gate 学路由。

**实战要注意的几点**:

- **数值尺度**:不同 encoder 输出 norm 差好几个数量级,fusion 前一定要 LayerNorm 或单独 scale
- **Missing modality**:训练时随机 drop 模态(让模型学会鲁棒);推理时用 learnable "modality missing" embedding 替代
- **数据量差异**:文本数据多、视频数据少,可以用 modality-specific learning rate 或 staged training
- **推荐里的典型用法**:item 多模态 → 离线编码成单一 item embedding → 当作 DLRM 的一路 sparse-like 特征喂进去,user 侧不变

---

## 5. Multi-task Head vs 多个 Loss — 区别在哪

**这两个术语经常混用,但严格说不一样。**

**多个 Loss 在同一个 head 上**:还是一个输出,但叠加多种监督信号。例:

- CE + KL distillation(蒸馏)
- CE + label smoothing
- Reconstruction + commitment loss(**VQ-VAE**, Vector Quantized Variational Autoencoder)
- 主任务 loss + 辅助 auxiliary loss(正则化用)

这种本质是**对单一预测目标加多种正则/知识源**,不改模型结构。

**Multi-task head (multi-head 架构)**:共享 backbone + 多个任务特定 head,**每个 head 有自己的输出和 label**:

- 例:CTR 和 CVR 联合训练,user/item 特征相同,但两个 head 预测两个目标
- 例:RecSys 多目标——点击、停留时长、点赞、转发、评论
- 推理时一次 forward 给出多个分数,业务侧加权融合

**为什么 multi-task 有用**:

- **数据增强**:相关任务共享表示,稀疏任务从密集任务受益(典型 CTR 数据多,CVR 数据少)
- **共享 backbone 推理高效**:线上一次 forward 多个输出
- **正则化**:任务相关性约束 backbone,降低过拟合

**核心难点和对应解法**:

- **Negative transfer**:任务冲突时强行共享反而互相拉低。解法:
  - **Shared-bottom**:最朴素,完全共享底层 + 多个独立 head
  - **MMoE** (Multi-gate Mixture-of-Experts, Ma et al., 2018):多个 expert 子网络,每个任务一个 gate 学着挑 expert 的加权组合,允许不同任务用不同的专家
  - **PLE** (Progressive Layered Extraction, Tencent, 2020):在 MMoE 上区分**任务共享专家**和**任务专属专家**,进一步缓解冲突
- **Loss balancing**:不同 loss 量级差太多。解法:GradNorm(梯度尺度归一)、uncertainty weighting(Kendall et al.)、手调 task weight

**一句话**:多 loss 单 head 是**多个监督打在同一个输出上**(改训练目标);multi-task 是**多个输出多个监督**(改模型架构);后者才涉及 MMoE/PLE 这类任务相关性建模。

---

## 6. RQ-VAE (Residual Quantized Variational Autoencoder) — 把 item 量化成层级语义 ID

**核心想法**:把 item 的连续 embedding 用**层级残差量化**变成一个离散码字元组 $(c_1, c_2, ..., c_N)$,作为 item 的"semantic ID"。这是生成式推荐(**TIGER**, Transformer Index for GEnerative Recommenders, Google 2023)的关键组件。

**算法**:

1. Encoder 把 item 内容(图+文+meta)编码成连续 latent $z = r_0$
2. 第 $d$ 层有一个 codebook $C_d = \{e_1^{(d)}, ..., e_K^{(d)}\}$。从中找最近向量,选中索引为 $c_d$
3. 计算残差 $r_{d+1} = r_d - e_{c_d}^{(d)}$,送入下一层
4. 递归 $N$ 层,得到层级码字 $(c_1, ..., c_N)$
5. Decoder 输入是所有选中码字之和 $\sum_d e_{c_d}^{(d)}$,重构原 latent
6. Loss = 重构 loss + commitment loss(让 encoder 输出靠近最近码字)+ codebook loss(让码字向量靠近被分配的输入)

**容易混淆的点**:每层 quantize 的**输入是上一层的残差** $r_{d-1}$,不是原始 $z$,也不是三组码字拼接;「三组码字都用到」只在**重构阶段**($\hat{z} = c_1 + c_2 + c_3$)成立。每层 codebook 的 k-means 是**独立训练**的(对所有样本走到该层的残差做聚类)。

**为什么是 residual 而不是直接 product quantization**:

- Residual 自然形成**粗→细**的层级:第一个 codebook 抓粗类目(比如"运动"),第二个抓中类目(比如"跑鞋"),后面抓具体品牌/款式
- 相似 item **共享前缀**:这是用 ID 做检索时的巨大优势——给定 user 历史预测的前缀,可以做 beam search,而且语义近的会自然落在同一前缀下
- 残差范数逐层衰减,所以每层 codebook 大小可以不同(高层小、底层大)

**关键 trick**:

- **k-means 初始化 codebook**:从一批 encoder 输出做 k-means,避免 codebook collapse(某些码字从来没被选中)
- VQ-VAE 也能用,但是 flat 的,丢了层级结构,所以 TIGER 选了 RQ-VAE

**在推荐里的应用 (TIGER)**:

- 给所有 item 算出 semantic ID 串(比如 1B 个 item → 每个变成长度 4、每位 256 字典的 ID 串)
- 用户历史变成 ID token 序列
- 训练一个 Transformer 做 next-ID generation,推理时 beam search 输出下一个 item 的 ID
- 好处:不需要 ANN 索引,长尾 item 不需要单独 embedding(由 codebook 组合表达),冷启动新 item 只要内容能编码就能进入系统

---

## 7. HSTU (Hierarchical Sequential Transduction Units) — Meta 的生成式推荐基础架构

**核心想法**(Zhai et al., ICML 2024,"Actions Speak Louder than Words"):把推荐重新定义为**序列转录(sequential transduction)任务**,像 LLM 一样训生成式模型,而不是传统 DLRM 那种点对点 CTR 预测。

**重新定义的两层意思**:

1. **数据表示**:用户的点击、购买、搜索、上下文都序列化成一个统一的 action token 序列;数值特征不再手工塞进去,而是让模型从序列结构里自己学
2. **训练范式**:autoregressive next-action prediction,一次预测整个序列,encoder cost 在所有目标上 amortize。对比 DLRM 每个 impression 一次 forward,样本利用率高得多

**HSTU 单元结构**:

类 Transformer block,但魔改了 attention:

- **Pointwise modulation** 替代 softmax:推荐场景的 vocabulary 是**非平稳的**(item 不断上下架,user 行为分布漂移),softmax 假设的"统一相似性度量"在长尾、非平稳 vocab 上不稳定。HSTU 用 SiLU 等门控的 pointwise normalization
- **简化线性层**:相比 Transformer 把 attention 模块外的线性层从 6 个减到 2 个,省内存
- **Operator fusion**:把 norm、dropout、激活融到一起,自研 kernel 比 FlashAttention2 在 8192 长度上快 5.3-15.2 倍

**实证结果**:

- 公开数据集(MovieLens, Amazon Books)上 NDCG 比 SASRec 等 baseline 高 65.8%
- 1.5 万亿参数模型部署到 Meta 多个产品,A/B 上线指标 +12.4%
- **首次在工业推荐里验证 power-law scaling law**——模型质量随训练算力按幂律提升,跨三个数量级,接近 GPT-3/LLaMA-2 规模。这是说 "recommendation 也可以有 foundation model" 的关键证据

**重要性**:

- 直接挑战 DLRM 几十年范式——HSTU 论文里直接说 "DLRMs fail to scale with compute",因为 DLRM 是"宽"而不是"深"的,堆参数 ≠ 堆能力
- 开启 GR (Generative Recommendation) 路线:RQ-VAE 做 item tokenization,HSTU 做 sequence backbone,合起来对标 LLM 的两件事(tokenizer + transformer)
- 后续 Meta 又出 OneRec 等加强版本(注:OneRec 实际是 Kuaishou 的工作,见下方对照)

**HSTU vs OneRec(Kuaishou)对照**:两者常被并提但范式不同。HSTU 的 target 是 **item ID**(softmax over vocab),范式是 retrieval / 分类,本质是 scale up 的序列推荐(SASRec / BERT4Rec 升级版),解决「DLRM 不 scale → actions as tokens」。OneRec 的 target 是 **semantic ID tokens**(多 codebook 层级码字),范式是 seq2seq autoregressive 生成,本质是 LLM-style 端到端生成式推荐,直接替代召回 / 粗排 / 精排级联。target 不同只是结果——真正差异是「**分类范式 vs 生成范式**」。

---

## 8. RankMixer — 异构特征下放弃 self-attention

**核心问题**(ByteDance, 2025):推荐数据是**数百个异构特征字段拼接**——user_id 在一个 ID 空间(亿级),item_category 在另一个(千级),hour_of_day 在另一个(24 个值)。每个 field 的语义空间完全不同。

Self-attention 的核心假设是 **token 之间存在统一的相似性度量** $\text{softmax}(QK^\top/\sqrt{d})$。这个假设在 NLP 里成立(所有 token 都是文字 subword,共享词表),但在推荐里**根本不成立**:user_id embedding 和 hour_of_day embedding 算内积本质上是没意义的。

更糟的是,DLRM、**DHEN**(Deep & Hierarchical Ensemble Network, Meta 2022)这些把所有 field 塞到同一个 interaction module 的做法,会让**高频特征主导,长尾特征被冲掉**——内积的 magnitude 被高方差的特征 dominate。

**RankMixer 的解法**:借鉴 MLP-Mixer 思路但为推荐重新设计:

**(a) Multi-head token mixing**(替代 self-attention)

- Parameter-free 的 reshape/transpose 操作:`(T, D) → reshape (T, H, D/H) → permute (H, T, D/H) → reshape (T, D)`,几乎免费(只改 stride / 内存布局),零参数实现跨 token 信息搬运
- 没有 QKV 投影、没有 softmax,IO 和算力都省
- 异构特征下 token mixing 反而比 self-attention 强,因为不强加错误的相似性假设
- **为什么不用 FC mixing**:FC 能学任何置换,permute 看似冗余;但 FC mixing 是 $O(T^2 D^2)$ 参数 + memory-bound,违背初衷——设计哲学是 mixing 坚决 0 参数,参数预算全砸到 **PFFN**(Per-token FFN,见 (b))

**(b) Per-token FFN**(关键创新)

(术语澄清:FFN 即 transformer block 里 attention 后那两层 MLP,$\text{FFN}(x) = W_2\,\sigma(W_1 x + b_1) + b_2$;分工上 attention 跨 token 通信,FFN per-token 加工。RankMixer 沿用这个分工——mixing 通信 + PFFN 加工。)

- 每个 feature token **独立一份 FFN 参数**,不共享
- 因为各个 feature subspace 语义不同,共享 FFN 等于强迫不同语义用同一组参数学,是 capacity 浪费 + interference 来源
- 这样既保留了"每个 field 独立建模"的能力,又通过 token mixing 拿到了 cross-field 交互

**(c) Sparse-MoE 扩到 1B 参数**

- Per-token FFN 进一步 MoE 化,但 routing 不平衡是个问题
- 用 ReLU routing + adaptive L1 penalty 替代 Top-k softmax,让 token 选 expert 数量灵活、保持可微

**硬件感知**:

- Parameter-free mixing → IO bound 缓解
- **MFU** (Model FLOPs Utilization, GPU 算力实际利用率)从 4.5% 提到 45%(传统手工特征交叉模块在 GPU 上是 CPU 时代的 legacy,很多碎算子)
- **参数量扩 100 倍,推理延迟几乎不变**——这是工业部署关键

**部署**:抖音 Feed Ranking 全流量,active days +0.2%,duration +0.5%。后续 TokenMixer-Large(2026)进一步加 SwiGLU、Pre-Norm、residual 改进,扩到 7B-15B。

**硬约束:T 必须固定**:PFFN 第 $t$ 个 token 有专属 FFN 参数 → $T$ 在模型定义时写死,不能变长。这里的「token」**不是 NLP token**,而是「语义特征组」(user / item / context / sequence summary 各一个,$T$ 是个位数到数十);变长行为序列在进 RankMixer **之前**先被 **DIN**(Deep Interest Network, Alibaba 2018)/ **SIM**(Search-based Interest Model, Alibaba 2020)/ **LONGER**(Long-sequence user behavior modeling)聚合成定长 token。**心智模型**:RankMixer 是 **DLRM 的替代品(ranking 阶段)**,不是 SASRec 的替代品(召回 / 长序列建模阶段)。

**关键洞察 takeaway**:NLP 那套 token-uniform 假设搬到推荐不灵,正确做法是**给每个 feature subspace 独立参数**,然后用 cheap 的 mixing 操作做交互。

---

## 跨工作的脉络梳理

把上面 8 个工作串起来,可以看到几条主线:

**特征交叉这一条**:
FM(二阶,共享 factor)→ DLRM(二阶,独立 embedding + dot product)→ DCN v1(N 阶,rank-1 cross)→ DCN v2(N 阶,full-rank + low-rank + MoE)→ RankMixer(放弃统一交叉模块,per-token FFN + mixing)

**序列建模这一条**:
GRU4Rec → SASRec(self-attention)→ BERT4Rec → HSTU(去 softmax + pointwise gate + scaling law)

**离散化 / 检索这一条**:
ANN 索引 → VQ-VAE → RQ-VAE / TIGER(层级 semantic ID + 生成式检索)

**Scaling law 这一条**:
DLRM(scale 不动,因为是宽而非深)→ HSTU(首次证明 RecSys 可以 LLM-style scaling)→ RankMixer(用更高 MFU 做 100x 参数扩展)

**正在发生的范式迁移**:
传统"特征工程 + DLRM"→ "sequence-as-language + foundation model"。GR 路线(RQ-VAE + HSTU)是这次迁移的旗手,RankMixer 走的是相对保守的"在 ranking 阶段做架构现代化"路线。两条路线短期内会并存,长期看 GR 更有 scaling 潜力。
