# Missing Data Handling

## Overview

Missing data is pervasive in real-world ML systems -- around 48% of studies encounter datasets with missing values. Understanding *why* data is missing (mechanism) determines which imputation method is appropriate. This topic covers missingness mechanisms (MAR/MCAR/MNAR), pattern discovery via KDE, and six imputation methods ranging from simple ARIMA to principled probabilistic approaches (PPCA, MCMC). For MLE interviews, the key is matching the right method to the data characteristics and justifying the choice.

## Core Concepts

### Missing Data Mechanisms

The mechanism behind missingness determines which imputation methods are valid:

| Mechanism | Definition | Example | Valid Methods |
|-----------|-----------|---------|---------------|
| **MCAR** (Missing Completely At Random) | Missingness is independent of both observed and unobserved values | Random sensor dropout | Any method; simple imputation (mean, Hot-Deck) often sufficient |
| **MAR** (Missing At Random) | Missingness depends on observed data but not on the missing values themselves | Sensor fails during high-traffic hours (traffic volume is observed) | Statistical methods (EM, multiple imputation) that condition on observed data |
| **MNAR** (Missing Not At Random) | Missingness depends on the unobserved values themselves | Sensor overloads and fails precisely when traffic is extremely high | Learning algorithms (Random Forest, deep models); requires modeling the missingness mechanism |

Key insight: **MNAR is the hardest case** -- the very values you need are correlated with their own absence. Detecting MNAR requires domain knowledge since you cannot statistically distinguish it from MAR using observed data alone.

### How to Detect Missingness Mechanism

- **MCAR test**: Compare distributions of observed values when another variable is vs. is not missing. If distributions differ, not MCAR.
- **MAR evidence**: If missingness can be predicted from other observed features, likely MAR.
- **MNAR suspicion**: If missingness rates correlate with the expected value range (e.g., high-value readings missing more often), suspect MNAR. Requires domain expertise.

### Pattern Discovery

Before imputing, understand the structure of missingness:

**Binary indicator matrix**: Given $n$ sensors reporting over $t$ time slots, define:

$$
BM(t, n) = \begin{cases} 0, & \text{if } x(t, n) \text{ is null} \\ 1, & \text{otherwise} \end{cases}
$$

**Feature engineering on missingness**:
- Cumulative sum of missing indicators (cumsum) -- reveals bursts vs. scattered gaps
- Missing value span lengths -- categorize into minute/hour/day level gaps
- Index patterns -- detect periodic failures (e.g., always missing at midnight)

**Kernel Density Estimation (KDE)** for temporal pattern visualization:

$$
\hat{f}_K(x, y) = \sum_{i=1}^n K_{h_x}(x - x_i) \cdot K_{h_y}(y - y_i)
$$

Where $x$ and $y$ represent start and end times of missing segments. Kernel choices: Gaussian, tophat, Epanechnikov, exponential, linear, cosine. KDE reveals common missing patterns (periodic failures) vs. random noise.

### Data Representation

For traffic/time-series data with $N$ consecutive days, each with $D$ time slots:

$$
Y_c = [Y(1), \ldots, Y(N)], \quad Y(i) = [y_i(1), \ldots, y_i(D)]^T
$$

Concatenated series: $Y_{\text{series}} = [y(1), \ldots, y(D \times N)]^T$

### ARIMA-Based Imputation

**ARIMA(p, d, q)** -- Autoregressive Integrated Moving Average:

$$
\left(1 - \sum_{i=1}^p \alpha_i L^i\right)(1 - L)^d y(t) = \left(1 + \sum_{i=1}^q \beta_i L^i\right) \xi(t)
$$

Where $L$ is the backshift operator ($Ly(t) = y(t-1)$), $\xi(t)$ is white Gaussian noise.

- **p**: autoregressive order (past values)
- **d**: differencing degree (typically $d=1$ for traffic data)
- **q**: moving average order (past errors)
- Select $p, q$ via **AIC** (Akaike Information Criterion)
- Impute missing values one by one; each imputed value becomes "known" for the next prediction

**Strengths**: Captures temporal autocorrelation and seasonal patterns.
**Weaknesses**: Sequential imputation means errors can propagate; assumes stationarity after differencing.

### Bayesian Network (GMM) Imputation

Model the multivariate distribution $Y_{mv}(t) = [y(t-m), \ldots, y(t)]^T$ as a **Gaussian Mixture Model (GMM)**.

Fit GMM parameters using split-and-merge EM algorithm. Impute missing values as conditional expectations:

$$
\hat{y}(t) = E[y(t) \mid y(t-m), \ldots, y(t-1)]
$$

