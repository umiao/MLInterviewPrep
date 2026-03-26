# Learning to Rank: From RankNet to LambdaMART

## Overview

Learning to Rank (LTR) transforms ranking from heuristic scoring into a supervised ML problem. The evolution from RankNet (pairwise loss) through LambdaRank (NDCG-weighted gradients) to LambdaMART (gradient boosted trees with lambda gradients) represents the standard progression in search and recommendation systems. LTR is a core component of multi-stage ranking pipelines at companies like DoorDash, Uber, and Airbnb -- expect it in any search/ranking-focused MLE interview.

**DoorDash relevance:** DoorDash's search ranking (restaurant/item ranking for a user query) is a classic LTR application. The phone screen may probe: how you would design the ranking pipeline, what features to use, how to define relevance labels, and the trade-offs between pointwise/pairwise/listwise approaches.

## Core Concepts

### Ranking Problem Formulation

Given a query $q$ and a set of candidate documents $\{d_1, d_2, \ldots, d_n\}$, a ranking model $f(x_i)$ produces a score $s_i$ for each document, where $x_i$ encodes query-document features. Documents are sorted by score to produce the ranked list.

Three paradigms:

| Paradigm | Loss Unit | Example | Pros | Cons |
|----------|-----------|---------|------|------|
| Pointwise | Single doc | Regression on relevance label | Simple, standard ML | Ignores relative order |
| Pairwise | Document pair | RankNet, LambdaRank | Captures relative preference | $O(n^2)$ pairs per query |
| Listwise | Full list | ListNet, LambdaMART | Directly optimizes list metrics | More complex |

### RankNet: Pairwise Loss Foundation

For documents $i$ and $j$ under the same query with $y_i > y_j$, RankNet models the probability that $i$ should rank above $j$:

$$P_{ij} = \frac{1}{1 + e^{-\sigma(s_i - s_j)}}$$

where $\sigma > 0$ controls sigmoid steepness.

The loss is cross-entropy between predicted and true pairwise probabilities:

$$C_{ij} = \log(1 + e^{-\sigma(s_i - s_j)})$$

This is a standard logistic loss on the score difference $s_i - s_j$.

**Gradient with respect to $s_i$:**

$$\frac{\partial C_{ij}}{\partial s_i} = -\sigma(1 - P_{ij})$$

Intuition:
- Model correct ($P_{ij} \approx 1$): gradient $\approx 0$, minimal update
- Model wrong ($P_{ij} \approx 0$): gradient $\approx -\sigma$, strong correction

**RankNet limitation:** All pairwise errors are weighted equally. Swapping rank 1 and rank 2 is penalized the same as swapping rank 99 and rank 100 -- but top-of-list errors matter far more to users.

### NDCG: Position-Sensitive Evaluation

$$DCG@K = \sum_{i=1}^{K} \frac{2^{y_{\pi(i)}} - 1}{\log_2(i + 1)}$$

$$NDCG@K = \frac{DCG@K}{IDCG@K}$$

where $IDCG@K$ is DCG under the ideal (sorted by label) ranking.

**Why NDCG cannot be directly optimized:** The ranking operation (argsort) is non-differentiable -- position is a step function of scores, with gradients zero or undefined everywhere. LambdaRank circumvents this by constructing an implicit objective that directly defines per-document pseudo-gradients.

### LambdaRank: NDCG-Weighted Pairwise Gradients

The key insight: weight each pairwise gradient by the NDCG impact of swapping those two documents.

For pair $(i, j)$ with $y_i > y_j$:

$$\lambda_{ij} = -\sigma(1 - P_{ij}) \cdot |\Delta NDCG_{ij}|$$

where $|\Delta NDCG_{ij}|$ is the absolute NDCG change from swapping positions $p_i$ and $p_j$:

$$|\Delta NDCG_{ij}| = \frac{1}{IDCG} \left|(2^{y_i} - 2^{y_j})\left(\frac{1}{\log_2(p_j+1)} - \frac{1}{\log_2(p_i+1)}\right)\right|$$

**Per-document aggregation:**

$$\lambda_i = \sum_{j: y_i > y_j} \lambda_{ij} - \sum_{j: y_j > y_i} \lambda_{ji}$$

This $\lambda_i$ is the pseudo-gradient: it tells the learner how much and in which direction to adjust document $i$'s score.

### LambdaMART: Lambda Gradients + Gradient Boosted Trees

