"""Seed: T-P1-595 -- ML Fundamentals Q#28 single-page comprehensive content.

Writes the canonical answer for Question 28 (千级特征筛选与建模完整流程 /
Feature Selection & Modeling Pipeline at 1000+ Features) into
framework_nodes.description for the leaf at path
'ml-fundamentals/feature_engineering_selection/feature-selection-pipeline-1000features'.

Per user clarification (Discord msgs 1496180848553103402 / 1496182009976979476
/ 1496183573684817964 / 1496183668912296036): this is ONE page answering
ONE question about large-scale feature selection + adoption. Do NOT split
into multiple leaves. The 4 originally-separate gap topics are folded in:
  - Filter methods depth (MI / mRMR / chi2 / F-test)      -> Section 3.6
  - Feature interaction detection (Friedman H / SHAP pair) -> Section 4.4
  - Categorical encoding + target-encoding CV leakage      -> Section 3.5
  - FS vs Dimensionality Reduction (PCA / AE / PLS)        -> Section 4.5
  - Nested CV + post-selection inference                   -> Section 6

CRITICAL user constraint (msg 1496182009976979476): every technical term /
acronym gets **English full name** (acronym, 中文) on first mention +
1-3 sentence intuition + math formulation (KaTeX) where applicable + when-
to-use / failure mode guidance. No name-drop.

Idempotency:
  - Expected description is a single raw-string constant.
  - Second run yields updated=0 skipped=1 conflict=0.
  - SHA-256 of (path, description) captured pre/post for audit.
  - If the existing description is neither the placeholder
    'TODO[MLF-feature-selection-pipeline-1000features]' nor the new content,
    script aborts with [CONFLICT] before any write.
  - DB backup (sqlite file copy) written before any mutation, suffix
    `_pre_q28_content_YYYYMMDD_HHMMSS.db`.

Acceptance:
  - framework_nodes row at the target path updated.
  - Description contains KaTeX math, section headers, 4+ comparison tables.
  - Every term in the grep-able checklist (see validate_content) appears.
  - Re-run is no-op (updated=0).
"""
from __future__ import annotations

import hashlib
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
BACKUP_DIR = REPO_ROOT / "data"

TARGET_PATH = (
    "ml-fundamentals/feature_engineering_selection/"
    "feature-selection-pipeline-1000features"
)
PLACEHOLDER = "TODO[MLF-feature-selection-pipeline-1000features]"


