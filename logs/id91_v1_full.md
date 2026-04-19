# Ads & Click Prediction

## Overview

**Ads & Click Prediction（广告与点击预测）**系统是收入导向型 ML 系统的典型代表。广告系统融合了 **Click-Through Rate** (CTR, 点击率)、出价优化、拍卖机制和预算调控等多个技术模块。该主题是 Meta、Google、Amazon 等拥有广告业务公司的面试必考题。理解广告系统需要同时掌握经济学原理和 ML 技术。

广告系统的核心挑战在于：如何在用户体验、广告主 **Return on Investment** (ROI, 投资回报率) 和平台收入之间取得三方平衡，同时满足毫秒级延迟和数十万 QPS 的性能要求。

## Core Concepts

### Ads Serving Pipeline

广告服务的完整流水线涵盖从请求到反馈的闭环：

```
广告请求 -> 候选筛选 -> CTR 预测 -> 出价计算
    -> 竞价排名 -> 广告展示 -> 点击/转化追踪 -> 模型更新
```

每个环节的延迟预算通常总计不超过 100ms，其中 CTR 模型推理约占 5-20ms。

### Click-Through Rate Prediction

CTR 模型预测用户在给定上下文下点击广告的概率 $P(\text{click} | \text{user, ad, context})$：

$$
\text{eCPM} = \text{CTR} \times \text{bid} \times 1000
$$

**effective Cost Per Mille** (eCPM, 有效千次展示成本) 是广告排序的核心指标。拥有最高 eCPM 的广告赢得竞价（简化模型）。这个公式同时考虑了广告的相关性（CTR 反映用户兴趣）和商业价值（bid 反映广告主的出价意愿）。

### Feature Categories

广告 CTR 模型的特征可以分为四大类，每类的更新频率不同：

| 类别 | 示例 | 更新频率 |
|------|------|---------|
| 用户特征 | 人口统计、兴趣标签、行为历史 | 小时/天级 |
| 广告特征 | 创意素材、落地页、类目 | 广告变更时 |
| 上下文特征 | 时间、设备、页面内容 | 实时 |
| 交叉特征 | 用户-广告亲和度、历史 CTR | 实时 |

实时特征（如用户近期点击行为、当前会话上下文）往往是 CTR 提升的最大来源。

### Model Architecture Evolution

CTR 模型经历了五代演进，每一代引入了新的特征交互方式：

| 代际 | 模型 | 核心创新 |
|------|------|---------|
| 第1代 | **Logistic Regression** (LR, 逻辑回归) | 稀疏特征，可解释性强 |
| 第2代 | **Gradient Boosted Decision Trees** (GBDT, 梯度提升决策树) + LR | 非线性特征交叉 |
| 第3代 | **Wide & Deep** | 记忆性 + 泛化性的统一 |
| 第4代 | **Deep & Cross Network v2** (DCN-v2, 深度交叉网络v2) / **Deep Learning Recommendation Model** (DLRM, 深度学习推荐模型) | 显式交叉网络，大规模 Embedding 表 |
| 第5代 | **Deep Interest Network** (DIN, 深度兴趣网络) / **Deep Interest Evolution Network** (DIEN, 深度兴趣演化网络) | 对用户行为序列的注意力机制 |

### Auction Mechanisms

**Second-price auction（第二价格拍卖）**（经典 GSP 模型）：

$$
\text{payment} = \frac{\text{eCPM}_{\text{2nd}}}{\text{CTR}_{\text{winner}}}
$$

广告主实际支付的 **Cost Per Click** (CPC, 每次点击成本) 等于第二高 eCPM 除以自己的 CTR。这种机制鼓励广告主如实出价。

**Vickrey-Clarke-Groves** (VCG) 拍卖：如实出价是占优策略。胜出者支付的费用等于其存在对其他参与者造成的外部性成本。VCG 拍卖保证了激励相容性，但实现复杂度较高。

近年来，许多广告平台转向 **First-price auction（第一价格拍卖）**，因为它更简单且收入更可预测，但需要广告主进行出价 shading（降低出价以避免多付）。

### Calibration

CTR 模型必须良好校准，才能正确定价：

$$
\text{Calibration} = \frac{\text{Predicted avg CTR}}{\text{Observed avg CTR}}
$$

校准比 $1.0$ 表示预测偏高，低于 $1.0$ 表示预测偏低。一个 **Area Under the Curve** (AUC, ROC曲线下面积) 很高但校准不良的模型会导致广告定价错误——高估 CTR 会导致广告主过度支付，低估 CTR 会导致平台收入损失。常用校准方法包括 **Platt Scaling（普拉特缩放）**和 **Isotonic Regression（保序回归）**。

### Budget Pacing

**Budget Pacing（预算调控）**确保广告主的预算在投放周期内均匀消耗，避免过早花完：

$$
\text{pacing\_multiplier} = \frac{\text{remaining\_budget}}{\text{ideal\_remaining\_budget}}
$$