LambdaMART = LambdaRank gradients + MART (Multiple Additive Regression Trees, i.e., GBDT).

XGBoost also needs second-order derivatives (Hessian) for tree splitting:

$$w_{ij} = \sigma^2 \cdot P_{ij}(1 - P_{ij}) \cdot |\Delta NDCG_{ij}|$$

Aggregated per document: $w_i = \sum_{j: y_i > y_j} w_{ij} + \sum_{j: y_j > y_i} w_{ji}$

**One boosting round:**
1. Score all documents with current model, sort per query
2. Enumerate pairs $(i, j)$ with different labels within each query group
3. Compute $|\Delta NDCG_{ij}|$ for each pair
4. Compute $\lambda_{ij}$ (gradient) and $w_{ij}$ (hessian) per pair
5. Aggregate to per-document $(\lambda_i, w_i)$
6. Build a new tree using $(\lambda_i, w_i)$ as (gradient, hessian) -- standard XGBoost splitting
7. Update scores: $s_i \leftarrow s_i + \eta \cdot f_t(x_i)$

The tree splitting criterion is identical to standard XGBoost regression:

$$\text{Gain} = \frac{1}{2}\left[\frac{G_L^2}{H_L + \lambda_{reg}} + \frac{G_R^2}{H_R + \lambda_{reg}} - \frac{(G_L + G_R)^2}{H_L + H_R + \lambda_{reg}}\right] - \gamma$$

### Why LambdaMART Beats Pure Pairwise

| Dimension | RankNet (pure pairwise) | LambdaMART (NDCG-weighted) |
|-----------|------------------------|---------------------------|
| Error weighting | All pairs equal | Top-position pairs weighted more |
| Metric alignment | Indirect (pairwise accuracy) | Direct (NDCG injected via delta) |
| Position sensitivity | None | Top errors penalized heavily |
| Model capacity allocation | Spread uniformly | Concentrated on user-visible positions |

### Signal Flow Summary

```
Relevance labels
      |
Current model scores -> Sort -> Enumerate pairs (i, j)
                                      |
                              Compute |delta_NDCG_ij|
                                      |
                        lambda_ij = RankNet_gradient * |delta_NDCG_ij|
                                      |
                        Aggregate per document -> (lambda_i, w_i)
                                      |
                        XGBoost builds new tree using (lambda_i, w_i)
                                      |
                        Update: s_i <- s_i + eta * f_t(x_i)
                                      |
                              Next round: re-sort, re-pair ...
```

## Implementation

### XGBoost LTR Configuration

```python
import xgboost as xgb

params = {
    "objective": "rank:ndcg",              # LambdaMART with NDCG weighting
    "eval_metric": "ndcg@10",              # Evaluate top-10 NDCG
    "lambdarank_pair_method": "topk",      # Bias pair sampling toward top positions
    "lambdarank_num_pair_per_sample": 8,   # Pairs per document
    "eta": 0.1,
    "max_depth": 6,
    "min_child_weight": 10,                # Min hessian sum in leaf
    "subsample": 0.8,
    "colsample_bytree": 0.8,
}

dtrain = xgb.DMatrix(X_train, label=y_train)
dtrain.set_group(group_sizes)  # docs per query: [5, 3, 8, ...]

dval = xgb.DMatrix(X_val, label=y_val)
dval.set_group(val_group_sizes)

model = xgb.train(
    params, dtrain,
    num_boost_round=500,
    evals=[(dval, "val")],
    early_stopping_rounds=50,
)
```

### Pair Sampling Strategies

| Strategy | Behavior | Best for |
|----------|----------|----------|
| `mean` | Uniform random pair sampling | General use |
| `topk` | Bias toward top-position pairs | `rank:ndcg` (recommended) |
| `map` | Bias toward MAP-relevant pairs | `rank:map` |

`topk` doubles down on position sensitivity: both the lambda weighting and the sampling favor top-of-list corrections.

### Query Group Setup

```python
# Method 1: set_group (list of group sizes)
group_sizes = [5, 3, 8]  # query 1 has 5 docs, query 2 has 3, ...
dtrain.set_group(group_sizes)

# Method 2: qid parameter (XGBoost >= 1.4)
dtrain = xgb.DMatrix(X_train, label=y_train, qid=query_ids)
```

Groups ensure pairs are only constructed within the same query -- never across queries.

### Gradient Computation Walkthrough

**Step 1: RankNet gradient for a single pair**