DESC_Q28 = r"""# 千级特征筛选与建模完整流程

> 场景：业务方扔来 1000+ 个候选特征（原始、派生、embedding、第三方），问题是：选哪些、怎么选、选完怎么证明选对了、上线后怎么维护。整条流水线按下面 7 节走，每节都有**为什么必须放在这个位置**的理由，位置错了整条链会在后面的某一节悄悄漏数据或在上线后掉点。

本页把 4 个原本考虑单独成篇的专题直接内嵌：**Filter 方法细节**进 §3.6，**FS vs 降维**进 §4.5，**特征交互检测**进 §4.4，**类别编码 + Target Encoding CV 泄漏**进 §3.5。

---

## 1. 先划分数据 —— 一切之前

**规则**：把数据切成 train / val / test（或 time-series 的过去/近期/未来），**然后**所有特征工程、缺失填补、encoding、归一化、FS 只能 fit 在 train 上，transform 应用到 val/test。顺序颠倒 = data leakage，模型在离线看起来多好、上线后就会掉多少。

三种切法按数据性质选：

| 数据类型 | 切法 | 原因 |
|----------|------|------|
| iid 横截面（用户评分、图像分类） | 随机分层 stratified split | 保类别比，样本之间无时序依赖 |
| 时序（风控违约、推荐点击） | Time-aware split（past → future） | 随机切会把"未来信息"混进 train，放出来 AUC 虚高 |
| 同一实体多行（同一用户多次会话） | Group split（GroupKFold 按 user_id） | 随机切会让同一用户同时出现在 train 和 test，模型记住用户 ID 就赢 |

**不变约束**：

- `scaler.fit(X_train)` 后 `scaler.transform(X_val)`，**永远不要** `fit(X_full)`。
- Target Encoding、缺失均值/中位数、PSI 的 reference 分布、MI 阈值——这些**所有基于统计量的变换**都只能在 train 子集上 fit。
- 随机种子固定（numpy、torch、sklearn 都要），不然一次 AUC 0.82、一次 0.79，没法判断是改动带来的还是随机性。

常见失败：某同学在 CV 开始之前就对全集做了 one-hot 和标准化，再进 KFold。CV AUC 0.88、线上 0.71，原因就是均值/方差里掺了 test 子集的信息。

---

## 2. Target Leakage 检查 —— 第二道门

**Target leakage（目标泄漏）**：某特征在训练时的值包含了只有"打完 label 之后"才能知道的信息。典型：风控里的 `collected_amount`（催收回款额）在发放贷款时还未产生，它高度依赖 `is_default` 的结果；广告里的 `post_click_dwell_time` 发生在 click 之后，要预测 click 就等于作弊。

识别手段：

1. **语义审计**：列一张"特征 → 采集时间戳"的表，任何时间戳晚于 label 时间的直接删。
2. **Mutual Information** (MI, 互信息) 对目标的排序：$I(X; Y) = \sum_{x,y} p(x,y)\,\log \dfrac{p(x,y)}{p(x)\,p(y)}$。MI > 0.5 nats 的单一特征要手动核对业务含义，常常是泄漏。
3. **单变量 AUC**：用这一个特征做分类器，AUC 接近 1 的几乎全是泄漏。
4. **训练早停曲线**：加入该特征后第 1 个 epoch 就收敛到 99% 训练 AUC 而 val 也奇高——可疑。

**univariate correlation**（单变量相关性）和 MI 的选择：相关性只抓线性关系，MI 抓任意单调 / 非线性依赖，表格数据建议两者都算。为了避免数值型变量频繁分箱导致 MI 估计不稳，用 sklearn 的 `mutual_info_classif`（连续变量走 k-近邻熵估计）。

---

## 3. 粗筛：Feature Engineering 层面的无模型过滤

### 3.1 缺失值

不要无脑 mean-impute。先判断缺失类型：

- **MCAR**（Missing Completely At Random，完全随机缺失）：删或均值填，影响小。
- **MAR**（Missing At Random，条件随机缺失）：缺失由其他观测变量决定，建模时用这些变量预测缺失值。
- **MNAR**（Missing Not At Random，非随机缺失）：缺失本身携带信号。例如"年收入"字段在高净值客户那里更容易缺失（保护隐私），那么 `is_missing(income)` 就是一个有用的二值特征。

**实操**：数值型变量加 `is_missing_X` 指示列 + 中位数填；类别型加 "Missing" 作为一个独立 level。树模型（XGBoost、LightGBM）对缺失有原生分支策略，不必强填。

### 3.2 共线性 —— Variance Inflation Factor

**Variance Inflation Factor** (VIF, 方差膨胀因子)：衡量特征 $x_j$ 被其他特征共线性预测的程度。对 $x_j$ 用剩余所有特征做回归拿到 $R_j^2$，则

$$\text{VIF}_j \;=\; \dfrac{1}{1 - R_j^2}$$

**读法**：$R_j^2 = 0$ 时 VIF=1（无共线性）；$R_j^2 = 0.9$ 时 VIF=10，系数方差放大 10 倍；经验阈值 VIF>10 删。

**替代路线**：VIF 在 1000+ 特征规模下算起来慢（每个变量一次 $O(p^2)$ 回归，总 $O(p^3)$）。更快的做法是**层次聚类法**（hierarchical clustering on Spearman correlation），给相关矩阵做 agglomerative clustering，每个 cluster 保留一个代表变量。

### 3.3 稳定性 —— PSI / CSI

**Population Stability Index** (PSI, 群体稳定度指数)：衡量一个变量从训练期到近期 / 生产期的分布漂移。分桶后：

$$\text{PSI} \;=\; \sum_{i=1}^{K} (p_i - q_i)\,\log\!\dfrac{p_i}{q_i}$$

其中 $p_i$ 是 train 在第 $i$ 桶的占比，$q_i$ 是近期数据在第 $i$ 桶的占比。**阈值**：PSI < 0.1 稳定；0.1–0.25 轻微漂移；>0.25 分布已明显变化，这个变量上线后不可靠。

**Characteristic Stability Index** (CSI, 特征稳定度指数)：和 PSI 形式相同，但 $p, q$ 换成"score 分桶下某变量的条件分布"，用于诊断模型打分的漂移到底由哪些变量驱动。实操链：PSI 抓"变量级漂移"、CSI 抓"打分级漂移的归因"。

### 3.4 低方差 —— 最便宜的一刀

**低方差过滤**：某个 one-hot 列 99.9% 取值都是 0，保留它只会增加噪声和过拟合风险。sklearn `VarianceThreshold(threshold=0.01)` 一行搞定。类别变量换成"出现频率最高的 level 占比 > 0.99" 作为阈值。

### 3.5 类别编码 + Target Encoding 的 CV Leakage 陷阱

**编码策略对比表**：

| 方法 | 公式 | 适用场景 | 风险 |
|------|------|----------|------|
| **One-Hot** | $K$ 个 level → $K$ 个 0/1 列 | 低基数（$K < 50$）、线性模型 | 高基数炸维度 |
| **Frequency Encoding**（频次编码） | $\text{enc}(c) = \text{count}(c) / N$ | 高基数、树模型 | 不同类别频次相同时碰撞 |
| **Target Encoding**（目标编码） | $\text{enc}(c) = \mathbb{E}[y \mid X=c]$ | 高基数 + 相关信号 | **CV 泄漏**（见下） |
| **Weight of Evidence** (WOE, 证据权重) | $\text{WOE}(c) = \log\!\dfrac{P(X=c \mid y=1)}{P(X=c \mid y=0)}$ | 风控二分类，配合 Information Value 筛变量 | 只适合 binary target |
| **CatBoost Ordered Target Statistics** | 对每个样本只用**该样本之前**的行做 target stat | 高基数 + 防泄漏 | CatBoost 专有 |

**Target-Encoding CV Leakage 陷阱**：朴素做法是把 `train_all` 上算好的 $\mathbb{E}[y\|c]$ 作为编码值。但这样每个 CV fold 里 train 和 val 共享同一份编码表，val fold 的 label 已经"间接泄漏"进 val 的特征值——离线 CV AUC 比真实 test 高 2–5 个点。

**正确做法**：

- **Out-of-fold Target Encoding**：用 K 折 CV 的方式，每个 fold 只用 out-of-fold 样本计算该 fold 内样本的编码值。等价于 KFold 套 KFold。
- **Smoothing**：低频 level 直接用经验 mean 不稳，加 Bayesian smoothing $\text{enc}(c) = \dfrac{n_c \cdot \bar{y}_c + \alpha \cdot \bar{y}}{n_c + \alpha}$，$\alpha$ 经验 10–50。
- **CatBoost ordered TS**：Catboost 内置的"按随机排列的前缀均值"，天然避免泄漏。
- **WOE 在风控里更稳**：因为它是比率不是均值，对低频 level 的方差控制更好，配合 **Information Value** (IV) 做变量筛选是金融风控标准流程。

### 3.6 Filter Methods —— 四大无模型打分

| 方法 | 公式 / 统计量 | 特征类型 | 目标类型 | 优点 | 局限 |
|------|---------------|----------|----------|------|------|
| **Mutual Information** (MI, 互信息) | $I(X;Y) = \sum_{x,y} p(x,y) \log \dfrac{p(x,y)}{p(x)p(y)}$ | 任意 | 任意 | 抓非线性 | 高维联合分布估计不稳 |
| **maximum Relevance Minimum Redundancy** (mRMR, 最大相关最小冗余) | $\max_S \frac{1}{\|S\|}\sum_{x_i \in S} I(x_i;y) - \frac{1}{\|S\|^2}\sum_{x_i,x_j \in S} I(x_i;x_j)$ | 任意 | 任意 | 同时考虑与 $y$ 相关、特征间不冗余 | 贪心近似 NP-hard |
| **chi-squared** ($\chi^2$, 卡方) | $\chi^2 = \sum_{i,j} \dfrac{(O_{ij} - E_{ij})^2}{E_{ij}}$ | 类别 | 类别 | 快 | 非负值限制、不抓连续 |
| **ANOVA F-test**（F 检验，F-statistic） | $F = \dfrac{\text{MS}_{\text{between}}}{\text{MS}_{\text{within}}}$ | 数值 | 类别（多分类） | 经典统计 | 只抓组间均值差异，不抓分布差异 |

**Filter 方法路由表**（feature type × target type）：

| 特征类型\目标 | 数值目标（回归） | 类别目标（分类） |
|---------------|-------------------|-------------------|
| 数值 | Pearson / Spearman / MI | ANOVA F-test / MI |
| 类别 | ANOVA F-test（反向） | $\chi^2$ / MI / WOE-IV |

**排序**：优先 **mRMR**，因为它惩罚冗余；次选 **MI** 作基线；$\chi^2$ 和 F 只在你明确知道特征/目标类型匹配时用。

---

## 4. 模型驱动特征选择

粗筛砍掉一半后仍有 500+ 特征，需要模型打分。

### 4.1 线性模型路线 —— L1 / Elastic Net / Stability Selection

- **L1 正则化 / Lasso**（Lasso = Least Absolute Shrinkage and Selection Operator，最小绝对收缩与选择算子）：$\min_\beta \; \tfrac{1}{2n}\|y - X\beta\|_2^2 + \lambda \|\beta\|_1$，L1 penalty 在 0 处不可导，最优解 sparse —— 很多系数恰好为 0，直接完成选择。
- **Elastic Net**（弹性网）：$\lambda_1 \|\beta\|_1 + \lambda_2 \|\beta\|_2^2$，L2 让高度相关变量一起保留而不是 Lasso 那样随机保一个，对**相关特征组**更稳。
- **Stability Selection**（稳定性选择）：在 $B$ 次 bootstrap（自助重采样）上跑 Lasso，记录每个特征被选中的频率 $\hat{\Pi}_j^\lambda$：

  $$\hat{\Pi}_j^\lambda \;=\; \dfrac{1}{B} \sum_{b=1}^{B} \mathbb{1}\{\hat{\beta}_j^{(b,\lambda)} \neq 0\}$$

  选择 $\hat{\Pi}_j \geq \pi_{\text{thr}}$（经验 $\pi_{\text{thr}} = 0.6$–$0.9$）的特征。**Meinshausen & Bühlmann 2010** 证明这个阈值对应于族错误率 FWER 控制。比单次 Lasso 稳得多，代价是 $B$ 倍训练时间。

### 4.2 树模型路线 —— Permutation / SHAP / Null Importance / Boruta

**GBDT**（Gradient Boosted Decision Tree，梯度提升决策树）的原生 feature importance（基于 split gain 或 Gini impurity 减少）有**高基数偏差**：分裂次数多的连续变量 / 高基数类别被高估。**不要**直接用原生 importance 选特征。四种替代方案：

- **Permutation Importance**（置换重要性）：把某列的值随机打乱，观察 val AUC 下降量。下降越多，这列越重要。优点：测量的是**实际预测贡献**，不受 split 次数扭曲。缺点：高度相关特征会被**互相低估**（打乱 $x_1$ 时 $x_2$ 还在，模型仍能预测）。

- **SHAP**（SHapley Additive exPlanations，沙普利可加解释）：从博弈论沙普利值推出来的加性贡献值。对样本 $x$ 和特征 $j$：

  $$\phi_j(x) \;=\; \sum_{S \subseteq F \setminus \{j\}} \dfrac{|S|!\,(|F| - |S| - 1)!}{|F|!} \,\big[\,f(S \cup \{j\}) - f(S)\,\big]$$

  $F$ 是所有特征、$S$ 是不含 $j$ 的子集、$f(S)$ 是用子集 $S$ 预测的期望输出。TreeSHAP 在树模型上有 $O(TLD^2)$ 的多项式精确算法（$T$ 棵树、$L$ 叶子、$D$ 深度）。全局重要性 = $\mathbb{E}_x[\|\phi_j(x)\|]$。SHAP 的**加性分解**（$\sum_j \phi_j(x) = f(x) - \mathbb{E}[f]$）让它既能排序又能解释单条预测。

- **Null Importance / Shuffle Test**（零重要性 / 打乱检验）：把**目标** $y$ 整体打乱，重训模型，记录每个特征在"无信号"状态下的 importance 分布（重复 30–100 次）。真实 importance > null 分布 95 分位的才算有信号。有效剔除那些靠过拟合吃分的"幸运特征"。

- **Boruta**（博鲁塔，Kursa & Rudnicki 2010）：给每个真实特征 $x_j$ 造一个 **shadow feature**（影子特征）—— 把 $x_j$ 的列完全打乱。真实+影子一起喂进 Random Forest，只有在 importance 显著（经验上 > 所有影子特征的最大值）超过影子的真实特征被判定为"有信号"，直到所有特征都被判定或达到最大迭代。比 null importance 的单次 shuffle 更严格。

### 4.3 专用包装方法 —— RFECV / Group Lasso

- **RFECV**（Recursive Feature Elimination with Cross-Validation，递归特征消除 + 交叉验证）：从全集开始，训一次模型、拿 importance、删最弱的 $k$ 个，在 CV 上评分，重复到只剩 1 个。曲线最优点就是选中的子集。优点：直接优化 CV 指标；缺点：$O(p^2)$ 训练次数，1000 特征很慢，常用于粗筛后再做。

- **Group Lasso**（组套索 / 结构化稀疏）：当特征天然分组（一组 one-hot 的 city dummies、同一段时间窗口的滞后特征），Group Lasso 的 penalty 是**每组的 L2 范数之和**：

  $$\lambda \sum_{g=1}^{G} \sqrt{|g|} \,\|\beta_g\|_2$$

  迫使整个组要么全零要么全非零，避免 Lasso 把 one-hot 组里随机挑一两个 dummy 留下的尴尬。属于 **structured sparsity**（结构化稀疏）的一种。

### 4.4 交互感知选择 —— Friedman H / SHAP Interaction

当模型有非线性交互时，单变量 importance 会漏掉"A 和 B 单独弱、但 A×B 强"的对。

- **Friedman H-statistic**（Friedman H 统计量）：度量变量 $j, k$ 的二阶交互强度。
  令 $\text{PD}_j, \text{PD}_k, \text{PD}_{jk}$ 为 Partial Dependence（偏依赖）函数，则：

  $$H_{jk}^2 \;=\; \dfrac{\sum_i \big[\text{PD}_{jk}(x_i) - \text{PD}_j(x_i) - \text{PD}_k(x_i)\big]^2}{\sum_i \text{PD}_{jk}(x_i)^2}$$

  $H_{jk} \in [0,1]$，$H_{jk} = 0$ 意味着无二阶交互（可加分解）、接近 1 意味着交互主导。

- **SHAP Interaction Values**（SHAP 交互值）：把 $\phi_j(x)$ 进一步分解成 $\phi_{j,k}(x)$ —— TreeSHAP 支持 $O(TLD^2)$ 的精确计算。全局交互强度排序能直接给出 top-K 交互对，然后构造 $x_j \cdot x_k$、$x_j / x_k$ 等派生特征喂回模型。

### 4.5 FS vs Dimensionality Reduction —— 选特征还是做降维

**区别**：FS 保留原始可解释的列（便于业务审计），DR 通过线性 / 非线性变换产生新坐标（更紧但语义丢失）。

| 方法 | 核心 | 监督 / 无监督 | 失败模式 |
|------|------|-----------------|----------|
| **PCA** (Principal Component Analysis, 主成分分析) | 对协方差矩阵 $\Sigma$ 做 eigendecomposition：$\Sigma v_i = \lambda_i v_i$，取 top-K $\lambda_i$ 的 $v_i$ 投影 | 无监督 | 方差大 ≠ 对 $y$ 有用；非线性结构丢 |
| **SVD** (Singular Value Decomposition, 奇异值分解) | $X = U\Sigma V^\top$，与 PCA 数学等价但数值更稳 | 无监督 | 同 PCA |
| **Factor Analysis**（因子分析） | 假定 $x = \Lambda f + \epsilon$，$f$ 是低维潜在因子 | 无监督 | 模型假设强 |
| **Autoencoder** (AE, 自编码器) | 训一个 encoder-decoder 网络，重构损失 $\mathcal{L}_{\text{AE}} = \|x - g(f(x))\|_2^2$，bottleneck 层是低维表示 | 无监督 | 非凸，需调超参 |
| **Partial Least Squares** (PLS, 偏最小二乘) | 找方向 $w$ 使 $\text{Cov}(Xw, y)$ 最大（PCA 最大化方差、PLS 最大化协方差） | **监督** | 只对回归 / 线性关系直接；解释性差 |
| **Kernel PCA**（核 PCA） | 对 kernel 矩阵 $K_{ij} = k(x_i, x_j)$ 做 PCA，$k$ 是 RBF / poly | 无监督 | 核选择、$O(N^2)$ |

**选择树**：

1. 需要可解释 / 业务审计 / 监管 → **FS**，不碰 DR。
2. 有大量高度相关的数值特征、且业务可解释度不是强约束 → **PCA** 到 95% 方差。
3. 回归任务、特征数远大于样本数 → **PLS**，因为它把目标信息也用上。
4. 高维非线性（图像、序列 embedding）→ **Autoencoder** 或已有的预训练 embedding。
5. 表格分类任务在 1000 特征下 → **FS 优先**，DR 只作为可选补充列（把 PCA 前 20 维当新特征和 FS 结果并列，再跑一次 importance）。

---

## 5. Ablation Study —— 证明"这些特征真的有用"

选完特征不等于收工。Ablation 是对 FS 结果的交叉验证。

| 粒度 | 做法 | 成本 | 何时用 |
|------|------|------|--------|
| **Leave-One-Out** (LOO, 留一法) | 逐个删单个特征、重训、看 AUC delta（AUC 变化） | $O(|S|)$ 次训练 | 最终精选集很小（<50）时 |
| **Group Ablation**（组消融） | 按业务语义分组（user / item / interaction / temporal），每次删一组 | $O(G)$ 次训练 | 回答"哪类信号最关键" |
| **Forward Ablation / Greedy Addition**（前向贪心添加） | 从空集开始，每轮加入让 val AUC 提升最多的那个特征，直到提升 < $\epsilon$ | $O(|S|^2)$ 次训练 | 最终要向业务解释"这 10 个特征为什么入选" |

**输出**：每个特征（或组）的 AUC delta 和 **p-value**（通过 bootstrap 或 DeLong 检验估）。AUC delta 置信区间跨 0 的特征即使"入选"也要打个问号。

---

## 6. 最终验证 —— 上线前的最后一道门

### 6.1 Test 集 + Calibration + Subgroup

- **Test 集一次性**：CV 已经看过 val 多次，test 只能评估一次。超过一次就变成了"隐性 val"。
- **Calibration**（概率校准）：ROC 好不代表概率准。看 **reliability diagram**（可靠性图）或 **Expected Calibration Error**（ECE）。未校准的概率在阈值类决策（比如风控通过率）里会系统性偏。用 Platt scaling 或 Isotonic regression 修。
- **Subgroup 分析**：按 user_segment、geo、time 拆分 test，分组看指标。全局 AUC 0.85 但某 segment 只有 0.60 就是 fairness / robustness 隐患。

### 6.2 Selection Stability

跑 $B$ 次 bootstrap、每次都做完整 FS 流水线，统计每个特征被选中的频率 $\hat{\Pi}_j$。$\hat{\Pi}_j < 0.5$ 的特征说明选择过程本身不稳，即使这次选上了换个数据切分就会掉出。参考的阈值：$\geq 0.9$ 极稳、$0.7$–$0.9$ 可接受。

### 6.3 Nested CV —— 防止选择本身过拟合 CV

普通 CV 的问题：如果你在**每个 fold** 的 train 内部做完整 FS + 模型调参 + 评估，但**还用同一个 CV 的结构**挑最终的超参组合，这个 CV 分数就乐观偏差了。

**Nested CV**（嵌套交叉验证）：**outer loop** 评估模型、**inner loop** 调参和选特征。

- Outer：K 折，每折的 test 子集完全不参与任何 selection / tuning。
- Inner：在当前 outer-train 上再跑 K' 折，用 inner val 选参 + 做 FS，得到的"流水线"在 outer test 上评一次。
- 最终 outer 分数的均值和方差就是**诚实的泛化估计**。

经验公式：outer $K=5$、inner $K'=3$ 够用，总训练次数 $K \cdot K' \cdot (\text{tune grid})$。

### 6.4 Post-Selection Inference —— 选完之后的 p-value 不可信

天真做法是 Lasso 选完后跑 OLS 再看系数 p-value。**这些 p-value 是错的**：因为"这些变量被选中"这个事件本身就已经 condition 在数据上，标准正态假设不再成立。

**Lee-Sun-Sun-Taylor 2016**（*Exact post-selection inference for sequential regression procedures*）给出了 **Polyhedral Selection Event**（多面体选择事件）框架：Lasso 的选择集 $\hat{S}$ 对应 $y$ 落在某多面体 $\{Ay \leq b\}$ 的区域，在这个条件下系数的 truncated-normal 分布有闭式解，得到**selective p-value**（选择性推断 p 值）。这比朴素 p-value 保守得多但可信。

**Knockoff Filter**（knockoff 过滤器，Barber & Candès 2015）：给每个真实变量 $X_j$ 构造一个 knockoff $\tilde{X}_j$，满足 (i) $\tilde{X}$ 和 $X$ 联合分布某种交换对称、(ii) $\tilde{X}$ 与 $y$ 条件独立（给定 $X$）。然后用任意选择器（Lasso、Boruta 风格）对 $[X, \tilde{X}]$ 打分，某阈值下保留"真实分数明显高于 knockoff"的变量，可证明控制 **False Discovery Rate** (FDR, 错误发现率) 在目标水平 $q$ 以下。不需要分布假设、不需要 p-value。

### 6.5 FDR 与 Benjamini-Hochberg

多个变量 / 多组 subgroup / 多个模型同时做 hypothesis test 时，每个 test 5% 显著性、10 个 test 大概率至少一个假阳。

**Benjamini-Hochberg** (BH, Benjamini-Hochberg 步降法，1995)：控制 **FDR** = E[假阳 / 所有拒绝] $\leq q$（比 Bonferroni 控 FWER 宽松、检出力高）。步骤：

1. 对 $m$ 个 p-value 升序 $p_{(1)} \leq \ldots \leq p_{(m)}$。
2. 找最大 $k$ 满足 $p_{(k)} \leq \dfrac{k}{m}\,q$。
3. 拒绝前 $k$ 个对应假设。

在 selection stability / subgroup 分析 / A/B 多臂实验的事后分析里都要用。

### 6.6 Shadow Deployment

模型训好的最后一步：**shadow deployment**（影子部署）—— 新模型和旧模型并行接线上流量、新模型的预测**不真正影响决策**只落日志，对比两个模型在真实流量上的分布、延迟、subgroup 表现。覆盖"CV 上好 → 生产也好"最后一英里。至少跑 1 周、覆盖工作日 / 周末 / 促销 / 故障等多种 traffic pattern 才上灰度。

---

## 7. 工程与业务维度 —— 特征再好，上不了线也白搭

离线指标 top 的特征如果在线推理链路上有问题，会变成技术债。7 维度 checklist：

- **成本**：某些特征要调外部 API、要跑图神经网络上游、要聚合 90 天窗口。单特征边际 AUC +0.001 但推理时延 +10ms、存储 +1TB，不划算。
- **Latency**（延迟）：线上服务一般有 p99 预算（广告排序 100ms、搜索 200ms），特征计算要在预算内。把昂贵特征移到 batch pre-compute（每日 / 每小时算好落 feature store）、实时链路只读 KV。
- **Interpretability**（可解释性）：风控、医疗、反欺诈场景的模型要能向合规 / 法务 / 监管解释"为什么拒绝这个客户"。深度 embedding 特征和黑盒 DR 特征上不了线。FS 选出的原始列 + SHAP 解释是合规友好的组合。
- **Drift Monitoring**（漂移监控）：上线后每日 / 每周算每个特征的 PSI vs 训练分布，超阈值报警。PSI > 0.25 的特征要排查：是季节性 / 营销活动 / 数据管道故障还是真实分布变化。
- **Feature Store**（特征仓库）：统一注册、版本化、训练-线上同源的平台（Feast、Tecton、自研）。避免两份代码一份线下 SQL、一份线上 Python 算同一个特征产生微小差异。
- **Train-Serve Skew**（训练-服务偏斜）：离线训练用 pandas 算特征、线上用 gRPC 服务算特征，两边实现不一致是最常见的"离线好、线上差"根因。解决：feature logic 写一份、训练和服务共享同一段代码（Feature SDK）。
- **Maintenance / 维护成本**：特征多了，owner 就稀释。每季度做 feature audit —— 删掉近 90 天 SHAP 贡献几乎为零、PSI 不稳、owner 已离职的特征，保持集合精简。

---

## 8. L4 vs L5 面试答题 bar

同一道"1000 特征怎么选"，不同 level 的答题深度：

| 维度 | L4 senior 的 bar | L5 staff+ 的 bar |
|------|-------------------|-------------------|
| **流水线** | 能说全 7 节、顺序正确 | 能讲为什么这个顺序不可颠倒，并给 1–2 个自己踩过的坑 |
| **Filter 方法** | 知道 MI / chi² / F | 知道 mRMR 的冗余惩罚推导、能讲 F-test 的 within/between 方差分解 |
| **Target Encoding** | 知道会泄漏、用 out-of-fold | 能讲 Catboost ordered TS 的随机排列机制、WOE 为什么在风控更稳 |
| **Stability / Boruta / Null Importance** | 知道名词 | 能说明 Stability Selection 对应 FWER 控制、Boruta 与 shadow feature 的关系 |
| **FS vs DR** | 知道区别 | 能判断什么场景用 PLS 而不是 PCA |
| **Post-selection Inference** | 知道"普通 p-value 不能用" | 能讲 Polyhedral event / Knockoff / BH 的各自适用场景 |
| **工程维度** | 说出 latency / drift | 能连接到 feature store 架构、train-serve skew 的具体防御手段 |

---

## 9. 参考

- Guyon & Elisseeff 2003, *An Introduction to Variable and Feature Selection* —— 经典综述，filter/wrapper/embedded 分类的原始出处。
- Meinshausen & Bühlmann 2010, *Stability Selection* —— Stability Selection 的 FWER 控制证明。
- Kursa & Rudnicki 2010, *Feature Selection with the Boruta Package* —— Boruta shadow feature 方法。
- Lundberg & Lee 2017, *A Unified Approach to Interpreting Model Predictions* —— SHAP 和 TreeSHAP。
- Lee, Sun, Sun, Taylor 2016, *Exact Post-Selection Inference for Sequential Regression Procedures* —— polyhedral selection event。
- Barber & Candès 2015, *Controlling the False Discovery Rate via Knockoffs* —— knockoff filter 的 FDR 控制。
- Benjamini & Hochberg 1995, *Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing* —— BH 过程原始出处。
- Friedman 2001, *Greedy Function Approximation: A Gradient Boosting Machine* —— Friedman H-statistic 的定义。
"""


