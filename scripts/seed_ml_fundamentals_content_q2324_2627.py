"""Seed: T-P0-546 -- ML Fundamentals X-depth batch Q#23/#24/#26/#27.

[T-MLF-06d] Fills placeholder descriptions for four T3 leaves under
`ml-fundamentals/llm_stats/` with X-depth content (moderate expansion,
5-section template: 问题设定 / 推导 / 物理意义 / 常见追问 / 参考).

Unlike the Y-depth entries (Q#21, #22, #25) which run 8k-12k chars with
exhaustive derivations, X-depth aims for ~3.5k-5k chars per leaf:
complete structure + calibrated acronym expansion + formula context,
but without the deep-dive proof walkthroughs.

Leaves touched:

  #23 tokenization-bpe-wordpiece-sentencepiece
      Acronyms expanded on first use: BPE, LM, PMI.
      Covers BPE (frequency merges), WordPiece (likelihood/PMI merges),
      SentencePiece (raw-byte, language-agnostic wrapper supporting BPE
      or unigram LM). LLaMA-SentencePiece-BPE vs T5-SentencePiece-unigram.

  #24 scaling-law-chinchilla
      Acronyms expanded on first use: FLOP, LR.
      Kaplan 2020 (N ~ C^0.73, D ~ C^0.27) vs Hoffmann 2022 Chinchilla
      (N ~ C^0.5, D ~ C^0.5; ~20 tokens/param). Methodology bug (fixed
      LR schedule undertrained small models), GPT-3 undertraining,
      LLaMA-3 1875 tokens/param factoring inference cost.

  #26 clt-vs-lln
      Acronyms expanded on first use: CLT, LLN, IID. Inline symbols
      a.s., ->_P, ->_d defined.
      LLN (bias vanishes pointwise / almost-surely) vs CLT (variance
      decays at 1/sqrt(n) with Gaussian shape). Motivates CIs and
      hypothesis tests.

  #27 ab-test-pvalue-sample-size-multiple-testing
      Acronyms expanded on first use: MDE, FWER, FDR, BH, CI.
      p-value misconceptions (NOT P(H0|data)); two-means and
      two-proportions sample-size formulas; Bonferroni/Holm (FWER)
      vs Benjamini-Hochberg (FDR).

Idempotency:
  - Each leaf has a stable expected description; second run yields
    updated=0 skipped=4 conflict=0.
  - SHA-256 of the 4 (path, description) pairs captured pre/post.
  - If a leaf's existing description is neither the placeholder
    `TODO[MLF-<slug>]` nor the new content, script aborts with
    [CONFLICT] before any write.

Acceptance:
  - 4 framework_nodes.description rows updated.
  - Each description contains KaTeX math ($ or $$) and '## ' headers.
  - Re-run is no-op (updated=0 skipped=4).
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"


# ---------------------------------------------------------------------------
# Q#23 Tokenization: BPE / WordPiece / SentencePiece
# ---------------------------------------------------------------------------

DESC_TOKENIZATION = r"""# Tokenization：BPE / WordPiece / SentencePiece

## 1. 问题设定

语言模型的输入是离散 token 序列，tokenizer 的任务是把原始文本切成固定词表里的一串 id。三条硬约束：(i) 词表要有限（softmax over vocabulary 的 $O(|V|)$ 开销与 embedding 参数量 $|V| \cdot d$ 都和 $|V|$ 线性相关）；(ii) 罕见词或拼写错误不能变成 **Out-Of-Vocabulary** (OOV, 未登录词) 丢给 `<unk>`——LLM 里任何一个 token 被 `<unk>` 吞掉都是信息损失；(iii) 多语言 / 代码 / emoji 这些非典型输入也要能编码。

主流解法都是**subword tokenization**（子词分词）：把词拆成更小的可组合单位。三种代表算法：

- **Byte Pair Encoding** (BPE, 字节对编码)：按**频率**贪心合并相邻符号对。
- **WordPiece**：按**似然增益**合并，等价于最大化合并后语言模型对训练语料的似然，度量上近似 **Pointwise Mutual Information** (PMI, 点互信息)。
- **SentencePiece**：一个**语言无关**的框架工具，直接在原始字节流上训练，无需预分词（pre-tokenization），支持 BPE 或 unigram **Language Model** (LM, 语言模型) 两种合并策略。

第一次出现的其他术语：UTF-8 byte 级编码、merge rule、vocabulary size $|V|$。

## 2. 推导：三种合并准则

### 2.1 BPE（Sennrich 2016）

初始化：把每个词拆成 UTF-8 字节序列 + 结尾符 `</w>`。统计语料里所有**相邻符号对** $(a, b)$ 的出现次数 $\mathrm{count}(a, b)$。每轮取频率最高的一对合并成新 token `ab`，加入词表，重写语料里所有出现：

$$\text{merge} \;=\; \arg\max_{(a, b)}\;\mathrm{count}(a, b)$$

重复 $M$ 次（$M = |V| - |$base$|$）。决策准则**只看频率**，简单、快、确定性强。

