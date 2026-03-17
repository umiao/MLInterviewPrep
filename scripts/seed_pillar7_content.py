"""Seed Pillar 7 (Math & Statistics Foundations) framework node descriptions.

Usage:
    python scripts/seed_pillar7_content.py

Populates the `description` field for all 14 Pillar 7 leaf nodes
in the framework_nodes table. Idempotent -- overwrites existing content.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, get_engine  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Content for each leaf topic, keyed by path
# ---------------------------------------------------------------------------

CONTENT: dict[str, str] = {}

# ===== PROBABILITY & STATISTICS =====

CONTENT["pillar7.probability_statistics.probability_basics"] = r"""# Probability Basics (Bayes, Conditional)

## Overview
Probability is the mathematical language of uncertainty. A senior MLE must fluently reason about conditional probability, independence, Bayes' theorem, and the chain rule. These fundamentals underpin every ML model from logistic regression to diffusion models and appear in virtually every MLE interview.

## Core Concepts

### Axioms of Probability
For a sample space $\Omega$ and event $A$:

1. $P(A) \geq 0$
2. $P(\Omega) = 1$
3. For disjoint events $A_1, A_2, \ldots$: $P\!\left(\bigcup_i A_i\right) = \sum_i P(A_i)$

### Conditional Probability

$$
P(A \mid B) = \frac{P(A \cap B)}{P(B)}, \quad P(B) > 0
$$

**Independence**: $A \perp B \iff P(A \cap B) = P(A)P(B)$

**Conditional independence**: $A \perp B \mid C \iff P(A \cap B \mid C) = P(A \mid C)P(B \mid C)$

### Bayes' Theorem

