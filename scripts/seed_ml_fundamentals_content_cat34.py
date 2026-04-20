"""Seed: T-P0-541 -- ML Fundamentals T1 content fill, Cat 3-4 (7 leaves).

Replaces the placeholder TODO[MLF-<slug>] descriptions inserted by
seed_ml_fundamentals_skeleton.py (T-P0-538) with cleaned, KaTeX-rendered
markdown for the seven Tier-1 questions across unsupervised + DL training:

  unsupervised (2):
    - k-means-assumptions-and-failures (#7)
    - em-and-gmm                        (#8)

  dl_training (5):
    - batchnorm-vs-layernorm            (#9)
    - adam-vs-sgd-adamw                 (#10)
    - vanishing-exploding-gradient      (#11)
    - dropout                           (#12)
    - activation-function-evolution     (#13)

T1 = verbatim cleanup. The source attachment renders every formula three
times (LaTeX + glyph dump + glyph dump). This script collapses each triplet
to a single KaTeX block in $...$ / $$...$$ form, expands first-occurrence
acronyms per data/ml_fundamentals_inventory.yaml's acronyms_to_expand list
(format: **English full term** (acronym, 中文译名)), and preserves every
derivation and "追问预判" section.

Idempotency:
  - Each leaf has a stable expected description; second run yields
    updated=0 skipped=7 conflict=0.
  - SHA-256 of the 7 description blobs captured pre/post for audit.
  - If a leaf's existing description is neither the placeholder nor the
    new content (i.e. a human-edited intermediate state), the script
    aborts with [CONFLICT] before any write.

Acceptance:
  - 7 framework_nodes.description rows updated (path LIKE
    'ml-fundamentals/<cat>/<slug>')
  - Each description has KaTeX math ($ or $$ delimiters)
  - Each description has section headers (## ...)
  - Re-run is no-op (updated=0)
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"


# ---------------------------------------------------------------------------
# Cleaned descriptions. Raw strings to keep LaTeX backslashes literal.
# ---------------------------------------------------------------------------

DESC_KMEANS = r"""# K-means Assumptions and Failure Modes

## 1. 算法回顾

给定 $K$，迭代两步直到收敛：

- **Assign**：每个点分到最近的中心（欧氏距离）。
- **Update**：每个中心更新为被分到它的点的均值。

目标函数（**Within-Cluster Sum of Squares** (WCSS, 簇内平方和)）：

$$J = \sum_{k=1}^{K} \sum_{x \in C_k} \|x - \mu_k\|_2^2$$

## 2. 隐式假设

### (a) 簇是凸且各向同性的（球形）

因为用欧氏距离 + 均值作为中心，等价于假设每个簇是一个各向同性的球形高斯（identity covariance）。任何非凸或长条形的簇都会被硬生生切开。

### (b) 簇的大小（样本数）相近

目标函数里每个点权重一样，大簇的 SSE 会主导总 loss。为了降低总 loss，算法倾向于把大簇切小，把小簇和邻居合并 → 小簇被"吞掉"。

### (c) 簇的方差（紧密程度）相近

高方差簇的点离中心远，算法会把它们误判为属于相邻的紧凑簇。结果是松散的簇被挤压，紧凑的簇被扩张。

### (d) K 是已知的

K-means 需要预先给定 $K$，本身不会告诉你数据里有几个簇。

### (e) 欧氏距离合理

各维度尺度可比 → 必须先 standardize，否则量纲大的特征主宰距离。

## 3. 典型失败场景

| 场景 | 为什么挂 | 替代方案 |
|-----|---------|---------|
| 同心圆 / 环形 | 非凸，欧氏均值没意义 | Spectral clustering、DBSCAN |
| 月牙形 / 弯曲流形 | 非凸 | DBSCAN、HDBSCAN |
| 椭圆形簇（anisotropic） | 球形假设违反 | **Gaussian Mixture Model** (GMM, 高斯混合模型)（允许 full covariance） |
| 大小悬殊的簇 | 大簇 SSE 主导 | GMM、密度聚类 |
| 密度差异大的簇 | 稀疏簇被忽略 | DBSCAN / HDBSCAN（基于密度） |
| 含噪声 / 离群点 | 均值对 outlier 极敏感 | K-medoids、DBSCAN（自动识别噪声） |
| 高维数据 | 维度灾难 | 先降维（PCA / UMAP）再聚类 |
| categorical 特征 | 欧氏距离无意义 | K-modes / K-prototypes |
| 簇数未知 | 需预设 K | Elbow / Silhouette、DBSCAN、GMM+BIC |

## 4. 其他容易忽略的性质

- **对初始化敏感**：随机初始化可能陷入局部最优。K-means++ 初始化（按距离加权采样）大幅缓解，几乎是现代默认。
- **保证收敛，但不保证全局最优**：每步单调降低 $J$，但最终可能是局部最小。
- **Voronoi 切分**：收敛后的决策边界是线性的（Voronoi diagram），不能做非线性切分。
- **硬分配**：每个点只能属于一个簇。GMM 给的是软分配（每个点对每个簇的后验概率）。