### 2.2 WordPiece（Schuster & Nakajima 2012; BERT）

合并准则从频率换成**似然增益**：选择合并后最大化训练语料似然的对。用 unigram 近似：

$$\text{score}(a, b) \;=\; \frac{P(ab)}{P(a)\,P(b)} \;\propto\; \frac{\mathrm{count}(a, b)\,\cdot\, N}{\mathrm{count}(a)\,\cdot\,\mathrm{count}(b)}$$

这是 PMI 的乘性形式——如果 $a, b$ 总是一起出现（互信息高），就优先合并；如果只是分别都常见（如 `the` 和 `##s`），不合并。相比 BPE，WordPiece 更青睐**语义共现**而非单纯高频对。

### 2.3 SentencePiece（Kudo & Richardson 2018）

SentencePiece 不是一个独立的合并准则，而是一个**工具 + 框架**：

- 直接在**原始字节序列**上训练，不要求预分词（所以 `hello world` 和 `hello  world` 区别被保留）。
- 把空格当作普通字符 `▁`（U+2581）编码，拼回原文时零歧义。
- 支持两种 back-end：**SentencePiece-BPE**（frequency-based merges）与 **SentencePiece-unigram LM**（Kudo 2018，先定义一个大词表再基于 EM 剪枝，保留让语料似然最大的子集）。

关键优势：不依赖 Moses / Jieba / MeCab 这些语言特定的预处理器——LLaMA 家族、T5、mT5 都用 SentencePiece，是"一份模型跑所有语言"的必要前提。

## 3. 物理意义：三者的分工

| 算法 | 合并准则 | 依赖预分词 | 常见用户 |
|------|----------|-----------|----------|
| BPE | 频率 | 传统 BPE：是；byte-level BPE：否 | GPT-2 / GPT-3 / GPT-4（byte-level BPE） |
| WordPiece | 似然增益 (~PMI) | 是（Moses） | BERT、DistilBERT、Electra |
| SentencePiece-BPE | 频率（byte-level） | 否 | LLaMA-1/2/3、Mistral、Falcon |
| SentencePiece-unigram | 似然 + EM 剪枝 | 否 | T5、mT5、ALBERT |

几个重要的衍生点：

- **byte-level BPE**（GPT-2 首次使用）让 OOV 问题彻底消失：任意 Unicode 字符都能拆成 UTF-8 字节，再用 BPE 合并，词表不需要覆盖"所有字符"。代价是罕见语种的字符可能需要 2-4 个 token 表示一个字。
- **预分词的取舍**：BERT 先用 Moses 做语言级分词，这让词内 subword 有 `##` 前缀标识；SentencePiece 直接把空格纳入 token，简化数据管道但需要 `▁` 这类特殊字符。
- **词表大小**：$|V|$ 常见选项 32k (LLaMA-1)、50k (GPT-2)、128k (LLaMA-3)、256k (Gemma)。$|V|$ 大 → 每 token 表达力更强、序列更短（推理更快），但 embedding 参数膨胀 $|V| \cdot d$；$|V|$ 小 → embedding 省、但需要更多 token 表达同一句话。

## 4. 常见追问

### 4.1 Byte-level vs char-level vs subword

纯 byte-level（ByT5）参数省、鲁棒于拼写错误，但序列太长（每字符多 byte）；char-level（CANINE）居中；subword（BPE/WordPiece/SentencePiece）是 2024 年主流平衡点：序列短 + 压缩好 + 可处理 OOV。

### 4.2 为什么 LLaMA 用 SentencePiece-BPE 而不是 GPT 的 byte-level BPE

LLaMA 要服务多语言训练语料，SentencePiece 的"不需预分词 + 语言无关"是硬需求。另外 SentencePiece 对中文 / 日文这类无空格语言的切分更自然，byte-level BPE 会把一个汉字切成 3 个 byte token，导致中文模型训练效率低。

### 4.3 tokenizer 可以跨模型复用吗

通常不行——不同 tokenizer 训练语料不同，词表 id ↔ 字符映射各自独立，swap 后 embedding / LM head 参数全对不上。唯一例外：同系列新版本（如 LLaMA-2 → LLaMA-3）如果共享 tokenizer，可以复用 embedding 做初始化（LLaMA-3 升级到 128k 就**没法**直接复用）。

### 4.4 tokenizer drift：为什么 GPT-3 英文高效、中文差

GPT-3 的 tokenizer 在英文占主导的语料上训练，高频英文词（the, and, is）是单 token，中文常用字平均 2-3 个 token。所以同样字数的中文 prompt 消耗更多 token → 上下文窗口更快吃满 + 推理更贵。这是跨语言 scaling 中的隐藏税。

### 4.5 词表大小怎么选

经验：词表大小随**目标语言多样性**和**模型参数量**增长。单语英文模型 32k 够；多语 / 代码 / 数学混合 → 64k-128k；Gemma 2B 用 256k 是因为小模型下 embedding 参数占比可接受，且大词表能明显缩短序列。

