# Evaluation Metrics（评估指标）

## Overview

选择正确的评估指标与选择模型同样重要。指标应与业务目标对齐。面试中频繁考察指标之间的权衡、阈值选择以及不平衡数据集下的指标选择。理解每个指标的数学定义、适用场景和局限性是MLE面试的核心能力。

## Core Concepts

### Classification Metrics（分类指标）

#### Confusion Matrix（混淆矩阵）

|  | 预测为正 | 预测为负 |
|--|---------|---------|
| 实际为正 | **TP（True Positive，真正例）** | **FN（False Negative，假负例/漏报）** |
| 实际为负 | **FP（False Positive，假正例/误报）** | **TN（True Negative，真负例）** |

#### Core Metrics（核心指标）

**Precision（精确率）**——预测为正的样本中，真正为正的比例：

$$\text{Precision} = \frac{TP}{TP + FP}$$

高Precision意味着很少误报。适用场景：垃圾邮件过滤（用户不希望正常邮件被误判为垃圾邮件）。

**Recall / Sensitivity（召回率/灵敏度）**——实际为正的样本中，被正确识别的比例：

$$\text{Recall} = \frac{TP}{TP + FN}$$

高Recall意味着很少漏报。适用场景：疾病筛查（不希望遗漏真正的患者）。

**Specificity（特异度）**：

$$\text{Specificity} = \frac{TN}{TN + FP} = 1 - \text{FPR}$$

**F1 Score**——Precision和Recall的调和平均：

$$\text{F1} = \frac{2 \cdot P \cdot R}{P + R} = \frac{2 \cdot TP}{2 \cdot TP + FP + FN}$$

调和平均对较小值更敏感——当P和R差距很大时，F1会更接近较小的那个。

**F-beta Score**——P和R的加权调和平均：

$$F_\beta = \frac{(1+\beta^2) \cdot P \cdot R}{\beta^2 \cdot P + R}$$

- $\beta = 1$：F1，P和R同等重要
- $\beta = 2$：F2，Recall权重更大（宁可误报也不漏报）
- $\beta = 0.5$：F0.5，Precision权重更大（宁可漏报也不误报）

**Accuracy（准确率）**：

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

在不平衡数据集上有严重误导性：如果99%的样本为负类，全部预测为负的"模型"也有99%准确率。

#### AUC-ROC（ROC曲线下面积）

**ROC Curve（ROC曲线，Receiver Operating Characteristic）** 绘制的是在不同分类阈值下 **TPR（True Positive Rate，真正例率）** vs **FPR（False Positive Rate，假正例率）** 的曲线。

$$\text{TPR} = \frac{TP}{TP+FN}, \quad \text{FPR} = \frac{FP}{FP+TN}$$

**AUC（Area Under the Curve，曲线下面积）** 的概率解释：随机选取一个正样本和一个负样本，模型给正样本的分数高于负样本的概率。

$$\text{AUC} = P(\hat{y}_{pos} > \hat{y}_{neg})$$

| AUC值 | 含义 |
|-------|------|
| 1.0 | 完美分类器 |
| 0.5 | 随机猜测（无区分能力） |
| < 0.5 | 比随机差（标签可能反了） |

**AUC-ROC的优缺点**：
- 优点：阈值无关，适合比较不同模型
- 缺点：在严重不平衡数据上可能过于乐观（大量TN导致FPR看起来很低）

#### AUC-PR（PR曲线下面积）

**PR Curve（Precision-Recall曲线）** 绘制Precision vs Recall在不同阈值下的关系。

**为什么AUC-PR在不平衡数据上更好？** PR曲线不使用TN，因此不会被大量负样本"稀释"。当正类非常稀少时（如欺诈检测0.1%正类），PR曲线能更真实地反映模型性能。

**比较规则**：
- 正负样本比例接近：AUC-ROC和AUC-PR都可以
- 严重不平衡（正类 < 5%）：优先使用AUC-PR
- 基线参考：随机分类器的AUC-PR $\approx$ 正类比例

#### Log Loss（对数损失）

度量概率校准质量：

$$\text{LogLoss} = -\frac{1}{n}\sum_i [y_i \log p_i + (1-y_i)\log(1-p_i)]$$

不仅关注排序（是否能区分正负样本），还关注概率的绝对准确性。适用于需要将概率直接用于下游决策的场景（如广告竞价系统）。