## 5. 和 GMM 的关系

K-means 是 GMM 在以下特例下的极限：

- 协方差 $\Sigma_k = \sigma^2 I$（各向同性 + 同方差）。
- $\sigma^2 \to 0$（每个点必然硬分配到最近中心）。

所以 GMM 是 K-means 的自然概率化推广：可以建模椭圆簇、给出软分配、可以用 BIC 选 K。

## 6. 维度灾难深挖

高维空间里，对任意两点 $x_i, x_j$：

$$\frac{\max_j \|x_i - x_j\| - \min_j \|x_i - x_j\|}{\min_j \|x_i - x_j\|} \to 0 \quad (d \to \infty)$$

所有点两两距离趋于相等，"最近邻"概念失效。实践中：

- 文本、图像等高维原始特征上直接跑 K-means 几乎必挂。
- 先用 PCA / Autoencoder / UMAP 降到 $\sim 10$-$50$ 维，再聚类。
- 或换成基于其他结构的方法（spectral、graph-based）。

## 7. 实战 checklist

1. 先 standardize（除非特征本身同量纲）。
2. 用 K-means++ 初始化，多跑几次（`n_init=10`）。
3. 画 elbow / silhouette 选 K。
4. 如果结果很差，问自己：簇真的是球形的吗？密度一致吗？维度是不是太高？→ 换 GMM / DBSCAN / 先降维。
"""


DESC_EM_GMM = r"""# EM Algorithm with GMM

## 1. Motivation：为什么需要 GMM 和 EM

K-means 假设簇是球形、硬分配，很多场景不够用——比如两个簇重叠，一个点可能模糊属于两者。**Gaussian Mixture Model** (GMM, 高斯混合模型) 是它的概率化推广：把数据建模为 $K$ 个高斯的加权叠加，每个点给出**软分配**（对每个分量的归属概率），同时学出每个簇的椭圆形状（协方差）。

$$P(x) = \sum_{k=1}^K \pi_k\, \mathcal{N}(x \mid \mu_k, \Sigma_k)$$

要学参数 $\{\pi_k, \mu_k, \Sigma_k\}$，自然想用 **Maximum Likelihood Estimation** (MLE, 最大似然估计)。但 log-likelihood 里 log 外面套着 sum（$\log \sum_k \pi_k \mathcal{N}(\cdot)$），没有闭式解、非凸，所有参数耦合在一起解不开。

**Expectation-Maximization** (EM, 期望最大化) 的解法思路：既然不知道每个点属于哪个分量（这是隐变量 $z_n$），那就"假装知道"——先猜一个软分配，再基于这个分配反过来更新参数，来回迭代。

## 2. 算法流程

**初始化**：通常先跑 K-means 拿一组 $\mu_k$ 作为起点（避免随机初始化陷入很差的局部最优），$\Sigma_k$ 设成单位矩阵，$\pi_k = 1/K$。

**E 步 — 算 responsibility**：给定当前参数，对每个样本 $n$ 和每个分量 $k$ 算软概率

$$\gamma_{nk} = P(z_n = k \mid x_n, \theta) = \frac{\pi_k\, \mathcal{N}(x_n \mid \mu_k, \Sigma_k)}{\sum_j \pi_j\, \mathcal{N}(x_n \mid \mu_j, \Sigma_j)}$$

就是 Bayes 规则。直觉：样本 $n$ 有多大比例"属于"分量 $k$。

**M 步 — 加权 MLE**：把 $\gamma_{nk}$ 当权重，对每个分量做加权均值和加权协方差。记 $N_k = \sum_n \gamma_{nk}$：

$$\pi_k = \frac{N_k}{N}, \quad \mu_k = \frac{1}{N_k}\sum_n \gamma_{nk}\, x_n, \quad \Sigma_k = \frac{1}{N_k}\sum_n \gamma_{nk}(x_n - \mu_k)(x_n - \mu_k)^\top$$

两步交替，直到 log-likelihood 不再上升。

## 3. 参数的物理意义

- $\pi_k$ — **mixing weight**：分量 $k$ 的"占比"，从混合模型里随便抽一个点来自分量 $k$ 的先验概率，$\sum_k \pi_k = 1$。
- $\mu_k$ — **mean**：分量 $k$ 这个高斯的**中心位置**（对标 K-means 的 cluster center）。
- $\Sigma_k$ — **covariance**：分量 $k$ 的**形状和朝向**，$d \times d$ 对称正定矩阵。
  - 对角线：每个维度的方差（簇在各轴方向的拉伸）。
  - 非对角线：维度间的相关性（簇的倾斜方向）。
  - $\Sigma = \sigma^2 I$ → 球形簇（退化成 K-means）；对角 → 轴对齐椭圆；一般形式 → 任意方向椭圆。

M 步做三件事：更新占比 $\pi_k$、更新每个簇的中心 $\mu_k$、更新每个簇的形状 $\Sigma_k$。