## 5. 参考

- Sennrich, Haddow, Birch 2016, *Neural Machine Translation of Rare Words with Subword Units* —— BPE 的原始论文（从数据压缩算法借用过来）。
- Schuster & Nakajima 2012, *Japanese and Korean Voice Search* —— WordPiece 首次提出；BERT (Devlin 2018) 是最广泛的用例。
- Kudo & Richardson 2018, *SentencePiece: A simple and language independent subword tokenizer* —— SentencePiece 框架。
- Kudo 2018, *Subword Regularization* —— unigram LM tokenization 的正式定义。
"""


# ---------------------------------------------------------------------------
# Q#24 Scaling Law: Chinchilla vs Kaplan
# ---------------------------------------------------------------------------

DESC_SCALING_LAW = r"""# Scaling Law：Chinchilla 修正 Kaplan

## 1. 问题设定

给定固定的计算预算 $C$（单位 **Floating-Point Operation** (FLOP, 浮点运算次数)，典型量级 $10^{21}$–$10^{24}$），要如何分配给**模型参数量** $N$ 和**训练 token 数** $D$，才能最小化最终的 validation loss $L(N, D)$？

约束关系（对 Transformer 训练）：

$$C \;\approx\; 6 \cdot N \cdot D$$

系数 6 来自 forward 的 2 倍（matmul 的乘加配对） + backward 的 4 倍（激活梯度 + 权重梯度）。所以 $N$ 和 $D$ 之间是**一换一**的乘法关系：加倍参数等价于减半 token 数（在预算不变下）。

问题转化为：在 $N \cdot D = \text{const}$ 约束下，哪个 $(N^\star, D^\star)$ 让 loss 最低？

第一次出现的其他缩写：**Learning Rate** (LR, 学习率)、compute-optimal、Chinchilla、Kaplan's law。

## 2. 推导：两个 scaling law 的数学形式

### 2.1 参数化的 loss surface

Kaplan 2020 与 Hoffmann 2022 都假设 loss 的渐近形式：

$$L(N, D) \;=\; E \;+\; \frac{A}{N^{\alpha}} \;+\; \frac{B}{D^{\beta}}$$

其中 $E$ 是**不可约的熵下界**（真实语言的内在不确定性），$A/N^\alpha$ 是参数不足导致的欠拟合项，$B/D^\beta$ 是数据不足导致的欠拟合项。两项都是幂律衰减，指数 $\alpha, \beta$ 由经验拟合。

对 $C = 6ND$ 约束做 Lagrange：$\frac{\partial L}{\partial N} = \lambda \cdot D$、$\frac{\partial L}{\partial D} = \lambda \cdot N$，消去 $\lambda$ 得到最优 $(N^\star, D^\star)$ 满足：

$$\frac{\alpha A}{N^{\alpha + 1}} \cdot N \;=\; \frac{\beta B}{D^{\beta + 1}} \cdot D \;\Longrightarrow\; N^\star \propto C^{\beta / (\alpha + \beta)},\;\; D^\star \propto C^{\alpha / (\alpha + \beta)}$$

最终 loss 随 $C$ 的 scaling 也是幂律：$L - E \propto C^{-\alpha\beta/(\alpha+\beta)}$。

### 2.2 Kaplan 2020 vs Hoffmann 2022 的拟合差

**Kaplan（OpenAI）2020**：在 $C$ 增长时，$N$ 要涨得比 $D$ 快：

$$N^\star \propto C^{0.73}, \quad D^\star \propto C^{0.27}$$

**Hoffmann et al. 2022（DeepMind Chinchilla）**：在更 careful 的实验（400+ 跑，每跑重新调 LR schedule）后得到：

$$N^\star \propto C^{0.5}, \quad D^\star \propto C^{0.5}$$

等价地 $D^\star / N^\star \approx 20$，即**~20 tokens per parameter** 的经验法则。Chinchilla 70B 训了 1.4T token 就是这个比例。

## 3. 物理意义：Kaplan 的方法论 bug

Kaplan 的 $N^{0.73}$ 说"多加参数比多喂 token 更划算"——GPT-3（175B 参数，300B token，比例 ~1.7 tokens/param）直接按这条建议来的。Chinchilla 的反驳：**GPT-3 严重欠训练**，同样算力下一个 70B + 1.4T token 模型（Chinchilla 本尊）在所有下游任务上都赢 GPT-3 175B。

Hoffmann 定位 bug 为：

- Kaplan 对所有规模用**固定的 LR schedule**。小模型在固定 schedule 下会提前进入 LR 过小阶段——loss 还没收敛 cosine decay 已经把 LR 压到 1e-6。这让**小模型看起来数据饱和更快**，loss 伪平台化，拟合出来的 $\beta$ 被低估。
- Chinchilla 给每个规模独立 tune schedule（cosine 长度与 $D$ 同步），小模型的欠拟合项 $B/D^\beta$ 收敛得更干净，$\beta$ 拟合上升，最优 $D/N$ 比例随之改变。

