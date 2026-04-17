"""Seed shared knowledge cards -- phase 2 (T-P1-189).

Follow-up to seed_knowledge_cards_shared.py (phase 1 covered 2 of 14 SHARED
topics). This phase seeds the remaining 12 SHARED canonical cards identified
by the T-P0-184 audit (docs/staging/analysis/company_prep_overlap.md section 2,
Tier=SHARED): topics 1, 2, 7, 8, 10, 14, 18, 20, 22, 24, 26, 27.

Canonical prose: Chinese by default per feedback_lc_notes_chinese; algorithm
names, formula symbols, and complexity notation stay English. Formula rules
from repo conventions: use \\mid not bare |, single-line $$ blocks with blank
lines around consecutive display math.

Usage:
    python scripts/seed_knowledge_cards_shared_phase2.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

COMPANY_IDS = {
    "LinkedIn": 1,
    "Uber": 5,
    "Adobe": 23,
    "Pinterest": 29,
}


CARDS = [
    {
        "slug": "activation-functions",
        "title": "激活函数 (ReLU / GELU / SiLU / SwiGLU)",
        "tags": ["deep-learning", "activation", "transformer"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 30,
        "source_line_end": 80,
        "canonical_body": r"""## 动机

线性组合的堆叠仍是线性函数，激活函数引入**非线性**以赋予网络表达能力。现代设计还关注：(1) 梯度稳定（避免消失/爆炸），(2) 稀疏激活，(3) 计算与内存代价。

## 常见激活函数

$$
\text{ReLU}(x) = \max(0, x)
$$

$$
\text{LeakyReLU}(x) = \max(\alpha x, x), \quad \alpha \in (0, 1)
$$

$$
\text{GELU}(x) = x \cdot \Phi(x) \approx 0.5 x \bigl(1 + \tanh\bigl[\sqrt{2/\pi}(x + 0.044715 x^3)\bigr]\bigr)
$$

$$
\text{SiLU}(x) = x \cdot \sigma(x), \quad \sigma(x) = \frac{1}{1 + e^{-x}}
$$

$$
\text{SwiGLU}(x, W, V) = \text{SiLU}(xW) \odot (xV)
$$

其中 SwiGLU 是门控线性单元（GLU）族的一员，现代 LLM（LLaMA、PaLM）常用。

## 选型准则

| 场景 | 推荐 | 理由 |
|---|---|---|
| 经典 CNN / MLP | ReLU | 简单、稀疏、易优化 |
| ReLU dead neuron 问题 | LeakyReLU / PReLU | $x<0$ 仍有梯度 |
| Transformer FFN | GELU / SiLU | 平滑、负区间保留弱信号 |
| Modern LLM FFN | SwiGLU | 门控提升质量（以 1.5x 参数量换 perplexity） |
| 输出层概率 | sigmoid / softmax | 对应 BCE / CE 的 inverse link |

## 工程注意

- **ReLU dead neurons**：若某神经元长期输出 0（大负偏置），其梯度恒为 0 无法恢复。用较小学习率或 LeakyReLU 缓解。
- **GELU vs SiLU 精度差异**：tanh 近似版 GELU 与精确版（调 erf）在 fp16 下略有差，推理框架实现需对齐训练。
- **SwiGLU 额外计算**：相比 ReLU 多一条线性投影 $xV$，通常把 FFN hidden dim 降到 $2/3$ 以保持 FLOPs。

## 面试追问

1. **为什么 ReLU 优于 sigmoid/tanh？** sigmoid 饱和区梯度趋 0，ReLU 在正区间梯度恒为 1，解决深层网络梯度消失。
2. **SwiGLU 为什么被 LLM 广泛采纳？** Noam Shazeer 的对比实验显示在同 FLOPs 下 perplexity 更低；门控结构提供更灵活的信息路由。
3. **输出层为什么不用 ReLU？** ReLU 无上界不适合概率；分类任务输出层配合损失（softmax+CE, sigmoid+BCE）保证数值稳定与概率语义。
""",
    },
    {
        "slug": "loss-functions",
        "title": "损失函数 (BCE / CE / MSE / BPR / Huber)",
        "tags": ["loss", "optimization", "ml-theory"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 44,
        "source_line_end": 78,
        "canonical_body": r"""## 损失函数与概率解释

损失函数通常来自最大似然估计（MLE）：$\mathcal{L}(\theta) = -\log p(y \mid x; \theta)$。选择损失等同于选择**输出分布假设**。

## 回归损失

$$
\text{MSE}(y, \hat{y}) = \frac{1}{N} \sum_i (y_i - \hat{y}_i)^2
$$

$$
\text{MAE}(y, \hat{y}) = \frac{1}{N} \sum_i \lvert y_i - \hat{y}_i \rvert
$$

$$
\text{Huber}_\delta(e) = \begin{cases} \tfrac{1}{2} e^2 & \lvert e \rvert \le \delta \\ \delta(\lvert e \rvert - \tfrac{1}{2}\delta) & \lvert e \rvert > \delta \end{cases}
$$

- MSE 假设高斯噪声，对异常值敏感；MAE 对应 Laplace 噪声，对异常值鲁棒但 0 处不可微；Huber 结合二者。

## 二分类损失

$$
\text{BCE}(y, \hat{p}) = -\bigl[y \log \hat{p} + (1-y) \log (1-\hat{p})\bigr]
$$

其中 $\hat{p} = \sigma(z)$，对 $z$ 求梯度得 $\hat{p} - y$——这是 BCE 与 sigmoid 搭配的优雅之处（梯度无饱和）。实战常用 `BCEWithLogitsLoss` 在 log-space 数值稳定。

## 多分类损失

$$
\text{CE}(y, \hat{p}) = -\sum_{k=1}^K y_k \log \hat{p}_k
$$

其中 $\hat{p}_k = \text{softmax}(z)_k$。Label smoothing：$y_k \leftarrow (1-\epsilon) y_k + \epsilon / K$，防过度自信。

## 排序损失

$$
\text{BPR}(u, i, j) = -\log \sigma\bigl(s_{u,i} - s_{u,j}\bigr)
$$

其中 $i$ 是正样本 $j$ 是负样本，鼓励正样本得分高于负样本。配合负采样 / in-batch negatives 在推荐与检索中广泛使用。

## 选型速查