## 4. 关键性质

- **单调不减**：每次迭代保证 log-likelihood 不降（不会变糟）。
- **只能收敛到局部最优**，所以常多次随机重启选最好的。
- **K 是超参数**，EM 不会自己选；用 BIC / AIC / held-out likelihood 选。
- **极限情形**：$\Sigma_k \to 0$ 时 GMM 退化为 K-means（软分配退化为硬分配）。

## 5. **Evidence Lower Bound** (ELBO, 证据下界) 视角

EM 其实在最大化 log-likelihood 的 ELBO：

$$\log P(x) = \underbrace{\mathcal{L}(q, \theta)}_{\text{ELBO}} + D_{\text{KL}}(q(z) \,\|\, P(z \mid x, \theta))$$

- E 步：固定 $\theta$，让 $q(z) = P(z \mid x, \theta)$ → **Kullback-Leibler Divergence** (KL, KL 散度) 项 = 0，ELBO 撑到最大 = $\log P(x)$。
- M 步：固定 $q$，最大化 ELBO 关于 $\theta$，单调拉高 $\log P(x)$。

这个框架推广到一般的隐变量模型——HMM 的 Baum-Welch、pLSA 的训练、缺失数据 MLE 都是 EM 的具体实例；VAE 的训练也是 ELBO 最大化的变分版本。

## 6. 常见追问预判

- **怎么选 K**：BIC / AIC，或跑 `BayesianGaussianMixture`（DPMM）把 K 设得偏大让它自动压掉多余分量。
- **协方差奇异**：某个分量只分到 1-2 个点会炸，实践中加 $\Sigma_k + \epsilon I$ 正则。
- **计算贵**：每轮 $O(N K d^2)$，高维 $d$ 大时用 diagonal 或 tied covariance 简化。
- **EM 的通用性**：任何"隐变量 + MLE"的问题都可以 EM 框架。
"""


DESC_BN_LN = r"""# BatchNorm vs LayerNorm

## 1. **Batch Normalization** (BN, 批归一化) 的基本行为

对一个 mini-batch $B$，BN 在**每个特征维度上独立做 normalize**：

$$\hat x_i = \frac{x_i - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}}, \quad y_i = \gamma \hat x_i + \beta$$

其中 $\mu_B, \sigma_B^2$ 是**跨 batch 维度**统计出来的均值方差，$\gamma, \beta$ 是可学习的 scale / shift。

## 2. Training vs Inference 的关键差别

| 维度 | Training | Inference |
|-----|---------|-----------|
| 均值方差 | 当前 batch 的 $\mu_B, \sigma_B^2$ | 训练时累计的 running mean / var |
| 是否依赖 batch | 是 | 否（batch size = 1 也能跑） |
| 梯度 | 通过 $\mu_B, \sigma_B^2$ 回传 | 不涉及 |

训练时一边算 batch statistics，一边用 **Exponential Moving Average** (EMA, 指数移动平均) 维护 global 的 running statistics；推理时切换成用 running statistics，这样同一个样本进来的输出才是确定的、不依赖 batch 里其他样本。

**常见坑**：忘记 `model.eval()` 会继续用当前 batch 的统计，推理结果会随 batch 组成漂移。

## 3. BN 的局限

- **小 batch 会挂**：batch size 太小（检测模型、分布式训练每卡 2-4 个样本），$\mu_B, \sigma_B^2$ 估计噪声巨大，BN 失效。替代：GroupNorm（按 channel 分组 norm，不依赖 batch）。
- **序列长度变化**：NLP 里句子长度不一，batch 维度上跨不同位置 / 不同句子 norm 没有语义意义，padding token 还会污染统计量。
- **训练 / 推理行为不一致**：经典 bug 来源。
- **串行依赖**：BN 需要同步 batch 内所有样本，分布式训练里要 sync-BN，通信开销大。

## 4. 为什么 Transformer 用 **Layer Normalization** (LN, 层归一化)

LN 在**每个样本自己的特征维度上** normalize，不跨 batch：

$$\hat x = \frac{x - \mu_x}{\sqrt{\sigma_x^2 + \epsilon}}$$

其中 $\mu_x, \sigma_x^2$ 只在**当前 token 的 hidden dim 上**算。

优势：

- **和 batch 无关**：小 batch 甚至 batch=1（LLM 推理一个 query）都没问题。
- **和序列长度无关**：变长输入、padding 完全不影响——每个 token 自己算自己的。
- **训练 / 推理行为完全一致**：没有 running statistics，没有模式切换。
- **适合自回归生成**：推理时一个 token 一个 token 出，根本凑不出 batch 统计。

## 5. Normalization 全家桶

对一个 $(N, C, H, W)$ 的 feature：

- **BN**：沿 $(N, H, W)$ 聚合，每个 channel 一套 $\mu, \sigma$ → 依赖 batch。
- **LN**：沿 $(C, H, W)$ 聚合，每个样本一套 → 不依赖 batch。
- **InstanceNorm**：沿 $(H, W)$ 聚合，每个样本每个 channel 一套 → 风格迁移常用。
- **GroupNorm**：把 channel 分组，沿 $(C_{\text{group}}, H, W)$ 聚合 → 小 batch 场景替代 BN。

