"""Populate Ranking-as-Allocation system design module with all 8 sections.

Usage:
    python scripts/content_ranking_allocation.py

This is the SIGNATURE PROJECT -- deepest coverage, most personal ownership voice.
Idempotent: overwrites existing content for the ranking-allocation slug.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

# ---------------------------------------------------------------------------
# Section 1: Overview & Motivation
# ---------------------------------------------------------------------------

OVERVIEW = r"""## Overview & Motivation

### The Pointwise Ranking Problem

Traditional search ranking scores each item independently against the query,
then sorts by score. This **pointwise paradigm** ignores a critical reality:
users see a *page* of results, not individual items. When every item is scored
in isolation, the result page becomes **homogeneous** -- dominated by the same
sellers, the same category, the same price range.

### Why Homogeneity Hurts

| Stakeholder | Impact of Homogeneous Results |
|-------------|------------------------------|
| **Buyers** | Reduced exploration; fatigue from redundant listings; higher bounce rate |
| **Long-tail sellers** | Crowded out by top sellers who dominate relevance scores |
| **Platform** | Lower session continuation; reduced purchase diversity; marketplace health risk |

### The Allocation Insight

The search result page has $K$ slots (typically 48 on eBay SRP). Ranking is
fundamentally an **allocation problem**: distributing $K$ scarce slots across
competing objectives -- relevance, diversity, fairness, and revenue.

$$
\text{Ranking} \equiv \text{Allocating } K \text{ slots subject to constraints}
$$

This reframing unlocks a rich toolkit from operations research: constrained
optimization, budget management, and closed-loop policy control.

### What Makes This Project Unique

1. **Allocation framing** applied to search ranking (not just ad auctions)
2. **Soft + hard constraint hybrid** for flexible diversity management
3. **Closed-loop policy management** that auto-adjusts diversity budgets daily
   based on observed vs. target diversity metrics
4. **MUS calibration** enabling multi-model score combination
5. **Hierarchical segment budgets** handling sparse data gracefully

### Impact

- **+3.5%** page-level purchase rate
- **+2.8%** session continuation rate
- Allocation paradigm adopted across 3 search verticals at eBay
"""

# ---------------------------------------------------------------------------
# Section 2: Architecture Deep Dive
# ---------------------------------------------------------------------------

ARCHITECTURE = r"""## Architecture Deep Dive

### System Architecture Overview

The system has two major loops: an **online serving pipeline** that handles
real-time query traffic, and a **nearline/offline closed-loop** that adjusts
diversity policy based on observed outcomes.

### Online Serving Pipeline

```
Query -> QN (Candidate Generation) -> Cassini ORC (Late-Stage Ranking) -> Page Composer -> SRP
```

#### Query Node (QN) -- Candidate Generation

The QN retrieves 50-200 candidate items per query using inverted index lookup
plus lightweight relevance filtering. Critically, each candidate is tagged with
**diversity cohort labels**:

- **Seller cohort**: seller tier (power seller, mid-tier, long-tail)
- **Category cohort**: leaf category + parent category
- **Price bucket**: discretized price range (budget / mid / premium)
- **Condition cohort**: new, refurbished, used

These cohort tags are pre-computed and stored in the item index.

#### Cassini ORC -- Late-Stage Ranking

The ORC (Orchestration/Ranking/Composition) layer performs four sequential steps:

| Step | Latency | Description |
|------|---------|-------------|
| **Base relevance scoring** | ~5ms | Multi-model ensemble (relevance, freshness, personalization) |
| **MUS calibration** | <1ms | Normalize cross-model scores to common scale |
| **Policy allocation re-ranking** | <3ms | Greedy re-ranking with soft + hard diversity constraints |
| **Hard overrides** | <0.5ms | Regulatory, brand safety, and mandatory diversity floors/ceilings |

#### MUS Calibration Layer

Multiple ranking models contribute scores on different scales. **Model-Unified
Scoring (MUS)** normalizes them to a common distribution:

$$\hat{s}_i = \frac{s_i - \mu_m}{\sigma_m} \cdot \sigma_{\text{target}} + \mu_{\text{target}}$$

where $\mu_m, \sigma_m$ are per-model statistics refreshed hourly from recent
traffic samples.

#### Policy Allocation Re-ranking

The core re-ranker uses a **greedy algorithm with constraint penalty**:

1. Initialize: empty result set $R$, full candidate set $C$
2. For position $k = 1, \ldots, K$:
   - For each candidate $i \in C$: compute adjusted score
     $s'_i = s_i - \lambda \cdot \text{violation\_penalty}(i, R)$
   - Select $i^* = \arg\max_{i \in C} s'_i$
   - Add $i^*$ to $R$, remove from $C$
   - Update constraint satisfaction state

The **violation penalty** increases for candidates that would worsen constraint
violations (e.g., adding a 4th item from the same seller when the cap is 3).

#### Hard Overrides

Non-negotiable constraints applied as a post-processing filter:

- **Regulatory**: region-specific product restrictions
- **Brand safety**: blocklisted sellers or categories
- **Mandatory floors**: minimum representation for specific diversity dimensions

### Nearline/Offline Closed-Loop

```
User Interactions -> Profile Discovery -> DSBE Paradise Table
    -> Adjustment Engine -> Spark Job -> Updated Policy -> Serving Layer
```

#### Cassini Profile Discovery

Analyzes user interactions to build three profile types:

- **Query profiles**: what diversity patterns appear for each query type
- **Landing profiles**: which diversity configurations lead to engagement
- **Taste profiles**: per-user diversity preferences

#### DSBE Paradise Table

The **Diversity Segment Budget Engine (DSBE)** maintains a table of observed vs.
target diversity for each of ~2000 query segments:

| Segment | Dimension | Target | Observed | Gap |
|---------|-----------|--------|----------|-----|
| "shoes" x tier-1 | seller diversity | 0.65 | 0.58 | -0.07 |
| "shoes" x tier-1 | category diversity | 0.40 | 0.42 | +0.02 |
| "electronics" x tier-2 | seller diversity | 0.70 | 0.71 | +0.01 |

#### Adjustment Engine

Compares observed vs. target diversity and adjusts budgets:

$$b_j^{(t+1)} = b_j^{(t)} + \eta \cdot (b_j^{\text{target}} - \bar{d}_j^{(t)})$$

With three guardrails:
1. **Budget clamping**: $b_j \in [b_j^{\min}, b_j^{\max}]$
2. **Conservative learning rate**: $\eta = 0.1$
3. **Relevance guardrail**: freeze if NDCG drops >2% from baseline

#### Spark Job

Overnight batch job (~2 hours) that:
1. Processes previous day's interaction data
2. Computes updated diversity budgets per segment
3. Distributes new policy parameters to the serving layer
"""

# ---------------------------------------------------------------------------
# Section 3: Data Flow & Key Components
# ---------------------------------------------------------------------------

DATAFLOW = r"""## Data Flow & Key Components

### Online Path (per-query, <15ms total)

```
1. Query arrives at Query Node (QN)
   |
   v
2. QN: Candidate generation (inverted index + lightweight relevance)
   - Retrieves 50-200 candidates
   - Tags each with diversity cohort labels (seller, category, price, condition)
   |
   v
3. Cassini ORC: Base Relevance Scoring
   - 3-model ensemble: base relevance, freshness, personalization
   - Each model produces raw score on its own scale
   |
   v
4. Cassini ORC: MUS Calibration
   - Normalize each model's scores: z-score transform to target distribution
   - Combine calibrated scores into unified relevance score
   |
   v
5. Cassini ORC: Policy Allocation Re-ranking
   - Load diversity budgets for this query's segment from policy cache
   - Greedy selection with constraint penalty:
     * Soft constraints: seller variety, category diversity, price spread
     * Hard constraints: regulatory, brand safety, mandatory floors
   - Output: ordered list of K=48 items satisfying constraints
   |
   v
6. Cassini ORC: Hard Overrides
   - Final pass: enforce non-negotiable constraints
   - Swap out any items violating regulatory or safety rules
   |
   v
7. Page Composer
   - Assemble final SRP layout
   - Inject non-organic modules (ads, promotions) into reserved slots
   - Render to user
```

### Offline Feedback Loop (daily batch)

```
1. User Interactions (clicks, purchases, session continuation)
   |
   v
2. Profile Discovery (Cassini pipeline)
   - Query profiles: diversity patterns per query type
   - Landing profiles: which configurations drive engagement
   - Taste profiles: per-user diversity preferences
   |
   v
3. DSBE Paradise Table
   - Aggregate observed diversity metrics per segment
   - Compare against target diversity budgets
   - Compute gap: observed - target per dimension per segment
   |
   v
4. Adjustment Engine
   - For each segment-dimension pair:
     * If gap < 0 (under-diverse): increase budget
     * If gap > 0 AND relevance stable: maintain budget
     * If relevance dropping (NDCG drop >2%): freeze budget, alert team
   - Apply hierarchical shrinkage for sparse segments
   |
   v
5. Spark Job (overnight, ~2 hours)
   - Materialize updated budgets
   - Distribute to serving layer policy cache
   - Next day's queries use updated constraints
```