#### ECE（Expected Calibration Error，期望校准误差）

$$\text{ECE} = \sum_{b=1}^{B}\frac{n_b}{n}|\text{acc}(b) - \text{conf}(b)|$$

将预测概率分成 $B$ 个区间（bin），计算每个区间内实际准确率和平均预测概率的差异的加权平均。ECE越小说明概率校准越好。

**Reliability Diagram（可靠性图）**：将 $\text{acc}(b)$ vs $\text{conf}(b)$ 画在图上，完美校准的模型应该落在对角线上。

**校准方法**：
- **Platt Scaling（Platt缩放）**：用逻辑回归拟合 $P(y=1|f(x))$
- **Isotonic Regression（保序回归）**：非参数方法，数据量大时更灵活
- **Temperature Scaling（温度缩放）**：$p = \text{softmax}(z/T)$，对深度学习模型最常用

### Regression Metrics（回归指标）

$$\text{MSE} = \frac{1}{n}\sum(y_i - \hat{y}_i)^2, \quad \text{RMSE} = \sqrt{\text{MSE}}$$

RMSE与目标变量同单位，更易解释。

$$\text{MAE} = \frac{1}{n}\sum|y_i - \hat{y}_i|$$

对异常值更鲁棒，度量的是误差的中位数方向。

$$R^2 = 1 - \frac{\sum(y_i-\hat{y}_i)^2}{\sum(y_i-\bar{y})^2} = 1 - \frac{SS_{res}}{SS_{tot}}$$

$R^2$ 度量模型解释了多少目标变量的方差。$R^2 = 1$ 完美拟合；$R^2 = 0$ 等同于预测均值；$R^2 < 0$ 比预测均值还差。

**Adjusted $R^2$（调整 $R^2$）**：惩罚特征数量增加：

$$R^2_{adj} = 1 - \frac{(1-R^2)(n-1)}{n-p-1}$$

**MAPE（Mean Absolute Percentage Error，平均绝对百分比误差）**：

$$\text{MAPE} = \frac{1}{n}\sum\frac{|y_i - \hat{y}_i|}{|y_i|} \times 100\%$$

可解释为百分比误差，但当 $y_i = 0$ 或接近零时无定义。替代方案：**sMAPE（Symmetric MAPE，对称MAPE）** 或 **WAPE（Weighted APE，加权绝对百分比误差）**。

### Ranking Metrics（排序指标）

#### NDCG（Normalized Discounted Cumulative Gain，归一化折损累计增益）

$$\text{NDCG@k} = \frac{DCG@k}{IDCG@k}$$

其中：

$$DCG@k = \sum_{i=1}^{k}\frac{2^{rel_i}-1}{\log_2(i+1)}$$

$IDCG@k$ 是理想排序下的DCG（以最佳顺序排列的结果）。

**NDCG的关键特点**：
- 位置敏感：排在前面的相关结果贡献更大（对数折损）
- 支持分级相关性（不只是0/1，可以是0-5的评分）
- 归一化到 $[0, 1]$，便于比较不同查询

#### MAP@K（Mean Average Precision at K，K处平均精度均值）

$$\text{AP@K} = \frac{1}{\min(m, K)}\sum_{k=1}^{K}P(k) \cdot \text{rel}(k)$$

$$\text{MAP@K} = \frac{1}{|Q|}\sum_{q=1}^{|Q|}\text{AP@K}(q)$$

其中 $P(k)$ 是前 $k$ 个结果的Precision，$\text{rel}(k)$ 表示第 $k$ 个结果是否相关，$m$ 是相关文档总数。

#### MRR（Mean Reciprocal Rank，平均倒数排名）

$$\text{MRR} = \frac{1}{|Q|}\sum_{q=1}^{|Q|}\frac{1}{\text{rank}_q}$$

只关注第一个正确结果的排名。适用于只需要一个正确答案的场景（如问答系统）。

#### Hit Rate@K（命中率）

$$\text{Hit Rate@K} = \frac{|\{q : \text{top-K results contain a relevant item}\}|}{|Q|}$$

简单直观，常用于推荐系统评估。

### Ranking Metrics Comparison（排序指标对比）