For pair $(i, j)$ with $y_i > y_j$, the RankNet cross-entropy loss is:

$$C_{ij} = \log(1 + e^{-\sigma(s_i - s_j)})$$

Differentiating with respect to $s_i$:

$$\frac{\partial C_{ij}}{\partial s_i} = \frac{-\sigma e^{-\sigma(s_i - s_j)}}{1 + e^{-\sigma(s_i - s_j)}} = -\sigma\left(1 - \frac{1}{1 + e^{-\sigma(s_i - s_j)}}\right) = -\sigma(1 - P_{ij})$$

By symmetry: $\frac{\partial C_{ij}}{\partial s_j} = \sigma(1 - P_{ij})$

**Step 2: NDCG swap delta**

Given $i$ at position $p_i$ and $j$ at position $p_j$, swapping only changes those two positions' DCG contributions:

$$\Delta DCG_{ij} = (2^{y_i} - 2^{y_j})\left(\frac{1}{\log_2(p_j+1)} - \frac{1}{\log_2(p_i+1)}\right)$$

$$|\Delta NDCG_{ij}| = \frac{|\Delta DCG_{ij}|}{IDCG}$$

**Step 3: Lambda = RankNet gradient * swap delta**

$$\lambda_{ij} = -\sigma(1 - P_{ij}) \cdot |\Delta NDCG_{ij}|$$

**Step 4: Hessian approximation for XGBoost**

$$w_{ij} = \sigma^2 \cdot P_{ij}(1 - P_{ij}) \cdot |\Delta NDCG_{ij}|$$

**Step 5: Per-document aggregation**

Each document sums over all pairs it participates in:

$$\lambda_i = \sum_{j: y_i > y_j} \lambda_{ij} - \sum_{j: y_j > y_i} \lambda_{ji}$$

$$w_i = \sum_{j: y_i > y_j} w_{ij} + \sum_{j: y_j > y_i} w_{ji}$$

The pair $(\lambda_i, w_i)$ is fed to XGBoost as the (gradient, hessian) for document $i$ -- from here, tree building proceeds identically to standard regression.

### XGBoost LTR Parameter Reference

**Ranking-specific parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `objective` | str | -- | `"rank:ndcg"` for LambdaMART with NDCG, `"rank:map"` for MAP, `"rank:pairwise"` for RankNet |
| `eval_metric` | str | -- | `"ndcg@K"`, `"map@K"`, or `"pre@K"` (precision). K is the cutoff |
| `lambdarank_pair_method` | str | `"mean"` | Pair sampling: `"mean"` (uniform), `"topk"` (top-biased, best for NDCG), `"map"` (MAP-biased) |
| `lambdarank_num_pair_per_sample` | int | 1 | How many pairs each document participates in per round. Higher = more compute, potentially better gradients |
| `lambdarank_unbiased` | bool | `false` | Enable unbiased LTR (IPW-based position bias correction) |
| `lambdarank_bias_norm` | float | 2.0 | Normalization term for the unbiased LTR position bias model |

**Tree parameters (same as regression, but tuning differs):**

| Parameter | Typical LTR Value | Why |
|-----------|-------------------|-----|
| `eta` (learning_rate) | 0.05-0.1 | Lower than regression; ranking gradients are noisier |
| `max_depth` | 4-8 | Deeper trees for complex feature interactions |
| `min_child_weight` | 10-100 | Higher than regression; min hessian sum in leaf prevents noisy splits from rare pairs |
| `subsample` | 0.7-0.9 | Row sampling reduces overfitting |
| `colsample_bytree` | 0.7-0.9 | Feature sampling for diversity |
| `gamma` | 0-1 | Min loss reduction for split; regularization |
| `lambda` (reg_lambda) | 1-10 | L2 regularization on leaf weights |
| `num_boost_round` | 200-1000 | Use early stopping to determine |

**Data format requirements:**
- Labels: integer relevance grades (e.g., 0-4). Higher = more relevant
- Groups: must specify which documents belong to the same query via `set_group()` or `qid=`
- Features: query-document feature vectors (not query features alone)

### Toy Example: 5 Documents (Full Hand Calculation)

**Setup:** One query, 5 documents with graded relevance labels (0-4 scale):

| Doc | Label ($y$) | Score ($s$) | Current Rank |
|-----|-------------|-------------|-------------|
| A   | 4           | 1.2         | 2           |
| B   | 1           | 1.5         | 1           |
| C   | 3           | 0.8         | 3           |
| D   | 0           | 0.5         | 4           |
| E   | 2           | 0.3         | 5           |