REQUIRED_TERMS: tuple[str, ...] = (
    # Section 2
    "target leakage",
    "Mutual Information",
    "univariate correlation",
    "MI",
    # Section 3
    "MNAR",
    "is_missing",
    "VIF",
    "Variance Inflation Factor",
    "hierarchical clustering",
    "PSI",
    "Population Stability Index",
    "CSI",
    "Characteristic Stability Index",
    "Target Encoding",
    "WOE",
    "Weight of Evidence",
    "Frequency Encoding",
    "CatBoost",
    "mRMR",
    "maximum Relevance Minimum Redundancy",
    "chi-squared",
    "ANOVA F-test",
    "F-statistic",
    # Section 4
    "L1",
    "Lasso",
    "Least Absolute Shrinkage and Selection Operator",
    "Elastic Net",
    "Stability Selection",
    "bootstrap",
    "GBDT",
    "Gradient Boosted Decision Tree",
    "Gini impurity",
    "Permutation Importance",
    "SHAP",
    "SHapley Additive exPlanations",
    "Null Importance",
    "Shuffle Test",
    "Boruta",
    "shadow feature",
    "RFECV",
    "Recursive Feature Elimination",
    "Group Lasso",
    "structured sparsity",
    "Friedman H",
    "SHAP Interaction",
    # Section 4.5
    "PCA",
    "Principal Component Analysis",
    "SVD",
    "Singular Value Decomposition",
    "Factor Analysis",
    "Autoencoder",
    "PLS",
    "Partial Least Squares",
    "Kernel PCA",
    # Section 5
    "Leave-One-Out",
    "LOO",
    "group ablation",
    "forward",
    "greedy",
    "p-value",
    "AUC delta",
    # Section 6
    "nested CV",
    "outer",
    "inner",
    "post-selection inference",
    "Polyhedral Selection Event",
    "Lee-Sun-Sun-Taylor",
    "Knockoff",
    "Barber",
    "FDR",
    "False Discovery Rate",
    "Benjamini-Hochberg",
    "BH",
    "Calibration",
    "subgroup",
    "shadow deployment",
    # Section 7
    "latency",
    "p99",
    "Interpretability",
    "Drift",
    "feature store",
    "Train-Serve Skew",
)


