# Naive Bayes and EM Algorithm

## Overview

Naive Bayes is one of the simplest yet surprisingly effective classifiers, grounded in Bayes' theorem with a strong (naive) independence assumption. The EM algorithm is a general-purpose iterative method for maximum likelihood estimation in latent variable models. Together they cover two interview-critical themes: probabilistic classification and parameter estimation under incomplete data. Both are frequently asked as warmup questions that test statistical foundations before deeper ML topics.

## Core Concepts

### Bayes' Theorem Foundation

Classification goal: find the label $Y$ that maximizes the posterior probability given features $X$:

$$
P(Y=k \mid X) = \frac{P(X \mid Y=k) \, P(Y=k)}{P(X)}
$$

Since $P(X)$ is constant across classes, the decision rule simplifies to:

$$
\hat{Y} = \arg\max_k \; P(X \mid Y=k) \, P(Y=k)
$$

$P(Y=k)$ is the **class prior** (estimated from label frequencies). $P(X \mid Y=k)$ is the **class-conditional likelihood** -- the hard part.

### The Naive Independence Assumption

Computing $P(X^1, \ldots, X^D \mid Y)$ directly requires exponential samples. The "naive" assumption treats features as conditionally independent given the class:

$$
P(X^1, \ldots, X^D \mid Y=k) = \prod_{d=1}^{D} P(X^d \mid Y=k)
$$

This reduces the estimation from $O(M^D)$ joint probabilities to $O(D \cdot M)$ univariate distributions ($M$ = number of unique values per feature).

**Why it works despite being wrong:** The assumption is almost always violated in practice, yet NB often performs well because:
- Classification only needs the correct **ranking** of posteriors, not accurate probability values
- Estimation errors across features tend to partially cancel out
- With limited data, the bias from independence is less harmful than the variance from estimating full joint distributions

### Discrete Naive Bayes (Multinomial/Categorical)

For categorical features, estimate class-conditional probabilities by counting:

$$
P(X^d = v_j \mid Y=k) = \frac{\text{count}(X^d = v_j \text{ and } Y=k)}{\text{count}(Y=k)}
$$

**Problem:** If a feature value $v_j$ never appears with class $k$ in training data, $P(X^d = v_j \mid Y=k) = 0$, which zeros out the entire product.

**Laplace smoothing** (additive smoothing with parameter $l$):

$$
P(X^d = v_j \mid Y=k) = \frac{\text{count}(X^d = v_j, Y=k) + l}{\text{count}(Y=k) + l \cdot M_d}
$$

$$
P(Y=k) = \frac{\text{count}(Y=k) + l}{N + l \cdot K}
$$

where $M_d$ = number of unique values of feature $d$, $K$ = number of classes, $N$ = total samples. When $l=1$, this is standard Laplace smoothing. The parameter $l$ controls the tradeoff between observed counts and a uniform prior.

### Gaussian Naive Bayes

For continuous features, model each $P(X^d \mid Y=k)$ as a Gaussian:

$$
P(X^d \mid Y=k) = \frac{1}{\sqrt{2\pi\sigma_{dk}^2}} \exp\left(-\frac{(X^d - \mu_{dk})^2}{2\sigma_{dk}^2}\right)
$$

Estimate parameters from class-specific sample statistics:

$$
\mu_{dk} = \mathbb{E}[X^d \mid Y=k], \quad \sigma_{dk}^2 = \mathbb{E}[(X^d - \mu_{dk})^2 \mid Y=k]
$$

**Limitation:** Assumes unimodal, symmetric distributions per feature per class. For multimodal data, this fails -- motivating the Gaussian Mixture Model (next section).

### EM Algorithm: Motivation and Intuition

When data has **latent (hidden) variables**, direct maximum likelihood estimation (MLE) is intractable because the log-likelihood involves a log of sums:

$$
\log L(\theta) = \sum_{i=1}^{N} \log \sum_{z} P(x_i, z \mid \theta)
$$

The log-sum makes taking derivatives and finding a closed-form solution impossible. The EM algorithm circumvents this by iteratively constructing and maximizing a **lower bound** on $\log L(\theta)$.