Current ranking: B -> A -> C -> D -> E. Problem: B (label=1) ranked #1, but A (label=4) should be #1.

**Step 1: Compute current NDCG**

| Position | Doc | gain = $2^y - 1$ | discount = $1/\log_2(i+1)$ | Contribution |
|----------|-----|-------------------|-----------------------------|-------------|
| 1 | B | $2^1 - 1 = 1$ | $1/\log_2 2 = 1.000$ | 1.000 |
| 2 | A | $2^4 - 1 = 15$ | $1/\log_2 3 = 0.631$ | 9.464 |
| 3 | C | $2^3 - 1 = 7$ | $1/\log_2 4 = 0.500$ | 3.500 |
| 4 | D | $2^0 - 1 = 0$ | $1/\log_2 5 = 0.431$ | 0.000 |
| 5 | E | $2^2 - 1 = 3$ | $1/\log_2 6 = 0.387$ | 1.161 |

$$DCG = 1.000 + 9.464 + 3.500 + 0.000 + 1.161 = 15.125$$

Ideal ranking: A -> C -> E -> B -> D (by label: 4, 3, 2, 1, 0):

$$IDCG = 15 \times 1.000 + 7 \times 0.631 + 3 \times 0.500 + 1 \times 0.431 + 0 \times 0.387 = 21.348$$

$$NDCG = \frac{15.125}{21.348} = 0.709$$

**Step 2: Compute $|\Delta NDCG|$ for key pairs**

Pair (A, B) -- A at position 2, B at position 1, $y_A=4 > y_B=1$:

$$\Delta DCG_{AB} = (2^4 - 2^1)\left(\frac{1}{\log_2(1+1)} - \frac{1}{\log_2(2+1)}\right) = (15 - 1)(1.000 - 0.631) = 14 \times 0.369 = 5.167$$

$$|\Delta NDCG_{AB}| = \frac{5.167}{21.348} = 0.2420$$

Pair (E, D) -- E at position 5, D at position 4, $y_E=2 > y_D=0$:

$$\Delta DCG_{ED} = (2^2 - 2^0)\left(\frac{1}{\log_2(4+1)} - \frac{1}{\log_2(5+1)}\right) = (3 - 0)(0.431 - 0.387) = 3 \times 0.044 = 0.132$$

$$|\Delta NDCG_{ED}| = \frac{0.132}{21.348} = 0.0062$$

**Comparison: top pair gets 39x the weight of bottom pair** -- this is the NDCG position weighting in action.

**Step 3: Compute lambda gradients ($\sigma = 1$)**

Pair (A, B): model has $s_A = 1.2 < s_B = 1.5$ (wrong order):

$$P_{AB} = \frac{1}{1 + e^{-(1.2 - 1.5)}} = \frac{1}{1 + e^{0.3}} = \frac{1}{2.350} = 0.4256$$

$$\lambda_{AB} = -(1 - 0.4256) \times 0.2420 = -0.5744 \times 0.2420 = -0.1390$$

- Doc A receives $\lambda = -0.1390$ (negative = push score UP)
- Doc B receives $\lambda = +0.1390$ (positive = push score DOWN)

Pair (E, D): model has $s_E = 0.3 < s_D = 0.5$ (wrong order):

$$P_{ED} = \frac{1}{1 + e^{-(0.3 - 0.5)}} = \frac{1}{1 + e^{0.2}} = \frac{1}{2.221} = 0.4502$$

$$\lambda_{ED} = -(1 - 0.4502) \times 0.0062 = -0.5498 \times 0.0062 = -0.0034$$

Near-zero -- the learner barely updates these bottom-ranked docs.

**Step 4: Aggregate per document**

Doc A participates in pairs with B, C, D, E (A has the highest label). Its total lambda is:

$$\lambda_A = \lambda_{AB} + \lambda_{AC} + \lambda_{AD} + \lambda_{AE}$$

where $\lambda_{AB}$ dominates (largest $|\Delta NDCG|$ because A is misranked at a top position). The result is a large negative $\lambda_A$, driving A's score strongly upward.

**Step 5: XGBoost builds a tree**