| 任务 | 损失 | 输出层 |
|---|---|---|
| 回归（正态噪声） | MSE | linear |
| 回归（厚尾 / 鲁棒） | Huber / MAE | linear |
| 二分类 | BCE | sigmoid |
| 多分类 | CE | softmax |
| 多标签 | BCE per-label | sigmoid |
| pairwise ranking | BPR / margin hinge | dot / MLP |
| 检索对比学习 | InfoNCE | normalized dot |

## 面试追问

1. **为什么不用 MSE 做分类？** 与 sigmoid 组合时梯度含 $\sigma'(z) = \hat{p}(1-\hat{p})$，当 $\hat{p}$ 接近 0/1 时梯度消失；BCE 的梯度为 $\hat{p} - y$ 始终正比于误差。
2. **CE 与 KL 散度的关系？** $\text{CE}(p, q) = H(p) + \text{KL}(p \parallel q)$；训练时 $H(p)$ 为常数，优化 CE 等价于最小化 KL。
3. **BPR 为什么能避免冷启动排序塌缩？** 它只关心 pairwise 序，而非绝对分值，无需对得分的绝对尺度建模。
""",
    },
    {
        "slug": "classification-metrics",
        "title": "分类评估指标 (Precision / Recall / F1 / AUC / PR-AUC)",
        "tags": ["evaluation", "ml-theory", "classification"],
        "source_company": "Uber",
        "source_file": "docs/company/uber/bps_knn_ml_fundamentals.md",
        "source_line_start": 499,
        "source_line_end": 538,
        "canonical_body": r"""## 混淆矩阵与基本定义

| | 预测正 | 预测负 |
|---|---|---|
| 实际正 | TP | FN |
| 实际负 | FP | TN |

$$
\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}
$$

$$
F_\beta = (1 + \beta^2) \cdot \frac{\text{Precision} \cdot \text{Recall}}{\beta^2 \cdot \text{Precision} + \text{Recall}}
$$

$F_1$ 是 $\beta=1$ 时 precision 与 recall 的调和平均。$\beta > 1$ 偏重 recall（医疗筛查），$\beta < 1$ 偏重 precision（垃圾邮件）。

## ROC-AUC

ROC 曲线横轴 FPR $= FP / (FP + TN)$，纵轴 TPR $= \text{Recall}$。AUC 等于**随机抽取一个正样本与一个负样本，模型给正样本打分更高的概率**（Mann-Whitney U 统计量）。对类别比例变化不敏感。

## PR-AUC

PR 曲线横轴 Recall，纵轴 Precision。类别**极度不平衡**（点击率、欺诈）时 PR-AUC 比 ROC-AUC 更能反映实际业务价值——ROC 中 FPR 的分母 $FP + TN$ 被海量负样本稀释。

## 校准 (Calibration)

排序对但概率失真会影响下游决策（阈值、期望收益）。常用方法：

- **Platt scaling**：$\hat{p}_\text{cal} = \sigma(a \hat{s} + b)$，在 hold-out 集上拟合。
- **Isotonic regression**：分段单调回归，灵活但需更多数据。
- **诊断**：reliability diagram、ECE（Expected Calibration Error）。

## 选型速查

| 场景 | 主指标 |
|---|---|
| 类别平衡 / 全面排序 | ROC-AUC |
| 类别极不平衡（CTR / fraud / malicious） | PR-AUC、Precision@K |
| 单一阈值决策 | F1 / Precision@Recall=R |
| 概率用于期望计算 | 先看 AUC + ECE |
| 多分类 | Macro-F1（平等）/ Micro-F1（样本加权） |

## 面试追问

1. **AUC = 0.5 说明什么？** 模型与随机等效，但仍可能在特定阈值下有用；应结合 PR 曲线再判断。
2. **为什么不平衡数据用 PR-AUC？** ROC 的 FPR 对大量真负样本稀释不敏感，AUC 高但 Precision@K 仍可能极低。
3. **F1 与 AUC 谁更稳定？** AUC 无需选阈值、对类别比例鲁棒；F1 依赖阈值和比例，部署前要配合阈值扫描。
""",
    },
    {
        "slug": "logistic-regression",
        "title": "逻辑回归推导与工程要点",
        "tags": ["ml-theory", "classification", "glm"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 81,
        "source_line_end": 141,
        "canonical_body": r"""## 模型形式

逻辑回归建模 $P(y=1 \mid x) = \sigma(w^\top x + b)$，其中 $\sigma(z) = 1/(1+e^{-z})$。线性打分经 sigmoid 挤压到 $(0, 1)$，可解释为概率。

## MLE 推导

似然：

$$
\mathcal{L}(w) = \prod_{i=1}^N \hat{p}_i^{y_i} (1 - \hat{p}_i)^{1 - y_i}
$$

负对数似然（NLL）即 BCE 损失：

$$
J(w) = -\frac{1}{N} \sum_i \bigl[y_i \log \hat{p}_i + (1 - y_i) \log (1 - \hat{p}_i)\bigr]
$$

对 $w$ 梯度：

$$
\nabla_w J = \frac{1}{N} \sum_i (\hat{p}_i - y_i) x_i
$$

形式与线性回归的梯度 $(\hat{y} - y)x$ 完全一致——这是"广义线性模型 (GLM) 配 canonical link 时梯度无 sigmoid'项"的普遍性质。

## 二阶信息与求解

Hessian：

$$
H = \frac{1}{N} \sum_i \hat{p}_i (1 - \hat{p}_i) x_i x_i^\top
$$

凸函数（对 $w$），可用 L-BFGS、Newton-Raphson（IRLS）或 SGD 求解。sklearn 默认 L-BFGS / liblinear。

## 正则化版本

$$
J_\text{reg}(w) = J(w) + \lambda \lVert w \rVert_2^2 \quad \text{或} \quad \lambda \lVert w \rVert_1
$$

参考 `overfitting-l1-l2` 卡片。L2 提升条件数加速收敛；L1 得到稀疏解做特征选择。

## 多分类扩展

Softmax regression：

$$
P(y=k \mid x) = \frac{e^{w_k^\top x}}{\sum_{j} e^{w_j^\top x}}
$$

与 One-vs-Rest 相比可保证概率归一，且梯度 $= (\hat{p} - y) x^\top$ 仍具同一形式。

## 工程要点