**Intuitive example (two coins):** Given flip results but not knowing which coin produced each result, EM alternates between:
1. Guessing which coin each result came from (soft assignment)
2. Updating coin bias estimates using weighted counts

### E-Step and M-Step

**E-Step (Expectation):** Compute the posterior distribution over latent variables given current parameters $\theta^{(t)}$:

$$
Q(z) = P(z \mid x, \theta^{(t)})
$$

This creates a complete-data expected log-likelihood (the lower bound):

$$
\mathbb{E}_{Q(z)}[\log P(x, z \mid \theta)]
$$

**M-Step (Maximization):** Find parameters that maximize this expected log-likelihood:

$$
\theta^{(t+1)} = \arg\max_\theta \; \mathbb{E}_{Q(z)}[\log P(x, z \mid \theta)]
$$

Each iteration is guaranteed to increase $\log L(\theta)$ (or leave it unchanged at convergence).

### Convergence Guarantee via Jensen's Inequality

The convergence proof relies on Jensen's inequality. Since $\log$ is concave:

$$
\log \sum_z Q(z) \frac{P(x, z \mid \theta)}{Q(z)} \geq \sum_z Q(z) \log \frac{P(x, z \mid \theta)}{Q(z)}
$$

The E-step chooses $Q(z) = P(z \mid x, \theta^{(t)})$ to make the bound **tight** (equality holds when $\frac{P(x,z \mid \theta)}{Q(z)}$ is constant). The M-step then pushes the bound upward. Since the log-likelihood is bounded above (for well-posed problems), convergence is guaranteed.

**Critical caveat:** Convergence is to a **local optimum** only. The initialization determines which local optimum is reached. Mitigation strategies:
- Multiple random restarts (pick best final likelihood)
- K-means initialization (for GMM)
- Deterministic initialization heuristics

### GMM: EM Applied to Gaussian Mixtures

A Gaussian Mixture Model assumes data comes from $K$ Gaussian components:

$$
P(x) = \sum_{k=1}^{K} \pi_k \, \mathcal{N}(x \mid \mu_k, \Sigma_k)
$$

where $\pi_k$ are mixing weights ($\sum_k \pi_k = 1$).

**E-Step:** Compute responsibility (soft assignment) of component $k$ for point $x_i$:

$$
\gamma_{ik} = \frac{\pi_k \, \mathcal{N}(x_i \mid \mu_k, \Sigma_k)}{\sum_{j=1}^{K} \pi_j \, \mathcal{N}(x_i \mid \mu_j, \Sigma_j)}
$$

**M-Step:** Update parameters using weighted statistics:

$$
\mu_k = \frac{\sum_i \gamma_{ik} x_i}{\sum_i \gamma_{ik}}, \quad \Sigma_k = \frac{\sum_i \gamma_{ik}(x_i - \mu_k)(x_i - \mu_k)^T}{\sum_i \gamma_{ik}}, \quad \pi_k = \frac{\sum_i \gamma_{ik}}{N}
$$

### EM and K-Means: The Connection

K-means is a special case of EM for GMM where:
- All covariances are $\sigma^2 I$ (spherical, equal)
- As $\sigma \to 0$, soft assignments $\gamma_{ik}$ become hard assignments (0 or 1)
- E-step becomes "assign to nearest centroid"
- M-step becomes "recompute centroid as mean of assigned points"

## Implementation