The $(\lambda_i, w_i)$ pairs are passed to XGBoost as (gradient, hessian). The tree splits to minimize the standard gain formula. After this tree, scores update: $s_i \leftarrow s_i + \eta \cdot f_t(x_i)$. Next round: re-sort, re-pair, re-compute lambdas. As A moves to position 1, $|\Delta NDCG|$ shrinks and gradients converge to zero.

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Pointwise vs pairwise vs listwise | "How would you approach ranking?" | Pointwise ignores order; pairwise captures preference; listwise optimizes list metrics directly |
| Why not optimize NDCG directly | "Why use lambda tricks?" | Argsort is non-differentiable; lambda gradients are pseudo-gradients that bypass this |
| Position discount in NDCG | "Why log denominator?" | Models diminishing user attention: position 1 matters far more than position 10 |
| Feature engineering for LTR | "What features for search ranking?" | Query-doc similarity, doc quality, user context, historical CTR, freshness |
| Multi-stage ranking | "Design a search system" | Candidate retrieval (cheap) -> first-pass ranking -> LTR re-ranking (expensive) |
| Online vs offline metrics | "How to evaluate ranking?" | Offline: NDCG, MAP, MRR. Online: CTR, conversion, session success |
| Cold-start items | "New items have no engagement data" | Blend content features with collaborative signals; explore-exploit tradeoffs |
| Label collection | "Where do relevance labels come from?" | Implicit (clicks, conversions, dwell time) or explicit (human raters) |
| DoorDash search ranking | Phone screen scenario | Query = user search, docs = restaurants/items, labels = order/click signals |
| Calibration in ranking | "Scores vs probabilities" | LTR scores are ordinal, not calibrated probabilities; separate calibration if needed |

### Common Interview Questions with Answers

**Q1: Explain the progression from RankNet to LambdaRank to LambdaMART.**

**RankNet** (2005, Burges et al.) introduced pairwise learning: for each pair of documents $(i, j)$ with $y_i > y_j$, it minimizes a logistic loss $C_{ij} = \log(1 + e^{-\sigma(s_i - s_j)})$ to ensure $s_i > s_j$. Limitation: all pair errors are weighted equally regardless of position -- swapping rank 1 and 2 is penalized the same as swapping rank 99 and 100.

**LambdaRank** (2006) keeps the RankNet gradient direction but multiplies it by $|\Delta NDCG_{ij}|$, the NDCG change from swapping positions $i$ and $j$. This creates a pseudo-gradient $\lambda_{ij} = -\sigma(1-P_{ij}) \cdot |\Delta NDCG_{ij}|$ that focuses learning on top-position errors. It doesn't have an explicit loss function -- it directly defines the gradient as if one existed, hence "lambda."

**LambdaMART** (2010) combines LambdaRank's pseudo-gradients with MART (gradient boosted trees). Instead of training a neural net, it feeds $(\lambda_i, w_i)$ as (gradient, hessian) to a tree ensemble. This gives the interpretability and efficiency of GBDT with NDCG-aware ranking optimization. XGBoost's `rank:ndcg` implements exactly this.

**Q2: Why can't we directly optimize NDCG? How does LambdaRank solve this?**

NDCG depends on the ranking (argsort) of documents by score. Argsort is a discrete operation -- each document's position is a step function of the scores, with gradient zero almost everywhere and undefined at the jumps. You cannot compute $\partial NDCG / \partial \theta$.

LambdaRank's solution: don't try to differentiate NDCG. Instead, for each document pair with different labels, define a pseudo-gradient that combines (a) the RankNet gradient direction (which pair member should score higher) with (b) the $|\Delta NDCG|$ magnitude (how much NDCG would change if their positions swapped). This implicitly optimizes an objective function whose gradient happens to be these lambdas. Empirically, models trained this way achieve higher NDCG than those optimizing surrogate losses like pairwise cross-entropy.

**Q3: What is the role of $|\Delta NDCG|$ in the lambda gradient?**

$|\Delta NDCG_{ij}|$ serves as a position-sensitive importance weight. It answers: "If the model swapped documents $i$ and $j$ in the current ranking, how much would NDCG change?"

- Swapping two documents near the top of the list (where discount $1/\log_2(k+1)$ is large) produces a large $|\Delta NDCG|$ -- these pairs get strong gradients.
- Swapping two documents deep in the list (where discount is tiny) produces near-zero $|\Delta NDCG|$ -- these pairs are effectively ignored.
- Swapping documents with very different relevance labels produces larger $|\Delta NDCG|$ than swapping documents with similar labels.