## 6. **Root Mean Square Normalization** (RMSNorm, 均方根归一化)

LLaMA 系列用的变体：

$$\hat x = \frac{x}{\sqrt{\text{mean}(x^2) + \epsilon}} \cdot \gamma$$

去掉了减均值那一步只做 rescale。经验上效果和 LN 相当，但少一次均值计算、少一个可学参数 $\beta$，**工程上更快**。现在主流 LLM（LLaMA / Mistral / Qwen）都换成了 RMSNorm。

## 7. 常见追问预判

- **Pre-LN vs Post-LN**：原始 Transformer 是 Post-LN（norm 在残差后），训练不稳定需要 warmup；现代 LLM 都改成 Pre-LN（norm 在残差前），梯度更稳，可以不用 warmup。
- **BN 为什么在 CV 仍然主流**：图像任务 batch 大、长度固定（spatial dim），BN 的正则化副作用（batch 内样本互相"看见"）反而有益。
- **LN 对极端值更鲁棒**：但也意味着在方差很小的特征维度上会放大噪声，所以在某些场景需要额外 gating 或 QK-Norm。
"""


DESC_ADAM_SGD = r"""# Adam vs SGD and AdamW

## 1. **Stochastic Gradient Descent** (SGD, 随机梯度下降) 和 momentum

**Plain SGD**：$w \leftarrow w - \eta \nabla L$，每步直接沿负梯度走。噪声大、学习率敏感、在山谷（ravine）里来回震荡。

**SGD with momentum**：

$$v_t = \beta v_{t-1} + \nabla L, \quad w \leftarrow w - \eta v_t$$

引入动量，累积历史梯度方向，震荡被平均掉，收敛更快更稳。

## 2. **Adaptive Moment Estimation** (Adam, 自适应动量估计) 在做什么

Adam = momentum + 自适应学习率 两件事合起来，用 **Exponential Moving Average** (EMA, 指数移动平均) 维护一阶矩和二阶矩：

$$m_t = \beta_1 m_{t-1} + (1 - \beta_1)\nabla L \qquad (\text{一阶矩：momentum})$$

$$v_t = \beta_2 v_{t-1} + (1 - \beta_2)(\nabla L)^2 \qquad (\text{二阶矩：gradient 的 RMS})$$

$$w \leftarrow w - \eta \cdot \frac{\hat m_t}{\sqrt{\hat v_t} + \epsilon}$$

$\hat m, \hat v$ 是 bias correction，因为 $m_0 = v_0 = 0$ 初始偏小：$\hat m_t = m_t / (1 - \beta_1^t)$，$\hat v_t = v_t / (1 - \beta_2^t)$。

**直觉**：

- $m_t$ 像 momentum，让方向更稳。
- $v_t$ 像"每个参数自己的 gradient 尺度"，梯度大的维度学习率自动变小、梯度小的维度学习率自动变大——**per-parameter adaptive learning rate**。

这近似做了"gradient normalization"——每个参数都被自己的历史梯度幅度归一化。

## 3. Adam vs SGD 的优劣

| 维度 | SGD (+ momentum) | Adam |
|-----|------------------|------|
| 学习率 | 所有参数共享，需要精调 + schedule | 自适应，对 lr 没那么敏感 |
| 收敛速度 | 慢但稳 | 快，特别是前期 |
| 泛化 | 往往更好 | 经验上略差 |
| 超参数 | lr + momentum | lr + $\beta_1, \beta_2, \epsilon$ |
| 稀疏梯度 | 差 | 好（embedding、NLP 场景） |
| 适用 | CV 分类、ResNet 时代主流 | Transformer / LLM / 不规则 loss landscape |

"泛化更差"的直觉：Adam 的自适应步长让优化器倾向找到 sharp minimum（loss 表面尖的底）；SGD 的固定 lr + 噪声让它更倾向 flat minimum（loss 表面平的底）。普遍的经验是 flat minima 泛化更好——这是个活跃研究话题，不是定论。

**"更容易进 local minima" 这个说法要小心**：现代 DL 里，非凸 loss 的鞍点远比 local minima 多，真正的 local minima 质量通常都差不多，是否泛化好更多取决于收敛到哪种形状的 minimum（sharp vs flat），不是"是否陷进 local"。

## 4. **AdamW** (AdamW, 解耦权重衰减 Adam) 解决的问题

**核心问题**：L2 regularization 和 weight decay 在 SGD 下等价，在 Adam 下不等价。

传统做法把 L2 写进 loss：$L + \tfrac{\lambda}{2}\|w\|^2$，梯度里多了一项 $\lambda w$。

**在 SGD 下**：

$$w \leftarrow w - \eta(\nabla L + \lambda w) = (1 - \eta\lambda) w - \eta \nabla L$$

