"""Populate module-arbitration system design with all 8 markdown sections.

Content sourced from docs/PLAN_system_design_showcase.md section 6.1.
Idempotent: overwrites existing content for the module-arbitration slug.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "module-arbitration"

# ---------------------------------------------------------------------------
# S1: Overview & Motivation
# ---------------------------------------------------------------------------
OVERVIEW = r"""## Overview & Motivation

eBay's Search Results Page (SRP) traditionally rendered a **fixed module layout**:
organic listing results occupied predetermined slots, with static ad placements
and promotional modules inserted at hardcoded positions. This architecture had
served eBay well at small scale, but created three escalating problems:

### The Problem

1. **No value signal per module.** There was no mechanism to evaluate which
   modules create the most value per impression. A promotional banner might
   occupy premium real estate while generating less engagement than an organic
   result that was pushed below the fold.

2. **Static allocation ignores context.** The optimal page composition depends
   on query intent, user segment, device type, and time of day. A fixed layout
   treats a "Nike Air Max" brand query the same as a long-tail "vintage brass
   lamp shade" query -- but the ideal mix of ads, recommendations, and organic
   results differs dramatically.

3. **Scaling bottleneck for new modules.** Every new module type (visual
   similarity, cross-category recommendations, sponsored brand ads) required
   product negotiations for a fixed page slot. This created organizational
   friction and slowed experimentation.

### The Insight

Frame the SRP as a **content marketplace** where modules compete for page real
estate based on predicted value. Each module type submits a "bid" (predicted
engagement value), and a centralized arbitration system allocates page positions
to maximize total page value subject to user-experience constraints.

### Business Impact

- Enables **data-driven allocation** of page space across module types
- Provides a **transparent "price discovery" mechanism** -- each team can see
  how their module's value compares to alternatives
- Scales from 12 to 200+ module types without manual slot negotiation
- Page-level GMV increased ~4% from better allocation
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = r"""## Architecture Deep Dive

The system is split into an **offline pre-computing layer** that builds value
estimates and an **online two-stage query execution** pipeline that performs
real-time arbitration.

### Offline / Pre-computing Layer

| Component | Responsibility |
|-----------|---------------|
| **Module Registration** | Metadata store: module type, placement constraints, A/B variant registration, content provider endpoints |
| **Module Performance & Features** | Historical CTR, CVR, revenue per module aggregated from Kafka engagement streams |
| **Contextual Value Predictor** | Gradient-boosted models (XGBoost/LightGBM) predicting value of each module given query context |
| **Global Thompson Sampling** | Exploration/exploitation for new or low-traffic modules; maintains Beta posteriors per module |
| **Feature Engineering & Model Training** | Daily batch training on 6 months of engagement data; features include query intent, user segment, device, time-of-day |
| **Module Register Table** | Stores all registered modules (~200 total) with pre-computed base scores; refreshed every 6 hours |

### Online Two-Stage Query Execution

**Stage 1: River & Module Content** (Adaptive HMAC + top-N selection)

- Query context + user features used to select **eligible modules** from the
  Register Table (15-30 candidates from ~200 total)
- Content fetch runs in parallel for each candidate module:
  - In-Cassini modules: local retrieval
  - External providers: SaaS/IIS stream with **50ms timeout**
- Stage 1 latency budget: **<20ms** for selection + content fetch initiation

**Stage 2: Module Arbitration (The Core)**

This is the central decision engine with four sub-components:

1. **Module Placement Optimizer** -- Decides number and position of available
   slots per placement zone (top, middle, bottom, sidebar)
2. **Module Filter** -- Applies quality thresholds (minimum predicted CTR,
   content quality score) to prevent worst-case UX
3. **River Composition & Value Maximizer** -- Solves a constrained optimization
   (LP relaxation + rounding) to maximize total page value
4. **Page Composer** -- Final layout with modules interleaved into organic
   results, respecting visual constraints (no adjacent ads, diversity rules)

Stage 2 latency budget: **<10ms** for the full arbitration pipeline.

### Feedback Loop

Engagement events (clicks, impressions, add-to-cart) stream via **Kafka** back
to the offline layer, closing the loop for model retraining and Thompson
Sampling posterior updates.
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & Key Components
# ---------------------------------------------------------------------------
DATAFLOW = r"""## Data Flow & Key Components