### Key Data Stores

| Store | Type | Contents | Update Frequency |
|-------|------|----------|-----------------|
| **Item Index** | Inverted index (Cassini) | Item features + diversity cohort tags | Real-time (listing updates) |
| **Policy Cache** | In-memory key-value | Diversity budgets per segment-dimension | Daily (post Spark job) |
| **DSBE Paradise Table** | Hive/HDFS table | Observed vs. target diversity per segment | Daily aggregation |
| **Model Statistics** | Redis | Per-model $\mu_m, \sigma_m$ for MUS calibration | Hourly refresh from traffic samples |
| **Profile Store** | Key-value (Cassini) | Query/landing/taste profiles | Nearline updates (minutes) |

### Constraint Types

| Type | Examples | Enforcement | Flexibility |
|------|----------|-------------|-------------|
| **Hard** | Regulatory restrictions, brand safety, mandatory diversity floors | Post-processing filter (items swapped out) | Zero tolerance -- must be satisfied |
| **Soft** | Seller variety, category spread, price range diversity | Greedy penalty during re-ranking | Budget-based -- allowed to under-satisfy if relevance cost too high |
"""

# ---------------------------------------------------------------------------
# Section 4: Formulas & Algorithms
# ---------------------------------------------------------------------------

FORMULAS = r"""## Formulas & Algorithms

### Core Allocation Objective

The ranking problem is formulated as constrained allocation:

$$
\max_{x} \sum_{i=1}^{N} x_i \cdot s_i \quad \text{s.t.} \quad \sum_{i \in G_j} x_i \geq b_j \;\forall j, \quad \sum_i x_i = K
$$

where:
- $x_i \in \{0, 1\}$: selection indicator for item $i$
- $s_i$: calibrated relevance score
- $G_j$: item group for diversity dimension $j$ (e.g., all items from long-tail sellers)
- $b_j$: minimum budget (floor) for group $j$
- $K = 48$: page size (number of slots)

This is an **integer linear program** -- NP-hard in general, but the greedy
approximation works well because the constraint structure is simple
(cardinality + group lower bounds).

### MUS Calibration

Model-Unified Scoring normalizes scores from different ranking models to a
common target distribution:

$$
\hat{s}_i = \frac{s_i - \mu_m}{\sigma_m} \cdot \sigma_{\text{target}} + \mu_{\text{target}}
$$

where:
- $s_i$: raw score from model $m$
- $\mu_m, \sigma_m$: mean and standard deviation of model $m$'s scores
  (estimated from recent traffic, refreshed hourly)
- $\mu_{\text{target}} = 0, \sigma_{\text{target}} = 1$: target distribution
  parameters (standard normal)

**Why not just z-score?** The target parameters allow control over the combined
score's dynamic range. In practice, $\sigma_{\text{target}}$ is tuned per
model to reflect its offline NDCG contribution weight.

### Greedy Re-ranking with Constraint Penalty

For each position $k = 1, \ldots, K$:

$$
s'_i = s_i - \lambda \cdot \text{violation\_penalty}(i, R_k)
$$

where:
- $R_k$: items already placed in positions $1, \ldots, k-1$
- $\lambda$: penalty weight (tuned via offline evaluation)

The **violation penalty** function:

$$
\text{violation\_penalty}(i, R) = \sum_{j=1}^{J} w_j \cdot \max\left(0, \; c_j(R \cup \{i\}) - b_j^{\max}\right)
$$

where $c_j(R \cup \{i\})$ counts items from group $j$ in the result set if
item $i$ were added, and $b_j^{\max}$ is the ceiling constraint.

**Complexity**: $O(K \cdot N)$ for $K=48$ slots and $N=200$ candidates, giving
~9,600 scoring operations per query -- easily under 3ms.

### Closed-Loop Budget Adjustment

Daily update rule:

$$
b_j^{(t+1)} = \text{clamp}\left(b_j^{(t)} + \eta \cdot (b_j^{\text{target}} - \bar{d}_j^{(t)}), \; b_j^{\min}, \; b_j^{\max}\right)
$$