教训：**scaling law 的指数不是物理常数，是 setup 的函数**。LR schedule、weight decay、batch size、warmup 都会影响拟合曲线。

另一个重要角度：Chinchilla 的 "compute-optimal" 只考虑**训练**的 FLOP。推理时每生成一个 token 的算力 $\propto N$（每样本 $2N$ FLOP），所以生产环境倾向于**更小但训练更久**的模型——LLaMA-3 8B 训了 15T token（~1875 tokens/param），远超 Chinchilla 最优比。在训练 FLOP 上"欠参数过训练"，但总生命周期（训练+推理）成本更低。这是 2024+ 的新范式："post-Chinchilla over-training"。

## 4. 常见追问

### 4.1 emergent abilities 与 scaling

GPT-3 展现的 in-context learning、few-shot reasoning 被描述为 "emergent"——某规模以下能力几乎为 0，超过某规模突然涌现。Schaeffer 2023 *Are Emergent Abilities a Mirage?* 反驳：所谓 emergence 很大程度上是**评测指标**的非线性（准确率是 thresholded），换成对数似然或 token-level 概率差，scaling 仍是平滑 power law。结合 Chinchilla，真正的问题不是"多大才 emergence"，而是"在给定 C 下，$N$ 和 $D$ 比例对不对"。

### 4.2 Chinchilla 适用于 fine-tuning 吗

不直接适用。Fine-tune 的数据预算 $D$ 往往远小于 pretrain，主要约束是**遗忘 / 过拟合**而非 compute-optimality。LoRA / PEFT 下更是如此——$N$ 被冻结，只有少量 adapter 参数可训。scaling law 对 fine-tune 的指导更偏经验（epochs、LR、rank $r$）。

### 4.3 数据不够怎么办：数据重复 vs 数据合成

Chinchilla 比例要 ~20 tokens/param，但全网高质量英文文本有限（Villalobos 2022 估算 ~10T-100T token 上限）。两条路线：

- **多 epoch 训练**：Muennighoff 2023 *Scaling Data-Constrained Language Models* 发现数据重复 4 个 epoch 内 loss 仍按 scaling law 下降，但超过 8 epoch 后收益快速衰减，等价于 token 数虚标。
- **合成数据**：Phi 系列、Llama-3 后期混入大量合成 instruction/reasoning 数据，突破"真实数据上限"。合成数据的 quality 决定这条路有多远。

### 4.4 推理成本改写了最优比

LLaMA-3 8B 用 15T token 训练（~1875 tokens/param，Chinchilla 的 ~94 倍）。数学上 Chinchilla 在训练 FLOP 最优，但 Meta 的考虑是：模型一旦训出来要服务数亿用户，**推理 FLOP $\gg$ 训练 FLOP**，此时把参数压到最小而 token 喂到最多是更划算的整体最优。Sardana 2024 *Beyond Chinchilla-Optimal* 给出把推理成本纳入目标函数后的修正 scaling law。

### 4.5 为什么 $C = 6ND$ 的系数是 6 不是 2

单个 token 前向的 matmul FLOP $\approx 2N$（每个参数做一次乘加，计 2 FLOP）。反向传播要算激活梯度 + 权重梯度，matmul 量是前向的 2 倍，总反向 $\approx 4N$。合计 $\approx 6N$，再乘 $D$ 个 token 就是 $6ND$。Attention 和 LayerNorm 的 non-linear 部分常被忽略（相对 matmul 是低阶量）。

## 5. 参考

- Kaplan et al. 2020, *Scaling Laws for Neural Language Models* —— OpenAI 原始 scaling paper，$N^{0.73}$ 结论；GPT-3 的设计依据。
- Hoffmann et al. 2022, *Training Compute-Optimal Large Language Models* —— Chinchilla paper，修正 Kaplan，$D/N \approx 20$ 法则。
- Sardana et al. 2024, *Beyond Chinchilla-Optimal: Accounting for Inference* —— 把推理 FLOP 纳入优化后的修正。
- Muennighoff et al. 2023, *Scaling Data-Constrained Language Models* —— 数据重复与合成的 scaling 行为。
"""


# ---------------------------------------------------------------------------
# Q#26 CLT vs LLN
# ---------------------------------------------------------------------------

DESC_CLT_VS_LLN = r"""# CLT vs LLN：两个极限定理的分工

## 1. 问题设定

给定**独立同分布**（**Independent and Identically Distributed**，IID，独立同分布）样本 $X_1, X_2, \ldots, X_n$，每个的期望 $\mu = \mathbb{E}[X_i]$，方差 $\sigma^2 = \mathrm{Var}(X_i) < \infty$。研究样本均值 $\bar{X}_n = \frac{1}{n}\sum_{i=1}^n X_i$ 随 $n \to \infty$ 的行为，两条核心定理：

- **Law of Large Numbers** (LLN, 大数定律)：$\bar{X}_n$ 收敛到真值 $\mu$（描述 **bias 消失**）。
- **Central Limit Theorem** (CLT, 中心极限定理)：$\sqrt{n}(\bar{X}_n - \mu)$ 收敛到正态分布（描述 **variance 的衰减速度 + 分布形状**）。