**Strengths**: Captures multimodal distributions (e.g., weekday vs. weekend traffic).
**Weaknesses**: GMM component selection is sensitive; computationally heavier than ARIMA.

### k-NN Based Imputation

Non-parametric, weighted approach:

**Selection step**: Find $k$ nearest daily flow vectors to the corrupted vector $Y(i)$ using a similarity metric (Euclidean distance or Pearson correlation).

**Imputation step**: Compute weighted average of the $k$ neighbors' corresponding entries, weighted by correlation coefficients:

$$
\hat{y}_{\text{missing}} = \frac{\sum_{j=1}^k w_j \cdot y_j}{\sum_{j=1}^k w_j}
$$

Where $w_j$ is the correlation-based weight for neighbor $j$.

**Hyperparameter**: Select $k$ via grid search or cross-validation.

**Strengths**: No distributional assumptions; captures local patterns.
**Weaknesses**: Fails when no similar historical patterns exist; computationally expensive for large datasets.

### Local Least Squares (LLS) Imputation

Uses the same selection step as k-NN, but imputes via linear regression:

**Imputation step**: Decompose selected vectors into matrices $A$ (observed dimensions) and $B$ (missing dimensions):

$$
\hat{Y}_{\text{mis}}(i) = B \left((A^T A)^{-1} A^T Y_{\text{obs}}(i)\right)
$$

This is a pseudo-inverse regression. Requires $A$ to be full-rank.

**Strengths**: Captures linear relationships between observed and missing dimensions.
**Weaknesses**: Assumes linear structure; fails when $A$ is rank-deficient.

### PPCA-Based Imputation

**Probabilistic Principal Component Analysis** assumes observed data depends on latent variables:

$$
Y = Wx + \mu + \epsilon
$$

Where $x \sim \mathcal{N}(0, I)$ is a $q$-dimensional latent variable, $\epsilon \sim \mathcal{N}(0, \sigma^2 I)$ is isotropic noise, and $\mu$ is the mean.

Fit via **EM algorithm**:

**E-step**: Compute expected complete-data log-likelihood:

$$
Q(\Phi \mid \Phi^k) = E_{X, Y_{\text{mis}} \mid Y_{\text{obs}}, \Phi^k}[\log p_c(Y_c, X \mid \Phi^k)]
$$

Update estimates of $Y_{\text{mis}}^k$ and latent variables $X^k$.

**M-step**: Maximize to update parameters:

$$
\Phi^{k+1} = \arg\max_{\Phi} Q(\Phi \mid \Phi^k)
$$

**Strengths**: Principled probabilistic framework; handles high-dimensional data via dimensionality reduction.
**Weaknesses**: Gaussian assumption may not hold; conditional expectation can be hard to compute (may need MCMC approximation).

### MCMC with Data Augmentation

Assumes the data follows a distribution with parameters $\Phi$ (e.g., Gaussian). Uses Gibbs sampling to iteratively:

**I-step (Imputation)**: Given current parameters $\Phi^k$, sample missing values:

$$
Y_{\text{mis}}^{k+1} \sim p(Y_{\text{mis}} \mid Y_{\text{obs}}, \Phi^k)
$$

**P-step (Posterior)**: Update parameters given completed data:

$$
\Phi^{k+1} \sim p(\Phi \mid Y_{\text{obs}}, Y_{\text{mis}}^{k+1})
$$

This constructs a Markov chain $(\hat{Y}_{\text{mis}}^1, \Phi^1), \ldots, (\hat{Y}_{\text{mis}}^N, \Phi^N)$.

Final estimate (after discarding burn-in):

$$
\hat{Y}_{\text{mis}} = \frac{1}{N_{\text{sample}} - N_{\text{burn-in}}} \sum_{t=N_{\text{burn-in}}+1}^{N_{\text{sample}}} Y_{\text{mis}}^t
$$

Typical settings: $N_{\text{sample}} = 1500$, $N_{\text{burn-in}} = 500$. The burn-in period allows the Markov chain to converge before averaging.

**Strengths**: Provides uncertainty estimates; theoretically sound under correct model specification.
**Weaknesses**: Computationally expensive; convergence diagnostics needed; sensitive to distributional assumptions.

## Implementation

