# Bias-Variance Tradeoff

## Overview

The bias-variance tradeoff is the fundamental tension in supervised learning: a model cannot simultaneously minimize both bias (systematic error from wrong assumptions) and variance (sensitivity to training data fluctuations). Understanding this decomposition -- and diagnosing which error dominates -- is essential for model selection, tuning, and debugging in MLE interviews.

## Core Concepts

### Error Decomposition

For a given input $x$, the expected prediction error of a model $\hat{f}$ trained on dataset $D$ decomposes as:

$$
E_D\left[(y - \hat{f}(x))^2\right] = \underbrace{\left(E_D[\hat{f}(x)] - f(x)\right)^2}_{\text{Bias}^2} + \underbrace{E_D\left[(\hat{f}(x) - E_D[\hat{f}(x)])^2\right]}_{\text{Variance}} + \underbrace{\sigma^2}_{\text{Irreducible}}
$$

Where:
- **Bias$^2$**: How far the average prediction (over all possible training sets) is from the true value. Measures systematic error from model assumptions.
- **Variance**: How much predictions fluctuate across different training sets. Measures instability/sensitivity to data.
- **Irreducible error ($\sigma^2$)**: Noise inherent in the data (unknown factors, measurement error). Cannot be reduced by any model.

### Bias

- Comes from **erroneous assumptions** in the learning algorithm (e.g., assuming linearity when the true function is nonlinear)
- High bias = the model consistently misses the target = **underfitting**
- Measures the gap between the model's average prediction and the true expected value
- Introducing a bias term in linear models simplifies learning but fails when the true relationship violates the linearity assumption

**High-bias indicators:**
- High training error AND high test error
- Training and test errors are close to each other (both bad)
- Model is too simple for the data complexity

### Variance

- Comes from the model's **sensitivity to noise/fluctuations** in the training set
- High variance = the model fits training noise as if it were signal = **overfitting**
- Reveals how concentrated (stable) the model's predictions are across different training samples
- A model with high variance produces very different predictions when trained on different subsets of the data

**High-variance indicators:**
- Low training error but high test error (large generalization gap)
- Performance varies significantly across different train/test splits
- Model is too complex relative to available data

### Model Complexity Curve

As model complexity increases:

| Complexity | Bias | Variance | Training Error | Test Error | Regime |
|-----------|------|----------|---------------|------------|--------|
| Low (e.g., linear) | High | Low | High | High | Underfitting |
| Optimal | Balanced | Balanced | Moderate | Minimized | Sweet spot |
| High (e.g., deep tree) | Low | High | Low | High | Overfitting |

The optimal model minimizes **total error** (Bias$^2$ + Variance), not either component alone.

### How Ensemble Methods Address Bias vs Variance

- **Bagging** (e.g., Random Forest): Trains multiple models on bootstrap samples, averages predictions. Reduces **variance** while keeping bias roughly constant. Works best with high-variance base learners (deep trees).
- **Boosting** (e.g., GBM, XGBoost): Sequentially fits models to residual errors. Reduces **bias** by combining many weak learners into a strong one. Can increase variance if not regularized.
- **Stacking**: Combines diverse models via a meta-learner, can reduce both bias and variance depending on base model diversity.

### K-Fold Cross-Validation

K-fold CV partitions data into $k$ folds, trains on $k-1$ folds and validates on the remaining one, rotating through all folds:

- **Reduces variance** of the generalization estimate by averaging performance across $k$ different train/test splits, reducing dependence on any single split
- **Increases bias** slightly because each training set uses only $\frac{k-1}{k}$ of the data (less data = slightly worse fit)
- Higher $k$ = less bias (more training data per fold) but more variance (folds are more correlated) and higher compute cost
- Common choices: $k=5$ or $k=10$ (empirically good bias-variance balance)
- Leave-one-out ($k=n$): lowest bias but highest variance and computational cost

## Implementation

