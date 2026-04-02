"""Fix: Apply follow-up sections that failed in the first enrichment pass.

Sections 2 (LR), 3 (GD), and 6 (RF) follow-ups didn't apply because
upstream acronym replacements changed the target text.

Task: T-P0-265
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def get_content(conn: sqlite3.Connection) -> str:
    """Read doc#24 content."""
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id=24")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#24 not found")
        sys.exit(1)
    return row[0]


def fix(content: str) -> str:
    """Apply the 3 missing follow-up sections."""

    # Section 2: Logistic Regression follow-ups
    # The CE replacement changed "(Multinomial" to "= Multinomial"
    content = content.replace(
        "- Follow-up: \u591a\u5206\u7c7b\u600e\u4e48\u529e\uff1f\u2192 Softmax + Categorical **CE (Cross-Entropy\uff0c\u4ea4\u53c9\u71b5)** = Multinomial Logistic Regression\n\n---\n\n## 3. Gradient Descent",
        """- Follow-up: \u591a\u5206\u7c7b\u600e\u4e48\u529e\uff1f\u2192 Softmax + Categorical **CE (Cross-Entropy\uff0c\u4ea4\u53c9\u71b5)** = Multinomial Logistic Regression

### Follow-up \u95ee\u9898\u8be6\u89e3

**Q: Logistic Regression \u7684\u51b3\u7b56\u8fb9\u754c\u662f\u4ec0\u4e48\u5f62\u72b6\uff1f**

\u7ebf\u6027\u7684\u3002$w^Tx + b = 0$ \u5b9a\u4e49\u4e86\u4e00\u4e2a\u8d85\u5e73\u9762\uff0c\u5c06\u7279\u5f81\u7a7a\u95f4\u5206\u4e3a\u4e24\u534a\u3002\u8fd9\u5c31\u662f\u4e3a\u4ec0\u4e48 Logistic Regression \u662f\u7ebf\u6027\u5206\u7c7b\u5668 \u2014 \u5b83\u53ea\u80fd\u5904\u7406\u7ebf\u6027\u53ef\u5206\u7684\u6570\u636e\u3002\u5bf9\u4e8e\u975e\u7ebf\u6027\u53ef\u5206\u7684\u6570\u636e\uff0c\u53ef\u4ee5\uff1a
- \u6dfb\u52a0\u591a\u9879\u5f0f\u7279\u5f81 (polynomial features)
- \u4f7f\u7528 kernel trick (\u7c7b\u4f3c SVM)
- \u6362\u7528\u66f4\u590d\u6742\u7684\u6a21\u578b (Neural Network, Tree-based)

**Q: Logistic Regression \u600e\u4e48\u5904\u7406\u591a\u5206\u7c7b\uff1f**

```python
import numpy as np

def softmax(z: np.ndarray) -> np.ndarray:
    \"\"\"Softmax: \u591a\u5206\u7c7b\u8f93\u51fa\u5c42\uff0c\u5c06logits\u8f6c\u4e3a\u6982\u7387\u5206\u5e03\u3002

    \u6570\u503c\u7a33\u5b9a\u7248\u672c\uff1a\u51cf\u53bb\u6700\u5927\u503c\u9632\u6b62 exp overflow\u3002
    \"\"\"
    z_shifted = z - np.max(z, axis=-1, keepdims=True)
    exp_z = np.exp(z_shifted)
    return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

def categorical_cross_entropy(
    y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-15
) -> float:
    \"\"\"\u591a\u5206\u7c7b\u4ea4\u53c9\u71b5\u635f\u5931\u3002

    Args:
        y_true: one-hot \u7f16\u7801\u7684\u771f\u5b9e\u6807\u7b7e (N, C)
        y_pred: softmax \u8f93\u51fa\u7684\u6982\u7387 (N, C)
    \"\"\"
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(np.sum(y_true * np.log(y_pred), axis=-1))

# \u793a\u4f8b: 3\u5206\u7c7b
logits = np.array([[2.0, 1.0, 0.1], [0.5, 2.5, 0.3]])
probs = softmax(logits)
print(f"Softmax probs: {np.round(probs, 3)}")
# \u6bcf\u884c\u548c\u4e3a1
print(f"Row sums: {np.round(probs.sum(axis=1), 3)}")
```

**Q: Logistic Regression \u548c SVM (Support Vector Machine\uff0c\u652f\u6301\u5411\u91cf\u673a) \u6709\u4ec0\u4e48\u533a\u522b\uff1f**

| | Logistic Regression | SVM |
|---|---|---|
| \u8f93\u51fa | \u6982\u7387 $p \\in (0,1)$ | \u5206\u7c7b\u6807\u7b7e (\u8ddd\u79bb\u8d85\u5e73\u9762\u7684margin) |
| \u635f\u5931\u51fd\u6570 | Log loss (BCE) | Hinge loss: $\\max(0, 1-y\\cdot f(x))$ |
| \u5bf9 outlier | \u654f\u611f (\u6240\u6709\u70b9\u90fd\u5f71\u54cd\u51b3\u7b56\u8fb9\u754c) | \u9c81\u68d2 (\u53ea\u6709 support vectors \u5f71\u54cd) |
| \u9002\u7528\u573a\u666f | \u9700\u8981\u6982\u7387\u8f93\u51fa\u65f6 | \u9ad8\u7ef4\u7a00\u758f\u6570\u636e (text) |

---

## 3. Gradient Descent""",
    )

    # Section 3: Gradient Descent follow-ups
    # LARS was expanded in PART 1
    content = content.replace(
        "- Follow-up: \u6709\u6ca1\u6709\u65b9\u6cd5\u8ba9\u5927batch\u4e5f\u80fd\u6cdb\u5316\u597d\uff1f\u2192 **LARS (Layer-wise Adaptive Rate Scaling)**/LAMB (Layer-wise Adaptive Moments for Batch training) optimizer, learning rate warmup\n\n---\n\n## 4. Overfitting / Underfitting",
        """- Follow-up: \u6709\u6ca1\u6709\u65b9\u6cd5\u8ba9\u5927batch\u4e5f\u80fd\u6cdb\u5316\u597d\uff1f\u2192 **LARS (Layer-wise Adaptive Rate Scaling)**/LAMB (Layer-wise Adaptive Moments for Batch training) optimizer, learning rate warmup

### Follow-up \u95ee\u9898\u8be6\u89e3

**Q: \u68af\u5ea6\u6d88\u5931\u548c\u68af\u5ea6\u7206\u70b8\u662f\u4ec0\u4e48\uff1f\u600e\u4e48\u89e3\u51b3\uff1f**

- **\u68af\u5ea6\u6d88\u5931 (Vanishing Gradient)**: \u6df1\u5c42\u7f51\u7edc\u4e2d\uff0c\u68af\u5ea6\u7ecf\u8fc7\u591a\u5c42\u53cd\u5411\u4f20\u64ad\u540e\u53d8\u5f97\u6781\u5c0f (\u63a5\u8fd10)\uff0c\u5bfc\u81f4\u6d45\u5c42\u53c2\u6570\u51e0\u4e4e\u4e0d\u66f4\u65b0\u3002\u5e38\u89c1\u4e8e sigmoid/tanh \u6fc0\u6d3b (\u5bfc\u6570\u6700\u59270.25)\u3002
- **\u68af\u5ea6\u7206\u70b8 (Exploding Gradient)**: \u68af\u5ea6\u503c\u4e0d\u65ad\u7d2f\u4e58\u5bfc\u81f4\u6781\u5927\uff0c\u53c2\u6570\u66f4\u65b0\u8df3\u8dc3\uff0c\u8bad\u7ec3\u4e0d\u7a33\u5b9a\u3002\u5e38\u89c1\u4e8e RNN\u3002

\u89e3\u51b3\u65b9\u6848\uff1a
- \u68af\u5ea6\u6d88\u5931: ReLU \u6fc0\u6d3b, Residual connections (skip connections), Batch Normalization, LSTM/GRU (RNN\u573a\u666f)
- \u68af\u5ea6\u7206\u70b8: Gradient clipping ($\\|g\\| > \\text{threshold}$ \u65f6\u7f29\u653e), \u5408\u9002\u7684\u6743\u91cd\u521d\u59cb\u5316 (Xavier/He), \u964d\u4f4e\u5b66\u4e60\u7387

```python
import numpy as np

def gradient_clip(gradients: list[np.ndarray], max_norm: float = 1.0) -> list[np.ndarray]:
    \"\"\"Gradient clipping by global norm.

    \u5982\u679c\u68af\u5ea6\u7684\u5168\u5c40\u8303\u6570\u8d85\u8fc7 max_norm\uff0c\u7b49\u6bd4\u4f8b\u7f29\u653e\u6240\u6709\u68af\u5ea6\u3002
    \"\"\"
    total_norm = np.sqrt(sum(np.sum(g ** 2) for g in gradients))
    clip_coef = max_norm / (total_norm + 1e-6)
    if clip_coef < 1.0:
        gradients = [g * clip_coef for g in gradients]
    return gradients

# \u793a\u4f8b
grads = [np.array([3.0, 4.0]), np.array([5.0, 12.0])]
print(f"Before clip - norms: {[np.linalg.norm(g) for g in grads]}")
clipped = gradient_clip(grads, max_norm=5.0)
print(f"After clip  - norms: {[np.round(np.linalg.norm(g), 3) for g in clipped]}")
```

**Q: Learning rate \u592a\u5927\u6216\u592a\u5c0f\u4f1a\u600e\u6837\uff1f**

- **\u592a\u5927**: \u66f4\u65b0\u6b65\u5e45\u8fc7\u5927\uff0closs \u9707\u8361\u751a\u81f3\u53d1\u6563 (diverge)
- **\u592a\u5c0f**: \u6536\u655b\u6781\u6162\uff0c\u53ef\u80fd\u5361\u5728\u5c40\u90e8\u6781\u5c0f\u503c\u6216\u978d\u70b9 (saddle point)
- **\u6700\u4f73\u5b9e\u8df5**: \u4f7f\u7528 learning rate finder (Leslie Smith \u65b9\u6cd5) \u2014 \u4ece\u6781\u5c0f LR \u5f00\u59cb\u9010\u6b65\u589e\u5927\uff0c\u627e\u5230 loss \u4e0b\u964d\u6700\u5feb\u7684\u533a\u95f4

---

## 4. Overfitting / Underfitting""",
    )

    # Section 6: Random Forest follow-ups
    # MLE title was expanded in PART 1
    content = content.replace(
        "- Follow-up: **OOB (Out-of-Bag\uff0c\u888b\u5916\u6837\u672c)** error \u662f\u4ec0\u4e48\uff1f\u2192 \u6bcf\u68f5\u6811\u6709\u7ea6 36.8% \u7684\u6837\u672c\u6ca1\u88ab\u9009\u4e2d\uff0c\u53ef\u7528\u4f5c\u9a8c\u8bc1\u96c6\n\n---\n\n## 7. MLE (Maximum Likelihood Estimation\uff0c\u6700\u5927\u4f3c\u7136\u4f30\u8ba1) \u63a8\u5bfc",
        """- Follow-up: **OOB (Out-of-Bag\uff0c\u888b\u5916\u6837\u672c)** error \u662f\u4ec0\u4e48\uff1f\u2192 \u6bcf\u68f5\u6811\u6709\u7ea6 36.8% \u7684\u6837\u672c\u6ca1\u88ab\u9009\u4e2d\uff0c\u53ef\u7528\u4f5c\u9a8c\u8bc1\u96c6

### Follow-up \u95ee\u9898\u8be6\u89e3

**Q: OOB error \u4e3a\u4ec0\u4e48\u7ea6 36.8% \u7684\u6837\u672c\u6ca1\u88ab\u9009\u4e2d\uff1f**

Bootstrap \u6709\u653e\u56de\u91c7\u6837 $N$ \u6b21\uff0c\u67d0\u4e2a\u6837\u672c\u5728\u4e00\u6b21\u62bd\u6837\u4e2d\u4e0d\u88ab\u9009\u4e2d\u7684\u6982\u7387\u662f $(1 - 1/N)$\u3002$N$ \u6b21\u90fd\u4e0d\u88ab\u9009\u4e2d\u7684\u6982\u7387\u662f\uff1a

$(1 - 1/N)^N \\to e^{-1} \\approx 0.368$

\u6240\u4ee5\u7ea6 36.8% \u7684\u6837\u672c\u6ca1\u88ab\u7528\u4e8e\u8bad\u7ec3\u8be5\u6811\uff0c\u53ef\u4ee5\u5f53\u4f5c\u9a8c\u8bc1\u96c6\u3002OOB error \u662f\u4e00\u79cd\u514d\u8d39\u7684\u4ea4\u53c9\u9a8c\u8bc1\uff0c\u4e0d\u9700\u8981\u989d\u5916\u5212\u5206\u6570\u636e\u3002

**Q: XGBoost \u548c Random Forest \u600e\u4e48\u9009\uff1f**

| \u573a\u666f | \u63a8\u8350 | \u539f\u56e0 |
|------|------|------|
| \u6570\u636e\u91cf\u5c0f (<10K) | Random Forest | \u4e0d\u5bb9\u6613 overfit, \u5c11\u8c03\u53c2 |
| \u8868\u683c\u6570\u636e\u7ade\u8d5b | XGBoost/LightGBM | Boosting \u6548\u679c\u66f4\u597d |
| \u9700\u8981 feature importance | Random Forest | MDI \u7b80\u5355\u76f4\u89c2 |
| \u9700\u8981\u6982\u7387\u6821\u51c6 | XGBoost | \u81ea\u5e26 calibration |
| \u8bad\u7ec3\u65f6\u95f4\u7d27 | Random Forest | \u53ef\u5b8c\u5168\u5e76\u884c |
| \u7279\u5f81\u6709\u7f3a\u5931\u503c | XGBoost | \u539f\u751f\u652f\u6301\u7f3a\u5931\u503c\u5904\u7406 |

**Q: Bagging vs Boosting \u7684\u6838\u5fc3\u533a\u522b\uff1f**

```
Bagging (Bootstrap AGGregatING):
  Data \u2500\u2500> [Bootstrap Sample 1] \u2500\u2500> Tree 1 \u2500\u2500\u2510
  Data \u2500\u2500> [Bootstrap Sample 2] \u2500\u2500> Tree 2 \u2500\u2500\u253c\u2500\u2500> \u5e73\u5747/\u6295\u7968 \u2500\u2500> \u6700\u7ec8\u9884\u6d4b
  Data \u2500\u2500> [Bootstrap Sample 3] \u2500\u2500> Tree 3 \u2500\u2500\u2518
  (\u5e76\u884c\u8bad\u7ec3, \u51cf\u5c11 variance)

Boosting:
  Data \u2500\u2500> Tree 1 \u2500\u2500> Residual 1 \u2500\u2500> Tree 2 \u2500\u2500> Residual 2 \u2500\u2500> Tree 3 \u2500\u2500> ...
  (\u4e32\u884c\u8bad\u7ec3, \u51cf\u5c11 bias, \u6bcf\u68f5\u6811\u4fee\u6b63\u524d\u4e00\u68f5\u7684\u9519\u8bef)
```

---

## 7. MLE (Maximum Likelihood Estimation\uff0c\u6700\u5927\u4f3c\u7136\u4f30\u8ba1) \u63a8\u5bfc""",
    )

    return content


def save_content(conn: sqlite3.Connection, content: str) -> None:
    """Write fixed content back to doc#24."""
    cur = conn.cursor()
    cur.execute(
        "UPDATE company_documents SET content=? WHERE id=24",
        (content,),
    )
    conn.commit()


def main() -> None:
    """Run fix pipeline."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        content = get_content(conn)
        print(f"Before fix: {len(content)}c")

        fixed = fix(content)
        print(f"After fix: {len(fixed)}c")
        print(f"Added: {len(fixed) - len(content)}c")

        if len(fixed) == len(content):
            print("WARNING: No changes applied!")
        else:
            save_content(conn, fixed)
            print("Saved to database.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