```python
import numpy as np
from typing import Literal


def detect_missingness_type(
    data: np.ndarray,
    indicator: np.ndarray,
) -> Literal["MCAR", "MAR", "MNAR_suspect"]:
    """Heuristic missingness mechanism detection.

    Args:
        data: Original data matrix (NaN for missing).
        indicator: Binary matrix (1=observed, 0=missing).

    Returns:
        Detected mechanism type as string.
    """
    from scipy import stats

    n_cols = data.shape[1]
    mar_evidence = 0

    for col in range(n_cols):
        missing_mask = indicator[:, col] == 0
        if missing_mask.sum() == 0 or (~missing_mask).sum() == 0:
            continue
        # Check if other columns differ when this col is missing
        for other_col in range(n_cols):
            if other_col == col:
                continue
            obs_when_present = data[~missing_mask, other_col]
            obs_when_missing = data[missing_mask, other_col]
            # Remove NaNs from comparison
            obs_when_present = obs_when_present[~np.isnan(obs_when_present)]
            obs_when_missing = obs_when_missing[~np.isnan(obs_when_missing)]
            if len(obs_when_present) < 5 or len(obs_when_missing) < 5:
                continue
            _, p_val = stats.ks_2samp(obs_when_present, obs_when_missing)
            if p_val < 0.05:
                mar_evidence += 1

    if mar_evidence == 0:
        return "MCAR"
    return "MAR"  # MNAR requires domain knowledge to confirm


def select_imputation_method(
    missing_pct: float,
    is_temporal: bool,
    mechanism: str,
    data_size: int,
) -> str:
    """Recommend an imputation method based on data characteristics.

    Args:
        missing_pct: Fraction of missing values (0-1).
        is_temporal: Whether data has temporal ordering.
        mechanism: Missingness mechanism (MCAR/MAR/MNAR).
        data_size: Number of observations.

    Returns:
        Recommended method name with rationale.
    """
    if missing_pct < 0.05:
        return "Mean/median imputation (low missing rate, simple is fine)"
    if mechanism == "MCAR" and missing_pct < 0.2:
        return "k-NN imputation (MCAR + moderate missing rate)"
    if is_temporal:
        if missing_pct < 0.3:
            return "ARIMA (temporal data, moderate gaps)"
        return "PPCA or MCMC (temporal data, large gaps need probabilistic)"
    if mechanism == "MAR":
        return "Multiple imputation / MICE (MAR mechanism)"
    return "MCMC with DA (complex missingness, need uncertainty estimates)"
```