```python
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# --- Gaussian Naive Bayes (continuous features) ---
gnb = GaussianNB(var_smoothing=1e-9)  # smoothing added to variance
gnb.fit(X_train, y_train)
probs = gnb.predict_proba(X_test)  # calibrated posteriors

# --- Multinomial Naive Bayes (text/count data) ---
mnb = MultinomialNB(alpha=1.0)  # alpha = Laplace smoothing parameter
mnb.fit(X_train_counts, y_train)

# --- Gaussian Mixture Model (EM) ---
gmm = GaussianMixture(
    n_components=3,
    covariance_type="full",    # "full", "tied", "diag", "spherical"
    n_init=10,                  # multiple restarts
    init_params="kmeans",       # k-means initialization
    max_iter=200,
)
gmm.fit(X)
labels = gmm.predict(X)         # hard assignment
responsibilities = gmm.predict_proba(X)  # soft assignment (gamma)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| NB as baseline | Any classification task | Train in $O(ND)$, predict in $O(DK)$ -- hard to beat for speed |
| Laplace smoothing justification | Zero-probability issue | Without smoothing, one unseen feature zeroes entire posterior |
| Gaussian vs Multinomial NB | Feature type question | Gaussian for continuous; Multinomial for counts/frequencies; Bernoulli for binary |
| EM intuition explanation | Latent variable models | "Chicken and egg" -- alternate between guessing hidden state and updating parameters |
| GMM vs K-Means | Clustering algorithm choice | GMM gives soft assignments + models covariance; K-means is hard assignment + spherical only |
| EM convergence caveats | "Does EM always find the best solution?" | Guaranteed monotonic increase but only local optimum; use multiple restarts |

### Common Interview Questions

- [ ] When does the naive independence assumption actually work well?
- [ ] Explain the EM algorithm intuitively (use the two-coin example)
- [ ] Why might EM converge to a bad solution? How do you mitigate this?
- [ ] What is the relationship between EM and K-means?
- [ ] How does Laplace smoothing work and why is it necessary?
- [ ] Gaussian NB assumes what about each feature? When does this break?
- [ ] Compare generative (NB) vs discriminative (LR) classifiers

## Comparisons

### Naive Bayes Variants

| Aspect | Gaussian NB | Multinomial NB | Bernoulli NB |
|--------|------------|----------------|--------------|
| Feature type | Continuous | Counts/frequencies | Binary (0/1) |
| Distribution | $\mathcal{N}(\mu, \sigma^2)$ per feature | Multinomial per document | Bernoulli per feature |
| Smoothing | Variance smoothing | Laplace ($\alpha$) | Laplace ($\alpha$) |
| Use case | Sensor data, measurements | Text classification (TF) | Short text, binary features |
| Handles absent features | N/A (continuous) | Smoothing covers it | Explicitly models absence |

### Generative vs Discriminative Classifiers

| Aspect | Naive Bayes (Generative) | Logistic Regression (Discriminative) |
|--------|--------------------------|--------------------------------------|
| Models | Joint $P(X, Y)$ via $P(X \mid Y) P(Y)$ | Conditional $P(Y \mid X)$ directly |
| Training data needed | Less (uses prior structure) | More (no distributional assumptions) |
| Independence assumption | Required (naive) | Not required |
| Convergence speed | Reaches asymptote faster | Better asymptotic accuracy |
| Calibration | Often poor (extreme probabilities) | Better calibrated |
| Missing features | Handle naturally (skip missing) | Need imputation |

### EM Algorithm vs Alternatives

| Aspect | EM | Gradient Descent (MLE) | Variational Inference |
|--------|----|----------------------|----------------------|
| Latent variables | Native support | Requires marginalization | Native support |
| Convergence | Monotonic increase | Not guaranteed (step size) | Monotonic ELBO increase |
| Guarantees | Local optimum | Local optimum | Local optimum (of ELBO) |
| Closed-form updates | Often yes (exponential family) | No (iterative) | Sometimes |
| Scalability | $O(NKD)$ per iteration | Minibatch-friendly | Minibatch-friendly |

## Key Takeaways

- [ ] Naive Bayes decision rule: $\hat{Y} = \arg\max_k P(Y=k) \prod_d P(X^d \mid Y=k)$ -- maximize prior times likelihood
- [ ] Independence assumption reduces parameter count from exponential to linear in $D$
- [ ] Laplace smoothing adds $l$ to numerator and $l \cdot M$ to denominator to prevent zero probabilities
- [ ] Gaussian NB models each feature as $\mathcal{N}(\mu_{dk}, \sigma^2_{dk})$ per class -- fast but assumes unimodal
- [ ] EM alternates: E-step computes $Q(z) = P(z \mid x, \theta^{(t)})$; M-step maximizes expected complete-data log-likelihood
- [ ] Jensen's inequality guarantees EM monotonically increases log-likelihood, but only to a local optimum
- [ ] GMM is the canonical EM application: E-step computes responsibilities $\gamma_{ik}$, M-step updates $\mu_k, \Sigma_k, \pi_k$
- [ ] K-means is a hard-assignment, spherical-covariance special case of EM for GMM