这恰好等于"先衰减再更新"的 weight decay。所以 L2 reg = weight decay。

**在 Adam 下这不成立**：$\lambda w$ 这一项会一起进 $m_t$ 和 $v_t$，被自适应学习率 $1 / \sqrt{\hat v_t}$ 缩放——梯度大的参数，正则力度反而被缩小，这没有道理。大参数本该被惩罚得更狠，结果是被惩罚得更轻。

**AdamW 的修正**：把 weight decay 从梯度里拿出来，单独作用在参数上：

$$\boxed{\ w \leftarrow w - \eta \cdot \frac{\hat m_t}{\sqrt{\hat v_t} + \epsilon} - \eta \lambda w\ }$$

decay 项不经过 $v_t$ 的缩放，行为回到 SGD 下干净的"按比例衰减"。

来源：Loshchilov & Hutter, *Decoupled Weight Decay Regularization* (2017)。现代 Transformer / LLM 训练基本全部用 AdamW，不用 Adam。

## 5. 常见追问预判

- **为什么 Transformer 坚持用 Adam/AdamW**：Transformer loss landscape 不规则，参数量大、梯度尺度跨多个量级（比如 embedding vs attention weights），per-parameter adaptive lr 帮助巨大；CV 的 ResNet 上 SGD + momentum 泛化更好，所以 CV 圈部分坚持 SGD。
- **Warmup + cosine schedule**：Adam 早期 $\hat v_t$ 不稳定，大 lr 会炸，所以 LLM 训练标配 linear warmup + cosine decay。
- **$\beta_1, \beta_2$ 默认值**：默认 $0.9, 0.999$；LLM 大 batch 训练常用 $0.9, 0.95$（$\beta_2$ 调低让二阶矩对梯度变化响应更快）。
- **其他变体**：LAMB（大 batch 训练）、Lion（Google 2023，只用 sign + momentum，参数和显存更省）、Shampoo / Sophia（二阶方法）。
"""


DESC_VANISH_EXPLODE = r"""# Vanishing / Exploding Gradient

## 1. 成因：链式法则的连乘放大 / 衰减

深度网络的反向传播是一个长链式乘法：

$$\frac{\partial L}{\partial w_1} = \frac{\partial L}{\partial h_L} \cdot \prod_{l=2}^{L} \frac{\partial h_l}{\partial h_{l-1}} \cdot \frac{\partial h_1}{\partial w_1}$$

每层的 Jacobian $\partial h_l / \partial h_{l-1}$ 大致是**权重矩阵 × 激活函数导数**。如果这个量的"典型大小"是 $r$，那总梯度 $\propto r^L$：

- $r < 1$ → 指数衰减 → **梯度消失**（gradient vanishing）。
- $r > 1$ → 指数爆炸 → **梯度爆炸**（gradient exploding）。

两端都导致训练失败：消失时浅层学不动，爆炸时参数飞、loss 变 NaN。

## 2. 两个常见具体诱因

**(a) 激活函数饱和**：sigmoid 的导数 $\sigma'(z) \in (0, 0.25]$，tanh 导数 $\in (0, 1]$，多层相乘就消失。这是早期深度网络训不起来的主因。

**(b) 权重初始化不当**：权重方差太大 → 前向激活爆炸、反向梯度爆炸；太小 → 前向激活消失、反向梯度消失。

## 3. 缓解手段

### 激活函数

换成不饱和的：**Rectified Linear Unit** (ReLU, 修正线性单元)（正半轴导数恒为 1）及其变体 LeakyReLU / GELU / SiLU。这是最基础也最有效的一步。

### 初始化

让每层的输入输出方差大致保持一致：

- **Xavier / Glorot** 初始化（适配 tanh / sigmoid）：方差 $= 1 / n_{\text{in}}$。
- **He / Kaiming** 初始化（适配 ReLU）：方差 $= 2 / n_{\text{in}}$。

现代框架默认就是这些，但自定义层时容易踩坑。

### Normalization

把每层输入强制拉回一个合理的分布：

- BatchNorm / LayerNorm / RMSNorm 让激活值不会漂移到饱和区，梯度就不会消失。
- 这也是 Transformer 离不开 LayerNorm 的原因之一。

### 残差连接（Residual / Skip connections）

**Residual Network** (ResNet, 残差网络) 的核心：$h_{l+1} = h_l + F(h_l)$。反向传播时梯度可以**直接绕过** $F$ 流回浅层，不管 $F$ 里乘了多少次衰减：

$$\frac{\partial h_{l+1}}{\partial h_l} = I + \frac{\partial F}{\partial h_l}$$

那个 $I$ 保底保证了梯度不会随深度指数衰减。这是训练 100+ 层网络的关键创新，Transformer 的 "$x + \text{Attn}(x)$" 也是同样思路。

### Gradient clipping（专治爆炸）

梯度范数超过阈值就按比例缩放：

$$g \leftarrow g \cdot \min\left(1,\ \frac{\tau}{\|g\|}\right)$$