### Request Path (Online)

```
User Query
  |
  v
Query Context Extraction
  (query intent classification, user profile lookup, device/geo features)
  |
  v
Stage 1: Candidate Module Selection
  - Eligible modules from Register Table (15-30 from ~200)
  - Parallel content fetch from providers (50ms timeout)
  |
  v
Stage 2: Module Arbitration
  |-- Placement Optimization: how many slots per position zone?
  |-- Quality Filtering: minimum CTR/quality threshold gate
  |-- Value Maximization: LP relaxation + greedy rounding
  |-- Page Composition: final layout with interleaved modules
  |
  v
Rendered SRP (sent to client)
  |
  v
User Interactions (click, impression, scroll, add-to-cart)
  |
  v
Kafka Event Stream
```

### Feedback Path (Offline)

```
Kafka Event Stream
  |
  v
Spark Processing (~500M impressions/day, ~20M clicks/day)
  |
  v
HDFS Feature Store (6 months rolling window)
  |
  v
+-- XGBoost/LightGBM Model Training (daily batch)
|     -> Updated Contextual Value Predictor
|
+-- Thompson Sampling Posterior Update (hourly)
|     -> Updated Beta(alpha, beta) per module
|
+-- Module Register Table Refresh (every 6 hours)
      -> Pre-computed base scores for all ~200 modules
```

### Key Data Stores

| Store | Technology | Size | Refresh |
|-------|-----------|------|---------|
| Module Register Table | In-memory cache (Cassini) | ~200 entries | Every 6 hours |
| Feature Store | HDFS + Spark | 6 months engagement data | Streaming ingestion |
| Thompson Sampling State | Redis | Beta posteriors per module | Hourly |
| Engagement Log | Kafka + HDFS | ~500M impressions/day | Real-time |
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms
# ---------------------------------------------------------------------------
FORMULAS = r"""## Formulas & Algorithms

### Expected Value per Module

The predicted value of placing module $m$ on a query $q$ for user $u$:

$$E[V_m] = P(\text{click}|m, q, u) \cdot \text{Revenue}(m) + \alpha \cdot P(\text{engagement}|m)$$

where:
- $P(\text{click}|m, q, u)$ is the contextual CTR prediction from XGBoost
- $\text{Revenue}(m)$ is the expected revenue per click for module $m$
- $\alpha$ is a tunable weight balancing revenue vs. engagement
- $P(\text{engagement}|m)$ captures non-click engagement (scroll, dwell time)

### Thompson Sampling for Module Exploration

For each module $m$, maintain a Beta posterior over its success rate:

$$\theta_m \sim \text{Beta}(\alpha_m + s_m, \beta_m + f_m)$$

where:
- $s_m$ = number of "successes" (clicks) in the sliding window
- $f_m$ = number of "failures" (impressions without click) in the sliding window
- $\alpha_m, \beta_m$ = prior parameters (set from module-type similarity for cold start)

**Sliding-window variant:** Observations decay with discount factor $\gamma = 0.95$ per day:

$$s_m^{(t)} = \sum_{d=0}^{6} \gamma^d \cdot s_m^{(t-d)}$$

This makes the posterior "forget" old performance and adapt to regime changes
within 3-5 days.

### Page Value Maximization (Integer LP)

$$\max \sum_{m \in M} \sum_{p \in P} x_{m,p} \cdot V(m, p)$$

Subject to:

$$\sum_{p \in P} x_{m,p} \leq 1 \quad \forall m \in M \quad \text{(each module placed at most once)}$$

$$\sum_{m \in M} x_{m,p} \leq 1 \quad \forall p \in P \quad \text{(each position holds at most one module)}$$

$$x_{m,p} \in \{0, 1\}$$

Additional constraints:
- **Diversity**: no more than $k$ modules of the same type
- **Adjacency**: no two ad modules in consecutive positions
- **Minimum organic**: at least $r$ organic results in top $n$ positions

**In practice:** We use LP relaxation (allowing fractional $x_{m,p} \in [0, 1]$)
solved via a specialized network flow solver in $O(n \cdot m)$, followed by
deterministic greedy rounding that respects hard constraints.
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = r"""## Production Constraints