- **特征归一化**：加速 SGD / L-BFGS 收敛，避免数值问题。
- **高基数类别特征**：embedding / target encoding，避免 one-hot 维数爆炸。
- **类别不平衡**：`class_weight='balanced'` 等价于加权 loss，或用采样；不改变排序（AUC 不变），改变阈值与 calibration。
- **线性不可分时**：加交叉特征、多项式展开或切换 GBDT / DNN。

## 面试追问

1. **为什么 sigmoid + BCE 梯度简洁？** 指数族 canonical link 性质。
2. **LR 与 SVM 区别？** LR 产出校准概率，对异常值更敏感（soft margin 的 hinge 只惩罚 margin 内外）。
3. **LR 能否过拟合？** 特征维度极高或存在完全可分数据时 $w \to \infty$，需 L2 正则或 early stop。
""",
    },
    {
        "slug": "tree-ensembles",
        "title": "决策树 / 随机森林 / 梯度提升",
        "tags": ["tree", "ensemble", "ml-theory"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 263,
        "source_line_end": 367,
        "canonical_body": r"""## 决策树

**分裂准则**：

$$
\text{Gini}(S) = 1 - \sum_{k} p_k^2, \quad \text{Entropy}(S) = -\sum_{k} p_k \log p_k
$$

$$
\text{InfoGain} = I(S) - \sum_{v} \frac{\lvert S_v \rvert}{\lvert S \rvert} I(S_v)
$$

回归树用方差减少：$\sum_v \frac{\lvert S_v \rvert}{\lvert S \rvert} \mathrm{Var}(S_v)$。

**优点**：可解释、无需特征缩放、处理混合类型；**缺点**：高方差、易过拟合、对样本微扰敏感。

## Random Forest

- 每棵树用 bootstrap 样本（bagging），每次分裂随机选 $\sqrt{p}$ 或 $p/3$ 个特征。
- 最终预测取多数投票 / 均值。
- 方差分析：若基学习器两两相关 $\rho$，平均后方差为

$$
\rho \sigma^2 + \frac{1 - \rho}{n} \sigma^2
$$

随机选特征降低 $\rho$，`bagging` 降低后项。**主要降 variance，不怎么降 bias**。

## Gradient Boosting (GBDT)

每一步拟合当前残差（即损失的负梯度）：

$$
f_{t}(x) = f_{t-1}(x) + \eta \cdot h_t(x), \quad h_t \approx -\nabla_{f} \mathcal{L}(y, f_{t-1}(x))
$$

- $\eta$（shrinkage / learning rate）小则需要更多树，鲁棒性更好。
- 主要降 bias，需控制 variance：限深度（浅树即弱学习器）、subsample、early stopping。
- XGBoost / LightGBM / CatBoost 在分裂算法、直方图、类别特征处理上做了系统化优化。

## RF vs GBDT 对比

| 维度 | Random Forest | GBDT |
|---|---|---|
| 主要降 | variance | bias |
| 并行 | 树独立可并行 | 顺序依赖 |
| 调参数量 | 较少 | 较多（lr / n\_estimators / depth） |
| 过拟合风险 | 低（树多不一定过拟合） | 高（需 early stop） |
| 类别不平衡 | class\_weight | scale\_pos\_weight |

## 工程要点

- **Shallow trees + many iterations** 是 GBDT 标配（depth 4-8）。
- **Leaf-wise vs level-wise**：LightGBM 用 leaf-wise（挑当前损失下降最多的叶子）收敛快但需 `max_leaves` 控制。
- **Categorical features**：CatBoost ordered target statistics 避免 target leakage。

## 面试追问

1. **为什么 bagging 不适合深层神经网络？** 相关性 $\rho$ 过高，方差削减有限；成本也高。
2. **GBDT 如何支持二分类？** 用对数损失，计算负梯度（即 $y - \hat{p}$）作为目标去拟合。
3. **树模型不需要归一化？** 分裂只看顺序，单调变换不影响；但 one-hot 高基数 + GBDT 会稀释分裂收益，考虑 target encoding。
""",
    },
    {
        "slug": "feature-engineering-scaling",
        "title": "特征工程与尺度归一化",
        "tags": ["feature-engineering", "preprocessing", "ml-engineering"],
        "source_company": "Uber",
        "source_file": "docs/company/uber/bps_knn_ml_fundamentals.md",
        "source_line_start": 158,
        "source_line_end": 613,
        "canonical_body": r"""## 为什么特征工程仍重要

端到端深度学习在图像/文本领域弱化了手工特征，但在表格 / 广告 / 搜索 / 风控中，特征工程仍是模型质量的首要驱动。目标是**让线性或浅模型也能抓住非线性信号**。

## 数值特征处理

- **Standardization**：$x' = (x - \mu) / \sigma$，适合存在极值的分布（收入、时长）。
- **Min-max**：$x' = (x - x_\min) / (x_\max - x_\min)$，适合有边界的特征（评分）。
- **对数 / Box-Cox**：压缩长尾，常用于金额、点击次数。
- **分箱 (binning)**：把连续值切成桶（等频 / 等距 / 决策树自动分箱），对线性模型补充非线性，对 GBDT 影响较小。

## 类别特征

- **One-hot**：维度 = 类别数；适合低基数。
- **Target encoding / mean encoding**：用目标均值替换；需用 K-fold 或平滑以防过拟合。CatBoost 的 ordered TS 是工程化解法。
- **Embedding**：深度模型中常用；冷启动用 hash trick / default bucket。
- **Frequency encoding**：出现次数代替类别本身，对长尾类别合适。

## 缺失值

- **显式标记**：增加 is\_missing bool；避免信息丢失。
- **填充**：均值 / 中位数 / 类别众数；时间序列用前值。
- **模型级支持**：XGBoost / LightGBM 可把 NaN 作为独立分支。

## 特征交叉

- **数值-数值**：比值、差值、对数之差（弹性）。
- **数值-类别**：按类别分组的 mean / std / count。
- **类别-类别**：二元组 one-hot、FM / FFM 的二阶交互。

## 哪些模型对尺度敏感？

| 模型 | 需要缩放? | 理由 |
|---|---|---|
| KNN | 必须 | 距离度量由大尺度特征主导 |
| K-means | 必须 | 同上 |
| SVM (RBF) | 必须 | 核函数依赖距离 |
| Logistic / Linear Regression | 推荐 | 加速优化，配合 L2 更公平 |
| NN | 推荐 | BN 部分缓解，但输入层规模仍影响稳定性 |
| 决策树 / GBDT / RF | 不需要 | 分裂仅看相对顺序 |