where:
- $b_j^{(t)}$: current budget for dimension $j$
- $b_j^{\text{target}}$: desired diversity level (set by business rules)
- $\bar{d}_j^{(t)}$: observed diversity metric (averaged over the day)
- $\eta = 0.1$: learning rate (conservative to prevent oscillation)
- $b_j^{\min}, b_j^{\max}$: human-set guardrail bounds

**Convergence**: With $\eta = 0.1$ and clamped bounds, new budget targets
stabilize within 3-7 days. The system converges monotonically when
$\bar{d}_j^{(t)}$ responds linearly to $b_j^{(t)}$ (approximately true in
the operating range).

### Budget Exploration via Thompson Sampling

For segments where the optimal budget is uncertain, we explore:

$$
b_j^{\text{explore}} \sim \mathcal{N}(b_j^{(t)}, \sigma_j^2)
$$

where $\sigma_j^2$ starts high for new segments and shrinks as observations
accumulate. This balances exploration of potentially better budgets against
exploitation of known-good settings.

### Hierarchical Shrinkage for Sparse Segments

For segments with few daily queries, budget estimates are noisy. We apply
empirical Bayes shrinkage:

$$
\hat{b}_j^{\text{segment}} = \alpha_j \cdot b_j^{\text{segment}} + (1 - \alpha_j) \cdot b_j^{\text{parent}}
$$

where:
- $\alpha_j = \frac{n_j}{n_j + n_0}$: shrinkage weight
- $n_j$: observation count for this segment
- $n_0$: prior strength (tuned to ~100 daily queries)
- $b_j^{\text{parent}}$: parent segment's budget (e.g., intent category level)

| Observation Count | Shrinkage $\alpha$ | Budget Source |
|-------------------|-------------------|---------------|
| >500 daily queries | ~0.83 | Mostly segment-specific |
| 100-500 queries | 0.50-0.83 | Partial shrinkage |
| <100 queries | <0.50 | Mostly inherited from parent |
"""

# ---------------------------------------------------------------------------
# Section 5: Production Constraints
# ---------------------------------------------------------------------------

PRODUCTION_CONSTRAINTS = r"""## Production Constraints

### Throughput & Latency

| Metric | Value | Context |
|--------|-------|---------|
| **QPS** | ~50K queries/sec at peak | Same traffic as Module Arbitration (shared Cassini serving path) |
| **Candidate set per query** | 50-200 items after QN retrieval | Diversity re-ranking operates on this post-retrieval set |
| **Page size** | $K = 48$ slots | Standard eBay SRP page; allocation fills exactly $K$ slots |
| **Re-ranking latency** | <3ms (greedy with constraint penalty) | $O(K \cdot N)$ for $K=48, N=200$ = ~9,600 operations |
| **MUS calibration latency** | <1ms (simple normalization per query) | Pre-computed $\mu_m, \sigma_m$ per model, refreshed hourly |
| **Total ORC latency budget** | <15ms end-to-end | Includes base scoring (~5ms), MUS (<1ms), re-ranking (<3ms), overrides (<0.5ms), overhead |

### Constraint Dimensions

| Dimension | Hard Constraints | Soft Constraints |
|-----------|-----------------|-----------------|
| **Seller** | Max 3 items per seller (anti-spam) | Seller tier diversity target (% long-tail representation) |
| **Category** | Mandatory category breadth floor | Category diversity budget per segment |
| **Price** | None | Price bucket spread target |
| **Condition** | Region-specific (refurb disclosure laws) | Condition mix diversity |
| **Brand safety** | Blocklisted seller/category removal | None (hard only) |
| **Regulatory** | Region-specific product restrictions | None (hard only) |

### Scale Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Hard constraint types** | 8 active categories | Seller cap, category floor, condition diversity, brand safety, regulatory, etc. |
| **Soft constraint dimensions** | 4 (seller, category, price bucket, condition) | Each has independent budget per query segment |
| **Query segments** | ~2,000 segments (query intent x user tier) | Budget targets maintained per segment in DSBE Paradise Table |
| **Policy update frequency** | Daily batch (overnight Spark job) | ~2 hours to process previous day's data and compute new budgets |
| **Closed-loop convergence** | 3-7 days for new budget targets to stabilize | Learning rate $\eta = 0.1$, clamped to $[b^{\min}, b^{\max}]$ range |
| **Model statistics refresh** | Hourly | Per-model $\mu_m, \sigma_m$ for MUS calibration |

### Monitoring & Alerting

