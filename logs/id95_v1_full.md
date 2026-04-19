# Fraud & Trust Safety

## Overview

**Fraud & Trust Safety** (欺诈检测与信任安全) 系统保护平台免受各类滥用：支付欺诈、虚假账户、垃圾信息、诈骗和违规行为。这些系统面临极端的 **Class Imbalance** (类别不平衡)、对抗性攻击者和严格的延迟要求。常见于金融科技公司（Stripe、PayPal）、交易平台（Amazon、eBay）和社交平台（Meta、Twitter）。

欺诈检测的独特挑战在于：攻击者会主动适应和规避检测系统，形成持续的攻防博弈。此外，标签延迟（拒付可能在 30-90 天后才确认）和极低的欺诈率（通常 0.1-1%）使得模型训练和评估尤为困难。

## Core Concepts

### Fraud Detection Pipeline

欺诈检测的完整流水线是一个从实时决策到反馈闭环的系统：

```
事件（交易/操作）
    |
    v
[Real-time Rules Engine（实时规则引擎）] -- 硬性拦截（速率限制、黑名单）
    |
    v
[ML Risk Scoring（ML 风险评分）] -- 在 <50ms 内计算 P(fraud)
    |
    v
[Decision Engine（决策引擎）] -- 通过 / 人工审核 / 拦截
    |
    v
[Human Review Queue（人工审核队列）] -- 处理临界案例
    |
    v
[Feedback Loop（反馈闭环）] -- 标签回流用于模型重训练
```

规则引擎和 ML 模型的组合是工业标准：规则引擎处理已知模式（速度快、可解释），ML 模型处理新型攻击（自适应、泛化能力强）。

### Feature Engineering for Fraud

**特征工程** 是欺诈检测中最关键的环节，好的特征往往比模型选择更重要：

| 特征类型 | 示例 | 计算方式 |
|---------|------|---------|
| **Velocity Features** (速率特征) | 过去 1h/24h/7d 的交易次数 | 滑动窗口计数器 |
| **Graph Features** (图特征) | 设备共享、IP 聚类 | 连通分量分析 |
| **Behavioral Features** (行为特征) | 打字速度、浏览模式 | 会话分析 |
| **Historical Features** (历史特征) | 过往拒付记录、账户年龄 | 查找表 |
| **Network Features** (网络特征) | 共享支付方式、地址 | 图特征 |

图特征是最强大的欺诈信号——欺诈团伙通常共享设备指纹、IP 地址或支付方式。**Device Fingerprinting** (设备指纹) 通过收集浏览器特征、屏幕分辨率、字体列表等信息唯一标识设备。

### Class Imbalance Handling

欺诈率通常为 0.1-1%。直接使用标准分类方法会导致模型倾向于全部预测为非欺诈。处理策略：

$$
\mathcal{L}_{\text{weighted}} = -\sum [w_+ \cdot y \log \hat{y} + w_- \cdot (1-y) \log(1-\hat{y})]
$$

其中 $w_+$ 和 $w_-$ 分别是正类和负类的权重，通过增大正类权重来弥补数量劣势。

| 策略 | 适用场景 |
|------|---------|
| 类别权重 ($w_+ = 100$) | 始终是好的基线方法 |
| **SMOTE** (**Synthetic Minority Over-sampling Technique**, 合成少数类过采样) / 过采样 | 表格数据、小数据集 |
| **Focal Loss** (聚焦损失): $\alpha(1-p_t)^\gamma \text{CE}$ | 深度模型、困难样本挖掘。$\gamma$ 越大越聚焦于困难样本 |
| **Anomaly Detection** (异常检测) | 无监督方法，检测新型欺诈 |
| **Isolation Forest** (隔离森林) 集成 | 与监督模型互补 |

### Evaluation Metrics

标准准确率在极度不平衡时无意义（99.9% 准确率可能只是全部预测为非欺诈）。应使用：

$$
\text{Precision@k} = \frac{\text{top-k 预测中的真实欺诈数}}{k}
$$

关键指标：**PR-AUC** (**Precision-Recall AUC**, 精度-召回率曲线下面积)、操作点处的 **F1 Score**、给定 **TPR** (**True Positive Rate**, 真正率) 下的 **FPR** (**False Positive Rate**, 假正率)、以及业务指标（挽回的损失金额 / 误拦截造成的损失）。

### Adversarial Considerations