| Metric | Value | Context |
|--------|-------|---------|
| **QPS** | ~50K queries/sec at peak (US market) | Each query triggers full two-stage arbitration |
| **Candidate modules per query** | 15-30 eligible modules (from ~200 registered total) | Stage 1 prunes aggressively by query context |
| **Stage 1 latency budget** | <20ms for module selection + content fetch initiation | Content fetch runs async with 50ms timeout |
| **Stage 2 latency budget** | <10ms for arbitration (LP + page composition) | LP operates on 15-30 candidates for ~48 page slots |
| **End-to-end latency (P99)** | <150ms total SRP render (arbitration is ~30ms of this) | Dominated by content fetch from external providers |
| **Module Register Table size** | ~200 registered modules, ~50 active per market | Refreshed every 6 hours with offline scores |
| **Offline model retraining** | Daily batch; Thompson Sampling posteriors updated hourly | Feature store contains 6 months of engagement data |
| **Data volume** | ~500M impressions/day, ~20M clicks/day feeding back | Kafka ingestion, Spark processing, HDFS storage |

### Latency Breakdown (P50)

```
Query parsing + context extraction:    5ms
Stage 1 module selection:             12ms
Stage 1 content fetch (async):       ~45ms (with 50ms timeout)
Stage 2 arbitration:
  - Placement optimization:            2ms
  - Quality filtering:                 1ms
  - LP solve + rounding:               5ms
  - Page composition:                  2ms
Total Stage 2:                        10ms
Response serialization:                3ms
---
Total (excluding content fetch):     ~30ms
Total (with content fetch):         ~75ms P50, ~150ms P99
```

### Scaling Considerations

- Module Register Table fits in memory (~200 entries, <1MB)
- LP solver operates on small problem size (30 modules x 48 positions)
  making exact LP relaxation feasible within latency budget
- Thompson Sampling state (Beta posteriors) stored in Redis for
  cross-pod consistency; read latency <1ms
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = r"""## Trade-off Analysis

| Decision | Option A | Option B | Our Choice & Why |
|----------|----------|----------|------------------|
| Exploration strategy | UCB (Upper Confidence Bound) | Thompson Sampling | **Thompson Sampling** -- better empirical performance with non-stationary rewards; UCB too conservative for seasonal module performance shifts |
| Optimization scope | Per-slot greedy allocation | Whole-page LP optimization | **Whole-page LP** -- greedy misses cross-module interactions (e.g., ad fatigue when adjacent ads); LP captures page-level value at ~2x latency cost |
| Cold-start modules | Random exploration | Contextual bandits with prior from module-type similarity | **Contextual bandits** -- use module type similarity to warm-start Beta posteriors; pure random wastes too many impressions on bad placements |
| Quality gate | Hard threshold (block below X) | Soft penalty in objective function | **Hybrid** -- hard gate prevents worst-case UX (blocks truly bad modules); soft penalty for borderline modules preserves exploration opportunity |
| Scoring location | All offline (pre-computed) | All online (real-time) | **Hybrid** -- offline pre-computes base value and module features (cheap); online adjusts for real-time context like query intent and user session (expensive but necessary) |

### Detailed Analysis: Thompson Sampling vs. UCB

**Why TS wins for this domain:**

- Module performance is **non-stationary** (seasonal trends, promotions,
  inventory changes). TS with a sliding window naturally adapts because
  sampling from the posterior automatically balances exploration based on
  uncertainty.
- UCB1's confidence bound $\sqrt{\frac{2 \ln n}{n_m}}$ shrinks monotonically,
  which means it eventually stops exploring even when the environment shifts.
- **Empirical result:** Sliding-window TS achieved 12% higher cumulative
  module CTR than fixed-window TS during Q4 2024, and 8% higher than UCB1.

### Detailed Analysis: Greedy vs. LP

**Why whole-page LP is worth the latency cost:**

- Greedy allocation assigns each slot independently, missing **cross-module
  effects**: ad fatigue (adjacent ads reduce click-through on both), content
  diversity (showing 3 similar recommendation modules wastes page real estate).
- LP formulation captures these via constraints (adjacency rules, type-diversity
  limits) and optimizes the **joint** page value.
- The LP relaxation + rounding approach keeps latency at ~5ms (vs. exact ILP
  which would be infeasible) while staying within 2.5% of the exact optimum
  on 98.7% of queries.
"""