## 防泄漏

**只用训练集拟合缩放器 / 编码器**，再应用到 val / test。K-fold target encoding 必须在每折内部独立计算。时间序列切分需保持时间顺序（无未来信息）。

## 面试追问

1. **KNN 中 height(cm) 与 income(USD) 混用会怎样？** 距离被 income 的绝对尺度主导，等价于 height 没用；先 standardize。
2. **target encoding 过拟合风险？** 直接用训练集均值会"偷看"标签；用 K-fold + 平滑 $\bar{y}_c \leftarrow (n_c \bar{y}_c + m \bar{y}) / (n_c + m)$。
3. **缺失值填 0 可能引入什么偏差？** 若 0 有语义（如点击数 = 0 表示新用户），等同把缺失映射为"零行为用户"，可能误导模型；显式 is\_missing 更安全。
""",
    },
    {
        "slug": "lru-cache-threaded",
        "title": "LRU Cache 实现与并发扩展",
        "tags": ["data-structure", "concurrency", "coding"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 847,
        "source_line_end": 1001,
        "canonical_body": r"""## 需求与复杂度目标

LRU (Least Recently Used) 缓存需要：

- `get(key)` 命中返回 value 并把该 key 标记为"最近使用"；未命中返回 -1。
- `put(key, value)` 插入/更新，并在超过容量时淘汰**最久未使用**的 key。
- 目标：`get` 与 `put` 均摊 $O(1)$。

## 标准实现：HashMap + 双向链表

- `HashMap<Key, Node*>` 提供 $O(1)$ 定位。
- 双向链表节点存 $(key, value)$，head 端是最新、tail 端是最旧。
- `get`：HashMap 找节点 $\to$ 从链表中摘下 $\to$ 插到 head。
- `put`：若已存在则更新并 move-to-head；否则新建节点插到 head；若超容量摘 tail 节点并从 HashMap 删除。

```python
class Node:
    __slots__ = ("k", "v", "prev", "next")
    def __init__(self, k=0, v=0):
        self.k, self.v = k, v
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.cap = capacity
        self.map: dict[int, Node] = {}
        self.head, self.tail = Node(), Node()
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node: Node) -> None:
        node.prev.next, node.next.prev = node.next, node.prev

    def _add_front(self, node: Node) -> None:
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node); self._add_front(node)
        return node.v

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            node = self.map[key]; node.v = value
            self._remove(node); self._add_front(node)
            return
        if len(self.map) >= self.cap:
            lru = self.tail.prev
            self._remove(lru); self.map.pop(lru.k)
        node = Node(key, value)
        self.map[key] = node; self._add_front(node)
```

## 并发扩展

**最简方案**：整个 `LRUCache` 外面套 `ReentrantLock` / Python `threading.Lock`。正确但高并发下锁争抢严重。

**分段锁 (Striped Lock)**：把 key 哈希到 $N$ 个段，每段独立 LRU + 锁。近似 LRU，吞吐随分段近似线性上升。Guava 的 `LoadingCache`、Caffeine 都是这条路。

**无锁结构**：Caffeine 使用 TinyLFU + W-TinyLFU，配合环形缓冲 (`RingBuffer`) 把访问事件异步刷入状态机，读路径近乎无锁。

## 变体

- **LFU**：按访问频率淘汰；用 freq → 双向链表 + 全 HashMap，复杂度仍 $O(1)$。
- **LRU-K**：记录最近 K 次访问时间，淘汰最久的第 K 次访问，抗扫描性强。
- **TTL**：给节点加过期时间，在 `get` 时检查或定时清理。

## 面试追问

1. **为什么不用 `collections.OrderedDict` 直接？** 可以，`move_to_end` 是 $O(1)$；面试常要求手写以考察链表操作。
2. **满时淘汰策略？** LRU 面向时间局部性（最近访问更可能再访问）；Netflix 混合 TTL + LFU 减少 burst 污染。
3. **并发下 move-to-head 是临界区，怎么减小代价？** 见分段锁 / Caffeine 异步队列；或退化为近似 LRU（CLOCK 算法）。
""",
    },
    {
        "slug": "dag-dfs-service-dependency",
        "title": "DAG / 服务依赖图 DFS 与拓扑排序",
        "tags": ["graph", "dfs", "topological-sort"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 1002,
        "source_line_end": 1100,
        "canonical_body": r"""## 场景

- **服务依赖图**：部署顺序、启动顺序、故障影响面分析。
- **任务调度**：Airflow / Spark DAG 任务先后。
- **课程先修**：LC 207 / 210。

## 拓扑排序两种实现

### Kahn 算法（BFS，按入度）

```python
from collections import defaultdict, deque

def topo_kahn(n: int, edges: list[tuple[int, int]]) -> list[int]:
    indeg = [0] * n
    g: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        g[u].append(v); indeg[v] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    order: list[int] = []
    while q:
        u = q.popleft(); order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else []
```

若 `len(order) < n`，说明图有环。时间 $O(V + E)$，空间 $O(V + E)$。

### DFS 三色法

节点状态：WHITE (未访问) / GRAY (在当前栈) / BLACK (已完成)。

- DFS 进入时置 GRAY，离开时置 BLACK 并推入栈。
- 若遇到 GRAY 邻居 $\Rightarrow$ **发现后向边 $\Rightarrow$ 有环**。
- 栈序的反转即拓扑序。

```python
WHITE, GRAY, BLACK = 0, 1, 2

def topo_dfs(n: int, edges: list[tuple[int, int]]) -> list[int]:
    g: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        g[u].append(v)
    color = [WHITE] * n
    order: list[int] = []

    def dfs(u: int) -> bool:
        color[u] = GRAY
        for v in g[u]:
            if color[v] == GRAY:
                return False  # cycle
            if color[v] == WHITE and not dfs(v):
                return False
        color[u] = BLACK
        order.append(u)
        return True

    for u in range(n):
        if color[u] == WHITE and not dfs(u):
            return []
    return order[::-1]
```

## 环检测与强连通分量

