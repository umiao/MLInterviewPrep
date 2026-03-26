# Evaluation Metrics for Classification

## Overview

Evaluation metrics quantify how well a classification model performs. Accuracy alone is misleading for imbalanced datasets -- metrics like precision, recall, F1-score, and ROC-AUC reveal different aspects of model quality. Choosing the right metric depends on the business cost of false positives vs false negatives, making this a critical MLE interview topic.

## Core Concepts

### Confusion Matrix

For binary classification, predictions fall into four categories:

|  | Predicted Positive | Predicted Negative |
|--|-------------------|--------------------|
| **Actual Positive** | TP (True Positive) | FN (False Negative) |
| **Actual Negative** | FP (False Positive) | TN (True Negative) |

- **TP + FP** = all samples predicted positive
- **TP + FN** = all samples that are actually positive
- **TP + FP + TN + FN** = total samples $m$

### Accuracy and Error Rate

$$
\text{Accuracy} = \frac{TP + TN}{m} = 1 - E(f;D)
$$

$$
E(f;D) = \frac{1}{m}\sum_{i=1}^{m} \mathbb{I}(f(x_i) \ne y_i)
$$

**Why accuracy is misleading:** With 99% negative samples, a model that always predicts "negative" achieves 99% accuracy but detects zero positives. Accuracy masks poor performance on the minority class.

### Precision

$$
P = \frac{TP}{TP + FP}
$$

"Of all samples I predicted positive, how many are actually positive?"