In the toy example: pair (A, B) at positions 1-2 gets $|\Delta NDCG| = 0.2420$, while pair (E, D) at positions 4-5 gets only $0.0062$ -- a 39x difference. This concentrates model capacity on the user-visible portion of the ranked list.

**Q4: How does XGBoost adapt its tree-building for ranking vs regression?**

The tree-building mechanism is **identical** -- the only difference is the gradient source.

In regression: gradients come from $\partial L / \partial \hat{y}$ for a pointwise loss $L$ (e.g., MSE).

In LambdaMART: gradients come from the aggregated lambda pseudo-gradients $\lambda_i$ (first-order) and $w_i$ (second-order Hessian approximation), computed from pairwise comparisons within each query group. These are fed into the same gain formula:

$$\text{Gain} = \frac{1}{2}\left[\frac{G_L^2}{H_L + \lambda_{reg}} + \frac{G_R^2}{H_R + \lambda_{reg}} - \frac{(G_L + G_R)^2}{H_L + H_R + \lambda_{reg}}\right] - \gamma$$

Leaf weights are computed as $w^* = -G_{leaf} / (H_{leaf} + \lambda_{reg})$, again identical to regression. The "ranking awareness" is entirely embedded in the lambdas, not in the tree structure.

The key additional requirement: a `group` (or `qid`) specification that tells XGBoost which documents share a query, so pairs are never constructed across queries.

**Q5: Design a restaurant ranking system for a food delivery app (DoorDash).**

See the dedicated DoorDash Phone Screen section below.

**Q6: What features would you use for search ranking? How to handle position bias?**

**Feature categories for food delivery ranking:**

1. **Query-document relevance**: BM25 text match between query and restaurant/item name, cuisine/category match, embedding cosine similarity (query vs restaurant description)
2. **Document quality**: average rating, review count, order volume (popularity), historical conversion rate, return customer rate
3. **User context**: distance from user, past order history (affinity to cuisine), dietary preferences, time of day (breakfast vs dinner), price sensitivity
4. **Real-time signals**: current estimated delivery time, restaurant open/closed status, current wait time, active promotions, stock availability
5. **Cross features**: user-restaurant affinity (collaborative filtering signal), query-category relevance for this specific user

**Position bias correction**: Users click top results more regardless of relevance. Two approaches:
- **Inverse Propensity Weighting (IPW)**: Estimate $P(\text{click} | \text{position})$ from randomized experiments, then weight each click by $1/P$ to debias. XGBoost supports this via `lambdarank_unbiased=True`.
- **Position as a feature**: Include display position as an input feature during training (using logged position), then set position=1 for all items at inference time (since all items will compete for position 1).

**Q7: Compare pointwise, pairwise, and listwise approaches with trade-offs.**

**Pointwise**: Treats each document independently. Train a regression model to predict relevance score (or classification for binary relevant/not). Loss: MSE, cross-entropy. Pros: simple, can use any standard ML model. Cons: completely ignores relative ordering between documents; the model doesn't know that getting rank 1 right matters more than rank 50; predicted scores may not produce good rankings.

**Pairwise** (RankNet): Converts the ranking problem into binary classification on pairs -- "should doc $i$ rank above doc $j$?" Loss: logistic loss on score difference. Pros: captures relative preferences, more aligned with ranking. Cons: $O(n^2)$ pairs per query (can be sampled); all pairs equally weighted regardless of position; optimizes pairwise accuracy which is only loosely correlated with NDCG.

**Listwise** (LambdaMART): Considers the entire ranked list. Uses pseudo-gradients weighted by $|\Delta NDCG|$ to focus on position-sensitive errors. Pros: directly optimizes ranking metrics, position-aware, state-of-the-art for tabular features. Cons: more complex to implement, requires query groups, $O(n^2)$ pair computation plus NDCG calculation per round.

**In practice**: Start with pointwise as baseline (fast iteration), move to LambdaMART for production ranking. Pure pairwise (RankNet) is rarely used directly -- LambdaMART strictly dominates it.

**Q8: How would you evaluate your ranking model offline and online?**

**Offline metrics** (computed on held-out labeled data):
- **NDCG@K**: Primary metric for graded relevance. Captures both relevance and position.
- **MAP**: Mean Average Precision -- better for binary relevance (relevant/not).
- **MRR**: Mean Reciprocal Rank -- for single-correct-answer scenarios (e.g., "find the exact restaurant").
- **Precision@K / Recall@K**: Simple binary metrics at cutoff K.
- **Pairwise accuracy**: Fraction of concordant pairs (useful for debugging, not for final evaluation).