一句话记忆："LLN 保证平均值的 bias 消失；CLT 告诉你 variance 以 $1/\sqrt{n}$ 速度衰减，且分布逼近 Gaussian。"

三种**收敛模式**（贯穿概率论）的简记：

| 符号 | 名字 | 定义（非严格） |
|------|------|---------------|
| $\xrightarrow{a.s.}$ | almost sure，几乎必然 | $P(\lim_n X_n = X) = 1$（除零测集外点点收敛） |
| $\xrightarrow{P}$ | in probability，依概率 | $\forall \varepsilon > 0,\; P(\lvert X_n - X \rvert > \varepsilon) \to 0$ |
| $\xrightarrow{d}$ | in distribution，依分布 | $F_n(x) \to F(x)$ 在 $F$ 的连续点 |

三者强度关系：$a.s. \Rightarrow P \Rightarrow d$（反向不成立）。LLN 给前两种之一，CLT 给第三种。

## 2. 推导：两定理的标准叙述

### 2.1 LLN 弱形式（Khinchin）

假设 $X_i$ IID 且 $\mu = \mathbb{E}[X_i]$ 存在。则

$$\bar{X}_n \xrightarrow{P} \mu, \quad \text{i.e.} \quad \forall \varepsilon > 0,\;\; P(\lvert \bar{X}_n - \mu \rvert > \varepsilon) \to 0 \text{ as } n \to \infty$$

证明要点：Chebyshev 不等式 $P(\lvert \bar{X}_n - \mu \rvert > \varepsilon) \leq \mathrm{Var}(\bar{X}_n) / \varepsilon^2 = \sigma^2 / (n \varepsilon^2) \to 0$。这里 $\mathrm{Var}(\bar{X}_n) = \sigma^2 / n$ 是"variance 随样本量线性缩减"的第一次出现。

### 2.2 LLN 强形式（Kolmogorov）

同样假设下（只需 $\mu$ 存在，不需要 $\sigma^2$），更强的结论：

$$\bar{X}_n \xrightarrow{a.s.} \mu, \quad \text{i.e.} \quad P\!\left(\lim_{n \to \infty} \bar{X}_n = \mu\right) = 1$$

强形式意味着**几乎每一条 sample path** 最终都进入 $\mu$ 的任意小邻域（除概率 0 的异常 path）。实用上两者的区别对 Monte Carlo 估计几乎无影响，但对 martingale / random walk 理论是关键。

### 2.3 CLT（Lindeberg-Lévy）

IID 且 $\sigma^2 < \infty$。定义标准化样本均值

$$Z_n \;=\; \frac{\bar{X}_n - \mu}{\sigma / \sqrt{n}} \;=\; \frac{\sqrt{n}\,(\bar{X}_n - \mu)}{\sigma}$$

则

$$\boxed{\;Z_n \;\xrightarrow{d}\; \mathcal{N}(0, 1)\;}$$

等价地 $\sqrt{n}\,(\bar{X}_n - \mu) \xrightarrow{d} \mathcal{N}(0, \sigma^2)$。关键信息三条：

- **rate**：偏离 $\mu$ 的典型尺度是 $\sigma / \sqrt{n}$，即**标准误**（standard error）。
- **shape**：波动分布是 Gaussian，**不管 $X_i$ 本身分布多怪**（只要方差有限）——这就是 CLT 的"中心"含义。
- **scaling**：样本量加 4 倍，误差减半。这是实验设计里样本量估算的数学根。

### 2.4 两者关系：CLT 蕴含 LLN（弱形式）

$\bar{X}_n - \mu = (\sigma/\sqrt{n}) \cdot Z_n$，$\sigma/\sqrt{n} \to 0$，$Z_n$ 依分布收敛到 $\mathcal{N}(0,1)$ 有界——乘积依概率到 0，即 LLN 弱形式。**但 LLN 成立不一定 CLT 成立**：比如 Cauchy 分布 $\mu$ 不存在（LLN 弱形式也不成立）、$t$-分布自由度 $\leq 2$ 时 $\sigma^2 = \infty$，LLN 仍成立但 CLT 失效。

## 3. 物理意义：这两条定理撑起了统计推断

LLN 是**估计量一致性**的基础：样本均值估计总体均值，样本方差估计总体方差，最大似然估计估计参数真值——都靠某种形式的 LLN 保证 $\hat{\theta}_n \to \theta^\star$。

CLT 是**置信区间 / 假设检验**的基础。给定标准误 $\sigma / \sqrt{n}$（或其估计 $\hat{\sigma}/\sqrt{n}$），**95% Confidence Interval** (CI, 置信区间) 写作：

$$\bar{X}_n \pm 1.96 \cdot \frac{\hat{\sigma}}{\sqrt{n}}$$