**Recurrent Neural Network** (RNN, 循环神经网络) / **Long Short-Term Memory** (LSTM, 长短期记忆) / 大模型训练标配。

### 学习率 warmup

训练初期参数不稳定，直接用大 lr 容易炸。用 linear warmup（lr 从 0 线性升到 peak）让前几百步温和过渡，现代 Transformer 训练标配。

### 架构层面（序列模型）

原始 RNN 梯度消失严重，LSTM / **Gated Recurrent Unit** (GRU, 门控循环单元) 用 gating 机制让信息通过 "cell state" 近乎无衰减地传递多步，是 Transformer 出现前解决长程依赖的主流方案。

## 4. 工程 checklist

怀疑梯度消失 / 爆炸时：

1. **数据**：先排除低级问题——输入有没有 NaN / Inf？label 是否正确？输入是否 standardize？
2. **loss 行为**：loss NaN / Inf → 多半爆炸；loss 长期不降 → 可能消失。
3. **监控 gradient norm**：这是最直接的信号；分层画出来看是哪几层的梯度量级异常。
4. **检查初始化**：自定义层是不是忘了正确初始化？
5. **加上 gradient clipping**（治标，但对 RNN / LLM 是标配）。
6. **加 normalization 层**：BN / LN / RMSNorm。
7. **加残差连接**：如果模型很深且没有 residual。
8. **换激活函数**：sigmoid / tanh → ReLU 族。
9. **lr warmup + 合适的 schedule**。
10. **模型规模 vs 数据量**：太大的模型在小数据上可能根本无法稳定训练。

## 5. 常见追问预判

- **为什么 ReLU 不彻底解决消失**：dead ReLU 问题——输入长期为负的神经元梯度恒为 0 也学不动。LeakyReLU / GELU 缓解。
- **Transformer 里哪里解决梯度问题**：LayerNorm + residual 两个一起发力，Pre-LN 比 Post-LN 梯度更稳。
- **LSTM 为什么能避免梯度消失**：cell state 的更新是加法而不是乘法（$c_t = f_t \odot c_{t-1} + i_t \odot \tilde c_t$），梯度沿 cell state 的路径几乎不衰减。
"""


DESC_DROPOUT = r"""# Dropout

## 1. 它在做什么

训练时每个前向 pass，对每个神经元以概率 $p$ **临时置零**（每次 mask 都随机重采样）。等价于在原网络里随机采一个子网络来训练这一步，下一步再采另一个。

## 2. 为什么 work：两个互补视角

### (a) 隐式 Ensemble（主流解释）

$n$ 个神经元有 $2^n$ 种可能的 mask → $2^n$ 个不同的子网络。每个 mini-batch 实际上在训练其中一个随机子网络，它们**共享权重**。推理时不 dropout，等价于对这 $2^n$ 个子网络做**近似的几何平均预测**。

Ensemble 能降 variance、提升泛化，dropout 把这个效果"免费"内化进一个模型里。

### (b) 防止 co-adaptation

没有 dropout 时，神经元之间容易形成**依赖组合**——特征 A 必须和特征 B 一起才 work，单独都不行。dropout 让任意神经元可能随时消失，迫使网络学出**冗余且独立**的表示。每个特征都要自己能打。

这和 L2 正则、数据增强是同一个思路：加噪 → 模型不能指望任何一个具体输入 → 学更鲁棒的表示。

## 3. Inference 时怎么处理

训练时激活的期望 = 原值 $\times (1 - p)$，推理时不 dropout，直接用原值会让**激活量级放大 $1 / (1 - p)$ 倍**，分布对不上。两种等价做法：

**(a) Vanilla dropout**：训练时不动、推理时把权重乘 $(1 - p)$。

**(b) Inverted dropout**（现代默认，PyTorch / TF 实现）：训练时保留的神经元乘 $1 / (1 - p)$，推理时什么都不做。

$$\text{train: } \hat x = \frac{x \odot m}{1 - p}, \quad m_i \sim \text{Bernoulli}(1 - p)$$

$$\text{infer: } \hat x = x$$

两种方式在期望意义上等价，inverted 更方便因为推理路径干净。

**注意**：推理和训练的激活**期望**对齐了，但 **variance 不一样**。这就是 Monte Carlo Dropout 的出发点——推理时故意保留 dropout，做多次前向取均值 + 方差，用作不确定性估计。

## 4. 常见追问预判

### 什么时候不该用 dropout

- **和 BatchNorm 一起用有冲突**：dropout 改变激活分布，BN 的 running stats 会被污染。经验做法是只用 BN，或 dropout 放在 BN 之后。
- **CNN 里效果有限**：空间相关性强，普通 dropout 容易被邻近像素补偿。改用 **Spatial Dropout**（整个 feature map channel 一起丢）。
- **Transformer 里位置**：attention weight 后、FFN 内部、残差加和前都会加 dropout，不同位置作用不同。

### Dropout 和 L2 的关系