**Online metrics** (from A/B tests):
- **CTR** (Click-Through Rate): Are users clicking on ranked results?
- **Conversion rate**: Are clicks turning into orders?
- **Average order value**: Is ranking driving higher-value orders?
- **Session success rate**: Does the user find what they want within the session?
- **Time to first order**: How quickly does the user convert?

**Critical distinction**: Offline metrics validate model quality; online metrics validate business impact. A model can improve NDCG but hurt conversion if, e.g., it over-promotes high-rated restaurants that are far away (high relevance but bad user experience).

**Q9: What is position bias in click data and how do you correct for it?**

Position bias: users are more likely to examine and click items shown at higher positions, regardless of actual relevance. A click at position 1 doesn't mean the item is more relevant than an unclicked item at position 10 -- the user may never have seen position 10.

**The core issue**: If you train on raw click data as labels, you're training a model to reproduce position bias, not actual relevance. The model learns "items shown at top get clicked" instead of "relevant items get clicked."

**Correction methods:**

1. **Inverse Propensity Weighting (IPW)**: Run randomized experiments where some items are shown at random positions. Estimate examination probability $P(\text{examine} | k)$ for each position $k$. Weight each training example by $1/P(\text{examine} | k)$. Higher-position clicks are down-weighted, lower-position clicks are up-weighted.

2. **Regression EM**: Jointly model examination probability (depends on position) and relevance probability (depends on item). EM alternates between estimating which clicks were due to relevance vs position.

3. **Position feature at train time**: Include the logged display position as a feature during training. At inference, set all positions to 1 (or a constant). The model learns to separate "the position effect" from "the relevance effect."

4. **Pair-level debiasing**: Only form pairs from items shown in similar positions, or re-weight pairs by position difference.

XGBoost supports `lambdarank_unbiased=True` for built-in IPW correction.

**Q10: How does multi-stage ranking work and where does LTR fit?**

Multi-stage ranking is necessary because applying a complex model to millions of candidates per query is infeasible.

| Stage | Candidates | Latency | Model Complexity |
|-------|-----------|---------|-----------------|
| **Retrieval** | Millions -> thousands | < 10ms | Simple: BM25, embedding ANN, inverted index |
| **First-pass ranking** | Thousands -> hundreds | < 50ms | Light model: logistic regression, small GBDT |
| **Re-ranking (LTR)** | Hundreds -> tens | < 100ms | Full LambdaMART or neural ranker with rich features |
| **Business rules** | Tens -> final list | < 5ms | Post-processing: diversity, freshness, ad slots |

**Where LTR fits**: The re-ranking stage. LTR models like LambdaMART are too expensive for millions of candidates but deliver the most value when applied to the top few hundred candidates from retrieval. They can use expensive features (user-item affinity, real-time signals) that retrieval models cannot.

**Q11: Explain the pair sampling strategies in XGBoost LTR.**

With $n$ documents per query, there are $O(n^2)$ possible pairs. Computing all pairs is expensive for large query groups. XGBoost offers three sampling strategies:

**`mean` (default)**: Uniformly random sampling. Each document is paired with `lambdarank_num_pair_per_sample` other documents chosen randomly. Good baseline, no position bias in sampling.

**`topk` (recommended for `rank:ndcg`)**: Biased sampling toward top-ranked documents. Documents near the top of the current ranking form more pairs. Rationale: top-position errors have the largest $|\Delta NDCG|$, so focusing pair sampling there gives the best gradient signal per compute budget. This creates a *double emphasis* on top positions -- once from the $|\Delta NDCG|$ weighting, once from sampling.

**`map` (for `rank:map`)**: Biased toward pairs that most affect MAP. MAP cares about the position of each relevant document, so sampling focuses on relevant-vs-irrelevant pairs near the relevant documents' current positions.

**Practical choice**: Use `topk` with `rank:ndcg` for search/ranking. Increase `lambdarank_num_pair_per_sample` (e.g., 8-16) when query groups are large for more stable gradients, at the cost of training speed.

**Q12: What happens to lambda gradients as the model converges?**

As training progresses, the model places high-relevance documents near the top of the ranking. This has two converging effects:

1. **$P_{ij} \to 1$ for correctly ordered pairs**: The RankNet component $\sigma(1 - P_{ij})$ shrinks to zero. If $s_i \gg s_j$ for all pairs where $y_i > y_j$, the gradient contribution from those pairs vanishes.