# ---------------------------------------------------------------------------
# S7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------
DEFENSE = r"""## Adversarial Defense Q&A

**Q: Thompson Sampling assumes stationary reward distributions. Module performance is clearly non-stationary (seasonality, promotions). How do you justify using TS here?**

> **Limitation acknowledged:** You are right -- standard TS assumes a stationary
> Beta posterior, and module CTR can shift 2-3x during Black Friday or flash
> sales.
>
> **Mitigation:** We use a sliding-window variant: the Beta posteriors are
> computed over a 7-day rolling window, not all-time. Old observations decay
> with a discount factor $\gamma = 0.95$ per day. This makes the posterior
> "forget" old performance and adapt to regime changes within 3-5 days.
>
> **Data:** In A/B testing, sliding-window TS achieved 12% higher cumulative
> module CTR than fixed-window TS during Q4 2024 (high seasonality), and 8%
> higher than UCB1. The convergence gap was largest for newly launched
> promotional modules.

---

**Q: Your whole-page LP claims <10ms but Integer LP is NP-hard. What is the real complexity?**

> **Limitation acknowledged:** Exact ILP is indeed NP-hard. We do not solve
> exact ILP in production.
>
> **Mitigation:** We use LP relaxation + deterministic rounding. The LP
> relaxation (allowing fractional assignments) solves in $O(n \cdot m)$ for
> $n$ modules and $m$ positions via a specialized network flow solver.
> Rounding uses a greedy procedure that respects hard constraints.
>
> **Data:** In offline analysis, the LP-relaxation-with-rounding solution is
> within 2.5% of the exact ILP optimum on 98.7% of queries. The 1.3% of
> worst-case queries involve >20 modules competing for 3-4 premium slots --
> even there, the gap is <5%. P99 solve time is 7ms for 30 modules / 48
> positions.

---

**Q: What happens when an external content provider is consistently slow? Do you not degrade the page?**

> **Limitation acknowledged:** Yes, a slow provider means its modules never
> make it past the 50ms timeout, effectively removing them from the
> marketplace.
>
> **Mitigation:** Three layers of defense:
>
> 1. **Monitoring** -- we track provider latency P50/P99 and alert at >40ms P50
> 2. **Caching** -- for providers with semi-static content (e.g., brand ads),
>    we cache the last successful response and serve stale content within a
>    1-hour TTL
> 3. **Graceful degradation** -- the page always renders with whatever modules
>    responded; we never show a blank slot. The system logs which modules were
>    dropped per query for offline analysis.
>
> **Data:** In 2024, provider timeout rate was ~0.3% of queries. With caching,
> effective availability was 99.85%. The revenue impact of dropped modules was
> estimated at <0.1% total page GMV.

---

**Q: Why not just let the product team manually set module priorities instead of building this marketplace?**

> **Limitation acknowledged:** Manual prioritization is simpler and works for
> a small number of module types (3-4).
>
> **Mitigation:** eBay SRP has ~200 registered module types across teams, and
> the optimal allocation varies by query type, user segment, and time of day.
> Manual rules cannot capture this dimensionality. The marketplace approach
> also provides a transparent "price discovery" mechanism -- each team can see
> how their module's value compares to alternatives, which aligns incentives.
>
> **Data:** After launching the marketplace, the number of active module types
> grew from 12 to 45 within 6 months, because teams could now launch new
> modules without negotiating for fixed page slots. Page-level GMV increased
> ~4% from better allocation.
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = r"""## Verbal Outline

### 3-Minute Version

1. **(30s) Context:** eBay SRP had a fixed module layout with no data-driven
   allocation. New modules required manual negotiation for page slots, and
   there was no signal for which modules created the most value per impression.

2. **(45s) Key Insight:** Treat the SRP as a content marketplace -- modules
   bid for page real estate based on predicted engagement value, and a
   centralized arbitration system allocates positions to maximize total page
   value.