两者都是正则化，都降 variance。dropout 有时可以理解为一种"随机的 L2"，但不完全等价。实践中常常一起用。

### DropConnect

丢的是权重（edges）而不是神经元（nodes），理论上更灵活，实践少用。

### 现代大模型里的 dropout

LLaMA / GPT 系列**几乎不用** dropout（或 $p$ 非常小）。原因是数据量巨大 + 大 batch，过拟合不是主要矛盾，欠拟合才是。Vision 小模型、中等规模 NLP 仍然常用。

### 和 ensemble 的精确关系

严格的 ensemble 是独立训练多个模型然后求平均；dropout 的子网络共享权重，所以是**近似 ensemble**，论文里叫 "cheap ensemble"。真正的 ensemble（多次随机种子训练不同模型再集成）效果往往更好但贵得多。
"""


DESC_ACTIVATION = r"""# Activation Function Evolution

## 1. **Rectified Linear Unit** (ReLU, 修正线性单元)

$$\text{ReLU}(x) = \max(0, x)$$

**优点**：正半轴导数恒为 1，解决了 sigmoid / tanh 的梯度消失；计算极快；稀疏激活（负值全置 0）。ResNet 时代的绝对主流。

**缺点**：

- **Dead ReLU**：输入长期为负的神经元梯度恒为 0，永远学不动。
- **非光滑**：在 $x = 0$ 处不可导（次梯度）。
- **非零均值**：输出恒 $\ge 0$，可能导致后一层梯度方向有偏。

**变体**：

- LeakyReLU：$\max(\alpha x, x)$，负半轴给一个小斜率 $\alpha \approx 0.01$。
- **Parametric ReLU** (PReLU, 参数化 ReLU)：$\alpha$ 可学。
- **Exponential Linear Unit** (ELU, 指数线性单元)：负半轴用指数过渡，均值更接近 0。

## 2. **Gaussian Error Linear Unit** (GELU, 高斯误差线性单元)

$$\text{GELU}(x) = x \cdot \Phi(x)$$

$\Phi$ 是标准正态的 CDF。直觉：ReLU 是"硬门"（要么通过要么堵死），GELU 是"软门"——按 $x$ 的大小**概率性加权通过**。

**性质**：

- 处处光滑可导。
- 对小的负值保留一点梯度（像 LeakyReLU），但过渡是光滑的。
- 计算上用 tanh 近似：

$$\text{GELU}(x) \approx 0.5 x \left(1 + \tanh\left[\sqrt{2 / \pi}(x + 0.044715 x^3)\right]\right)$$

BERT、GPT-2、GPT-3 都用 GELU，Transformer 时代的默认选择。

## 3. **Sigmoid Linear Unit** (SiLU, Sigmoid 线性单元) / **Swish**

$$\text{Swish}(x) = x \cdot \sigma(x) = \frac{x}{1 + e^{-x}}$$

就是 $x$ 乘上自己的 sigmoid。Google 2017 年用 NAS 搜出来的，形状和 GELU **几乎一模一样**（都是"光滑的 LeakyReLU"），但计算更便宜。PyTorch 里叫 SiLU。GELU 和 Swish 在实验上差别很小，现代多数实现倾向 Swish（更快）。

## 4. **Gated Linear Unit** (GLU, 门控线性单元) 系列

GLU 不是一个激活函数，而是一个**门控结构**。经典 GLU：

$$\text{GLU}(x) = (x W_1 + b_1) \odot \sigma(x W_2 + b_2)$$

两条支路，一条提供"内容"，另一条过 sigmoid 当"门"控制哪些维度通过。$\odot$ 是 element-wise 乘。

**Swish-Gated Linear Unit** (SwiGLU, Swish 门控线性单元)（LLaMA / PaLM / Mistral / Qwen 用的）把门换成 Swish：

$$\text{SwiGLU}(x) = \text{Swish}(x W_1) \odot (x W_2)$$

**GeGLU**（T5 变体）把门换成 GELU：

$$\text{GeGLU}(x) = \text{GELU}(x W_1) \odot (x W_2)$$

## 5. 为什么 LLM 都转向 GLU 系列

**(a) 表达力更强**：标准 FFN 是 Linear → activation → Linear，GLU 版本是 (Linear → Swish) $\odot$ Linear → Linear，多了一个乘法交互，可以选择性放大 / 抑制信息通路。

**(b) 经验效果稳定更好**：Noam Shazeer 2020 的 *GLU Variants Improve Transformer* 论文系统对比，GeGLU / SwiGLU 在相同参数预算下 perplexity 更低。

**(c) 参数量要打个折扣再比较**：原始 FFN 用 $4d$ 的 hidden dim，GLU 版本有两条支路所以实际算 $2 \times d_{\text{hidden}}$ 个参数。为了公平比较，GLU FFN 常把 hidden dim 调成 $\tfrac{2}{3} \times 4d = \tfrac{8}{3} d$，总参数量回到和 vanilla 差不多。在参数量对齐后 SwiGLU 仍然更好，这才是它被广泛采用的原因。