$$
P(\theta \mid D) = \frac{P(D \mid \theta)\, P(\theta)}{P(D)} = \frac{P(D \mid \theta)\, P(\theta)}{\sum_{\theta'} P(D \mid \theta')\, P(\theta')}
$$

| Component | Name | ML Interpretation |
|-----------|------|-------------------|
| $P(\theta \mid D)$ | Posterior | Updated belief after seeing data |
| $P(D \mid \theta)$ | Likelihood | How well model explains data |
| $P(\theta)$ | Prior | Initial belief before data |
| $P(D)$ | Evidence | Normalizing constant |

### Chain Rule of Probability

$$
P(A_1, A_2, \ldots, A_n) = \prod_{i=1}^{n} P(A_i \mid A_1, \ldots, A_{i-1})
$$

This is the foundation of autoregressive language models: $P(w_1, \ldots, w_T) = \prod_t P(w_t \mid w_{<t})$.

### Law of Total Probability

$$
P(A) = \sum_{i} P(A \mid B_i)\, P(B_i)
$$

where $\{B_i\}$ partitions $\Omega$. Used in mixture models: $P(x) = \sum_k \pi_k\, P(x \mid z=k)$.

## Implementation

```python
import numpy as np

def bayes_update(
    prior: np.ndarray, likelihood: np.ndarray,
) -> np.ndarray:
    # Compute posterior from prior and likelihood (discrete case).
    unnormalized = prior * likelihood
    evidence = unnormalized.sum()
    return unnormalized / evidence


def is_independent(p_a: float, p_b: float, p_ab: float, tol: float = 1e-9) -> bool:
    # Check if two events are independent.
    return abs(p_ab - p_a * p_b) < tol


# Example: disease testing
# P(disease) = 0.001, P(+|disease) = 0.99, P(+|healthy) = 0.05
prior = np.array([0.001, 0.999])        # [disease, healthy]
likelihood = np.array([0.99, 0.05])      # P(+ | each)
posterior = bayes_update(prior, likelihood)
# P(disease | +) ~ 0.019 -- the base rate fallacy!
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Base rate fallacy | Disease/spam/fraud testing | Low prevalence makes positive tests unreliable |
| Conditional independence | Naive Bayes | Features are NOT independent, but assumption still works |
| Chain rule | Autoregressive models | Decompose joint into conditionals |
| Total probability | Mixture models, marginalization | Sum over latent states |

### Common Interview Questions
- [ ] A disease affects 1 in 10,000. Test has 99% sensitivity, 1% false positive. Given positive test, what is P(disease)?
- [ ] Prove that conditional independence does not imply marginal independence.
- [ ] How does Naive Bayes use the conditional independence assumption?
- [ ] You draw two cards without replacement. What is P(2nd is ace | 1st is ace)?
- [ ] Explain the chain rule and connect it to autoregressive language models.

## Comparisons

| Aspect | Frequentist | Bayesian |
|--------|-------------|----------|
| Probability meaning | Long-run frequency | Degree of belief |
| Parameters | Fixed unknowns | Random variables |
| Inference | MLE, confidence intervals | Posterior, credible intervals |
| Key formula | $\hat{\theta} = \arg\max P(D \mid \theta)$ | $P(\theta \mid D) \propto P(D \mid \theta) P(\theta)$ |
| Strength | No prior needed | Incorporates prior knowledge |

## Key Takeaways
- Bayes' theorem is the foundation of probabilistic ML -- master the update mechanics
- Conditional independence is what makes graphical models tractable
- The base rate fallacy appears constantly in interview screening questions
- Chain rule connects probability theory directly to autoregressive generation
"""

CONTENT["pillar7.probability_statistics.common_distributions"] = r"""# Common Distributions

## Overview
Probability distributions are the building blocks of statistical modeling and ML. A senior MLE must know the key distributions, their parameters, moments, relationships, and when to use each. This topic appears in both theoretical questions and practical modeling decisions at every major tech company.

## Core Concepts

### Discrete Distributions

| Distribution | PMF/Support | Mean | Variance | Use Case |
|-------------|-------------|------|----------|----------|
| Bernoulli($p$) | $P(X=1)=p$ | $p$ | $p(1-p)$ | Binary classification |
| Binomial($n,p$) | $\binom{n}{k}p^k(1-p)^{n-k}$ | $np$ | $np(1-p)$ | Number of successes |
| Poisson($\lambda$) | $\frac{\lambda^k e^{-\lambda}}{k!}$ | $\lambda$ | $\lambda$ | Event counts |
| Geometric($p$) | $(1-p)^{k-1}p$ | $1/p$ | $(1-p)/p^2$ | Trials until first success |
| Categorical($\mathbf{p}$) | $P(X=k)=p_k$ | -- | -- | Multi-class classification |

### Continuous Distributions

**Normal (Gaussian)**:

$$
f(x) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)
$$

Properties: symmetric, $\mu \pm 1\sigma$ covers 68.3%, $\mu \pm 2\sigma$ covers 95.4%.

**Exponential($\lambda$)**:

$$
f(x) = \lambda e^{-\lambda x}, \quad x \geq 0
$$

Memoryless property: $P(X > s+t \mid X > s) = P(X > t)$. Models inter-arrival times.

**Beta($\alpha, \beta$)**:

$$
f(x) = \frac{x^{\alpha-1}(1-x)^{\beta-1}}{B(\alpha, \beta)}, \quad x \in [0,1]
$$

Conjugate prior for Bernoulli/Binomial. Mean $= \alpha/(\alpha+\beta)$.

**Gamma($\alpha, \beta$)**:

$$
f(x) = \frac{\beta^\alpha}{\Gamma(\alpha)} x^{\alpha-1} e^{-\beta x}, \quad x > 0
$$

Conjugate prior for Poisson rate. Exponential is Gamma(1, $\lambda$).

### Multivariate Normal

$$
f(\mathbf{x}) = \frac{1}{(2\pi)^{d/2}|\Sigma|^{1/2}} \exp\!\left(-\frac{1}{2}(\mathbf{x}-\boldsymbol{\mu})^\top \Sigma^{-1} (\mathbf{x}-\boldsymbol{\mu})\right)
$$

Key properties:
- Marginals and conditionals are also Gaussian
- $X_i \perp X_j \iff \Sigma_{ij} = 0$ (for jointly Gaussian)
- Mahalanobis distance: $d_M = \sqrt{(\mathbf{x}-\boldsymbol{\mu})^\top \Sigma^{-1}(\mathbf{x}-\boldsymbol{\mu})}$

### Distribution Relationships

$$
\text{Binomial}(n,p) \xrightarrow{n \to \infty} \text{Poisson}(np) \xrightarrow{\lambda \to \infty} \text{Normal}(\lambda, \lambda)
$$

## Implementation

```python
import numpy as np
from scipy import stats

def fit_and_compare(data: np.ndarray) -> dict[str, float]:
    # Fit common distributions and return log-likelihoods.
    results = {}

    # Normal
    mu, sigma = stats.norm.fit(data)
    results["normal"] = stats.norm.logpdf(data, mu, sigma).sum()

    # Exponential (positive data only)
    if (data > 0).all():
        _, scale = stats.expon.fit(data, floc=0)
        results["exponential"] = stats.expon.logpdf(data, 0, scale).sum()

    # Gamma
    if (data > 0).all():
        a, _, scale = stats.gamma.fit(data, floc=0)
        results["gamma"] = stats.gamma.logpdf(data, a, 0, scale).sum()

    return results


def kl_divergence_gaussians(
    mu0: float, sigma0: float, mu1: float, sigma1: float,
) -> float:
    # KL(N0 || N1) between two univariate Gaussians.
    return (
        np.log(sigma1 / sigma0)
        + (sigma0**2 + (mu0 - mu1)**2) / (2 * sigma1**2)
        - 0.5
    )
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Conjugate priors | Bayesian updates | Beta-Binomial, Gamma-Poisson, Normal-Normal |
| CLT approximation | Large sample sizes | Sum of iid RVs approaches Normal |
| Memoryless property | Exponential/Geometric | Only distributions with this property |
| Reparameterization trick | VAEs, gradient estimation | Sample from $N(0,1)$, shift/scale |

### Common Interview Questions
- [ ] When would you use Poisson vs. Negative Binomial for count data?
- [ ] Derive the MLE for the Gaussian distribution parameters.
- [ ] What is the conjugate prior for a Bernoulli likelihood? Derive the posterior.
- [ ] Explain the reparameterization trick and why it enables gradient-based optimization.
- [ ] How do you test if data follows a specific distribution?

## Comparisons

| Aspect | Gaussian | Poisson | Exponential |
|--------|----------|---------|-------------|
| Support | $(-\infty, \infty)$ | $\{0,1,2,\ldots\}$ | $[0, \infty)$ |
| Parameters | $\mu, \sigma^2$ | $\lambda$ | $\lambda$ |
| Mean = Variance? | No | Yes | No ($1/\lambda^2$) |
| ML use | Regression residuals | Event modeling | Survival analysis |

## Key Takeaways
- Know mean, variance, and support for each distribution cold
- Conjugate priors make Bayesian updates analytically tractable
- The Gaussian is ubiquitous due to CLT and maximum entropy
- Distribution choice affects model assumptions -- always justify it
"""

CONTENT["pillar7.probability_statistics.expectation_variance"] = r"""# Expectation & Variance

## Overview
Expectation and variance quantify the center and spread of random variables. A senior MLE must manipulate these quantities fluently -- linearity of expectation, variance decomposition, covariance, and moment generating functions appear constantly in derivations of loss functions, estimator properties, and algorithm analysis.

## Core Concepts

### Expectation

$$
E[X] = \begin{cases} \sum_x x\, P(X=x) & \text{discrete} \\[6pt] \int_{-\infty}^{\infty} x\, f(x)\, dx & \text{continuous} \end{cases}
$$

**Linearity** (always holds, no independence needed):

$$
E[aX + bY + c] = a\,E[X] + b\,E[Y] + c
$$

**Law of the Unconscious Statistician (LOTUS)**:

$$
E[g(X)] = \int g(x)\, f(x)\, dx
$$

### Variance

$$
\text{Var}(X) = E[(X - \mu)^2] = E[X^2] - (E[X])^2
$$

Properties:
- $\text{Var}(aX + b) = a^2 \text{Var}(X)$
- $\text{Var}(X + Y) = \text{Var}(X) + \text{Var}(Y) + 2\,\text{Cov}(X, Y)$
- If $X \perp Y$: $\text{Var}(X + Y) = \text{Var}(X) + \text{Var}(Y)$

### Covariance and Correlation

$$
\text{Cov}(X, Y) = E[XY] - E[X]\,E[Y]
$$

$$
\rho(X, Y) = \frac{\text{Cov}(X, Y)}{\sqrt{\text{Var}(X)\,\text{Var}(Y)}}, \quad -1 \leq \rho \leq 1
$$

**Key identity**: $\text{Var}\!\left(\sum_i X_i\right) = \sum_i \text{Var}(X_i) + 2\sum_{i<j} \text{Cov}(X_i, X_j)$

### Law of Total Expectation and Variance

$$
E[X] = E[E[X \mid Y]] \quad \text{(tower property)}
$$

$$
\text{Var}(X) = E[\text{Var}(X \mid Y)] + \text{Var}(E[X \mid Y])
$$

The variance decomposition is key: total variance = expected within-group variance + between-group variance. This is the foundation of ANOVA and the bias-variance tradeoff.

### Moment Generating Functions

$$
M_X(t) = E[e^{tX}], \quad E[X^n] = M_X^{(n)}(0)
$$

If $X \perp Y$: $M_{X+Y}(t) = M_X(t) \cdot M_Y(t)$.

## Implementation

```python
import numpy as np

def empirical_moments(data: np.ndarray) -> dict[str, float]:
    # Compute empirical mean, variance, skewness, kurtosis.
    n = len(data)
    mean = data.mean()
    var = data.var(ddof=1)  # unbiased
    centered = data - mean
    skew = (centered**3).mean() / var**1.5
    kurt = (centered**4).mean() / var**2 - 3  # excess kurtosis
    return {"mean": mean, "variance": var, "skewness": skew, "kurtosis": kurt}


def bias_variance_decomposition(
    y_true: np.ndarray, y_preds: np.ndarray,
) -> dict[str, float]:
    # Decompose MSE into bias^2 + variance (over multiple model fits).
    # Args:
    # y_true: shape (n_samples,)
    # y_preds: shape (n_models, n_samples)
    mean_pred = y_preds.mean(axis=0)
    bias_sq = ((mean_pred - y_true) ** 2).mean()
    variance = y_preds.var(axis=0).mean()
    mse = ((y_preds - y_true) ** 2).mean()
    return {"mse": mse, "bias_squared": bias_sq, "variance": variance}
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Linearity of expectation | Counting problems | Works even for dependent RVs |
| Indicator variables | Expected value of sums | $E[\sum I_i] = \sum P(A_i)$ |
| Variance decomposition | Bias-variance tradeoff | Total = within + between |
| Tower property | Hierarchical models | Iterate expectation over conditioning |

### Common Interview Questions
- [ ] Prove that $\text{Var}(X) = E[X^2] - (E[X])^2$.
- [ ] Expected number of coupon types collected before having all $n$ types?
- [ ] Derive the bias-variance decomposition of MSE.
- [ ] If $X$ and $Y$ have zero correlation, are they independent? Give a counterexample.
- [ ] What is $\text{Var}(\bar{X})$ for iid samples? Why does this matter for SGD?

## Comparisons

| Aspect | Standard Deviation | MAD (Mean Abs Deviation) |
|--------|-------------------|--------------------------|
| Formula | $\sqrt{E[(X-\mu)^2]}$ | $E[|X-\mu|]$ |
| Sensitivity to outliers | High (squared) | Lower (linear) |
| Analytically tractable | Yes | Less so |
| ML usage | Loss functions, confidence | Robust statistics |

## Key Takeaways
- Linearity of expectation is the most powerful trick in probability
- Variance decomposition is the mathematical basis of bias-variance tradeoff
- Covariance measures linear dependence -- zero covariance does NOT imply independence
- Tower property simplifies expectations in hierarchical/mixture models
"""

CONTENT["pillar7.probability_statistics.mle_map"] = r"""# MLE & MAP Estimation

## Overview
Maximum Likelihood Estimation (MLE) and Maximum A Posteriori (MAP) are the two dominant parameter estimation frameworks in ML. MLE finds parameters that maximize the data likelihood; MAP adds a prior to regularize. Understanding both is essential for deriving loss functions, understanding regularization, and answering theoretical interview questions.

## Core Concepts

### Maximum Likelihood Estimation

$$
\hat{\theta}_{\text{MLE}} = \arg\max_\theta P(D \mid \theta) = \arg\max_\theta \sum_{i=1}^{n} \log P(x_i \mid \theta)
$$

**Key properties**:
- Consistent: $\hat{\theta}_{\text{MLE}} \xrightarrow{P} \theta^*$ as $n \to \infty$
- Asymptotically efficient: achieves Cramer-Rao lower bound
- Asymptotically normal: $\sqrt{n}(\hat{\theta} - \theta^*) \xrightarrow{d} N(0, I(\theta^*)^{-1})$
- Invariant: if $\hat{\theta}$ is MLE, then $g(\hat{\theta})$ is MLE of $g(\theta)$

### Fisher Information

$$
I(\theta) = -E\!\left[\frac{\partial^2 \log P(X \mid \theta)}{\partial \theta^2}\right] = E\!\left[\left(\frac{\partial \log P(X \mid \theta)}{\partial \theta}\right)^2\right]
$$

**Cramer-Rao bound**: $\text{Var}(\hat{\theta}) \geq \frac{1}{n\, I(\theta)}$

### MAP Estimation

$$
\hat{\theta}_{\text{MAP}} = \arg\max_\theta \left[\log P(D \mid \theta) + \log P(\theta)\right]
$$

### MLE-MAP-Regularization Connection

| Prior $P(\theta)$ | MAP Objective | Equivalent Regularization |
|-------------------|---------------|---------------------------|
| $N(0, \sigma^2 I)$ | $\log P(D \mid \theta) - \frac{\|\theta\|_2^2}{2\sigma^2}$ | L2 / Ridge ($\lambda = \frac{1}{\sigma^2}$) |
| Laplace$(0, b)$ | $\log P(D \mid \theta) - \frac{\|\theta\|_1}{b}$ | L1 / Lasso ($\lambda = \frac{1}{b}$) |
| Uniform | $\log P(D \mid \theta)$ | No regularization (= MLE) |

### Common MLE Derivations

**Gaussian**: $\hat{\mu} = \bar{x}$, $\hat{\sigma}^2 = \frac{1}{n}\sum(x_i - \bar{x})^2$ (biased)

**Bernoulli**: $\hat{p} = \bar{x}$

**Poisson**: $\hat{\lambda} = \bar{x}$

## Implementation

```python
import numpy as np
from scipy.optimize import minimize

def mle_gaussian(data: np.ndarray) -> tuple[float, float]:
    # MLE for Gaussian parameters.
    mu = data.mean()
    sigma_sq = ((data - mu) ** 2).mean()  # MLE (biased)
    return mu, sigma_sq


def map_logistic_regression(
    X: np.ndarray, y: np.ndarray, lam: float = 1.0,
) -> np.ndarray:
    # MAP estimate for logistic regression with Gaussian prior (= L2).
    def neg_log_posterior(w: np.ndarray) -> float:
        logits = X @ w
        # Log-likelihood
        ll = (y * logits - np.logaddexp(0, logits)).sum()
        # Gaussian prior: -lambda/2 * ||w||^2
        prior = -0.5 * lam * (w @ w)
        return -(ll + prior)

    w0 = np.zeros(X.shape[1])
    result = minimize(neg_log_posterior, w0, method="L-BFGS-B")
    return result.x


def fisher_information_bernoulli(p: float) -> float:
    # Fisher information for Bernoulli(p).
    return 1.0 / (p * (1.0 - p))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Log-likelihood trick | Any MLE derivation | Take log, differentiate, set to zero |
| MLE = MAP with flat prior | Connecting frameworks | Regularization = informative prior |
| Cross-entropy loss | Classification | Negative log-likelihood of Bernoulli/Categorical |
| MSE loss | Regression | Negative log-likelihood of Gaussian |

### Common Interview Questions
- [ ] Derive the MLE for Gaussian mean and variance. Why is the variance estimator biased?
- [ ] Show that L2 regularization is equivalent to a Gaussian prior (MAP).
- [ ] What is Fisher information and what does it tell us about estimator quality?
- [ ] Why does cross-entropy loss correspond to MLE for classification?
- [ ] Compare MLE and MAP in the context of overfitting with small datasets.

## Comparisons

| Aspect | MLE | MAP | Full Bayesian |
|--------|-----|-----|---------------|
| Output | Point estimate | Point estimate | Full posterior |
| Prior | Not used | Used | Used |
| Overfitting risk | Higher | Lower | Lowest |
| Computational cost | Low | Low | High (MCMC/VI) |
| Regularization equiv. | None | L1/L2 | Implicit |

## Key Takeaways
- MLE maximizes likelihood; MAP adds a prior -- both give point estimates
- The MLE-to-loss-function mapping explains why we use MSE and cross-entropy
- Regularization strength $\lambda$ is inversely related to prior variance
- Fisher information sets a fundamental limit on estimation precision
"""

CONTENT["pillar7.probability_statistics.clt"] = r"""# Central Limit Theorem

## Overview
The Central Limit Theorem (CLT) is one of the most important results in probability -- it explains why the Gaussian distribution appears everywhere in nature and statistics. For a senior MLE, CLT underpins confidence intervals, hypothesis testing, the theoretical grounding of SGD convergence, and A/B testing methodology.

## Core Concepts

### Statement of CLT

Let $X_1, X_2, \ldots, X_n$ be iid random variables with mean $\mu$ and finite variance $\sigma^2$. Then:

$$
\frac{\bar{X}_n - \mu}{\sigma / \sqrt{n}} \xrightarrow{d} N(0, 1) \quad \text{as } n \to \infty
$$

Equivalently: $\bar{X}_n \approx N\!\left(\mu, \frac{\sigma^2}{n}\right)$ for large $n$.

### Convergence Rate (Berry-Esseen)

$$
\sup_x \left| P\!\left(\frac{\bar{X}_n - \mu}{\sigma/\sqrt{n}} \leq x\right) - \Phi(x) \right| \leq \frac{C \cdot E[|X - \mu|^3]}{\sigma^3 \sqrt{n}}
$$

where $C \leq 0.4748$. Convergence is $O(1/\sqrt{n})$.

### Standard Error

$$
\text{SE}(\bar{X}_n) = \frac{\sigma}{\sqrt{n}}, \quad \widehat{\text{SE}} = \frac{s}{\sqrt{n}}
$$

### Confidence Intervals

$$
\bar{X}_n \pm z_{\alpha/2} \cdot \frac{s}{\sqrt{n}}
$$

For 95% CI: $z_{0.025} = 1.96$. Requires $n \geq 30$ (rule of thumb).

### Multivariate CLT

For random vectors $\mathbf{X}_i \in \mathbb{R}^d$ with mean $\boldsymbol{\mu}$ and covariance $\Sigma$:

$$
\sqrt{n}(\bar{\mathbf{X}}_n - \boldsymbol{\mu}) \xrightarrow{d} N(\mathbf{0}, \Sigma)
$$

### CLT and SGD

Mini-batch gradient: $\hat{g}_B = \frac{1}{B}\sum_{i=1}^{B} \nabla \ell_i(\theta)$

By CLT: $\hat{g}_B \approx N\!\left(\nabla L(\theta),\, \frac{\Sigma_g}{B}\right)$

Gradient noise scales as $O(1/\sqrt{B})$ -- this is why larger batch sizes give smoother training but diminishing returns.

## Implementation

```python
import numpy as np

def confidence_interval(
    data: np.ndarray, confidence: float = 0.95,
) -> tuple[float, float, float]:
    # Compute CLT-based confidence interval for the mean.
    from scipy.stats import norm
    n = len(data)
    mean = data.mean()
    se = data.std(ddof=1) / np.sqrt(n)
    z = norm.ppf(1 - (1 - confidence) / 2)
    return mean, mean - z * se, mean + z * se


def clt_demonstration(
    distribution: str, n_samples: int, n_means: int = 10000,
) -> np.ndarray:
    # Generate sample means to demonstrate CLT convergence.
    rng = np.random.default_rng(42)
    if distribution == "exponential":
        samples = rng.exponential(1.0, (n_means, n_samples))
    elif distribution == "uniform":
        samples = rng.uniform(0, 1, (n_means, n_samples))
    elif distribution == "bernoulli":
        samples = rng.binomial(1, 0.3, (n_means, n_samples))
    else:
        raise ValueError(f"Unknown distribution: {distribution}")
    return samples.mean(axis=1)  # should be approximately normal


def required_sample_size(
    std: float, margin: float, confidence: float = 0.95,
) -> int:
    # Minimum sample size for desired margin of error.
    from scipy.stats import norm
    z = norm.ppf(1 - (1 - confidence) / 2)
    return int(np.ceil((z * std / margin) ** 2))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| CLT for A/B testing | Sample size estimation | $n \propto \sigma^2 / \epsilon^2$ |
| Batch size and noise | SGD convergence | Gradient noise $\sim O(1/\sqrt{B})$ |
| Normal approximation | Large count data | Binomial/Poisson to Normal |
| Delta method | Functions of means | $g(\bar{X}) \approx N(g(\mu), [g'(\mu)]^2 \sigma^2/n)$ |

### Common Interview Questions
- [ ] State the CLT. What are the assumptions? When does it fail?
- [ ] How does CLT justify the use of z-tests and t-tests?
- [ ] What is the relationship between mini-batch size and gradient noise in SGD?
- [ ] How would you determine the sample size needed for an A/B test?
- [ ] Explain the delta method and give an example.

## Comparisons

| Aspect | CLT (z-test) | t-test | Bootstrap |
|--------|-------------|--------|-----------|
| Assumption | Large $n$, known $\sigma$ | Small $n$, unknown $\sigma$ | Minimal |
| Distribution | Normal | Student-t ($n-1$ df) | Empirical |
| When to use | $n > 30$ | $n < 30$, normal population | Any distribution |
| Computational cost | Analytical | Analytical | Resampling |

## Key Takeaways
- CLT explains why the Normal distribution is so common in practice
- Standard error decreases as $1/\sqrt{n}$ -- quadruple samples to halve uncertainty
- In SGD, mini-batch size controls the variance of gradient estimates via CLT
- Sample size calculations for A/B tests are a direct CLT application
"""

CONTENT["pillar7.probability_statistics.hypothesis_testing"] = r"""# Hypothesis Testing

## Overview
Hypothesis testing is the statistical framework for making decisions under uncertainty. A senior MLE must understand p-values, type I/II errors, power analysis, and multiple testing correction -- these are critical for A/B testing, model comparison, and feature selection. This is one of the most frequently tested topics at tech companies.

## Core Concepts

### Framework

1. State null hypothesis $H_0$ and alternative $H_1$
2. Choose significance level $\alpha$ (typically 0.05)
3. Compute test statistic and p-value
4. Reject $H_0$ if p-value $< \alpha$

### Error Types

| | $H_0$ true | $H_0$ false |
|---|---|---|
| Reject $H_0$ | Type I error ($\alpha$) | Correct (Power = $1-\beta$) |
| Fail to reject | Correct ($1-\alpha$) | Type II error ($\beta$) |

### P-value

$$
p\text{-value} = P(\text{test stat} \geq \text{observed} \mid H_0 \text{ true})
$$

**NOT** the probability that $H_0$ is true. It is the probability of seeing data this extreme under $H_0$.

### Common Test Statistics

**Z-test** (known variance):

$$
Z = \frac{\bar{X} - \mu_0}{\sigma / \sqrt{n}} \sim N(0,1)
$$

**Two-sample t-test** (A/B testing):

$$
t = \frac{\bar{X}_A - \bar{X}_B}{\sqrt{\frac{s_A^2}{n_A} + \frac{s_B^2}{n_B}}} \sim t_\nu
$$

**Chi-squared test** (categorical data):

$$
\chi^2 = \sum_i \frac{(O_i - E_i)^2}{E_i}
$$

### Power Analysis

$$
\text{Power} = P(\text{reject } H_0 \mid H_1 \text{ true}) = 1 - \beta
$$

Required sample size for two-sample test with effect size $\delta$:

$$
n \geq \frac{(z_{\alpha/2} + z_\beta)^2 \cdot 2\sigma^2}{\delta^2}
$$

### Multiple Testing Correction

When testing $m$ hypotheses simultaneously:

- **Bonferroni**: reject if $p_i < \alpha/m$ (controls FWER)
- **Benjamini-Hochberg**: controls FDR at level $\alpha$
  1. Sort p-values: $p_{(1)} \leq \ldots \leq p_{(m)}$
  2. Find largest $k$ where $p_{(k)} \leq \frac{k}{m}\alpha$
  3. Reject all $H_{(1)}, \ldots, H_{(k)}$

## Implementation

```python
import numpy as np
from scipy import stats

def two_sample_test(
    group_a: np.ndarray, group_b: np.ndarray,
) -> dict[str, float]:
    # Two-sample t-test for A/B testing.
    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
    effect_size = (group_b.mean() - group_a.mean()) / np.sqrt(
        (group_a.var(ddof=1) + group_b.var(ddof=1)) / 2
    )  # Cohen's d
    return {"t_stat": t_stat, "p_value": p_value, "cohens_d": effect_size}


def required_sample_size_ab(
    baseline_rate: float, mde: float,
    alpha: float = 0.05, power: float = 0.8,
) -> int:
    # Sample size per group for a proportion A/B test.
    p1 = baseline_rate
    p2 = baseline_rate + mde
    pooled_var = p1 * (1 - p1) + p2 * (1 - p2)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    n = pooled_var * (z_alpha + z_beta) ** 2 / mde**2
    return int(np.ceil(n))


def benjamini_hochberg(p_values: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    # Benjamini-Hochberg FDR correction. Returns boolean mask of rejections.
    m = len(p_values)
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]
    thresholds = np.arange(1, m + 1) / m * alpha
    # Find largest k where p_(k) <= k/m * alpha
    below = sorted_p <= thresholds
    if not below.any():
        return np.zeros(m, dtype=bool)
    k = np.max(np.where(below)[0])
    rejected = np.zeros(m, dtype=bool)
    rejected[sorted_idx[:k + 1]] = True
    return rejected
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| A/B test design | Product experiments | Pre-compute sample size, run to completion |
| Sequential testing | Early stopping | Use O'Brien-Fleming or always-valid p-values |
| Multiple comparisons | Multi-variant tests | BH controls FDR; Bonferroni controls FWER |
| Practical significance | Beyond p-values | Small p-value with tiny effect = not useful |

### Common Interview Questions
- [ ] Design an A/B test for a new recommendation algorithm. How do you determine sample size?
- [ ] What is the difference between statistical and practical significance?
- [ ] Explain p-value. Why is "$p < 0.05$" not the same as "95% chance the treatment works"?
- [ ] You run 20 A/B tests and find 1 significant at $\alpha=0.05$. Is this real?
- [ ] How would you handle early stopping in an A/B test?

## Comparisons

| Aspect | Frequentist testing | Bayesian testing |
|--------|-------------------|-----------------|
| Output | p-value, reject/fail | Posterior odds, Bayes factor |
| Interpretation | Long-run error control | Direct probability statements |
| Sample size | Fixed in advance | Can update continuously |
| Multiple testing | Requires correction | Naturally handled by priors |
| Industry use | A/B testing standard | Growing adoption (Optimizely) |

## Key Takeaways
- P-value is NOT $P(H_0 \text{ true})$ -- it is $P(\text{data this extreme} \mid H_0)$
- Always compute required sample size BEFORE running an experiment
- Multiple testing without correction inflates false discoveries
- Effect size matters as much as statistical significance
"""

CONTENT["pillar7.probability_statistics.bayesian_inference"] = r"""# Bayesian Inference

## Overview
Bayesian inference provides a principled framework for updating beliefs with data. For a senior MLE, this encompasses posterior computation, conjugate models, MCMC methods, and variational inference. Bayesian methods are critical for uncertainty quantification, Thompson sampling in bandits, and Bayesian neural networks.

## Core Concepts

### Bayesian Update

$$
P(\theta \mid D) = \frac{P(D \mid \theta)\, P(\theta)}{P(D)} \propto P(D \mid \theta)\, P(\theta)
$$

### Conjugate Prior Families

| Likelihood | Prior | Posterior | Update Rule |
|-----------|-------|-----------|-------------|
| Bernoulli($p$) | Beta($\alpha, \beta$) | Beta($\alpha + k, \beta + n - k$) | Add successes/failures |
| Poisson($\lambda$) | Gamma($\alpha, \beta$) | Gamma($\alpha + \sum x_i, \beta + n$) | Add counts and observations |
| Normal($\mu$, known $\sigma^2$) | Normal($\mu_0, \sigma_0^2$) | Normal($\tilde{\mu}, \tilde{\sigma}^2$) | Precision-weighted average |
| Normal(known $\mu$, $\sigma^2$) | Inv-Gamma($\alpha, \beta$) | Inv-Gamma($\alpha + n/2, \beta + S/2$) | Add scaled residuals |

**Normal-Normal posterior** (known variance $\sigma^2$):

$$
\tilde{\mu} = \frac{\frac{\mu_0}{\sigma_0^2} + \frac{n\bar{x}}{\sigma^2}}{\frac{1}{\sigma_0^2} + \frac{n}{\sigma^2}}, \quad \tilde{\sigma}^2 = \frac{1}{\frac{1}{\sigma_0^2} + \frac{n}{\sigma^2}}
$$

### Markov Chain Monte Carlo (MCMC)

**Metropolis-Hastings**: Given current state $\theta$, propose $\theta' \sim q(\theta' \mid \theta)$, accept with probability:

$$
\alpha = \min\!\left(1, \frac{P(\theta' \mid D)\, q(\theta \mid \theta')}{P(\theta \mid D)\, q(\theta' \mid \theta)}\right)
$$

**Gibbs Sampling**: Special case where each parameter is sampled from its full conditional:

$$
\theta_j^{(t+1)} \sim P(\theta_j \mid \theta_{-j}^{(t)}, D)
$$

### Variational Inference

Approximate posterior $P(\theta \mid D)$ with tractable $q(\theta; \phi)$:

$$
\phi^* = \arg\min_\phi \text{KL}(q(\theta; \phi) \| P(\theta \mid D))
$$

Equivalent to maximizing the ELBO:

$$
\text{ELBO}(\phi) = E_{q}[\log P(D \mid \theta)] - \text{KL}(q(\theta; \phi) \| P(\theta))
$$

## Implementation

```python
import numpy as np

def beta_binomial_update(
    alpha_prior: float, beta_prior: float,
    successes: int, failures: int,
) -> tuple[float, float]:
    # Bayesian update for Beta-Binomial conjugate model.
    alpha_post = alpha_prior + successes
    beta_post = beta_prior + failures
    return alpha_post, beta_post


def thompson_sampling(
    alphas: np.ndarray, betas: np.ndarray,
) -> int:
    # Thompson sampling for multi-armed bandit.
    rng = np.random.default_rng()
    samples = rng.beta(alphas, betas)
    return int(np.argmax(samples))


def metropolis_hastings(
    log_posterior_fn: callable,
    initial: np.ndarray,
    n_samples: int = 10000,
    proposal_std: float = 0.1,
) -> np.ndarray:
    # Simple Metropolis-Hastings sampler.
    rng = np.random.default_rng(42)
    d = len(initial)
    samples = np.zeros((n_samples, d))
    current = initial.copy()
    current_lp = log_posterior_fn(current)

    for i in range(n_samples):
        proposal = current + rng.normal(0, proposal_std, d)
        proposal_lp = log_posterior_fn(proposal)
        log_alpha = proposal_lp - current_lp
        if np.log(rng.random()) < log_alpha:
            current = proposal
            current_lp = proposal_lp
        samples[i] = current

    return samples
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Conjugate updates | Online learning, bandits | Closed-form posterior updates |
| Thompson sampling | Exploration-exploitation | Sample from posterior, act greedily |
| ELBO maximization | Scalable Bayesian DL | VI trades exactness for speed |
| Credible intervals | Uncertainty quantification | 95% CI = 95% probability $\theta$ is inside |

### Common Interview Questions
- [ ] Derive the posterior for the Beta-Binomial conjugate model.
- [ ] Explain Thompson sampling and compare it to epsilon-greedy.
- [ ] What is the ELBO and why do we maximize it instead of minimizing KL directly?
- [ ] How does MCMC work? What are the convergence diagnostics?
- [ ] When would you prefer Bayesian inference over MLE?

## Comparisons

| Aspect | MCMC | Variational Inference |
|--------|------|----------------------|
| Accuracy | Asymptotically exact | Approximate |
| Speed | Slow (sequential) | Fast (optimization) |
| Scalability | Millions of params: hard | Billions of params: OK |
| Diagnostics | $\hat{R}$, ESS, trace plots | ELBO convergence |
| Use case | Small models, gold standard | VAEs, BNNs, large-scale |

## Key Takeaways
- Bayesian inference gives uncertainty estimates -- not just point predictions
- Conjugate priors enable analytically tractable updates for online learning
- Thompson sampling is the Bayesian approach to exploration-exploitation
- VI scales Bayesian methods to deep learning via the ELBO
"""

CONTENT["pillar7.probability_statistics.information_theory"] = r"""# Information Theory

## Overview
Information theory provides the mathematical framework for quantifying uncertainty, information content, and divergence between distributions. For a senior MLE, these concepts underpin cross-entropy loss, KL divergence, mutual information for feature selection, and the information bottleneck principle. Frequently tested in theoretical interviews at Google, Meta, and research-oriented roles.

## Core Concepts

### Entropy

$$
H(X) = -\sum_x P(x) \log P(x) = E[-\log P(X)]
$$

For continuous RVs (differential entropy):

$$
h(X) = -\int f(x) \log f(x)\, dx
$$

Properties:
- $H(X) \geq 0$ (discrete), $h(X)$ can be negative (continuous)
- Maximum entropy discrete: uniform. Maximum entropy continuous with fixed $\mu, \sigma^2$: Gaussian.
- $H(X, Y) = H(X) + H(Y \mid X) = H(Y) + H(X \mid Y)$

### Cross-Entropy

$$
H(p, q) = -\sum_x p(x) \log q(x) = H(p) + D_{\text{KL}}(p \| q)
$$

This is exactly the loss function for classification: $p$ = true labels, $q$ = model predictions.

### KL Divergence

$$
D_{\text{KL}}(p \| q) = \sum_x p(x) \log \frac{p(x)}{q(x)} = E_p\!\left[\log \frac{p(X)}{q(X)}\right]
$$

Properties:
- $D_{\text{KL}}(p \| q) \geq 0$ (Gibbs' inequality)
- NOT symmetric: $D_{\text{KL}}(p \| q) \neq D_{\text{KL}}(q \| p)$
- $D_{\text{KL}}(p \| q) = 0 \iff p = q$

**Forward vs. reverse KL**:
- $D_{\text{KL}}(p \| q)$: mean-seeking (q covers all modes of p)
- $D_{\text{KL}}(q \| p)$: mode-seeking (q concentrates on one mode)

### Mutual Information

$$
I(X; Y) = H(X) - H(X \mid Y) = H(Y) - H(Y \mid X) = D_{\text{KL}}(P_{XY} \| P_X P_Y)
$$

$I(X; Y) = 0 \iff X \perp Y$. Symmetric and non-negative.

### KL Between Gaussians

$$
D_{\text{KL}}(N_0 \| N_1) = \frac{1}{2}\left[\log\frac{|\Sigma_1|}{|\Sigma_0|} - d + \text{tr}(\Sigma_1^{-1}\Sigma_0) + (\mu_1-\mu_0)^\top \Sigma_1^{-1}(\mu_1-\mu_0)\right]
$$

This formula is used directly in the VAE loss.

## Implementation

```python
import numpy as np

def entropy(probs: np.ndarray) -> float:
    # Shannon entropy of a discrete distribution.
    p = probs[probs > 0]
    return -float((p * np.log2(p)).sum())


def cross_entropy(p: np.ndarray, q: np.ndarray) -> float:
    # Cross-entropy H(p, q).
    mask = p > 0
    return -float((p[mask] * np.log(q[mask])).sum())


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    # KL divergence D_KL(p || q).
    mask = p > 0
    return float((p[mask] * np.log(p[mask] / q[mask])).sum())


def mutual_information(joint: np.ndarray) -> float:
    # Mutual information from a joint probability table.
    p_x = joint.sum(axis=1)
    p_y = joint.sum(axis=0)
    outer = np.outer(p_x, p_y)
    mask = (joint > 0) & (outer > 0)
    return float((joint[mask] * np.log(joint[mask] / outer[mask])).sum())


def kl_gaussians_multivariate(
    mu0: np.ndarray, cov0: np.ndarray,
    mu1: np.ndarray, cov1: np.ndarray,
) -> float:
    # KL(N0 || N1) for multivariate Gaussians.
    d = len(mu0)
    cov1_inv = np.linalg.inv(cov1)
    diff = mu1 - mu0
    return 0.5 * (
        np.log(np.linalg.det(cov1) / np.linalg.det(cov0))
        - d
        + np.trace(cov1_inv @ cov0)
        + diff @ cov1_inv @ diff
    )
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Cross-entropy loss | Classification | Minimizing CE = minimizing KL from true dist. |
| KL in VAE | Generative models | ELBO = reconstruction - KL regularizer |
| MI for feature selection | High-dimensional data | MI captures nonlinear dependencies |
| Forward vs reverse KL | Choosing divergence | Mean-seeking vs mode-seeking behavior |

### Common Interview Questions
- [ ] Why do we use cross-entropy loss instead of MSE for classification?
- [ ] Explain KL divergence. Why is it not symmetric? Give an intuitive example.
- [ ] Derive the KL divergence between two univariate Gaussians.
- [ ] What is mutual information and how does it relate to feature selection?
- [ ] Explain the information bottleneck principle.

## Comparisons

| Aspect | KL Divergence | JS Divergence | Wasserstein |
|--------|--------------|---------------|-------------|
| Symmetry | No | Yes | Yes |
| Triangle inequality | No | Yes (sqrt) | Yes |
| Bounded | No | Yes ($\leq \log 2$) | No |
| Zero support handling | Undefined if $q(x)=0$ | Defined | Defined |
| GAN use | Original GAN (theory) | -- | WGAN |

## Key Takeaways
- Cross-entropy loss IS negative log-likelihood, which IS minimizing KL to true distribution
- KL divergence asymmetry matters: forward KL for VI, reverse KL for EM
- Mutual information is the gold standard for measuring any dependence between variables
- The VAE loss is reconstruction + KL(encoder || prior) -- both terms from information theory
"""

# ===== LINEAR ALGEBRA =====

CONTENT["pillar7.linear_algebra.matrix_operations"] = r"""# Matrix Operations

## Overview
Linear algebra is the computational backbone of ML. A senior MLE must be fluent in matrix operations, decompositions, and their computational complexity. Matrix multiplication, inverses, and norms appear in every layer of neural networks, kernel methods, and optimization algorithms.

## Core Concepts

### Fundamental Operations

| Operation | Notation | Complexity | Notes |
|-----------|----------|------------|-------|
| Matrix multiply | $C = AB$ | $O(n^2m)$ for $A_{n \times m}, B_{m \times p}$ | Most common bottleneck |
| Transpose | $A^\top$ | $O(1)$ (logical) | $(AB)^\top = B^\top A^\top$ |
| Inverse | $A^{-1}$ | $O(n^3)$ | Avoid computing explicitly |
| Determinant | $\det(A)$ | $O(n^3)$ via LU | $\det(AB) = \det(A)\det(B)$ |
| Trace | $\text{tr}(A)$ | $O(n)$ | $\text{tr}(AB) = \text{tr}(BA)$ |

### Matrix Types and Properties

| Type | Definition | Key Property |
|------|-----------|-------------|
| Symmetric | $A = A^\top$ | Real eigenvalues, orthogonal eigenvectors |
| Orthogonal | $A^\top A = I$ | Preserves norms: $\|Ax\| = \|x\|$ |
| Positive definite | $x^\top A x > 0, \forall x \neq 0$ | All eigenvalues $> 0$ |
| Positive semi-definite | $x^\top A x \geq 0$ | All eigenvalues $\geq 0$ |
| Idempotent | $A^2 = A$ | Projection matrices |

### Norms

**Vector norms**:

$$
\|x\|_1 = \sum|x_i|, \quad \|x\|_2 = \sqrt{\sum x_i^2}, \quad \|x\|_\infty = \max|x_i|
$$

**Matrix norms**:

$$
\|A\|_F = \sqrt{\sum_{ij} a_{ij}^2} = \sqrt{\text{tr}(A^\top A)}, \quad \|A\|_2 = \sigma_{\max}(A)
$$

### Rank and Null Space

$$
\text{rank}(A) + \text{nullity}(A) = n \quad \text{(rank-nullity theorem)}
$$

- $\text{rank}(A) = \text{rank}(A^\top) = \text{rank}(A^\top A)$
- $A$ is invertible $\iff$ $\text{rank}(A) = n$ $\iff$ $\det(A) \neq 0$

### Solving Linear Systems

Never compute $A^{-1}b$ explicitly. Instead:

1. **LU decomposition**: general case, $O(n^3)$
2. **Cholesky**: $A = LL^\top$ for PD matrices, $O(n^3/3)$ -- 2x faster than LU
3. **QR decomposition**: for least squares, numerically stable

$$
\text{Least squares}: \hat{x} = (A^\top A)^{-1} A^\top b \quad \text{(normal equations)}
$$

## Implementation

```python
import numpy as np

def solve_least_squares(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Solve least squares via QR (more stable than normal equations).
    Q, R = np.linalg.qr(A)
    return np.linalg.solve(R, Q.T @ b)


def condition_number(A: np.ndarray) -> float:
    # Condition number = sigma_max / sigma_min.
    s = np.linalg.svd(A, compute_uv=False)
    return float(s[0] / s[-1]) if s[-1] > 0 else float("inf")


def is_positive_definite(A: np.ndarray) -> bool:
    # Check PD via Cholesky decomposition.
    try:
        np.linalg.cholesky(A)
        return True
    except np.linalg.LinAlgError:
        return False


def gram_schmidt(V: np.ndarray) -> np.ndarray:
    # Orthogonalize columns of V via modified Gram-Schmidt.
    n, k = V.shape
    Q = np.zeros_like(V, dtype=float)
    for j in range(k):
        q = V[:, j].astype(float)
        for i in range(j):
            q -= np.dot(Q[:, i], q) * Q[:, i]
        norm = np.linalg.norm(q)
        if norm > 1e-10:
            Q[:, j] = q / norm
    return Q
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Avoid explicit inverse | Any $Ax = b$ | Use `np.linalg.solve`, not `np.linalg.inv` |
| Cholesky for PD systems | Covariance matrices, kernels | 2x faster than general solver |
| Condition number check | Numerical stability | High $\kappa$ = numerically unstable |
| Low-rank approximation | Dimensionality reduction | Keep top-$k$ singular values |

### Common Interview Questions
- [ ] Why should you never compute matrix inverses explicitly in practice?
- [ ] What is the condition number and why does it matter for ML?
- [ ] Prove that $A^\top A$ is always positive semi-definite.
- [ ] What is the rank of the outer product $uv^\top$?
- [ ] Explain the difference between Frobenius norm and spectral norm.

## Comparisons

| Solver | When to Use | Complexity | Stability |
|--------|------------|------------|-----------|
| LU | General systems | $O(n^3)$ | Good |
| Cholesky | PD systems (covariance) | $O(n^3/3)$ | Excellent |
| QR | Least squares | $O(2mn^2)$ | Best |
| SVD | Rank-deficient systems | $O(mn^2)$ | Best |

## Key Takeaways
- Never compute $A^{-1}$ explicitly -- always use decomposition-based solvers
- Positive definiteness is pervasive: covariance matrices, kernel matrices, Hessians
- Condition number predicts numerical issues -- add regularization ($A + \lambda I$) if high
- Frobenius norm = "element-wise L2", spectral norm = largest singular value
"""

CONTENT["pillar7.linear_algebra.eigendecomposition"] = r"""# Eigendecomposition

## Overview
Eigendecomposition reveals the fundamental structure of linear transformations. A senior MLE uses eigenvalues and eigenvectors in PCA, spectral clustering, PageRank, Hessian analysis for optimization, and covariance matrix analysis. This is a core theoretical topic that appears in interviews at all major companies.

## Core Concepts

### Definition

For a square matrix $A \in \mathbb{R}^{n \times n}$, eigenvalue $\lambda$ and eigenvector $v \neq 0$:

$$
Av = \lambda v
$$

Eigenvalues satisfy the characteristic equation:

$$
\det(A - \lambda I) = 0
$$

### Eigendecomposition (Spectral Decomposition)

For a diagonalizable matrix:

$$
A = V \Lambda V^{-1}
$$

where $V = [v_1 | \cdots | v_n]$ and $\Lambda = \text{diag}(\lambda_1, \ldots, \lambda_n)$.

For **symmetric** matrices ($A = A^\top$):

$$
A = Q \Lambda Q^\top, \quad Q^\top Q = I
$$

Properties of symmetric eigendecomposition:
- All eigenvalues are **real**
- Eigenvectors are **orthogonal** (can be chosen orthonormal)
- $A$ is PD $\iff$ all $\lambda_i > 0$
- $A$ is PSD $\iff$ all $\lambda_i \geq 0$

### Key Properties

| Property | Formula |
|----------|---------|
| Trace | $\text{tr}(A) = \sum_i \lambda_i$ |
| Determinant | $\det(A) = \prod_i \lambda_i$ |
| Matrix power | $A^k = V \Lambda^k V^{-1}$ |
| Matrix exponential | $e^A = V e^\Lambda V^{-1}$ |
| Inverse | $A^{-1} = V \Lambda^{-1} V^{-1}$ (if all $\lambda_i \neq 0$) |

### PCA as Eigendecomposition

Given centered data matrix $X \in \mathbb{R}^{n \times d}$:

$$
C = \frac{1}{n-1} X^\top X
$$

Eigendecompose covariance: $C = Q \Lambda Q^\top$.

Top-$k$ principal components: project onto $Q_k$ (first $k$ eigenvectors).

**Variance explained** by component $j$: $\frac{\lambda_j}{\sum_i \lambda_i}$.

### Rayleigh Quotient

$$
R(A, x) = \frac{x^\top A x}{x^\top x}
$$

$\lambda_{\min} \leq R(A, x) \leq \lambda_{\max}$. Maximum is achieved at the top eigenvector. This is the optimization formulation of PCA.

## Implementation

```python
import numpy as np

def pca(X: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # PCA via eigendecomposition of covariance matrix.
    # Returns: (projected_data, eigenvectors, explained_variance_ratio)
    X_centered = X - X.mean(axis=0)
    cov = np.cov(X_centered, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Sort descending
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    explained_ratio = eigenvalues / eigenvalues.sum()
    projected = X_centered @ eigenvectors[:, :k]
    return projected, eigenvectors[:, :k], explained_ratio[:k]


def power_iteration(
    A: np.ndarray, n_iter: int = 100, tol: float = 1e-10,
) -> tuple[float, np.ndarray]:
    # Find dominant eigenvalue/eigenvector via power iteration.
    rng = np.random.default_rng(42)
    v = rng.normal(size=A.shape[0])
    v = v / np.linalg.norm(v)

    for _ in range(n_iter):
        w = A @ v
        eigenvalue = v @ w
        v_new = w / np.linalg.norm(w)
        if np.abs(np.abs(v_new @ v) - 1.0) < tol:
            break
        v = v_new

    return float(eigenvalue), v


def spectral_clustering_laplacian(
    W: np.ndarray, k: int,
) -> np.ndarray:
    # Compute bottom-k eigenvectors of graph Laplacian for spectral clustering.
    D = np.diag(W.sum(axis=1))
    L = D - W
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    # Bottom k eigenvectors (skip first if it's the trivial all-ones)
    return eigenvectors[:, :k]
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| PCA | Dimensionality reduction | Top eigenvectors of covariance = max variance directions |
| Spectral clustering | Graph-based clustering | Bottom eigenvectors of Laplacian |
| Power iteration | Dominant eigenvalue | $O(n^2)$ per iteration, for sparse/large matrices |
| Hessian eigenvalues | Optimization landscape | Positive eigenvalues = local convexity |

### Common Interview Questions
- [ ] Derive PCA from the variance maximization perspective using eigenvectors.
- [ ] What are the eigenvalues of a projection matrix? Of an orthogonal matrix?
- [ ] How does the power iteration method work? What is its convergence rate?
- [ ] Explain spectral clustering and the role of the graph Laplacian.
- [ ] If $A$ has eigenvalues $\lambda_i$, what are the eigenvalues of $A^2$? Of $A^{-1}$?

## Comparisons

| Aspect | Eigendecomposition | SVD |
|--------|-------------------|-----|
| Input | Square matrices only | Any matrix |
| Symmetric matrix | $A = Q\Lambda Q^\top$ | Same (eigenvalues = singular values if PSD) |
| Computation | $O(n^3)$ | $O(\min(mn^2, m^2n))$ |
| PCA | Via covariance matrix | Directly on data matrix |
| Stability | Less stable for non-symmetric | More numerically stable |

## Key Takeaways
- Eigendecomposition of symmetric matrices is the foundation of PCA and spectral methods
- PCA = finding top eigenvectors of the covariance matrix = directions of maximum variance
- Power iteration is simple and efficient for finding the dominant eigenvalue
- Eigenvalues of the Hessian determine the curvature of the loss landscape
"""

CONTENT["pillar7.linear_algebra.svd"] = r"""# Singular Value Decomposition (SVD)

## Overview
SVD is the most important matrix decomposition in ML. It works for any matrix (not just square), provides optimal low-rank approximations, and underpins PCA, LSA, recommender systems, and pseudoinverses. A senior MLE must know the decomposition, its properties, and practical applications.

## Core Concepts

### SVD Decomposition

For any matrix $A \in \mathbb{R}^{m \times n}$:

$$
A = U \Sigma V^\top
$$

| Component | Shape | Properties |
|-----------|-------|------------|
| $U$ | $m \times m$ | Orthogonal. Columns = left singular vectors |
| $\Sigma$ | $m \times n$ | Diagonal. $\sigma_1 \geq \sigma_2 \geq \cdots \geq 0$ |
| $V$ | $n \times n$ | Orthogonal. Columns = right singular vectors |

**Compact (thin) SVD**: $A = U_r \Sigma_r V_r^\top$ where $r = \text{rank}(A)$.

### Relationship to Eigendecomposition

$$
A^\top A = V \Sigma^2 V^\top, \quad AA^\top = U \Sigma^2 U^\top
$$

- Singular values = $\sqrt{\text{eigenvalues of } A^\top A}$
- Right singular vectors = eigenvectors of $A^\top A$
- Left singular vectors = eigenvectors of $AA^\top$

### Eckart-Young Theorem (Optimal Low-Rank Approximation)

$$
A_k = \sum_{i=1}^{k} \sigma_i u_i v_i^\top = \arg\min_{\text{rank}(B)=k} \|A - B\|_F
$$

This is why truncated SVD works for dimensionality reduction:

$$
\frac{\|A - A_k\|_F^2}{\|A\|_F^2} = \frac{\sum_{i=k+1}^{r} \sigma_i^2}{\sum_{i=1}^{r} \sigma_i^2}
$$

### Pseudoinverse (Moore-Penrose)

$$
A^+ = V \Sigma^+ U^\top, \quad \Sigma^+_{ii} = \begin{cases} 1/\sigma_i & \sigma_i > 0 \\ 0 & \sigma_i = 0 \end{cases}
$$

Solves least squares: $\hat{x} = A^+ b$ minimizes $\|Ax - b\|_2$.

### Applications in ML

| Application | How SVD is Used |
|-------------|----------------|
| PCA | Truncated SVD on centered data matrix |
| LSA/LSI | SVD on term-document TF-IDF matrix |
| Recommender systems | SVD on user-item rating matrix |
| Image compression | Low-rank approximation per channel |
| Pseudoinverse | Regularized least squares |
| Whitening | $X_w = X V \Sigma^{-1}$ |

## Implementation

```python
import numpy as np

def truncated_svd_pca(
    X: np.ndarray, k: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # PCA via truncated SVD (more stable than covariance eigen).
    X_centered = X - X.mean(axis=0)
    U, s, Vt = np.linalg.svd(X_centered, full_matrices=False)
    # Top k components
    projected = U[:, :k] * s[:k]  # = X_centered @ Vt[:k].T
    explained_ratio = (s[:k] ** 2) / (s**2).sum()
    return projected, Vt[:k], explained_ratio


def low_rank_approx(
    A: np.ndarray, k: int,
) -> tuple[np.ndarray, float]:
    # Rank-k approximation and relative error.
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    A_k = (U[:, :k] * s[:k]) @ Vt[:k]
    rel_error = np.sqrt((s[k:]**2).sum() / (s**2).sum())
    return A_k, float(rel_error)


def pseudoinverse_solve(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Solve least squares via pseudoinverse (SVD-based).
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    # Filter small singular values for numerical stability
    threshold = 1e-10 * s[0]
    s_inv = np.where(s > threshold, 1.0 / s, 0.0)
    return (Vt.T * s_inv) @ (U.T @ b)


def matrix_completion_svd(
    M: np.ndarray, mask: np.ndarray, k: int, n_iter: int = 50,
) -> np.ndarray:
    # Simple SVD-based matrix completion (iterative).
    filled = M.copy()
    for _ in range(n_iter):
        U, s, Vt = np.linalg.svd(filled, full_matrices=False)
        approx = (U[:, :k] * s[:k]) @ Vt[:k]
        filled = M * mask + approx * (1 - mask)
    return filled
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| SVD for PCA | High-dimensional data | More stable than covariance eigendecomposition |
| Low-rank factorization | Recommender systems | User/item embeddings from SVD |
| Pseudoinverse | Underdetermined/overdetermined systems | Minimum norm / least squares solution |
| Eckart-Young | Compression, denoising | Optimal under Frobenius and spectral norm |

### Common Interview Questions
- [ ] What is the relationship between SVD and PCA? When would you prefer SVD over eigendecomposition?
- [ ] Explain the Eckart-Young theorem and its significance for dimensionality reduction.
- [ ] How are singular values related to eigenvalues of $A^\top A$?
- [ ] Describe how SVD is used in recommender systems (matrix factorization).
- [ ] What is the pseudoinverse and when do you need it?

## Comparisons

| Aspect | Full SVD | Truncated SVD | Randomized SVD |
|--------|----------|---------------|----------------|
| Complexity | $O(\min(mn^2, m^2n))$ | $O(mnk)$ | $O(mn\log k)$ |
| Exact | Yes | Yes (top-k) | Approximate |
| Large matrices | Slow | Better | Fast |
| Implementation | `np.linalg.svd` | `scipy.sparse.linalg.svds` | `sklearn.utils.extmath.randomized_svd` |

## Key Takeaways
- SVD works for ANY matrix -- it is the most general decomposition
- Truncated SVD gives the best rank-$k$ approximation (Eckart-Young)
- Use SVD instead of eigendecomposition of $X^\top X$ for numerical stability
- SVD-based matrix factorization is the foundation of collaborative filtering
"""

# ===== CALCULUS & OPTIMIZATION =====

CONTENT["pillar7.calculus_optimization.multivariable_calculus"] = r"""# Multivariable Calculus

## Overview
Multivariable calculus is the mathematical language of ML optimization. A senior MLE must be fluent in gradients, Jacobians, Hessians, and Taylor expansions -- these appear in every gradient-based optimization algorithm, from SGD to Adam to second-order methods. This is the theoretical foundation for understanding how and why neural networks learn.

## Core Concepts

### Gradient

For $f: \mathbb{R}^n \to \mathbb{R}$:

$$
\nabla f(x) = \begin{bmatrix} \frac{\partial f}{\partial x_1} \\ \vdots \\ \frac{\partial f}{\partial x_n} \end{bmatrix}
$$

The gradient points in the direction of steepest ascent. $\|\nabla f\|$ gives the rate of change.

### Jacobian

For $f: \mathbb{R}^n \to \mathbb{R}^m$:

$$
J_f = \begin{bmatrix} \frac{\partial f_1}{\partial x_1} & \cdots & \frac{\partial f_1}{\partial x_n} \\ \vdots & \ddots & \vdots \\ \frac{\partial f_m}{\partial x_1} & \cdots & \frac{\partial f_m}{\partial x_n} \end{bmatrix} \in \mathbb{R}^{m \times n}
$$

### Hessian

For $f: \mathbb{R}^n \to \mathbb{R}$:

$$
H_f = \nabla^2 f = \begin{bmatrix} \frac{\partial^2 f}{\partial x_1^2} & \cdots & \frac{\partial^2 f}{\partial x_1 \partial x_n} \\ \vdots & \ddots & \vdots \\ \frac{\partial^2 f}{\partial x_n \partial x_1} & \cdots & \frac{\partial^2 f}{\partial x_n^2} \end{bmatrix}
$$

The Hessian is symmetric (Schwarz's theorem). Its eigenvalues determine curvature:
- All $\lambda_i > 0$: local minimum (PD)
- All $\lambda_i < 0$: local maximum (ND)
- Mixed signs: saddle point

### Taylor Expansion

**First order** (linear approximation):

$$
f(x + \delta) \approx f(x) + \nabla f(x)^\top \delta
$$

**Second order** (quadratic approximation):

$$
f(x + \delta) \approx f(x) + \nabla f(x)^\top \delta + \frac{1}{2} \delta^\top H_f(x)\, \delta
$$

This is the foundation of Newton's method: set gradient of quadratic to zero:

$$
\delta^* = -H_f^{-1} \nabla f
$$

### Common Matrix Calculus Identities

| Expression | Derivative |
|-----------|-----------|
| $f = a^\top x$ | $\nabla_x f = a$ |
| $f = x^\top A x$ | $\nabla_x f = (A + A^\top)x$ |
| $f = \|Ax - b\|_2^2$ | $\nabla_x f = 2A^\top(Ax - b)$ |
| $f = \log\det(X)$ | $\nabla_X f = X^{-\top}$ |
| $f = \text{tr}(AXB)$ | $\nabla_X f = A^\top B^\top$ (w.r.t. $X$) |

## Implementation

```python
import numpy as np

def numerical_gradient(
    f: callable, x: np.ndarray, eps: float = 1e-5,
) -> np.ndarray:
    # Central difference gradient approximation.
    grad = np.zeros_like(x)
    for i in range(len(x)):
        e_i = np.zeros_like(x)
        e_i[i] = eps
        grad[i] = (f(x + e_i) - f(x - e_i)) / (2 * eps)
    return grad


def numerical_hessian(
    f: callable, x: np.ndarray, eps: float = 1e-5,
) -> np.ndarray:
    # Finite difference Hessian approximation.
    n = len(x)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            e_i, e_j = np.zeros(n), np.zeros(n)
            e_i[i], e_j[j] = eps, eps
            H[i, j] = (
                f(x + e_i + e_j) - f(x + e_i - e_j)
                - f(x - e_i + e_j) + f(x - e_i - e_j)
            ) / (4 * eps**2)
            H[j, i] = H[i, j]
    return H


def gradient_descent(
    f: callable, grad_f: callable,
    x0: np.ndarray, lr: float = 0.01, n_iter: int = 1000,
) -> np.ndarray:
    # Simple gradient descent with fixed learning rate.
    x = x0.copy()
    for _ in range(n_iter):
        x -= lr * grad_f(x)
    return x


def newtons_method(
    grad_f: callable, hess_f: callable,
    x0: np.ndarray, n_iter: int = 50,
) -> np.ndarray:
    # Newton's method for optimization.
    x = x0.copy()
    for _ in range(n_iter):
        g = grad_f(x)
        H = hess_f(x)
        x -= np.linalg.solve(H, g)
    return x
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Gradient check | Debugging backprop | Compare analytical vs numerical gradient |
| Hessian analysis | Characterizing critical points | Eigenvalues determine min/max/saddle |
| Matrix calculus | Deriving update rules | Memorize key identities above |
| Taylor expansion | Understanding optimizers | Newton = quadratic approx minimization |

### Common Interview Questions
- [ ] Derive the gradient of the MSE loss $\|Xw - y\|^2$ with respect to $w$.
- [ ] What does the Hessian tell us about the loss landscape? How do saddle points affect training?
- [ ] Explain Newton's method. Why is it not used directly in deep learning?
- [ ] What is the Jacobian and when do you need it vs. the gradient?
- [ ] How would you numerically verify that your gradient computation is correct?

## Comparisons

| Method | Convergence | Cost per Step | Hessian Needed |
|--------|------------|---------------|----------------|
| Gradient descent | Linear $O(\kappa \log 1/\epsilon)$ | $O(n)$ | No |
| Newton's method | Quadratic | $O(n^3)$ | Yes |
| Quasi-Newton (L-BFGS) | Superlinear | $O(n)$ | Approximated |
| Conjugate gradient | $O(\sqrt{\kappa})$ steps | $O(n)$ | No (Hessian-vector products) |

## Key Takeaways
- The gradient is the foundation of all modern ML training
- Hessian eigenvalues determine optimization landscape geometry
- Newton's method is theoretically beautiful but computationally impractical for deep learning
- Matrix calculus identities save time in derivations -- memorize the key ones
"""

CONTENT["pillar7.calculus_optimization.chain_rule"] = r"""# Chain Rule & Backpropagation

## Overview
The chain rule is the single most important calculus concept in deep learning. It enables backpropagation, the algorithm that makes training neural networks feasible. A senior MLE must understand both the mathematical chain rule and its computational implementation as reverse-mode automatic differentiation.

## Core Concepts

### Univariate Chain Rule

For $y = f(g(x))$:

$$
\frac{dy}{dx} = \frac{dy}{dg} \cdot \frac{dg}{dx} = f'(g(x)) \cdot g'(x)
$$

### Multivariate Chain Rule

For $f: \mathbb{R}^n \to \mathbb{R}$ composed with $g: \mathbb{R}^m \to \mathbb{R}^n$:

$$
\frac{\partial f}{\partial x_j} = \sum_{i=1}^{n} \frac{\partial f}{\partial g_i} \cdot \frac{\partial g_i}{\partial x_j}
$$

In matrix form: $\nabla_x f = J_g^\top \nabla_g f$

### Backpropagation Algorithm

For a computation graph with loss $L$:

**Forward pass**: compute each node's value from inputs to output.

**Backward pass**: compute gradients from output back to inputs.

For layer $l$ with input $h_{l-1}$, weights $W_l$, and activation $\sigma$:

$$
z_l = W_l h_{l-1} + b_l, \quad h_l = \sigma(z_l)
$$

$$
\frac{\partial L}{\partial W_l} = \frac{\partial L}{\partial z_l} h_{l-1}^\top, \quad \frac{\partial L}{\partial h_{l-1}} = W_l^\top \frac{\partial L}{\partial z_l}
$$

$$
\frac{\partial L}{\partial z_l} = \frac{\partial L}{\partial h_l} \odot \sigma'(z_l)
$$

### Common Activation Derivatives

| Activation | $\sigma(z)$ | $\sigma'(z)$ |
|-----------|-------------|-------------|
| Sigmoid | $\frac{1}{1+e^{-z}}$ | $\sigma(z)(1-\sigma(z))$ |
| Tanh | $\frac{e^z - e^{-z}}{e^z + e^{-z}}$ | $1 - \tanh^2(z)$ |
| ReLU | $\max(0, z)$ | $\mathbf{1}[z > 0]$ |
| Softmax | $\frac{e^{z_i}}{\sum_j e^{z_j}}$ | $\text{diag}(s) - ss^\top$ |

### Forward vs Reverse Mode AD

For $f: \mathbb{R}^n \to \mathbb{R}^m$:

| Mode | Computes | Cost | Best When |
|------|----------|------|-----------|
| Forward (tangent) | One column of Jacobian per pass | $O(n)$ passes for full Jacobian | $n \ll m$ |
| Reverse (adjoint) | One row of Jacobian per pass | $O(m)$ passes for full Jacobian | $m \ll n$ |

Deep learning: $m = 1$ (scalar loss), $n$ = millions of parameters. Reverse mode = ONE backward pass for all gradients.

### Vanishing / Exploding Gradients

For an $L$-layer network:

$$
\frac{\partial L}{\partial W_1} \propto \prod_{l=2}^{L} W_l^\top \cdot \text{diag}(\sigma'(z_l))
$$

- If $\|W_l\| < 1$: gradients vanish exponentially
- If $\|W_l\| > 1$: gradients explode exponentially

**Solutions**: residual connections, gradient clipping, careful initialization (Xavier/He), LayerNorm/BatchNorm.

## Implementation

```python
import numpy as np

class Linear:
    # A single linear layer with manual backprop.

    def __init__(self, in_dim: int, out_dim: int) -> None:
        # Xavier initialization
        scale = np.sqrt(2.0 / (in_dim + out_dim))
        self.W = np.random.randn(out_dim, in_dim) * scale
        self.b = np.zeros(out_dim)
        self.grad_W: np.ndarray | None = None
        self.grad_b: np.ndarray | None = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        self.x = x  # cache for backward
        return self.W @ x + self.b

    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        self.grad_W = np.outer(grad_output, self.x)
        self.grad_b = grad_output
        return self.W.T @ grad_output  # gradient w.r.t. input


def relu_forward(z: np.ndarray) -> np.ndarray:
    return np.maximum(0, z)


def relu_backward(grad_output: np.ndarray, z: np.ndarray) -> np.ndarray:
    return grad_output * (z > 0).astype(float)


def softmax_cross_entropy_backward(
    logits: np.ndarray, targets: np.ndarray,
) -> np.ndarray:
    # Combined softmax + cross-entropy backward (numerically stable).
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()
    return probs - targets  # elegant gradient!
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Backprop derivation | "Derive gradients for layer X" | Chain rule + cache forward values |
| Vanishing gradients | Architecture design | ResNets, LSTM gates solve this |
| Gradient checking | Debugging custom layers | $\frac{f(x+\epsilon) - f(x-\epsilon)}{2\epsilon}$ |
| Softmax + CE gradient | Output layer | Simplifies to $\hat{y} - y$ |

### Common Interview Questions
- [ ] Derive backpropagation for a 2-layer MLP with ReLU activation.
- [ ] Why does backpropagation use reverse-mode AD? Why not forward-mode?
- [ ] Explain the vanishing gradient problem and 3 solutions.
- [ ] Derive the gradient of softmax cross-entropy loss. Why is it so simple?
- [ ] How do residual connections help gradient flow?

## Comparisons

| Aspect | Backpropagation | Numerical Differentiation | Symbolic Differentiation |
|--------|----------------|--------------------------|-------------------------|
| Accuracy | Exact (up to float) | Approximate ($O(\epsilon^2)$) | Exact |
| Speed | $O(\text{forward pass})$ | $O(n \cdot \text{forward})$ | Can be exponential |
| Memory | Stores activations | Minimal | Expression growth |
| Use case | Training | Gradient checking | Closed-form derivations |

## Key Takeaways
- Backpropagation IS the chain rule applied via reverse-mode automatic differentiation
- Reverse mode computes all parameter gradients in a single backward pass
- The vanishing gradient problem drove architectural innovations (ResNets, LSTMs, normalization)
- Softmax + cross-entropy gradient simplifying to $\hat{y} - y$ is both elegant and practically important
"""

CONTENT["pillar7.calculus_optimization.convex_optimization"] = r"""# Convex Optimization

## Overview
Convex optimization is the theoretical foundation of ML optimization. While deep learning is non-convex, understanding convexity provides guarantees for SVMs, logistic regression, and regularized models, and illuminates why techniques like learning rate scheduling and momentum work. A senior MLE must know convexity conditions, duality, KKT conditions, and optimization algorithms.

## Core Concepts

### Convex Sets and Functions

A set $C$ is **convex** if $\forall x, y \in C, \lambda \in [0,1]$: $\lambda x + (1-\lambda)y \in C$.

A function $f$ is **convex** if:

$$
f(\lambda x + (1-\lambda)y) \leq \lambda f(x) + (1-\lambda) f(y)
$$

Equivalent conditions (for twice-differentiable $f$):
- **First order**: $f(y) \geq f(x) + \nabla f(x)^\top (y - x)$ (tangent line underestimates)
- **Second order**: $\nabla^2 f(x) \succeq 0$ (Hessian is PSD everywhere)

**Strictly convex**: strict inequality (unique global minimum).

**Strongly convex** ($m$-strongly): $\nabla^2 f \succeq mI$, convergence rate depends on $m$.

### Convex ML Problems

| Problem | Convex? | Why |
|---------|---------|-----|
| Linear regression (MSE) | Yes | Quadratic in $w$ |
| Logistic regression | Yes | Sum of log-sum-exp (convex) |
| SVM (hinge loss + L2) | Yes | Convex loss + convex regularizer |
| Neural networks | No | Non-convex due to compositions |
| Lasso (L1) | Yes | Convex but non-smooth at 0 |

### Lagrangian Duality

For a constrained optimization $\min_x f(x)$ s.t. $g_i(x) \leq 0$, $h_j(x) = 0$:

**Lagrangian**:

$$
\mathcal{L}(x, \lambda, \nu) = f(x) + \sum_i \lambda_i g_i(x) + \sum_j \nu_j h_j(x)
$$

**Dual function**: $d(\lambda, \nu) = \min_x \mathcal{L}(x, \lambda, \nu)$

**Weak duality**: $d^* \leq f^*$ (always holds).

**Strong duality**: $d^* = f^*$ (holds for convex problems satisfying Slater's condition).

### KKT Conditions

Necessary (and sufficient for convex) conditions for optimality:

1. **Stationarity**: $\nabla_x \mathcal{L} = 0$
2. **Primal feasibility**: $g_i(x^*) \leq 0$, $h_j(x^*) = 0$
3. **Dual feasibility**: $\lambda_i \geq 0$
4. **Complementary slackness**: $\lambda_i g_i(x^*) = 0$

### Convergence Rates

| Algorithm | Convex | Strongly Convex ($\mu > 0$) |
|-----------|--------|----------------------------|
| GD | $O(1/T)$ | $O(e^{-\mu T / L})$ (linear) |
| SGD | $O(1/\sqrt{T})$ | $O(1/T)$ |
| Nesterov accelerated | $O(1/T^2)$ | $O(e^{-\sqrt{\mu/L}\, T})$ |
| Newton | Quadratic (local) | Quadratic (local) |

Condition number $\kappa = L/\mu$ controls convergence: high $\kappa$ = slow.

### Proximal Methods (for Non-Smooth Problems)

For $\min_x f(x) + g(x)$ where $f$ is smooth and $g$ is non-smooth (e.g., L1):

$$
x^{k+1} = \text{prox}_{\eta g}\!\left(x^k - \eta \nabla f(x^k)\right)
$$

**Proximal operator**: $\text{prox}_g(v) = \arg\min_x \left\{g(x) + \frac{1}{2}\|x - v\|^2\right\}$

For L1: $\text{prox}_{\lambda\|\cdot\|_1}(v)_i = \text{sign}(v_i)\max(|v_i| - \lambda, 0)$ (soft thresholding).

## Implementation

```python
import numpy as np

def gradient_descent_convex(
    grad_f: callable, x0: np.ndarray,
    lr: float, n_iter: int,
) -> list[np.ndarray]:
    # GD with convergence tracking.
    trajectory = [x0.copy()]
    x = x0.copy()
    for _ in range(n_iter):
        x = x - lr * grad_f(x)
        trajectory.append(x.copy())
    return trajectory


def proximal_l1(v: np.ndarray, lam: float) -> np.ndarray:
    # Proximal operator for L1 norm (soft thresholding).
    return np.sign(v) * np.maximum(np.abs(v) - lam, 0)


def ista(
    X: np.ndarray, y: np.ndarray, lam: float,
    n_iter: int = 1000,
) -> np.ndarray:
    # Iterative Shrinkage-Thresholding (ISTA) for Lasso.
    n, d = X.shape
    w = np.zeros(d)
    L = np.linalg.norm(X.T @ X, ord=2) / n  # Lipschitz constant
    lr = 1.0 / L

    for _ in range(n_iter):
        grad = X.T @ (X @ w - y) / n
        w = proximal_l1(w - lr * grad, lam * lr)
    return w


def check_kkt(
    x: np.ndarray, grad_f: np.ndarray,
    g_vals: np.ndarray, lambdas: np.ndarray,
    tol: float = 1e-6,
) -> dict[str, bool]:
    # Verify KKT conditions.
    return {
        "primal_feasible": bool((g_vals <= tol).all()),
        "dual_feasible": bool((lambdas >= -tol).all()),
        "complementary_slackness": bool(
            (np.abs(lambdas * g_vals) < tol).all()
        ),
    }
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Convexity check | Choosing optimizer | Convex = guaranteed global optimum |
| KKT conditions | SVM derivation | Support vectors have $\lambda_i > 0$ |
| L1 vs L2 regularization | Feature selection | L1 proximal = soft thresholding = sparsity |
| Learning rate from $L$ | Setting hyperparameters | $\eta \leq 1/L$ guarantees convergence |

### Common Interview Questions
- [ ] Prove that logistic regression loss is convex.
- [ ] Derive the SVM dual using Lagrangian duality and KKT conditions.
- [ ] Why does L1 regularization produce sparse solutions but L2 does not?
- [ ] What is the condition number and how does it affect gradient descent convergence?
- [ ] Explain why deep learning works despite non-convexity.

## Comparisons

| Aspect | GD | SGD | Adam |
|--------|-----|-----|------|
| Per-step cost | $O(n)$ (full batch) | $O(1)$ (one sample) | $O(1)$ + momentum |
| Convergence (convex) | $O(1/T)$ | $O(1/\sqrt{T})$ | $O(1/\sqrt{T})$ (theory) |
| Hyperparameters | $\eta$ | $\eta$, schedule | $\eta$, $\beta_1$, $\beta_2$ |
| Practice (DL) | Rarely used | Good with schedule | Default choice |

## Key Takeaways
- Convex problems have global optima -- no bad local minima or saddle points
- KKT conditions are necessary and sufficient for convex constrained optimization
- L1 regularization = Laplace prior = soft thresholding = sparsity
- Condition number $\kappa = L/\mu$ controls how fast gradient methods converge
- Deep learning is non-convex but works due to overparameterization and good optimization landscape structure
"""


# ---------------------------------------------------------------------------
# Main: apply content to database
# ---------------------------------------------------------------------------

def main() -> None:
    """Populate Pillar 7 leaf nodes with content."""
    engine = get_engine()
    SessionLocal.configure(bind=engine)

    with SessionLocal() as db:
        updated = 0
        missing = []

        for path, content in CONTENT.items():
            node = db.query(FrameworkNode).filter(
                FrameworkNode.path == path
            ).first()
            if node is None:
                missing.append(path)
                continue

            node.description = content.strip()
            updated += 1

        db.commit()

    print(f"Updated {updated} framework nodes.")
    if missing:
        print(f"WARNING: {len(missing)} paths not found: {missing}")
    print("Done.")


if __name__ == "__main__":
    main()