```python
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

# Diagnosing bias vs variance via learning curves
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt

def plot_learning_curve(estimator, X, y, title):
    """Plot learning curve to diagnose bias vs variance."""
    train_sizes, train_scores, val_scores = learning_curve(
        estimator, X, y, cv=5,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='neg_mean_squared_error'
    )
    train_mean = -train_scores.mean(axis=1)
    val_mean = -val_scores.mean(axis=1)

    plt.plot(train_sizes, train_mean, label='Training error')
    plt.plot(train_sizes, val_mean, label='Validation error')
    plt.title(title)
    plt.xlabel('Training set size')
    plt.ylabel('MSE')
    plt.legend()

# High bias: both errors high and converging
# plot_learning_curve(LinearRegression(), X, y, "High Bias")

# High variance: training error low, validation error high (gap)
# plot_learning_curve(DecisionTreeRegressor(), X, y, "High Variance")

# Balanced: Random Forest reduces variance via bagging
# plot_learning_curve(RandomForestRegressor(n_estimators=100), X, y, "Balanced")

# K-fold CV to estimate generalization performance
model = RandomForestRegressor(n_estimators=100)
scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
print(f"CV MSE: {-scores.mean():.4f} +/- {scores.std():.4f}")
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Error decomposition | "Explain bias-variance tradeoff" | Total error = Bias$^2$ + Variance + Irreducible; you minimize the sum, not individual terms |
| Learning curve diagnosis | "Your model performs poorly" | Plot train vs val error; converging high = bias, diverging = variance |
| Complexity adjustment | "How would you fix this model?" | High bias: add features/complexity. High variance: regularize/simplify/add data |
| Ensemble selection | "Which ensemble method?" | Bagging for variance reduction (unstable models), boosting for bias reduction (weak models) |
| CV strategy | "How do you evaluate model performance?" | K-fold averages over splits; higher k = less bias but more variance in estimate |

### Common Interview Questions

- [ ] Explain the bias-variance tradeoff. What is the mathematical decomposition?
- [ ] Your model has high training error and high test error -- what is wrong and how do you fix it?
- [ ] Your model has low training error but high test error -- what is wrong and how do you fix it?
- [ ] How does model complexity relate to bias and variance?
- [ ] How do ensemble methods address bias vs variance? (Bagging vs boosting)
- [ ] What is K-fold cross-validation and how does it relate to the bias-variance tradeoff?
- [ ] Why can you not minimize both bias and variance simultaneously?

## Comparisons

| Aspect | High Bias (Underfitting) | High Variance (Overfitting) |
|--------|------------------------|---------------------------|
| Cause | Model too simple / wrong assumptions | Model too complex / insufficient data |
| Training error | High | Low |
| Test error | High | High |
| Train-test gap | Small (both bad) | Large (train good, test bad) |
| Fix: data | More features, polynomial terms | More training samples |
| Fix: model | Increase complexity, fewer constraints | Regularize (L1/L2), reduce features |
| Fix: ensemble | Boosting (reduce bias) | Bagging (reduce variance) |
| Example model | Linear regression on nonlinear data | Deep decision tree on small dataset |

## Key Takeaways

- [ ] Total prediction error = Bias$^2$ + Variance + Irreducible Error (memorize the MSE decomposition formula)
- [ ] Bias = systematic error from wrong assumptions (underfitting); variance = sensitivity to training noise (overfitting)
- [ ] You cannot minimize both simultaneously -- the optimal model balances them to minimize total error
- [ ] Diagnose via learning curves: converging high errors = bias problem; large train-test gap = variance problem
- [ ] High bias fix: increase model complexity, add features, reduce regularization
- [ ] High variance fix: more data, regularization, feature selection, simpler model
- [ ] Bagging reduces variance (averaging smooths noise); boosting reduces bias (sequential error correction)
- [ ] K-fold CV reduces variance of performance estimate but slightly increases bias (less training data per fold)