- High precision = model is **cautious** about positive predictions
- Optimize for precision when **false positives are costly** (spam filter: don't lose legitimate email)

### Recall (Sensitivity / True Positive Rate)

$$
R = \frac{TP}{TP + FN}
$$

"Of all actually positive samples, how many did I find?"

- High recall = model **aggressively** predicts positive
- Optimize for recall when **false negatives are costly** (cancer screening: don't miss a case)

### Precision-Recall Tradeoff

Pursuing high precision and high recall simultaneously is **contradictory**:
- Raising the classification threshold increases precision but decreases recall (model becomes more cautious, misses more positives)
- Lowering the threshold increases recall but decreases precision (model predicts more positives, including false ones)

### F1-Score

The harmonic mean of precision and recall:

$$
F1 = \frac{2PR}{P + R} = \frac{2}{\frac{1}{P} + \frac{1}{R}}
$$

**Why harmonic mean (not arithmetic)?** The harmonic mean penalizes extreme imbalance between P and R. If $P=1.0$ and $R=0.01$: arithmetic mean = 0.505 (looks OK), harmonic mean = 0.02 (correctly reflects poor recall).

### Macro-F1 vs Micro-F1

For multi-class classification with $N$ classes:

**Macro-F1:**
1. Compute $F1_i$ for each class $i$ independently (one-vs-rest confusion matrix)
2. Average: $\text{Macro-F1} = \frac{1}{N}\sum_{i=1}^{N} F1_i$

- Treats **all classes equally** regardless of size
- Use when each class matters equally (e.g., multi-disease diagnosis)

**Micro-F1:**
1. Pool all TP, FP, FN across classes: $\overline{TP} = \sum TP_i$, etc.
2. Compute F1 from pooled counts: $\text{Micro-F1} = F1(\overline{TP}, \overline{FP}, \overline{FN})$

- **Weights by class frequency** (larger classes dominate)
- Use when overall correctness matters more than per-class balance
- For binary classification, Micro-F1 = accuracy

### PR Curve and Break-Even Point

Construction:
1. Sort all samples by predicted probability of being positive (descending)
2. Move the threshold from high to low, computing (Precision, Recall) at each step
3. Plot Precision (y-axis) vs Recall (x-axis)

- Starts near $(0, 1)$: threshold is high, few positives predicted, precision is high
- Ends near $(1, \text{base rate})$: threshold is low, all predicted positive

**Break-Even Point (BEP):** The point where $P = R$ (intersection of PR curve with line $y = x$). Higher BEP = better model. Simpler than computing area under PR curve.

### ROC Curve and AUC

**ROC Curve** plots:

$$
TPR = \frac{TP}{TP + FN} \quad \text{(y-axis)} \quad \text{vs} \quad FPR = \frac{FP}{FP + TN} \quad \text{(x-axis)}
$$

Construction:
1. Sort samples by predicted positive probability (descending)
2. Start at $(0, 0)$: threshold = $+\infty$, nothing predicted positive
3. Lower threshold progressively; both TPR and FPR increase
4. End at $(1, 1)$: threshold = $-\infty$, everything predicted positive

**AUC (Area Under ROC Curve):**
- Random classifier: AUC = 0.5 (diagonal line $y = x$)
- Perfect classifier: AUC = 1.0
- AUC = 0.7 means "70% chance a randomly chosen positive sample is ranked higher than a randomly chosen negative sample"
- AUC is **threshold-independent** -- summarizes performance across all thresholds

**Ranking Loss:** For each positive-negative pair, if the positive has lower score, add 1 to loss (add 0.5 if equal). $AUC = 1 - L_{\text{rank}}$.

### Cost Curves (Advanced)

When different misclassification types have different business costs:
- Assign weight $w$ to false positives and $(1-w)$ to false negatives
- For each operating point on the ROC curve, draw a line from $(0, FPR)$ to $(1, FNR)$
- The lower envelope of all such lines gives the **expected cost curve**
- Area under this curve = total expected cost of the classifier
- Useful for choosing classifiers under asymmetric cost constraints

## Implementation

```python
import numpy as np
from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score, f1_score,
    roc_curve, roc_auc_score, precision_recall_curve, classification_report
)
import matplotlib.pyplot as plt

# Confusion matrix and basic metrics
y_true = np.array([1, 1, 1, 0, 0, 0, 1, 0, 1, 0])
y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 0, 0])

cm = confusion_matrix(y_true, y_pred)
# [[4, 1],   -> TN=4, FP=1
#  [2, 3]]   -> FN=2, TP=3

precision = precision_score(y_true, y_pred)  # 3/(3+1) = 0.75
recall = recall_score(y_true, y_pred)        # 3/(3+2) = 0.60
f1 = f1_score(y_true, y_pred)               # 2*0.75*0.60/(0.75+0.60) = 0.667

# Macro vs Micro F1 for multi-class
f1_macro = f1_score(y_true, y_pred, average='macro')
f1_micro = f1_score(y_true, y_pred, average='micro')

# ROC curve and AUC (requires probability scores)
y_scores = np.array([0.9, 0.4, 0.8, 0.3, 0.1, 0.7, 0.85, 0.2, 0.55, 0.15])
fpr, tpr, thresholds = roc_curve(y_true, y_scores)
auc = roc_auc_score(y_true, y_scores)

# PR curve
precision_vals, recall_vals, _ = precision_recall_curve(y_true, y_scores)

# Plot ROC
plt.plot(fpr, tpr, label=f'AUC = {auc:.2f}')
plt.plot([0, 1], [0, 1], 'k--', label='Random (AUC=0.5)')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Accuracy paradox | "Model has 99% accuracy but is bad" | Imbalanced data: model predicts majority class; use precision/recall/F1 instead |
| Precision vs recall tradeoff | "When optimize for which?" | FP costly -> precision (spam filter); FN costly -> recall (cancer screening) |
| F1 as harmonic mean | "Why not arithmetic mean?" | Harmonic mean penalizes extreme imbalance: P=1, R=0.01 gives F1=0.02 not 0.505 |
| Macro vs Micro F1 | "Multi-class evaluation" | Macro = equal class weight (rare classes matter); Micro = frequency-weighted (overall accuracy) |
| ROC-AUC interpretation | "What does AUC=0.7 mean?" | 70% probability a random positive ranks above a random negative; threshold-independent |
| PR curve vs ROC | "Which curve to use?" | PR curve more informative for highly imbalanced data (ROC can look optimistic) |
| Threshold selection | "How to choose threshold?" | Depends on business cost; PR BEP for balanced P/R; cost curves for asymmetric costs |

### Common Interview Questions

- [ ] Your classifier has 99% accuracy but is terrible. Why? How to fix?
- [ ] When do you optimize for precision vs recall? Give real-world examples.
- [ ] Explain ROC-AUC. What does AUC=0.7 mean intuitively?
- [ ] Macro vs Micro F1: when to use which?
- [ ] How do you evaluate a model on imbalanced data?
- [ ] Why is F1 the harmonic mean and not the arithmetic mean?
- [ ] What is the break-even point on a PR curve?

## Comparisons

| Aspect | Precision | Recall |
|--------|-----------|--------|
| Formula | $TP/(TP+FP)$ | $TP/(TP+FN)$ |
| Denominator | All predicted positive | All actually positive |
| Optimize when | FP is costly | FN is costly |
| Example | Spam filter (don't lose email) | Cancer screening (don't miss cases) |
| Raising threshold | Increases | Decreases |

| Aspect | ROC-AUC | PR-AUC |
|--------|---------|--------|
| Axes | TPR vs FPR | Precision vs Recall |
| Random baseline | 0.5 (diagonal) | Proportion of positives |
| Imbalanced data | Can be overly optimistic | More informative |
| Threshold-free | Yes | Yes |
| Best for | Balanced datasets, general comparison | Imbalanced datasets, positive class focus |

| Aspect | Macro-F1 | Micro-F1 |
|--------|----------|----------|
| Computation | Average F1 per class | F1 from pooled TP/FP/FN |
| Class weighting | Equal (each class = 1/N) | By frequency (larger classes dominate) |
| Use when | All classes equally important | Overall correctness matters most |
| Sensitive to | Rare class performance | Majority class performance |
| Binary case | Standard F1 | = Accuracy |

## Key Takeaways

- [ ] Accuracy is misleading for imbalanced data -- always check precision, recall, and F1
- [ ] Precision = "how many predicted positives are correct"; Recall = "how many actual positives were found"
- [ ] F1 = harmonic mean of P and R, penalizes extreme imbalance between them
- [ ] Macro-F1 treats all classes equally; Micro-F1 weights by class frequency
- [ ] ROC-AUC is threshold-independent; AUC = probability a random positive ranks above a random negative
- [ ] PR curves are more informative than ROC curves for highly imbalanced datasets
- [ ] Optimize precision when FP is costly (spam); optimize recall when FN is costly (cancer)
- [ ] Cost curves generalize to asymmetric misclassification costs