**(d) 梯度性质好**：乘法 gating 配合 residual connection，梯度流稳定。

## 6. 对比表

| 激活 | 公式 | 平滑 | 参数 | 用在哪 |
|-----|------|------|------|--------|
| ReLU | $\max(0, x)$ | 否 | 无 | ResNet / CNN |
| LeakyReLU | $\max(\alpha x, x)$ | 否 | $\alpha$ | CNN |
| GELU | $x \Phi(x)$ | 是 | 无 | BERT / GPT-2/3 |
| Swish / SiLU | $x \sigma(x)$ | 是 | 无 | 和 GELU 互换 |
| SwiGLU | $\text{Swish}(x W_1) \odot (x W_2)$ | 是 | 两组 $W$ | LLaMA / Mistral / Qwen |

## 7. 常见追问

- **为什么 ReLU 在 CV 仍然主流**：图像数据冗余度高、CNN 参数少，ReLU 的简单 + 稀疏反而有益；训练速度快也是生产考量。
- **GELU 的概率解释**：$x \Phi(x)$ 可以理解为 "$x$ 以 $\Phi(x)$ 的概率被保留"，结合了 dropout 的随机性思想（随机 × 大小）。
- **SwiGLU 的参数量代价**：标准 FFN 两个 $d \times 4d$ 矩阵 $= 8 d^2$；SwiGLU 三个 $d \times \tfrac{8}{3} d$ 矩阵 $= 8 d^2$（维度调整后）。对齐后参数持平，但计算图多了 gating 乘法。
"""


# Map each leaf path -> (placeholder, new_description)
LEAVES: dict[str, tuple[str, str]] = {
    "ml-fundamentals/unsupervised/k-means-assumptions-and-failures": (
        "TODO[MLF-k-means-assumptions-and-failures]",
        DESC_KMEANS,
    ),
    "ml-fundamentals/unsupervised/em-and-gmm": (
        "TODO[MLF-em-and-gmm]",
        DESC_EM_GMM,
    ),
    "ml-fundamentals/dl_training/batchnorm-vs-layernorm": (
        "TODO[MLF-batchnorm-vs-layernorm]",
        DESC_BN_LN,
    ),
    "ml-fundamentals/dl_training/adam-vs-sgd-adamw": (
        "TODO[MLF-adam-vs-sgd-adamw]",
        DESC_ADAM_SGD,
    ),
    "ml-fundamentals/dl_training/vanishing-exploding-gradient": (
        "TODO[MLF-vanishing-exploding-gradient]",
        DESC_VANISH_EXPLODE,
    ),
    "ml-fundamentals/dl_training/dropout": (
        "TODO[MLF-dropout]",
        DESC_DROPOUT,
    ),
    "ml-fundamentals/dl_training/activation-function-evolution": (
        "TODO[MLF-activation-function-evolution]",
        DESC_ACTIVATION,
    ),
}


def sha256_of_descriptions(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) pairs of the 7 target leaves."""
    h = hashlib.sha256()
    for path in sorted(LEAVES.keys()):
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE path = ?", (path,)
        ).fetchone()
        h.update(path.encode("utf-8"))
        h.update(b"\x00")
        h.update((row[0] or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def validate_content(path: str, content: str) -> None:
    """AC: each description must contain KaTeX math + at least one section header."""
    if "$" not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no $...$ math delimiter found")
    if "## " not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no '## ' section header found")


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    # Pre-flight: validate every staged content meets AC before touching DB.
    for path, (_placeholder, content) in LEAVES.items():
        validate_content(path, content)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_of_descriptions(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = {"UPDATED": 0, "SKIPPED": 0}
        for path, (placeholder, new_content) in LEAVES.items():
            row = conn.execute(
                "SELECT id, description FROM framework_nodes WHERE path = ?",
                (path,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f"[FAIL] missing node at path={path}")
            node_id, current = row
            if current == new_content:
                counts["SKIPPED"] += 1
                print(f"[SKIP]   id={node_id} path={path}")
                continue
            if current != placeholder:
                preview = (current or "")[:80].replace("\n", " ")
                raise RuntimeError(
                    f"[CONFLICT] path={path}: existing description neither "
                    f"placeholder nor expected new content. "
                    f"current[:80]={preview!r}"
                )
            conn.execute(
                "UPDATE framework_nodes SET description = ? WHERE id = ?",
                (new_content, node_id),
            )
            counts["UPDATED"] += 1
            print(
                f"[UPDATE] id={node_id} path={path} "
                f"len={len(new_content)} (was {len(current)})"
            )

        conn.commit()
        post_hash = sha256_of_descriptions(conn)
        print(f"[POST] sha256={post_hash}")
    finally:
        conn.close()

    print(
        f"[SUMMARY] updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total={counts['UPDATED'] + counts['SKIPPED']} (expected 7)"
    )
    if counts["UPDATED"] + counts["SKIPPED"] != 7:
        print("[FAIL] expected to touch exactly 7 leaves")
        return 1
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