欺诈者会持续适应检测系统，关键防御策略：
- **Feature Velocity Monitoring** (特征速率监控)：检测特征分布漂移，识别攻击模式变化
- **Model Versioning** (模型版本管理)：A/B 测试新模型与当前模型
- **Ensemble Diversity** (集成多样性)：多种模型类型（树模型、神经网络、图模型）抵抗同一攻击向量
- **Delayed Labels** (延迟标签)：拒付延迟 30-90 天到达，需要半监督学习处理近期无标签数据

## Implementation

```python
import numpy as np
from collections import defaultdict

class VelocityCounter:
    # 滑动窗口事件计数器用于欺诈特征

    def __init__(self, window_seconds: int = 3600) -> None:
        self.window = window_seconds
        self.events: dict[str, list[float]] = defaultdict(list)

    def add_event(self, key: str, timestamp: float) -> None:
        self.events[key].append(timestamp)

    def count(self, key: str, current_time: float) -> int:
        cutoff = current_time - self.window
        times = self.events.get(key, [])
        valid = [t for t in times if t > cutoff]
        self.events[key] = valid
        return len(valid)

def fraud_risk_score(
    features: np.ndarray, model, rules_blocked: bool,
) -> tuple[float, str]:
    # 规则 + ML 混合风险评分
    if rules_blocked:
        return 1.0, "BLOCK"
    score = float(model.predict_proba(features.reshape(1, -1))[0, 1])
    if score > 0.9:
        return score, "BLOCK"
    if score > 0.5:
        return score, "REVIEW"
    return score, "APPROVE"
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 规则 + ML 混合 | 任何欺诈系统 | 规则捕获已知模式；ML 捕获新型模式 |
| 基于图的检测 | 账户网络 | 欺诈团伙共享设备/IP/支付方式 |
| 流式特征 | 实时决策 | Flink/Kafka 实现速率计数器 |
| **HITL** (**Human-in-the-Loop**, 人机协同) | 高价值决策 | ML 做分流，人工决定临界案例 |
| 反馈延迟 | 标签延迟 | 用已确认标签训练，用半监督方法处理近期数据 |

### Common Interview Questions
- [ ] 设计实时支付欺诈检测系统
- [ ] 如何处理拒付的 30-90 天标签延迟？
- [ ] 设计社交平台的虚假账户检测系统
- [ ] 标签噪声下如何评估欺诈模型？
- [ ] 如何检测协调虚假行为（欺诈团伙）？

## Comparisons

| 维度 | 规则引擎 | 监督 ML | **GNN** (**Graph Neural Network**, 图神经网络) |
|------|---------|---------|-----|
| 延迟 | <1ms | 5-20ms | 50-200ms |
| 适应性 | 手动更新 | 重训练 | 重训练 |
| 新型欺诈 | 差 | 中等 | 好（结构性特征） |
| 可解释性 | 高 | 中等（SHAP） | 低 |
| 冷启动 | 立即可用 | 需要标签 | 需要图结构 |

## Key Takeaways
- [ ] 始终组合规则（快速、可解释）和 ML（自适应、泛化能力强）
- [ ] 类别不平衡要求谨慎选择评估指标（用 PR-AUC，不是准确率）
- [ ] 图特征（设备/IP/支付方式共享）是最强大的欺诈信号
- [ ] 为对抗性适应设计系统——欺诈者会持续探测和演化
- [ ] 反馈闭环和标签质量是最大的长期挑战


## Advanced Topics

### Explainability in Fraud Detection

反欺诈系统需要 **Explainability** (可解释性)，因为误杀正常用户会直接影响用户体验和客户关系。常用解释方法包括：**SHAP** (**SHapley Additive exPlanations**, Shapley 加性解释) 计算每个特征对预测的边际贡献；基于规则的解释将 ML 分数转化为人类可读的风险因素；**Counterfactual Explanation** (反事实解释) 告诉用户"如果XX条件不满足，交易就会通过"。

### Adaptive Risk Thresholds

反欺诈系统的风险阈值不应静态，而应根据业务场景动态调整。高价值交易需要更严格的阈值（误杀成本低于放行欺诈的损失），小额交易可以放宽以减少用户摩擦。**Risk-Based Authentication** (基于风险的认证) 根据风险分数决定认证强度：低风险直接放行，中风险要求短信验证码，高风险要求人脸识别或人工审核。

### Anti-Money Laundering

**AML** (**Anti-Money Laundering**, 反洗钱) 是金融欺诈检测的重要分支。洗钱者通过多层账户间的小额转账模糊资金来源。**Graph-Based Analysis** (基于图的分析) 特别适合检测这类模式：将账户构建为节点、转账为边的有向图，通过社区发现和异常子图检测识别可疑的资金流动网络。