2. **$|\Delta NDCG_{ij}| \to 0$ for remaining misorderings**: As the ranking approaches ideal, any remaining misorderings involve documents that are close together in both relevance and position. Swapping them causes minimal NDCG change.

The product $\lambda_{ij} = -\sigma(1 - P_{ij}) \cdot |\Delta NDCG_{ij}|$ thus shrinks from both factors. Per-document aggregated lambdas $\lambda_i \to 0$, tree leaf weights become tiny, and new trees contribute almost nothing. This is **self-regulating convergence** -- the model naturally stops updating when the ranking is good, even without explicit early stopping.

This is why early stopping on validation NDCG is effective: once the training signal has been exhausted, further trees add noise (overfitting to pair-level fluctuations) rather than signal.

### DoorDash Phone Screen: Search Ranking Scenario

A likely DoorDash phone screen question: "Design the ranking system for restaurant search."

**Structured answer framework:**

1. **Problem framing:** User types query -> retrieve candidate restaurants -> rank by predicted relevance/utility
2. **Label definition:** Implicit signals -- click-through, add-to-cart, order completion, with position-bias correction
3. **Feature categories:**
   - Query-restaurant: text match (BM25, embeddings), cuisine/category match
   - Restaurant quality: rating, review count, order volume, preparation time
   - User context: location, past orders, dietary preferences, time of day
   - Real-time: current wait time, delivery ETA, promotions active
4. **Model:** LambdaMART (XGBoost `rank:ndcg`) for interpretability and feature importance; neural ranker as second stage if needed
5. **Evaluation:** Offline NDCG@10, online A/B test on conversion rate and order value
6. **Iteration:** Feature importance analysis, error analysis on low-NDCG queries, handling cold-start restaurants

## Comparisons

### LTR Approaches

| Aspect | Pointwise | Pairwise (RankNet) | Listwise (LambdaMART) |
|--------|-----------|--------------------|-----------------------|
| Loss unit | Single document | Document pair | Document list (via lambdas) |
| Metric alignment | None (regression) | Indirect (pairwise accuracy) | Direct (NDCG-aware) |
| Position sensitivity | None | None | Yes (via delta NDCG) |
| Complexity | $O(n)$ | $O(n^2)$ pairs | $O(n^2)$ pairs + NDCG computation |
| When to use | Simple baselines | When pairwise labels available | Production search/ranking |

### Ranking Metrics

| Metric | Formula Intuition | Best for |
|--------|-------------------|----------|
| NDCG@K | Graded relevance, position-discounted | Multi-level relevance labels |
| MAP | Mean of precision at each relevant doc | Binary relevance |
| MRR | Reciprocal rank of first relevant doc | Single correct answer |
| Precision@K | Fraction relevant in top K | Simple binary evaluation |

### LTR in Practice: Company Applications

| Company | Application | Key Features |
|---------|-------------|-------------|
| DoorDash | Restaurant/item search ranking | Query-restaurant match, ETA, user history |
| Uber Eats | Menu item ranking | Similar to DoorDash + surge pricing signals |
| Airbnb | Listing search ranking | Location, price, host quality, guest preferences |
| LinkedIn | Job/feed ranking | Profile-job match, engagement prediction |
| Google | Web search | PageRank + hundreds of quality signals |

## Key Takeaways

- [ ] LambdaMART = LambdaRank gradients + gradient boosted trees; the standard production LTR algorithm
- [ ] The lambda trick: weight pairwise gradients by $|\Delta NDCG|$ to inject position sensitivity without differentiating through argsort
- [ ] Top-of-list errors get exponentially more gradient signal than bottom errors -- this matches user behavior
- [ ] XGBoost's `rank:ndcg` objective uses lambda/hessian pairs exactly like regression, only the gradient source differs
- [ ] Pair sampling strategy (`topk`) compounds with NDCG weighting for double emphasis on top positions
- [ ] Query groups are critical: pairs must be within-query only, never cross-query
- [ ] For DoorDash/food delivery search: frame as LTR with implicit labels (clicks, orders), position-bias correction, and multi-stage pipeline
- [ ] Offline metrics (NDCG, MAP) validate model quality; online A/B tests validate business impact
- [ ] Feature engineering matters as much as the model: query-doc similarity, item quality, user context, real-time signals
- [ ] As training converges, $|\Delta NDCG|$ shrinks and updates stabilize -- the model self-regulates