1.96 是 $\mathcal{N}(0, 1)$ 的 97.5% 分位——只有 CLT 提供了"分布是 Gaussian"的许可证才能用。同理 z-test、t-test、两样本均值差的检验统计量全都建立在 CLT 渐近正态性上。

**为什么两条都需要**：LLN 只说"样本均值往真值走"，但**没说走得多快**、**误差分布什么样**；CLT 补齐了这两个缺失——才能把"估计 $\hat{\mu}$"变成"置信区间 $\hat{\mu} \pm c \cdot \sigma/\sqrt{n}$"。没有 LLN 谈不上一致性；没有 CLT 谈不上 uncertainty quantification。

## 4. 常见追问

### 4.1 CLT 对**有限方差**的硬性要求

$\sigma^2 < \infty$ 是 CLT 的前提。常见反例：

- **Cauchy 分布**：$\mu, \sigma^2$ 都不存在，样本均值的分布和单个样本一样（仍是 Cauchy），$\sqrt{n}$ 缩放根本不生效。
- **Power-law tail**（$P(X > x) \sim x^{-\alpha}$，$\alpha < 2$）：方差发散，极限定理走 $\alpha$-stable 分布（Lévy-Khinchine），不再 Gaussian。金融收益率、网络流量常见这类重尾。

### 4.2 Berry-Esseen：CLT 收敛速率

CLT 说的是渐近 Gaussian，有限 $n$ 时误差多少？Berry-Esseen 不等式：

$$\sup_x \lvert P(Z_n \leq x) - \Phi(x) \rvert \;\leq\; \frac{C \cdot \mathbb{E}\lvert X_i - \mu \rvert^3}{\sigma^3 \cdot \sqrt{n}}$$

收敛速率 $O(1/\sqrt{n})$，常数 $C < 1$。要求**三阶绝对矩有限**。重尾（kurtosis 大）下常数大，小样本逼近差；这也是 $n = 30$ 经验法则的来源——对"轻尾 + 无重偏"的数据 $n \geq 30$ 一般够用。

### 4.3 非 IID 的 CLT：Lindeberg 条件

独立但不同分布的序列（independent, not identically distributed）：CLT 仍成立当**Lindeberg 条件**满足：

$$\forall \varepsilon > 0,\;\; \frac{1}{s_n^2} \sum_{i=1}^n \mathbb{E}\!\left[ (X_i - \mu_i)^2 \cdot \mathbf{1}\{\lvert X_i - \mu_i \rvert > \varepsilon s_n\} \right] \to 0$$

其中 $s_n^2 = \sum_i \sigma_i^2$。直观：没有任何单个 $X_i$ 贡献主导总方差。A/B test 跨用户异质性、时间序列 IID 假设违反时都要用这个扩展。

### 4.4 Slutsky 定理：CLT + 一致估计量

实际做检验时 $\sigma$ 未知，用 $\hat{\sigma}_n$ 替代。Slutsky：若 $Z_n \xrightarrow{d} Z$ 且 $\hat{\sigma}_n \xrightarrow{P} \sigma$，则 $Z_n \cdot (\sigma / \hat{\sigma}_n) \xrightarrow{d} Z$。所以用 $\hat{\sigma}$ 构造的 t 统计量，大样本下渐近标准正态——这是 t-test 在 $n$ 大时用 z 临界值的理论依据。

### 4.5 Bootstrap：CLT 失效时的备胎

当分布未知 / 尾重 / 样本小到 CLT 还没生效，用 bootstrap 替代：对样本集有放回重抽样 $B$ 次，每次算统计量 $\hat{\theta}_b$，用 $\{\hat{\theta}_b\}_{b=1}^B$ 的经验分位数构造 CI。不依赖 CLT 的 Gaussian 假设，代价是计算量 $O(B \cdot n)$。

## 5. 参考

- Durrett, *Probability: Theory and Examples* —— LLN、CLT、Berry-Esseen 的标准处理（第 2 章）。
- Lindeberg 1922 / Lévy 1925 —— IID 情形 CLT 的最一般证明。
- Efron 1979, *Bootstrap Methods* —— 当 CLT 不适用时的非参数替代。
"""


# ---------------------------------------------------------------------------
# Q#27 A/B Test: p-value, sample size, multiple testing
# ---------------------------------------------------------------------------

DESC_AB_TEST = r"""# A/B test：p-value、样本量、多重检验

## 1. 问题设定

A/B test（在线控制实验）的核心是对两组用户分别应用对照版本 A 和处理版本 B，收集关键指标（CTR、收入、留存），检验 B 的效应是否显著优于 A。三个关键决策：

- **p-value**：给定观测数据，如何量化"B 与 A 无差异"这个零假设被反驳的程度？
- **样本量**：要多少样本才能可靠检出一个业务期待的效应？
- **多重检验**：同时看 10 个指标时，如何控制整体误发现？

第一次出现的缩写：**Minimum Detectable Effect** (MDE, 最小可检测效应)、**Family-Wise Error Rate** (FWER, 族错误率)、**False Discovery Rate** (FDR, 错误发现率)、**Benjamini-Hochberg** (BH, 本杰明-霍克伯格)、**Confidence Interval** (CI, 置信区间)、t-test、z-test。