3. **(60s) Architecture:** Two-stage system. Offline layer pre-computes module
   values using XGBoost on 6 months of engagement data, with Thompson Sampling
   for exploration. Online layer runs two stages per query: (1) select eligible
   modules and fetch content in parallel, (2) solve a constrained LP to
   allocate page positions and compose the final layout.

4. **(30s) Core Algorithm:** Thompson Sampling with sliding-window posteriors
   for exploration, plus LP relaxation with deterministic rounding for
   whole-page optimization -- solves in <10ms for 30 modules and 48 positions.

5. **(15s) Result:** Page-level GMV increased ~4%. Module ecosystem grew from
   12 to 45 active types in 6 months without manual slot negotiation.

### 10-Minute Version

1. **(1 min) Context + Motivation:** Fixed layout problems -- no value signal,
   context-blind allocation, scaling bottleneck for new modules. Business
   impact of misallocation: premium real estate wasted on low-engagement
   modules while high-value modules were pushed below the fold.

2. **(2 min) Architecture Walkthrough:**
   - Offline layer: Module Registration (metadata, placement constraints),
     Value Prediction (XGBoost/LightGBM with contextual features), Thompson
     Sampling (Beta posteriors per module, sliding-window variant)
   - Online layer: Stage 1 -- candidate selection (15-30 from ~200) with
     parallel content fetch (50ms timeout). Stage 2 -- placement optimization,
     quality filtering, LP-based value maximization, page composition.

3. **(2 min) Core Algorithms:**
   - Expected value formula: $E[V_m] = P(\text{click}|m,q,u) \cdot \text{Revenue}(m) + \alpha \cdot P(\text{engagement}|m)$
   - Thompson Sampling: $\theta_m \sim \text{Beta}(\alpha_m + s_m, \beta_m + f_m)$ with $\gamma=0.95$ daily decay
   - LP formulation: maximize $\sum x_{m,p} \cdot V(m,p)$ subject to assignment, diversity, and adjacency constraints
   - LP relaxation + greedy rounding: $O(n \cdot m)$ solve, within 2.5% of exact ILP on 98.7% of queries

4. **(2 min) Production Constraints:**
   - 50K QPS, <10ms arbitration budget, <150ms E2E P99
   - LP relaxation makes NP-hard ILP tractable; network flow solver + greedy rounding
   - Provider timeout handling: monitoring, caching (1hr TTL), graceful degradation
   - Data scale: 500M impressions/day, 20M clicks/day, 6-month feature store

5. **(2 min) Trade-offs:**
   - Thompson Sampling vs. UCB: TS wins empirically in non-stationary setting
     (12% higher CTR in Q4 high-seasonality period)
   - Greedy vs. LP: LP captures cross-module interactions (ad fatigue,
     diversity) at 2x latency cost but stays within budget
   - Cold-start: contextual bandits with module-type priors vs. random exploration

6. **(1 min) Results + Lessons:**
   - GMV +4%, module ecosystem 12 to 45 types, transparent value discovery
   - What I would do differently: add counterfactual evaluation earlier to
     measure the true incremental value of each module (not just observed
     engagement which has selection bias)
"""


def populate_module_arbitration() -> None:
    """Update the module-arbitration record with all 8 markdown sections."""
    init_db()
    db = SessionLocal()

    try:
        record = (
            db.query(SystemDesign)
            .filter(SystemDesign.slug == SLUG)
            .first()
        )

        if record is None:
            print(f"[FAIL] No SystemDesign record found with slug='{SLUG}'.")
            print("Run scripts/seed_system_designs.py first to create the record.")
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
        print(f"[DONE] Updated all 8 sections for '{SLUG}'.")

        # Verify by re-reading
        db.refresh(record)
        sections = [
            ("overview", record.overview),
            ("architecture", record.architecture),
            ("dataflow", record.dataflow),
            ("formulas", record.formulas),
            ("production_constraints", record.production_constraints),
            ("tradeoffs", record.tradeoffs),
            ("defense", record.defense),
            ("verbal_outline", record.verbal_outline),
        ]
        for name, content in sections:
            length = len(content) if content else 0
            status = "[OK]" if length > 100 else "[WARN] short"
            print(f"  {status} {name}: {length} chars")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_module_arbitration()