| Monitor | Threshold | Action |
|---------|-----------|--------|
| **Segment diversity drop** | >10% below target for 2+ hours | Real-time Grafana alert to on-call |
| **NDCG guardrail** | >2% drop from segment baseline | Adjustment engine freezes segment budget |
| **Re-ranking latency P99** | >5ms | Auto-alert; fallback to relevance-only ordering |
| **Constraint violation rate** | >1% of queries with hard constraint violations | Immediate page alert; investigate constraint config |

### Failure Modes & Fallbacks

| Failure | Fallback | Recovery |
|---------|----------|----------|
| Policy cache unavailable | Use default diversity budgets (conservative, pre-configured) | Cache auto-repopulates on next Spark job |
| MUS statistics stale (>4 hours) | Use raw model scores without calibration | Hourly refresh job retries with exponential backoff |
| Re-ranking timeout (>5ms) | Return relevance-ordered candidates without diversity re-ranking | Log event for latency investigation |
| Adjustment engine produces anomalous budget | Clamping to $[b^{\min}, b^{\max}]$ catches extremes | Manual review triggered by out-of-range alert |
"""

# ---------------------------------------------------------------------------
# Section 6: Trade-off Analysis
# ---------------------------------------------------------------------------

TRADEOFFS = r"""## Trade-off Analysis

### Key Design Decisions

| Decision | Option A | Option B | Our Choice & Why |
|----------|----------|----------|------------------|
| **Ranking paradigm** | Pointwise (score each item independently) | Allocation (page-level constrained optimization) | **Allocation** -- pointwise ignores composition; two identical items both shown wastes slots. The allocation framing directly models the problem we care about: page-level user experience. |
| **Diversity enforcement** | Hard constraints only | Soft + hard hybrid | **Hybrid** -- hard for non-negotiable requirements (regulatory, brand safety); soft for preference-based diversity (seller variety). Hard-only is too rigid; soft-only risks critical violations. |
| **Constraint scope** | Per-query budgets | Per-query-segment budgets (clustered) | **Per-segment** -- individual queries are too noisy for stable budget estimation. Segments (~2,000) cluster similar queries, enabling reliable diversity targets while keeping granularity meaningful. |
| **Policy update frequency** | Daily batch | Near-real-time streaming | **Daily batch** -- diversity policy changes need careful evaluation for unintended side effects. Real-time updates risk oscillation and make debugging harder. Daily cadence provides stability with acceptable lag. |
| **Score normalization** | Raw model scores | MUS calibration (z-score to target) | **MUS calibration** -- multiple models contribute scores on incomparable scales. Raw score combination is meaningless. MUS enables principled ensemble without per-model weight tuning. |

### Deeper Trade-off Discussions

#### Allocation vs. Pointwise: The Composition Problem

Pointwise ranking optimizes $\sum_{i=1}^{K} s_i$ -- the sum of individual
relevance scores. This is equivalent to allocation with no constraints. The
problem: a page of 48 highly relevant but identical items (same seller, same
category, same price) maximizes pointwise NDCG but provides a terrible user
experience.

The allocation framing adds constraints that sacrifice some pointwise NDCG
(measured: -1.2%) but improve page-level metrics that actually correlate with
user satisfaction (+3.5% purchase rate, +2.8% session continuation).

**The key insight**: NDCG is a measurement tool, not the objective. When the
measurement diverges from user satisfaction, fix the measurement, not the system.

#### Daily vs. Real-Time Policy Updates