- **DAG 判定**：拓扑排序若覆盖所有节点则是 DAG。
- **SCC**：Tarjan / Kosaraju 在 $O(V + E)$ 内求强连通分量；缩点后是 DAG，常用于死锁检测与最短路预处理。

## 工程扩展

- **影响面分析**：从故障节点 BFS/DFS 沿反向依赖边收集下游服务集合。
- **部分拓扑排序**：优先级 + 入度，用优先队列（Kahn 变体）求字典序最小的拓扑序（LC 1203、Uber 服务启动顺序）。
- **Diamond 依赖**：服务 A 依赖 B, C；B, C 都依赖 D。拓扑序允许 B C 任序，但部署时 D 必须先启动。

## 面试追问

1. **Kahn vs DFS 选哪个？** Kahn 自然支持字典序最小拓扑排序，且易检测入度为 0 的起点；DFS 递归深度大时需显式栈。
2. **有环的依赖图如何修？** 找 SCC 缩点，把循环组合并为一个"原子启动单元"，或引入异步接口打破启动时依赖。
3. **更新依赖图时如何增量维护拓扑序？** 维护层序 (label) + 离线批量重算；在线增量拓扑排序是 Pearce-Kelly 算法。
""",
    },
    {
        "slug": "feed-ranking-system",
        "title": "Feed / 视频推荐排序系统",
        "tags": ["system-design", "ranking", "recommendation"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_sd_notes_content.md",
        "source_line_start": 639,
        "source_line_end": 698,
        "canonical_body": r"""## 系统分层

Feed / 短视频排序遵循**漏斗**结构：

1. **Retrieval (召回)**：从亿级候选挑数千，延迟预算约 20-50 ms。多路并行：协同过滤 / two-tower embedding / 标签召回 / trending。
2. **Pre-ranking (粗排)**：轻量模型（浅 DNN / LR）在几千 $\to$ 几百，延迟 5-10 ms。
3. **Ranking (精排)**：复杂模型（DeepFM / DLRM / wide&deep / transformer）做点-wise 打分，输出 pCTR / pCVR / pWatchTime。
4. **Re-ranking (重排)**：多样性、序列依赖、公平性、业务规则，输出最终 K 个。

## 打分公式

多目标融合常用线性加权或帕累托前沿：

$$
\text{score} = \alpha \cdot p\text{CTR} + \beta \cdot p\text{VV}^{\gamma} + \delta \cdot p\text{Like} - \eta \cdot p\text{Dislike}
$$

指标组合与权重由业务目标和 online A/B 决定；$p\text{VV}^\gamma$（$\gamma<1$）用于压制长视频偏差。

排序损失常用 pairwise BPR 或 listwise LambdaRank / lambdamart（面向 NDCG）：

$$
\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}, \quad \text{DCG@k} = \sum_{i=1}^{k} \frac{2^{\text{rel}_i} - 1}{\log_2(i+1)}
$$

## 特征

- **用户**：人口属性、长短期兴趣向量、过去 N 天点击序列。
- **内容**：标签、embedding、新鲜度、历史 CTR。
- **上下文**：时间、设备、网络、地理。
- **交叉**：用户-内容共现、用户塔 $\otimes$ 物料塔 dot。

## 工程约束

- **延迟**：整体 P99 < 200 ms，其中召回 + 粗排 < 80 ms，精排 < 80 ms，重排 < 30 ms。
- **实时性**：用户行为应在 1-5 分钟内反馈到短期兴趣；模型 daily / hourly 更新。
- **在线-离线一致**：特征管道分在线 (Flink) 与离线 (Spark) 两套，需 schema + 计算逻辑一致，防 training-serving skew。

## 评估

- **离线**：AUC、logloss、NDCG@k、多样性 (ILS)。
- **在线**：CTR、dwell time、留存、上滑、不喜欢率。
- **A/B 放量**：先 1% 小流量观察 anomaly，再逐步 ramp，避免 cannibalization。

## 面试追问

1. **为什么分粗排精排两段？** 精排模型单 QPS 代价高，粗排以更小模型把候选进一步裁剪，整体延迟可控。
2. **如何避免 feedback loop？** 负采样保留未曝光样本、counterfactual inverse-propensity weighting、exploration budget（$\epsilon$-greedy / Thompson）。
3. **视频 watch time 如何建模？** 常用 Weighted Logistic Regression（把观看时长作为正样本权重），或直接预测 $\log(\text{watch time})$。
""",
    },
    {
        "slug": "job-scheduler-rate-limit",
        "title": "任务调度与限流系统",
        "tags": ["system-design", "scheduling", "rate-limit"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_sd_notes_content.md",
        "source_line_start": 278,
        "source_line_end": 366,
        "canonical_body": r"""## 任务调度核心抽象

- **Task**：$(\text{id}, \text{payload}, \text{priority}, \text{earliest\_run}, \text{retry\_policy})$。
- **Queue**：优先级堆 / 时间堆 / 多级延迟队列。
- **Worker**：pool 里并发消费者；完成后 ack / nack。
- **Coordinator**：分配任务、重试、死信队列。

## 分类

| 类型 | 示例 | 典型实现 |
|---|---|---|
| Cron / 定时 | 日报 / 清理 | Quartz, Airflow scheduler |
| 延迟队列 | 订单 30 分钟未支付自动取消 | Redis ZSET, RabbitMQ TTL + DLX |
| 流式 / 事件驱动 | 用户行为处理 | Kafka + Flink |
| DAG 批处理 | ETL 管线 | Airflow, Luigi, Spark |

## 一致性与容错

- **Exactly-once**：kafka transactions + idempotent producer / consumer；或用去重表。
- **Leader 单点**：ZooKeeper / etcd 选主；worker 无状态可水平扩展。
- **Fencing token**：避免旧 leader 误操作。

## 限流 (Rate Limiting)

### Token Bucket

容量 $B$，填充速率 $r$ tokens/sec。请求消耗一个 token，桶空则拒绝或排队。支持**突发 burst**：瞬时最多 $B$ 个请求。

### Leaky Bucket

固定输出速率 $r$，请求入桶若超容量丢弃。输出平滑、不支持突发，适合带宽整形。

### Sliding Window Counter

过去 $W$ 秒内请求数 $\le N$：

$$
\text{count}(t) = \text{count}_\text{prev\_bucket} \cdot \frac{W - (t \mod W)}{W} + \text{count}_\text{curr\_bucket}
$$