典型的假设检验框架：

| 符号 | 含义 |
|------|------|
| $H_0$ | 零假设（B 与 A 无差异，$\Delta = 0$） |
| $H_1$ | 备择假设（$\Delta \neq 0$，或单边 $\Delta > 0$） |
| $\alpha$ | 显著性水平，type I error 上限（默认 0.05） |
| $\beta$ | type II error，统计 power $= 1 - \beta$（默认 $\beta = 0.2$） |
| $\delta$ / MDE | 业务认为值得检出的最小效应 |

## 2. 推导：p-value、样本量、corrections

### 2.1 p-value 的数学定义

$p$-value **是**：在 $H_0$ 为真的前提下，观察到比当前更极端统计量的概率。

$$p = P(\lvert T \rvert \geq \lvert t_{\text{obs}} \rvert \mid H_0)$$

判断：若 $p < \alpha$，**拒绝** $H_0$，否则不拒绝。$p$-value **不是**：

- $P(H_0 \mid \text{data})$（这要 Bayes，需要先验）；
- "结果是随机得到的概率"（$H_0$ 下本来就全是随机的）；
- 效应大小的度量（$n$ 巨大时微小差异也能 $p < 0.05$，反之亦然）。

### 2.2 两样本均值差的样本量公式

假设两组方差相同为 $\sigma^2$，期望差 $\Delta = \mu_B - \mu_A$。用 z-test 统计量 $T = (\bar{X}_B - \bar{X}_A) / \sqrt{2\sigma^2/n}$（每组 $n$ 样本）。要求：type I $\leq \alpha$ 且 power $= 1 - \beta$ 在 $\Delta \geq$ MDE 下成立。推出每组样本量：

$$\boxed{\; n \;=\; \frac{2 \sigma^2 \,(z_{\alpha/2} + z_\beta)^2}{\text{MDE}^2} \;}$$

常见参数：$\alpha = 0.05 \Rightarrow z_{\alpha/2} = 1.96$；$\beta = 0.2 \Rightarrow z_\beta = 0.84$。代入 $(z_{\alpha/2} + z_\beta)^2 = (1.96 + 0.84)^2 \approx 7.85$，即**经典 "7.85 常数"**：

$$n \;\approx\; \frac{15.7 \cdot \sigma^2}{\text{MDE}^2}$$

### 2.3 两样本比例差（CTR、转化率）

对比例 $p_A, p_B$（如 CTR），方差用 pooled estimate $\bar{p}(1 - \bar{p})$，其中 $\bar{p} = (p_A + p_B)/2$：

$$n \;=\; \frac{2 \, \bar{p}(1 - \bar{p})\,(z_{\alpha/2} + z_\beta)^2}{(p_B - p_A)^2}$$

例子：$p_A = 0.05$、MDE 相对 10% 即 $p_B = 0.055$、$\alpha = 0.05$、power $= 0.8$：

$$n \;\approx\; \frac{2 \times 0.0475 \times 7.85}{0.005^2} \;\approx\; 29{,}800 \text{ per arm}$$

这就是"小基线 + 小效应 = 巨大样本量"的直观来源——$(p_B - p_A)^2$ 在分母上是二次的。

### 2.4 多重检验：FWER vs FDR

同时做 $m$ 个独立检验，每个 $\alpha = 0.05$。若 $H_0$ 全为真，至少 1 个假阳性的概率 $= 1 - (1 - \alpha)^m$，$m = 10$ 时已 40%，$m = 100$ 时 99.4%。三种校正策略：

- **Bonferroni**（控制 FWER）：每检验用 $\alpha / m$ 作阈值。保守、简单。
- **Holm**（控制 FWER）：把 $p$-value 排序 $p_{(1)} \leq \cdots \leq p_{(m)}$，第 $k$ 小拒绝当 $p_{(k)} < \alpha/(m - k + 1)$。比 Bonferroni 更有 power。
- **Benjamini-Hochberg** (BH, 控制 FDR)：排序后找最大的 $k$ 使 $p_{(k)} \leq k \alpha / m$，前 $k$ 个全部拒绝。FDR = 期望的假发现占所有发现的比例。

**FWER vs FDR 的差别**：

- FWER $\leq \alpha$：$P(\text{任一假发现}) \leq \alpha$。适合医学、航空——一个错都致命。
- FDR $\leq \alpha$：$\mathbb{E}[\text{假发现} / \text{总发现}] \leq \alpha$。适合大规模探索（基因组 GWAS、指标 dashboard）——允许一定比例假阳性。

$m$ 大时 BH 的 power 远超 Bonferroni/Holm；$m$ 小（如 5 个核心指标）差距不大，为简单起见常用 Bonferroni。

## 3. 物理意义：A/B test 中的陷阱

### 3.1 $p$-value hacking / 早停