def sha256_of_description(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) pair of the target leaf."""
    h = hashlib.sha256()
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE path = ?",
        (TARGET_PATH,),
    ).fetchone()
    h.update(TARGET_PATH.encode("utf-8"))
    h.update(b"\x00")
    h.update((row[0] or "").encode("utf-8"))
    h.update(b"\x00")
    return h.hexdigest()


def validate_content(path: str, content: str) -> None:
    """Enforce AC: KaTeX math, section headers, 4+ tables, required terms."""
    if "$" not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no $...$ math delimiter found")
    if "## " not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no '## ' section header found")
    table_count = content.count("\n|")
    if table_count < 16:
        raise RuntimeError(
            f"[AC-FAIL] {path}: expected 4+ markdown tables "
            f"(>= 16 '|' row starts), got {table_count}"
        )
    content_lc = content.lower()
    missing = [t for t in REQUIRED_TERMS if t.lower() not in content_lc]
    if missing:
        raise RuntimeError(
            f"[AC-FAIL] {path}: missing required terms: {missing}"
        )
    if len(content) < 12_000:
        raise RuntimeError(
            f"[AC-FAIL] {path}: content length {len(content)} below 12000 target"
        )


def backup_db() -> Path:
    """Copy the sqlite DB to a timestamped backup before any write."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"mle_prep_pre_q28_content_{stamp}.db"
    shutil.copy2(DB_PATH, dest)
    print(f"[BACKUP] {dest.name}")
    return dest