近似平滑，内存 $O(1)$ per key，是 Cloudflare / Nginx 常用方案。

### Fixed Window

简单但有 **boundary burst**：在窗口边界可能瞬时 2x 速率通过。

## 分布式限流

- **集中式**：Redis `INCR` + TTL；网络 RTT 1-2 ms。
- **本地 + 采样回报**：每个节点本地维护配额，周期性向中心同步；降低 RTT 但有小幅漂移。
- **Quota 拉取**：worker 一次拉 N 个 token，用完再拉；适合低频调用。

## 面试追问

1. **为什么用堆实现延迟队列而非 sorted set？** 单机堆 $O(\log n)$ 插入/弹出，Redis ZSET 提供相同复杂度且支持持久化 + 分片。
2. **Token bucket 与 Leaky bucket 何时选？** 需要允许 burst（API gateway）选 token bucket；需要均匀输出（网络整形）选 leaky bucket。
3. **失败重试如何避免雪崩？** 指数退避 + jitter；熔断器（circuit breaker）在连续失败时短路；区分 retryable vs terminal error。
""",
    },
    {
        "slug": "top-k-stream",
        "title": "Top-K (流式 / 堆)",
        "tags": ["algorithm", "heap", "streaming"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_sd_notes_content.md",
        "source_line_start": 565,
        "source_line_end": 638,
        "canonical_body": r"""## 问题形态

- **静态 Top-K**：给定数组找前 K 大 / 小。
- **流式 Top-K**：数据持续到来，任意时刻返回当前前 K。
- **近似 Top-K**：数据规模极大，允许误差换空间（Count-Min Sketch + heap）。

## 堆解法

维护**大小为 K 的小顶堆**（找 Top-K 大）：

- 初始化：前 K 个元素建堆，$O(K)$。
- 每读入新元素 $x$：若 $x > heap[0]$ 则替换堆顶并下沉；否则忽略。
- 时间：$O(N \log K)$，空间 $O(K)$。

```python
import heapq
def top_k_largest(nums: list[int], k: int) -> list[int]:
    heap: list[int] = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return sorted(heap, reverse=True)
```

## Quickselect（静态数组）

基于三路快排思想，期望 $O(N)$ 找第 K 大：

- 随机选 pivot，partition 后根据 pivot 位置决定递归哪一侧。
- 最坏 $O(N^2)$；搭配 median-of-medians 可保证 $O(N)$。

流式场景不适用 quickselect，因为数据不可重读。

## 分布式 Top-K

**两阶段归并**：

1. 每个 shard 本地用堆算出 Top-K。
2. Coordinator 归并所有 shard 的 K×S 个候选，再取 Top-K。

复杂度 $O(N_\text{shard} \log K)$ per shard + $O(SK \log K)$ merge。

要求**具体的元素返回**而非仅计数时，此方案精确。若只要**频次 Top-K**（如"热搜词"），可用：

## 近似频次 Top-K (Heavy Hitters)

- **Count-Min Sketch**：$d$ 行 $w$ 列哈希计数，查询时取 $\min_d$；误差 $\epsilon = e/w$，失败概率 $\delta = e^{-d}$。
- **Space-Saving / Misra-Gries**：维护 K 个候选 counter；新元素若命中则 +1，否则挤掉计数最小者并用新元素顶替（计数继承）。内存 $O(K)$，精确度与 K 相关。

在搜索 trending 词、DDoS 检测、广告竞价 top bidder 场景应用广泛。

## 面试追问

1. **为什么 Top-K 大用小顶堆？** 堆顶是当前 Top-K 集合中最小的"门槛"，新元素只要大于它才替换；大顶堆则无法 $O(1)$ 获知门槛。
2. **数据量 $10^{12}$ 不能全加载，怎么办？** 分布式两阶段归并；或近似算法（Count-Min + Heavy Hitters）。
3. **Top-K 最少比较次数下界？** 对任意比较式算法，找 K 大下界是 $N + O(K \log K)$，quickselect 常数上更好。
""",
    },
    {
        "slug": "llm-personalization",
        "title": "LLM 个性化内容生成系统",
        "tags": ["llm", "personalization", "system-design"],
        "source_company": "LinkedIn",
        "source_file": "data/linkedin_sd_notes_content.md",
        "source_line_start": 462,
        "source_line_end": 564,
        "canonical_body": r"""## 场景

用 LLM 为每个用户生成定制化文案（LinkedIn InMail、邮件主题、商品描述、通知摘要）。与传统 ranking 不同，**输出是生成文本**而非排序 score，系统设计需同时权衡质量、延迟、成本、安全。

## 分层架构

1. **Retrieval / Context Building**：拉取用户画像、最近交互、目标受众、业务约束；组装 prompt。
2. **Prompt Templating**：角色 (role) + 少量 few-shot + 变量槽位；模板版本化做 A/B。
3. **LLM 调用**：本地部署微调模型（LoRA / SFT）或调外部 API，视 QPS 与隐私预算决定。
4. **Post-Processing**：安全过滤、重复率检测、品牌风格校准、字符长度裁剪。
5. **Online Ranking / 选优**：同一 prompt 采样 $n$ 个候选，用排序器（BLEU 对模板 + RM 打分）挑最优。

## 优化维度

### 质量
- **RLHF / DPO 对齐**：参考 T-P0-164 模块。优先 DPO（无 reward model，训练稳定）。
- **Retrieval-Augmented Generation**：把用户最新行为与产品信息作为 context 注入，减少幻觉。
- **Personalization via soft prompts**：为每类用户学一个 soft prefix，共享主干参数。

### 延迟
- **Streaming**：Server-Sent Events 先返回前 N token，TTFT $<300$ ms。
- **Speculative decoding**：小模型先猜 $k$ 个 token，大模型并行验证，吞吐 2-3x。
- **KV cache + PagedAttention**：减少内存碎片，提升 batch。
- **Continuous batching**：动态合并并发请求的 prefill/decode 步骤。

### 成本
- **Distillation**：70B $\to$ 7B，质量损失 $<5\%$ 但成本 / 延迟显著下降。
- **Quantization**：INT8 / INT4 (GPTQ / AWQ) 推理显存减半。
- **Cache**：相同 prompt 前缀的 KV 状态共享；相同产出对高重复场景命中率 > 30%。