实验每天看一次，一见到 $p < 0.05$ 就停——这等价于**重复检验**，真实 type I error 远大于 0.05。修复：预注册分析计划、用 sequential testing（mSPRT、alpha-spending）在线监控但保证总 $\alpha$。

### 3.2 业务效应 vs 统计效应

$p < 0.05$ 不代表效应大。$n$ 巨大时 0.01% 的 CTR 改进也能显著，但部署成本可能高于收益。应报告**效应大小** + **置信区间**：如 "CTR 提升 0.15% [0.08%, 0.22%]"，业务方从 CI 自行判断价值。

### 3.3 variance reduction：CUPED

CUPED（Deng 2013）用实验前期的 covariate $Y_{\text{pre}}$（同用户在实验前 7 天的指标）做回归残差：$Y^\star = Y - \theta(Y_{\text{pre}} - \mathbb{E}[Y_{\text{pre}}])$。消除用户间基线差异后方差降 $30\%$-$60\%$，等价于样本量放大 1.5-2.5 倍。是大厂 A/B 平台的标配。

### 3.4 SRM (Sample Ratio Mismatch)

流量 50/50 分流，实际观察到 49.5/50.5。做一次 Pearson 卡方检验，若 $p < 0.001$ 就是 SRM——分流器 bug、bot 不均、日志丢失。实验有 SRM 时所有结论都不可信，应先修复。

## 4. 常见追问

### 4.1 单边 vs 双边检验

业务常只关心"是否变好"，看起来应用单边检验。但单边 $\alpha = 0.05$ 对应双边 $\alpha = 0.10$——type I error 实际加倍。工业界默认用双边，避免和其他实验比较时的口径不一致。

### 4.2 novelty effect 与 primacy period

新功能推出初期用户好奇导致指标虚高（novelty），或新界面让老用户困惑导致指标下降（primacy）。修复：(i) 实验跑够长（至少 7 天 + 业务周期）；(ii) 分析稳定期而非全周期；(iii) 分新老用户拆分看。

### 4.3 A/A test：sanity check

把同一版本同时 A/A 分流，理论上应 95% 情况下 $p \geq 0.05$。若 A/A test 上频繁显著，说明 random unit 的 IID 假设出问题（同 user 跨 session、同公司多账号串联），需要切更大的随机单位或重新设计分配。

### 4.4 CUPED 的 $\theta$ 选取

$\theta^\star = \mathrm{Cov}(Y, Y_{\text{pre}}) / \mathrm{Var}(Y_{\text{pre}})$——就是 $Y$ 对 $Y_{\text{pre}}$ 的 OLS 斜率。直接在 control 组上拟合，应用到两组。$Y_{\text{pre}}$ 与 $Y$ 相关性越高，方差缩减越多。

### 4.5 Peeking 与 Bayesian alternatives

频率派的样本量 + 终点检验对"偷看"零容忍。Bayesian A/B test 每天更新后验 $P(\Delta > 0 \mid \text{data})$，自然允许中途决策，但需要先验 + 计算复杂。工业实践中常见折中：频率派做主分析，Bayesian 做决策辅助（"当前概率 B 赢 > 95% 且业务 acceptable"）。

## 5. 参考

- Kohavi, Tang, Xu 2020, *Trustworthy Online Controlled Experiments* —— 大厂 A/B test 实践的权威手册（Amazon / Microsoft 经验）。
- Benjamini & Hochberg 1995, *Controlling the False Discovery Rate* —— BH 过程的原始论文。
- Deng, Xu, Kohavi, Walker 2013, *Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data* —— CUPED 方法。
- Johari et al. 2017, *Peeking at A/B Tests: Why it matters, and what to do about it* —— 早停 / 偷看下的 sequential testing 解决方案。
"""


# ---------------------------------------------------------------------------
# Leaves registry
# ---------------------------------------------------------------------------

LEAVES: dict[str, tuple[str, str]] = {
    "ml-fundamentals/llm_stats/tokenization-bpe-wordpiece-sentencepiece": (
        "TODO[MLF-tokenization-bpe-wordpiece-sentencepiece]",
        DESC_TOKENIZATION,
    ),
    "ml-fundamentals/llm_stats/scaling-law-chinchilla": (
        "TODO[MLF-scaling-law-chinchilla]",
        DESC_SCALING_LAW,
    ),
    "ml-fundamentals/llm_stats/clt-vs-lln": (
        "TODO[MLF-clt-vs-lln]",
        DESC_CLT_VS_LLN,
    ),
    "ml-fundamentals/llm_stats/ab-test-pvalue-sample-size-multiple-testing": (
        "TODO[MLF-ab-test-pvalue-sample-size-multiple-testing]",
        DESC_AB_TEST,
    ),
}


def sha256_of_descriptions(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) pairs of the 4 target leaves."""
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
    """Update the 4 X-depth leaves idempotently."""
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

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

    total = counts["UPDATED"] + counts["SKIPPED"]
    print(
        f"[SUMMARY] updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total={total} (expected 4)"
    )
    if total != 4:
        print("[FAIL] expected to touch exactly 4 leaves")
        return 1
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