We considered streaming policy updates (update budgets after every query based on
the previous query's outcome). The problems:

1. **Oscillation**: Budget changes propagate instantly, but their effects take
   thousands of queries to measure reliably. Fast updates + slow feedback =
   oscillation.
2. **Debugging**: When a diversity metric drops, daily batches have clear
   attribution (yesterday's policy change). Real-time has an unattributable
   stream of micro-changes.
3. **Blast radius**: A daily batch bug affects one day. A real-time bug compounds
   continuously.

The daily cadence means we accept 24-hour lag in policy adaptation. This is
acceptable because diversity targets shift slowly (driven by catalog composition
and seasonal trends, not minute-to-minute).

#### Greedy vs. Exact ILP Solver

The allocation objective is an integer linear program. We could solve it exactly
(e.g., using CPLEX or Gurobi). We chose greedy because:

| Factor | Exact ILP | Greedy |
|--------|-----------|--------|
| **Latency** | 10-50ms (solver overhead) | <3ms |
| **Optimality** | Provably optimal | 95-98% of optimal (measured empirically) |
| **Interpretability** | Black-box solver output | Step-by-step placement logic; easy to debug |
| **Constraint changes** | Requires reformulation | Add penalty term |

The 2-5% optimality gap is acceptable given the 3-10x latency improvement.
For an online system serving 50K QPS, latency dominates.
"""

# ---------------------------------------------------------------------------
# Section 7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------

DEFENSE = r"""## Adversarial Defense Q&A

**Q: Your allocation framing sounds like it adds complexity for marginal gains. Can you quantify the relevance cost of diversity constraints?**

> **Limitation acknowledged:** Diversity constraints do reduce pure-relevance NDCG.
> Any constraint on a maximization problem reduces the optimal value -- this is a
> fundamental mathematical fact, not a design flaw.
>
> **Mitigation:** The key insight is that user satisfaction is not monotonically
> increasing with pointwise relevance. A page of 48 items from the same seller,
> all highly relevant, is a poor experience. We measure page-level engagement
> (session continuation, purchase rate), not just NDCG.
>
> **Data:** With diversity constraints active, pointwise NDCG drops 1.2% but
> page-level purchase rate increases 3.5% and session continuation rate increases
> 2.8%. The user is more likely to buy and more likely to come back. The diversity
> "cost" measured by NDCG is a measurement artifact -- NDCG rewards showing the
> "most relevant" items, but users want variety, not redundancy.

---

**Q: Your closed-loop adjusts budgets automatically. What prevents it from gaming metrics or drifting to degenerate states?**

> **Limitation acknowledged:** Closed-loop systems can drift, oscillate, or find
> reward-hacking equilibria. This is a real risk, not a theoretical one -- I have
> seen reward gaming in other ranking systems.
>
> **Mitigation:** Three guardrails prevent degenerate behavior:
>
> 1. **Budget clamping**: Every budget is clamped to $[b^{\min}, b^{\max}]$ per
>    constraint type, set by human-reviewed business rules. The system cannot set
>    seller diversity to 0% or 100%.
> 2. **Conservative learning rate**: $\eta = 0.1$ means maximum daily budget
>    change is approximately 10% of the gap between observed and target. Large
>    jumps are impossible.
> 3. **Relevance guardrail**: If NDCG drops >2% from baseline for any segment,
>    the adjustment engine freezes that segment's budget and alerts the team.
>
> **Data:** In 14 months of operation, the adjustment engine froze budgets 7 times
> (0.5% of segment-days). 5 were false alarms from seasonality shifts (e.g.,
> holiday traffic changing query distribution); 2 were genuine constraint
> misconfigurations caught early before user impact. No degenerate states reached
> in production.

---

**Q: MUS calibration normalizes scores, but different models may have fundamentally different quality levels. Doesn't normalization hide quality differences?**

> **Limitation acknowledged:** Yes, normalization equalizes the scale but not the
> information content of different models. A poorly trained model with calibrated
> scores still contributes noise.
>
> **Mitigation:** MUS calibration normalizes within the same relevance tier, not
> globally. A high-quality model's score distribution is tighter and more
> informative -- this property is preserved after normalization. The calibrated
> scores still have higher mutual information with relevance labels. Additionally,
> we weight models by their offline NDCG contribution in the final score
> combination, so low-quality models are down-weighted.
>
> **Data:** After MUS calibration, the ensemble of 3 ranking models (base
> relevance, freshness, personalization) achieved 2.1% higher NDCG than using
> raw scores from the single best model. The calibration enables meaningful score
> combination that would be impossible with raw scores on different scales.

---

**Q: Per-segment budgets with 2,000 segments -- how do you handle segments with sparse data?**

> **Limitation acknowledged:** Long-tail segments (rare query types + niche user
> tiers) have few observations per day, making budget adjustment noisy. Naive
> per-segment estimation would produce unreliable budgets.
>
> **Mitigation:** Hierarchical shrinkage (empirical Bayes): segments with <100
> daily queries inherit their parent segment's budget. The shrinkage weight
> $\alpha = n / (n + n_0)$ smoothly interpolates between segment-specific and
> parent estimates as observation count grows.
>
> This is the same principle as James-Stein estimation: pooling information across
> related groups improves estimation for all groups, especially sparse ones.
>
> **Data:** 65% of segments have >500 daily queries (reliable individual budgets).
> 30% have 100-500 (partial shrinkage). 5% have <100 (fully inherited from
> parent). The hierarchical approach reduced budget variance on sparse segments
> by 60% compared to per-segment-only estimation.

---

**Q: The greedy algorithm is suboptimal -- you're leaving relevance on the table. Why not use an exact solver?**

> **Limitation acknowledged:** Greedy is a heuristic. For an integer linear program,
> it does not guarantee the optimal solution.
>
> **Mitigation:** We measured the optimality gap empirically by running an exact ILP
> solver (Gurobi) on sampled queries offline. The greedy solution achieves 95-98%
> of optimal relevance score while running in <3ms vs. 10-50ms for the exact solver.
>
> At 50K QPS, the latency difference matters more than the 2-5% optimality gap.
> The greedy approach also has a critical operational advantage: it is transparent
> and debuggable. When a result page looks wrong, we can trace the greedy
> placement step-by-step. An ILP solver is a black box.
>
> **Data:** On a sample of 10,000 queries, greedy achieved 96.3% of optimal
> objective value on average. For 82% of queries, greedy produced the same
> top-10 as the exact solver. The differences were concentrated in queries with
> many competing constraints (rare edge cases).

---

**Q: This is your signature project. What is the biggest mistake you made, and what would you do differently?**

> **Honest answer:** The biggest mistake was not investing in **counterfactual
> evaluation** from day one. Every policy change required an A/B test -- typically
> 1-2 weeks of dedicated traffic allocation. With inverse propensity scoring (IPS)
> and doubly-robust estimators, we could have evaluated 10+ policy variants offline
> before committing to a single A/B test.
>
> I eventually built offline evaluation infrastructure, but by then we had spent
> approximately 3 months running sequential A/B tests that could have been
> parallelized. Each test consumed traffic that could have been serving production
> optimizations. The opportunity cost was significant: we likely delayed the final
> diversity configuration by 6-8 weeks.
>
> The root cause was overconfidence in the initial policy design. I assumed the
> first few A/B tests would converge quickly, so offline evaluation felt like
> over-engineering. In reality, the interaction between soft constraints, segment
> budgets, and learning rates created a configuration space much larger than I
> anticipated. Systematic offline exploration would have found good configurations
> faster.
>
> **What I would do differently:** Build the counterfactual evaluation framework in
> the first sprint, even before the first policy constraint. Specifically:
>
> 1. **Log propensity scores** from day one (the probability of each item being
>    shown in each position under the current policy)
> 2. **Implement IPS and doubly-robust estimators** for offline policy evaluation
> 3. **Use offline evaluation to narrow the A/B test space** from dozens of
>    configurations to 2-3 most promising ones
>
> **Lesson:** Any ranking system that plans to iterate on policies needs offline
> evaluation infrastructure from day one. A/B tests are for validation, not
> exploration. This applies directly to ride-matching, pricing, or any
> allocation system.

---

**Q: How do you ensure the diversity constraints do not systematically disadvantage certain sellers or create unfair outcomes?**

> **Limitation acknowledged:** Diversity constraints redistribute slots from
> dominant sellers to under-represented ones. Sellers who would rank highly on
> pure relevance lose slots. This is a deliberate trade-off, but it raises
> fairness questions.
>
> **Mitigation:** The constraints are designed for **marketplace health**, not
> individual seller outcomes. Seller caps (max 3 items per seller per page)
> prevent monopolization of result pages. Long-tail seller floors ensure new
> sellers get discovery exposure. Both are motivated by platform-level metrics:
>
> - Buyer satisfaction (variety = better experience)
> - Marketplace liquidity (more active sellers = healthier market)
> - Long-term revenue (diverse seller base reduces platform risk)
>
> We publish constraint policies to sellers and provide seller-facing dashboards
> showing their impression share and how it changes with policy updates.
>
> **Data:** After implementing seller diversity constraints, the number of sellers
> receiving at least one impression per day increased by 18%. Top-10 sellers'
> impression share decreased by 12%, but their conversion rate per impression
> increased by 8% (less competition per listing = higher quality traffic). Net
> seller satisfaction (measured by quarterly survey) was neutral -- top sellers
> understood the marketplace health argument.
"""

# ---------------------------------------------------------------------------
# Section 8: Verbal Outline
# ---------------------------------------------------------------------------

VERBAL_OUTLINE = r"""## Verbal Outline

### 3-Minute Version

**Target**: elevator pitch for a busy interviewer or panel setting.

1. **(30s) Problem**: Traditional pointwise ranking scores items independently,
   leading to homogeneous result pages -- same sellers, same categories, same
   price ranges. This hurts buyer exploration, long-tail sellers, and marketplace
   health.

2. **(45s) Key Insight**: Reframe ranking as resource allocation. A search page
   has $K=48$ slots; ranking is allocating those slots across competing objectives:
   relevance, diversity, fairness, revenue. This unlocks constrained optimization
   tools.

3. **(60s) Architecture**: Two loops. Online: MUS calibration normalizes multi-model
   scores, then greedy re-ranking fills slots subject to soft constraints (seller
   variety, category diversity) and hard constraints (regulatory, brand safety).
   Offline: closed-loop policy adjustment compares observed vs. target diversity
   per query segment, updates budgets daily with conservative learning rate and
   guardrails.

4. **(30s) Production Scale**: 50K QPS, <3ms re-ranking latency, 2,000 query
   segments with hierarchical shrinkage for sparse data, daily policy updates
   converging in 3-7 days.

5. **(15s) Results**: +3.5% purchase rate, +2.8% session continuation. Allocation
   paradigm adopted across 3 search verticals at eBay.

### 10-Minute Version

**Target**: deep-dive with a hiring manager or system design round.

1. **(1.5 min) Motivation & Problem Statement**
   - Why pointwise ranking fails: the composition problem with concrete examples
   - Business impact: homogeneity metrics, buyer fatigue data, long-tail seller
     crowding
   - The allocation insight: $K$ slots as scarce resource, constraints as policy
     levers

2. **(2 min) Allocation Formulation**
   - Objective function: maximize relevance subject to group constraints
   - Hard vs. soft constraint taxonomy with examples
   - MUS calibration: why multi-model normalization is necessary, the z-score
     transform, hourly refresh cadence

3. **(2 min) Online Architecture**
   - QN diversity cohort tagging at retrieval time
   - Cassini ORC pipeline: base scoring -> MUS -> greedy re-ranking -> hard overrides
   - Greedy algorithm details: constraint penalty function, complexity analysis,
     why not exact ILP

4. **(2 min) Closed-Loop Policy Management**
   - DSBE Paradise Table: observed vs. target per segment
   - Adjustment engine: update rule, learning rate, clamping, relevance guardrail
   - Convergence behavior and production stability data
   - Hierarchical shrinkage for sparse segments (empirical Bayes)

5. **(1.5 min) Production Constraints & Operational Reality**
   - QPS, latency budgets, failure modes and fallbacks
   - Monitoring: Grafana dashboards, alerting thresholds
   - 14-month operational track record: 7 freezes, 0 degenerate states

6. **(1 min) Retrospective & Lessons**
   - Biggest mistake: not building counterfactual evaluation from day one
   - 3 months of sequential A/B tests that could have been parallelized
   - Lesson: A/B tests are for validation, not exploration
   - How this applies to allocation systems at scale (ride-matching, pricing, etc.)

### Transition Phrases for Interview Flow

When connecting to other projects in the portfolio:

- **From PBE Pipeline**: "The unbiased training data from PBE is what makes the
  base relevance scores trustworthy enough to build allocation on top of."
- **To Module Arbitration**: "Once we had the allocation framework for items, the
  natural extension was applying the same paradigm to modules -- that became the
  Module Arbitration project."
- **To LLM Orchestration**: "The allocation infrastructure also provided the
  serving framework for LLM-generated artifacts -- they compete for the same
  page slots through the same constraint system."
"""


# ---------------------------------------------------------------------------
# Main: update the database record
# ---------------------------------------------------------------------------

def populate_ranking_allocation() -> None:
    """Find the ranking-allocation SystemDesign record and update all 8 sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == "ranking-allocation")
            .first()
        )

        if record is None:
            print("[FAIL] No SystemDesign record with slug='ranking-allocation' found.")
            print("       Run scripts/seed_system_designs.py first to create the record.")
            sys.exit(1)

        record.overview = OVERVIEW
        record.architecture = ARCHITECTURE
        record.dataflow = DATAFLOW
        record.formulas = FORMULAS
        record.production_constraints = PRODUCTION_CONSTRAINTS
        record.tradeoffs = TRADEOFFS
        record.defense = DEFENSE
        record.verbal_outline = VERBAL_OUTLINE

        db.commit()
        print("[DONE] Updated all 8 sections for ranking-allocation.")

        # Verify by re-reading
        db.refresh(record)
        sections = [
            "overview", "architecture", "dataflow", "formulas",
            "production_constraints", "tradeoffs", "defense", "verbal_outline",
        ]
        for section in sections:
            content = getattr(record, section)
            length = len(content) if content else 0
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {section}: {length} chars {status}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_ranking_allocation()