### 安全
- **Prompt injection 防护**：分隔用户输入与系统指令；白名单工具调用。
- **敏感内容**：regex + 分类器二道闸；RLHF reward model 包含 safety reward。
- **隐私**：不将 raw PII 直接入 prompt，改为 token 化 / 聚合统计。

## 指标

- **离线**：BLEU / ROUGE / embedding 相似度 vs 参考、人工评分、多样性 (self-BLEU)。
- **在线**：点击 / 回复 / 转化率；调性审查 pass rate；p95 TTFT。
- **护栏**：toxicity rate、hallucination rate、brand consistency。

## 面试追问

1. **为什么不把用户 ID 直接放进 prompt？** 隐私与幻觉风险；用短语化的兴趣聚合或 embedding prefix 更安全。
2. **如何选择在线精排 vs 离线缓存？** 低 QPS 高价值（招聘 InMail）走在线精排 + streaming；高 QPS 低差异化（通用推送摘要）走离线批量 + 缓存。
3. **RAG 与 fine-tune 哪个更适合个性化？** RAG 更新便宜、可解释，适合新鲜兴趣；fine-tune 捕捉稳定风格；生产常二者并用。
""",
    },
]


OVERLAYS = [
    # Classification metrics -- Adobe quant-quality overlay per audit §2 topic 7
    {
        "card_slug": "classification-metrics",
        "company_name": "Adobe",
        "angle": "product",
        "overlay_body": r"""Adobe 推理优化语境下的分类评估：
- Quantization (GPTQ/AWQ/SmoothQuant) 评估用**同一 prompt 集**对量化前后模型打分，比较 top-1 accuracy / PPL / MMLU。
- Calibration 非常关键：INT4 模型仍需保持 logits 排序 + 概率校准，否则下游 retrieval / routing 会失准。
- 指标组合：MMLU / HumanEval (acc) + PPL + output drift (BLEU vs fp16)。""",
        "source_file": "scripts/seed_adobe_day5_inference.py",
        "source_line_start": 379,
        "source_line_end": 458,
    },
    # Logistic regression -- Uber overlay
    {
        "card_slug": "logistic-regression",
        "company_name": "Uber",
        "angle": "product",
        "overlay_body": r"""Uber 的 ranking / CTR 场景：
- LR 仍是 CTR baseline，常与 FM / DeepFM 同时作为 ensemble 的一员；面试会问"何时 LR 足够"（特征稀疏高维 + 线性可分）。
- 与 KNN 对比：KNN 无参数、依赖距离；LR 有全局参数、可用 L2 正则和 calibration。
- 常被引申到"如何在线更新 LR"——FTRL-Proximal 算法（Google 2013）。""",
        "source_file": "docs/company/uber/bps_knn_ml_fundamentals.md",
        "source_line_start": 354,
        "source_line_end": 404,
    },
    # Feature engineering -- LinkedIn sampling overlay
    {
        "card_slug": "feature-engineering-scaling",
        "company_name": "LinkedIn",
        "angle": "interview-format",
        "overlay_body": r"""LinkedIn ML coding / prob 轮常把特征工程作为开放题：
- 与 stratified sampling（ml_coding:744）串联：不均衡数据先 sample 再建特征，还是特征后 sample？答：通常先 sample / reweight 再 fit encoder 避免 leakage。
- target encoding 的 K-fold 实现是高频白板题。""",
        "source_file": "data/linkedin_ml_coding_notes_content.md",
        "source_line_start": 744,
        "source_line_end": 846,
    },
    # LRU -- Uber OOD parking-lot overlay per audit topic 18
    {
        "card_slug": "lru-cache-threaded",
        "company_name": "Uber",
        "angle": "interview-format",
        "overlay_body": r"""Uber custom coding 把 LRU 语义嵌入 OOD 题：
- 停车场 OOD (custom:1473) 的"最近离开车位"策略其实是 LRU 变体；需要同时支持按车位号 / 按到达时间两种查询。
- 解法：HashMap<SpotId, Node> + 双向链表（按到达时间排序）+ 按车型分桶。
- Cheatsheet:502 把 OOD 归入"组合容器"类题型——考察数据结构选型能力而非算法难度。""",
        "source_file": "docs/company/uber/bps_custom_solutions.md",
        "source_line_start": 1473,
        "source_line_end": 1560,
    },
    # DAG DFS -- Uber cheatsheet overlay
    {
        "card_slug": "dag-dfs-service-dependency",
        "company_name": "Uber",
        "angle": "interview-format",
        "overlay_body": r"""Uber pattern cheatsheet 把 DFS/回溯列为独立模式：
- cheatsheet:87 给出 DFS 模板（visited + 回溯）与 union-find 的对比速查：检测无向图连通性用 UF；检测有向图环用 DFS 三色法。
- 自定义题 (custom) 常把 DAG 嵌入业务场景（司机调度依赖），需要把业务名词映射回"图 + 拓扑排序"。""",
        "source_file": "docs/company/uber/bps_pattern_cheatsheet.md",
        "source_line_start": 87,
        "source_line_end": 179,
    },
    # Feed ranking -- Uber ranking-as-allocation overlay (topic 22)
    {
        "card_slug": "feed-ranking-system",
        "company_name": "Uber",
        "angle": "product",
        "overlay_body": r"""Uber 把 ranking 框为**分配问题** (ranking-as-allocation, design:59)：
- 不仅预测 pCTR，还要考虑资源约束：司机供给、营销预算、补贴上限。
- 用拉格朗日乘子把约束转为 score 调整：$\text{score}' = \text{score} - \lambda \cdot \text{cost}$。
- 线上用对偶反馈调 $\lambda$（Proportional-Integral 控制器），保证日度预算 converge。
- 与 LinkedIn 广告排序 (sd:462) 的差异：Uber 的 supply 约束是**即时的**（司机此刻在哪），feed ranking 约束更多是 *slot-level diversity*。""",
        "source_file": "docs/company/uber/bps_design_architecture.md",
        "source_line_start": 59,
        "source_line_end": 165,
    },
    # Feed ranking -- LinkedIn InMail overlay
    {
        "card_slug": "feed-ranking-system",
        "company_name": "LinkedIn",
        "angle": "product",
        "overlay_body": r"""LinkedIn 短视频 / feed 侧重"职业场景"内容：