```python
def knn_impute(
    data: np.ndarray,
    k: int = 5,
    metric: str = "correlation",
) -> np.ndarray:
    """Weighted k-NN imputation for daily pattern vectors.

    Args:
        data: Matrix of shape (N_days, D_slots), NaN for missing.
        k: Number of neighbors.
        metric: Similarity metric ('correlation' or 'euclidean').

    Returns:
        Imputed data matrix.
    """
    result = data.copy()
    n_days, n_slots = data.shape

    for i in range(n_days):
        missing_idx = np.where(np.isnan(data[i]))[0]
        if len(missing_idx) == 0:
            continue

        observed_idx = np.where(~np.isnan(data[i]))[0]
        if len(observed_idx) == 0:
            continue

        # Find k nearest complete neighbors
        similarities = []
        for j in range(n_days):
            if i == j or np.any(np.isnan(data[j])):
                continue
            if metric == "correlation":
                obs_i = data[i, observed_idx]
                obs_j = data[j, observed_idx]
                if np.std(obs_i) == 0 or np.std(obs_j) == 0:
                    continue
                corr = np.corrcoef(obs_i, obs_j)[0, 1]
                similarities.append((j, corr))
            else:
                dist = np.linalg.norm(
                    data[i, observed_idx] - data[j, observed_idx]
                )
                similarities.append((j, -dist))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_k = similarities[:k]

        if not top_k:
            continue

        # Weighted average
        weights = np.array([max(s, 0.0) for _, s in top_k])
        if weights.sum() == 0:
            weights = np.ones(len(top_k))
        weights /= weights.sum()

        for idx in missing_idx:
            values = [data[j, idx] for j, _ in top_k]
            result[i, idx] = np.average(values, weights=weights)

    return result
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Mechanism identification first | Any missing data problem | Always determine MAR/MCAR/MNAR before choosing a method |
| Simple before complex | Low missing rates (<5%) | Mean/median/forward-fill often sufficient; don't over-engineer |
| Multiple imputation | MAR data, statistical inference | Single imputation underestimates uncertainty; create M imputed datasets |
| Temporal methods (ARIMA) | Time series with autocorrelation | Exploit temporal structure rather than treating each value independently |
| k-NN for local patterns | Spatial/pattern-based data | Find similar historical patterns; no distributional assumptions needed |
| PPCA for high-dimensional | Many correlated features | Dimensionality reduction handles curse of dimensionality |
| MCMC for uncertainty | Need confidence intervals | Provides posterior distribution, not just point estimates |
| Feature engineering on missingness | Predictive modeling | The missingness indicator itself can be predictive |
| Listwise deletion baseline | MCAR only, abundant data | Valid under MCAR but wastes data; use as sanity check |
| Domain-guided MNAR handling | Censored/truncated data | Model the missingness mechanism explicitly |

### Common Interview Questions

- [ ] How do you handle missing data in a production ML pipeline?
- [ ] What is the difference between MAR, MCAR, and MNAR? Why does it matter for imputation?
- [ ] When would you use simple imputation (mean/median) vs. sophisticated methods?
- [ ] How would you detect if data is MNAR?
- [ ] What is multiple imputation and when is it preferred over single imputation?
- [ ] How does ARIMA handle missing values in time series?
- [ ] Explain the k-NN imputation approach and its limitations.
- [ ] What is PPCA and how does it handle missing data?
- [ ] How does MCMC with Data Augmentation work for imputation?
- [ ] When should you delete rows with missing values vs. impute them?
- [ ] How would you validate the quality of imputed values?
- [ ] What features can you engineer from the missingness pattern itself?

## Comparisons

### Imputation Methods

| Method | Category | Assumptions | Handles MNAR | Uncertainty | Speed | Best For |
|--------|----------|------------|-------------|-------------|-------|----------|
| Mean/Median | Simple | None | No | No | O(n) | Low missing rate, quick baseline |
| Forward/Backward Fill | Interpolation | Temporal continuity | No | No | O(n) | Time series, short gaps |
| ARIMA | Prediction | Stationarity, temporal autocorrelation | No | No | O(n*p) | Temporally correlated series |
| BN/GMM | Prediction | Gaussian mixture | No | Partial | O(n*k*m) | Multimodal distributions |
| k-NN | Non-parametric | Similar patterns exist | No | No | O(n^2*d) | Pattern-based data, moderate size |
| LLS | Non-parametric | Linear relationship, full-rank | No | No | O(n*k*d) | When linear structure holds |
| PPCA | Statistical | Gaussian, linear latent | No | Yes | O(n*d*q) | High-dimensional, correlated |
| MCMC+DA | Statistical | Distributional model | Partial | Yes | O(n*T) | Need full posterior, research |

### Method Selection by Scenario

| Scenario | Missing Rate | Mechanism | Recommended Method | Why |
|----------|-------------|-----------|-------------------|-----|
| Quick prototype | <5% | Any | Mean/median | Simple, fast, good enough |
| Time series, short gaps | <20% | MCAR/MAR | ARIMA or forward-fill | Exploits temporal structure |
| Tabular data, moderate gaps | 5-30% | MAR | MICE / Multiple Imputation | Handles MAR correctly, preserves uncertainty |
| High-dimensional features | Any | MAR | PPCA | Dimensionality reduction helps |
| Need uncertainty estimates | Any | MAR | MCMC+DA | Full posterior distribution |
| Pattern-based data | <30% | MCAR | k-NN | Leverages similar historical observations |
| Censored data | Any | MNAR | Heckman / Tobit models | Must model selection mechanism |
| Production pipeline | Any | Any | Indicator + simple impute | Add binary "was_missing" feature; let model learn |

### Stochastic vs. Deterministic Methods

| Aspect | Prediction/Interpolation Methods | Statistical Learning Methods |
|--------|--------------------------------|----------------------------|
| Examples | ARIMA, forward-fill, linear interp | PPCA, MCMC, GMM |
| Captures stochastic variation | No | Yes |
| Provides uncertainty | No | Yes |
| Computational cost | Low | High |
| Missing neighbor handling | Fails when neighbors absent | Can still estimate |
| Typical use case | Operational, real-time | Research, offline analysis |

## Key Takeaways

- [ ] Always identify the missingness mechanism (MAR/MCAR/MNAR) before choosing an imputation strategy -- this is the first and most important decision
- [ ] Simple methods (mean, forward-fill) are often sufficient for low missing rates (<5%); don't over-engineer
- [ ] ARIMA exploits temporal autocorrelation and is well-suited for time series with seasonal patterns, using AIC to select (p, d, q)
- [ ] k-NN imputation makes no distributional assumptions but requires similar historical patterns to exist
- [ ] PPCA provides a principled probabilistic framework via latent variables ($Y = Wx + \mu + \epsilon$) with EM fitting
- [ ] MCMC with Data Augmentation gives full posterior uncertainty via alternating I-step (sample missing) and P-step (update params), with burn-in for convergence
- [ ] Feature engineering on missingness itself (binary indicators, gap lengths, temporal patterns via KDE) can be highly predictive for downstream models
- [ ] In production, the practical approach is often: add "is_missing" indicator features + simple imputation, then let the model learn the pattern
- [ ] Prediction/interpolation methods cannot capture stochastic variation in data; statistical learning methods can but at higher computational cost