def main() -> int:
    """Update the single Q#28 leaf with the comprehensive answer (idempotent)."""
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    validate_content(TARGET_PATH, DESC_Q28)
    print(f"[VALIDATE] content len={len(DESC_Q28)} chars OK")

    # Only back up when we might actually write.
    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_of_description(conn)
        print(f"[PRE]  sha256={pre_hash}")

        row = conn.execute(
            "SELECT id, description FROM framework_nodes WHERE path = ?",
            (TARGET_PATH,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] missing node at path={TARGET_PATH}")
            return 1
        node_id, current = row

        if current == DESC_Q28:
            print(f"[SKIP]   id={node_id} path={TARGET_PATH} (already up-to-date)")
            counts = {"UPDATED": 0, "SKIPPED": 1}
        elif current != PLACEHOLDER:
            preview = (current or "")[:80].replace("\n", " ")
            raise RuntimeError(
                f"[CONFLICT] path={TARGET_PATH}: existing description neither "
                f"placeholder nor expected new content. current[:80]={preview!r}"
            )
        else:
            backup_db()
            conn.execute(
                "UPDATE framework_nodes SET description = ? WHERE id = ?",
                (DESC_Q28, node_id),
            )
            conn.commit()
            counts = {"UPDATED": 1, "SKIPPED": 0}
            print(
                f"[UPDATE] id={node_id} path={TARGET_PATH} "
                f"len={len(DESC_Q28)} (was {len(current)})"
            )

        post_hash = sha256_of_description(conn)
        print(f"[POST] sha256={post_hash}")
    finally:
        conn.close()

    total = counts["UPDATED"] + counts["SKIPPED"]
    print(
        f"[SUMMARY] updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total={total} (expected 1)"
    )
    if total != 1:
        print("[FAIL] expected to touch exactly 1 leaf")
        return 1
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