当实际消耗超过计划时，降低出价系数来减缓投放速度；当消耗不足时，提高出价系数加速投放。

## Implementation

```python
import numpy as np

def compute_ecpm(ctr: np.ndarray, bid: np.ndarray) -> np.ndarray:
    # 计算有效千次展示成本用于广告排序
    return ctr * bid * 1000.0

def second_price_payment(
    winner_ctr: float, second_ecpm: float,
) -> float:
    # 第二价格拍卖中的每次点击成本计算
    if winner_ctr <= 0:
        return 0.0
    return second_ecpm / (winner_ctr * 1000.0)

def budget_pacing(
    remaining_budget: float, remaining_time_frac: float,
    spent_so_far: float, total_budget: float,
) -> float:
    # 预算调控乘数——平滑预算消耗
    ideal_spend = total_budget * (1.0 - remaining_time_frac)
    if ideal_spend <= 0:
        return 1.0
    return max(0.1, min(2.0, remaining_budget / ideal_spend))
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 多目标优化 | CTR + CVR + 质量 | 组合 $P(\text{click}) \times P(\text{convert}|\text{click}) \times \text{bid} \times \text{quality}$ |
| 延迟反馈 | 转化归因 | 转化事件延迟数小时/天到达；需要重要性加权 |
| 位置偏差 | 列表中的广告 | 高位置无论相关性如何都获得更多点击 |
| 探索-利用 | 新广告/创意 | 对冷启动广告使用 Thompson Sampling |
| 预算调控 | 广告活动优化 | 平滑消耗避免预算过早耗尽 |

### Common Interview Questions

- [ ] 为社交媒体广告平台设计 CTR 预测系统
- [ ] 如何处理模型训练中的延迟转化？
- [ ] 解释位置偏差及其去偏方法
- [ ] 如何设计广告活动的预算调控？
- [ ] 比较第一价格与第二价格拍卖

## Comparisons

| 维度 | 逻辑回归 | 深度 CTR (DCN-v2) | 序列模型 (DIN) |
|------|---------|-------------------|---------------|
| 训练速度 | 快 | 中等 | 慢 |
| 特征交互 | 手工交叉 | 自动学习 | 注意力机制 |
| 推理延迟 | <1ms | ~5ms | ~10ms |
| 冷启动 | 好（稀疏特征） | 中等 | 差（需要历史） |
| 可解释性 | 高 | 低 | 低 |

## Key Takeaways

- [ ] eCPM = CTR x Bid 是广告排序的基本公式
- [ ] 校准与区分度（AUC）同等重要
- [ ] 位置偏差校正对无偏训练至关重要
- [ ] 实时特征（近期点击、会话上下文）贡献最大增益
- [ ] 预算调控和拍卖设计与 ML 模型同等重要

## Advanced Topics

### Attribution Modeling

**Attribution（归因）**是广告系统的关键问题：用户在多个广告触点之间转化时，如何将转化价值分配给各个触点？

| 归因模型 | 原理 | 优缺点 |
|----------|------|--------|
| **Last-click（末次点击）** | 全部归因于最后一次点击 | 简单但忽略上游触点的贡献 |
| **First-click（首次点击）** | 全部归因于首次点击 | 简单但忽略下游触点的转化作用 |
| **Linear（线性归因）** | 均匀分配给所有触点 | 公平但不区分触点重要性 |
| **Data-driven（数据驱动）** | 基于 Shapley Value 或 ML 模型 | 最准确但计算复杂 |

### Creative Optimization

**Creative Optimization（广告创意优化）**使用 ML 自动选择最优的广告素材组合：标题、图片、CTA 按钮等元素通过 **Multi-Armed Bandit（多臂老虎机）**策略动态分配流量，快速找到 CTR 最高的创意版本。大规模创意优化需要处理组合探索问题，因为元素组合数呈指数增长。

### Privacy-Preserving Ads

随着隐私法规（**General Data Protection Regulation** (GDPR, 通用数据保护条例)、**California Consumer Privacy Act** (CCPA, 加州消费者隐私法)）和浏览器限制（第三方 Cookie 消亡），广告系统面临重大转型。**Privacy Sandbox** 等新技术通过 **Federated Learning（联邦学习）**和 **Differential Privacy（差分隐私）**在保护用户隐私的同时维持广告效果。**On-device Learning（端上学习）**在用户设备上进行个性化推理，避免个人数据传输到服务器，是隐私保护广告的重要方向。

### Real-time Bidding Pipeline

实时竞价管道的延迟预算通常仅有 50-100ms，需要在此时间内完成特征提取、CTR/CVR 预估、出价计算和预算校验。系统设计需要高度优化的推理服务（模型量化、特征缓存）和分层降级策略（当某个模型超时时回退到简单模型或历史统计值）。广告系统的可靠性直接关系到收入，因此需要完善的容灾和降级机制。