- 新鲜度衰减更平缓（职业机会有效期数周 vs 短视频数小时）。
- 多目标中 **Like / Comment / Share** 权重高于 watch time，因为内容以图文 + 短视频混合。
- re-ranking 需强约束同一发布者不连续出现、同一话题多样化。""",
        "source_file": "data/linkedin_sd_notes_content.md",
        "source_line_start": 96,
        "source_line_end": 179,
    },
    # Job scheduler -- Uber greedy overlay
    {
        "card_slug": "job-scheduler-rate-limit",
        "company_name": "Uber",
        "angle": "interview-format",
        "overlay_body": r"""Uber cheatsheet:332 把调度抽象为贪心问题：
- "N 个任务分配到 K 个 worker，最大化完成数" 常用贪心 + 堆 (cheatsheet:356)。
- custom 题里"server throughput heap"是 rate limit 的变体：给定时序请求，判断当前秒是否超限——滑窗队列或最小堆。""",
        "source_file": "docs/company/uber/bps_pattern_cheatsheet.md",
        "source_line_start": 332,
        "source_line_end": 441,
    },
    # Top-K -- Uber heap overlay
    {
        "card_slug": "top-k-stream",
        "company_name": "Uber",
        "angle": "interview-format",
        "overlay_body": r"""Uber heap 模板 (cheatsheet:356) + custom throughput 题：
- 实时 top-K 活跃司机区域：每分钟聚合订单数，维护 size-K 小顶堆。
- 分布式版本：各 shard 本地 top-K，再归并。
- 问"如果 K 也很大呢？"答：切换到近似算法 (Count-Min + Misra-Gries)。""",
        "source_file": "docs/company/uber/bps_pattern_cheatsheet.md",
        "source_line_start": 356,
        "source_line_end": 395,
    },
    # LLM personalization -- Adobe overlay (layer: model infra)
    {
        "card_slug": "llm-personalization",
        "company_name": "Adobe",
        "angle": "product",
        "overlay_body": r"""Adobe Firefly / creative-ops 语境的 LLM 个性化偏**模型侧**：
- DPO 对齐用于"品牌调性"一致化（day2_rlhf:240）。
- 推理优化：PagedAttention + continuous batching + speculative decoding（day5_inference:543）。
- 70B $\to$ 7B 蒸馏保质降本（day2_rlhf:433）。
- 与 LinkedIn InMail 的"retrieval + 模板工程"层侧重点不同：LinkedIn 更强调 prompt/RAG 质量，Adobe 更强调**服务层推理成本与延迟**。""",
        "source_file": "scripts/seed_adobe_day5_inference.py",
        "source_line_start": 459,
        "source_line_end": 665,
    },
]


def seed(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    ok = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_cards'"
    ).fetchone()
    if not ok:
        raise RuntimeError(
            "knowledge_cards table missing. Run migrate_add_knowledge_cards.py first."
        )

    upserted_cards = 0
    for card in CARDS:
        existing = cur.execute(
            "SELECT id FROM knowledge_cards WHERE slug=?", (card["slug"],)
        ).fetchone()
        if existing:
            cur.execute(
                """UPDATE knowledge_cards
                   SET title=?, canonical_body=?, tags=?, source_company=?,
                       source_file=?, source_line_start=?, source_line_end=?,
                       updated_at=CURRENT_TIMESTAMP
                   WHERE slug=?""",
                (
                    card["title"],
                    card["canonical_body"],
                    json.dumps(card["tags"], ensure_ascii=False),
                    card["source_company"],
                    card["source_file"],
                    card["source_line_start"],
                    card["source_line_end"],
                    card["slug"],
                ),
            )
            print(f"[UPDATE] {card['slug']}")
        else:
            cur.execute(
                """INSERT INTO knowledge_cards
                   (slug, title, canonical_body, tags, source_company,
                    source_file, source_line_start, source_line_end)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    card["slug"],
                    card["title"],
                    card["canonical_body"],
                    json.dumps(card["tags"], ensure_ascii=False),
                    card["source_company"],
                    card["source_file"],
                    card["source_line_start"],
                    card["source_line_end"],
                ),
            )
            print(f"[INSERT] {card['slug']}")
        upserted_cards += 1

    upserted_overlays = 0
    for ov in OVERLAYS:
        row = cur.execute(
            "SELECT id FROM knowledge_cards WHERE slug=?", (ov["card_slug"],)
        ).fetchone()
        if row is None:
            print(f"[SKIP overlay] card not found: {ov['card_slug']}")
            continue
        card_id = row[0]
        company_id = COMPANY_IDS[ov["company_name"]]
        existing = cur.execute(
            """SELECT id FROM company_card_overlays
               WHERE card_id=? AND company_id=? AND angle=?""",
            (card_id, company_id, ov["angle"]),
        ).fetchone()
        if existing:
            cur.execute(
                """UPDATE company_card_overlays
                   SET overlay_body=?, source_file=?, source_line_start=?,
                       source_line_end=?
                   WHERE id=?""",
                (
                    ov["overlay_body"],
                    ov["source_file"],
                    ov["source_line_start"],
                    ov["source_line_end"],
                    existing[0],
                ),
            )
            print(f"[UPDATE overlay] {ov['card_slug']} / {ov['company_name']} / {ov['angle']}")
        else:
            cur.execute(
                """INSERT INTO company_card_overlays
                   (card_id, company_id, angle, overlay_body,
                    source_file, source_line_start, source_line_end)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    card_id,
                    company_id,
                    ov["angle"],
                    ov["overlay_body"],
                    ov["source_file"],
                    ov["source_line_start"],
                    ov["source_line_end"],
                ),
            )
            print(f"[INSERT overlay] {ov['card_slug']} / {ov['company_name']} / {ov['angle']}")
        upserted_overlays += 1

    conn.commit()
    total_cards = cur.execute("SELECT COUNT(*) FROM knowledge_cards").fetchone()[0]
    total_overlays = cur.execute("SELECT COUNT(*) FROM company_card_overlays").fetchone()[0]
    print(f"\n[SUMMARY] phase 2 upserted {upserted_cards} cards / {upserted_overlays} overlays")
    print(f"[VERIFY] table totals: cards={total_cards}, overlays={total_overlays}")
    conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_DB)
    print(f"Seeding knowledge cards phase 2: {db_path}")
    seed(db_path)