| 指标 | 位置敏感 | 分级相关性 | 适用场景 |
|------|---------|-----------|---------|
| NDCG@K | 是（对数折损） | 是 | 搜索排序、推荐系统 |
| MAP@K | 是（线性） | 否（二元） | 多个相关结果 |
| MRR | 只看第一个 | 否 | 第一个结果最重要（问答） |
| Hit Rate@K | 否 | 否 | 推荐系统top-K |

### Offline vs Online Metrics（线下与线上指标）

| 线下指标 | 线上指标 | 说明 |
|---------|---------|------|
| AUC-ROC | **CTR（Click-Through Rate，点击率）** | 线下高AUC不一定线上CTR高 |
| NDCG | 用户停留时间 | 排序质量 vs 用户体验 |
| F1 | **Conversion Rate（转化率）** | 分类质量 vs 业务价值 |
| LogLoss | **Revenue（收入）** | 概率校准 vs 最终收益 |

线下指标是线上指标的代理——它们可能不一致。例如：AUC提高但CTR下降（模型学会了区分但排序不对），NDCG提高但用户满意度下降（相关性定义与用户需求不匹配）。

## Implementation

```python
from sklearn.metrics import (
    precision_recall_curve, roc_auc_score, average_precision_score,
    f1_score, log_loss, ndcg_score, mean_squared_error
)
import numpy as np

# AUC-ROC and AUC-PR
auc_roc = roc_auc_score(y_true, y_prob)
auc_pr = average_precision_score(y_true, y_prob)

# F1 with optimal threshold
precisions, recalls, thresholds = precision_recall_curve(y_true, y_prob)
f1_scores = 2 * precisions * recalls / (precisions + recalls + 1e-8)
best_threshold = thresholds[np.argmax(f1_scores)]

# NDCG
from sklearn.metrics import ndcg_score
ndcg = ndcg_score([y_true_relevance], [y_pred_scores], k=10)

# ECE (Expected Calibration Error)
def expected_calibration_error(y_true, y_prob, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob < bins[i+1])
        if mask.sum() == 0:
            continue
        acc = y_true[mask].mean()
        conf = y_prob[mask].mean()
        ece += mask.sum() / len(y_true) * abs(acc - conf)
    return ece
```

## Interview Patterns

| 模式 | 适用场景 | 关键洞察 |
|------|---------|---------|
| Precision vs Recall权衡 | 不平衡分类 | 垃圾邮件：优化Precision；疾病检测：优化Recall |
| AUC-ROC vs AUC-PR | 严重不平衡 | AUC-ROC可能被大量TN误导；AUC-PR更真实 |
| 线下 vs 线上指标 | 系统设计 | 线下：AUC, NDCG。线上：CTR, 转化率, 收入 |
| 阈值选择 | "如何设阈值？" | 业务成本矩阵：最小化期望成本 |
| 排序指标选择 | 搜索/推荐 | NDCG支持分级相关性；MAP要求二元相关性 |
| 校准重要性 | 概率用于下游 | 竞价系统需要校准良好的概率 |

### Common Interview Questions

- **为什么准确率对不平衡数据有误导性？** 99%负类时全预测负的"模型"也有99%准确率
- **直觉解释AUC-ROC？AUC=0.5意味着什么？** 随机正样本排在随机负样本前面的概率；0.5=随机猜测
- **何时用F2而非F1？** Recall更重要时（如疾病筛查——漏诊代价高）
- **线下和线上指标何时不一致？举例？** AUC提升但CTR下降——模型学会区分但排序策略不对
- **生产中如何选择分类阈值？** 构建成本矩阵 $C_{FP}, C_{FN}$，选择使期望成本最小的阈值
- **NDCG和MAP的区别？** NDCG支持分级相关性（0-5分），MAP只支持二元相关性
- **什么是概率校准，为什么重要？** 预测概率0.8的样本中应有80%为正——竞价、风控等场景需要

## Key Takeaways

- 始终选择与业务目标对齐的指标，而非仅关注模型质量
- 不平衡数据：使用AUC-PR、F1或加权指标，不要用Accuracy
- 排序场景：NDCG是位置敏感且支持分级相关性的首选
- 校准在概率被下游使用时至关重要（如竞价系统、风控系统）
- 线上指标（CTR、收入）是最终真相；线下指标是它们的代理
- ECE和可靠性图是评估概率校准质量的标准工具
- 面试核心：能根据业务场景选择合适的指标，并解释为什么
