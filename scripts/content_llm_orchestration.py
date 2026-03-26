"""Populate content for the llm-orchestration system design module.

Loads all 8 markdown sections (overview, architecture, dataflow, formulas,
production_constraints, tradeoffs, defense, verbal_outline) into the
SystemDesign record with slug='llm-orchestration'.

Idempotent: overwrites existing content on re-run.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

SLUG = "llm-orchestration"

# ---------------------------------------------------------------------------
# S1: Overview & Motivation
# ---------------------------------------------------------------------------
OVERVIEW = """\
## Overview & Motivation

Traditional search relies on **keyword matching + learned ranking**, which struggles
with complex multi-intent queries (e.g., "vintage leather jacket under $100 with
free shipping from top-rated sellers"). LLMs understand nuanced intent but cannot
perform retrieval at scale due to hallucination, latency, and lack of real-time
inventory awareness.

### The Proxy Pattern

Our solution uses the LLM as an **artifact generator**, not a retrieval engine:

1. The LLM analyzes the query and produces **structured artifacts**: intent tags,
   filter constraints, and query rewrites.
2. The existing **Cassini** search engine executes retrieval using those artifacts.

> **Key insight**: LLM intelligence + Cassini reliability. The LLM never touches
> inventory directly -- it only shapes the instructions that Cassini follows.

### Why This Matters

| Approach | Intent Understanding | Retrieval Accuracy | Latency | Hallucination Risk |
|----------|---------------------|-------------------|---------|-------------------|
| Keyword search | Low | High | Low | None |
| End-to-end LLM | High | Low | High | High |
| **Proxy pattern** | **High** | **High** | **Medium** | **None** |

The proxy pattern captures the best of both worlds: the LLM's semantic
understanding combined with Cassini's battle-tested retrieval pipeline.
"""

# ---------------------------------------------------------------------------
# S2: Architecture Deep Dive
# ---------------------------------------------------------------------------
ARCHITECTURE = """\
## Architecture Deep Dive

### Online Inference Stack

The online path processes each query through a multi-stage pipeline:

```
Query -> SaaS Orchestrator -> Context Manager -> Generator LLM -> Artifact Set -> Cassini -> Response
```

**Components:**

- **SaaS Orchestrator**: Routes the query into the processing pipeline, manages
  timeouts (80ms budget for LLM), and handles fallback logic.
- **Context Manager**: Aggregates session context -- prior queries, clicks, cart
  contents, and browsing history -- into a compact prompt for the LLM.
- **Generator LLM**: A fine-tuned ~7B parameter model producing structured artifacts.
  Small enough for P99 < 65ms inference on A10 GPUs.
- **Agent Artifact Set**: The LLM's output, containing:
  - **Intent/Affinity Digest**: semantic query decomposition
  - **Proxy**: filter and constraint specifications
  - **SrpAgentGist**: structured summary for downstream components

### Cassini Execution Engine

Cassini processes artifacts through four ranking stages:

1. **L1 Ranking (Popularity)**: Fast candidate retrieval using inverted index +
   popularity priors. Narrows from millions to ~1000 candidates.
2. **Intent-Affinity Gating**: Soft-gates candidates using LLM-generated intent
   signals. Down-weights (not removes) non-matching items.
3. **L2 Ranking (Neural)**: Full neural ranking model scores the gated candidate set.
4. **Attribution-Aware Diversity Scoring**: MMR-style re-ranking with source
   provenance bonuses for underrepresented sellers/categories.

### Offline Learning & Evolution Loop

```
Sojourner/Cassini logs
  -> Unified Feature Table (streaming aggregation)
  -> Learning Core:
       - Distance Calibration (4-hour cycle)
       - MLR Training (daily)
       - Proxy Execution feedback
  -> SDF Service deploys updated models
```

The offline loop continuously improves both the LLM's artifact quality and
Cassini's ranking models using production engagement data.
"""

# ---------------------------------------------------------------------------
# S3: Data Flow & Key Components
# ---------------------------------------------------------------------------
DATAFLOW = """\
## Data Flow & Key Components

### Online Path (per query)

```
User Query
  |
  v
SaaS Orchestrator (timeout budget: 200ms total)
  |
  v
Context Manager (session history, cart, prior clicks)
  |
  v
Generator LLM (~7B, P50: 35ms, P99: 65ms)
  |
  +---> Intent/Affinity Digest
  +---> Proxy (filter constraints)
  +---> SrpAgentGist (structured summary)
  |
  v
Cassini Execution Engine
  |---> L1 Retrieval (popularity-based, ~1000 candidates)
  |---> Intent-Affinity Gating (soft gate, confidence threshold 0.7)
  |---> L2 Neural Ranking (full scoring)
  |---> Attribution-Aware Diversity (MMR + source bonus)
  |
  v
Structured JSON Response -> Structured Builder -> User
```

### Offline Path (continuous)

```
User Interactions (clicks, purchases, dwell time)
  |
  v
Sojourner + Cassini Logs (raw events)
  |
  v
Unified Feature Table (~2TB, 2-week sliding window)
  |  (streaming aggregation via Kafka + Spark)
  |
  v
Learning Core
  |---> Distance Calibration (every 4 hours)
  |---> MLR Training (daily, ~50M query-artifact-engagement triples)
  |---> Proxy Execution Feedback (artifact quality monitoring)
  |
  v
SDF Service (model deployment) -> Updated Generator LLM + Cassini models
```

### Fallback Chain

When the LLM path is unavailable, the system degrades gracefully:

1. **Primary**: LLM generates artifacts, Cassini executes
2. **Tier 2**: Cached artifacts from similar recent queries
3. **Tier 3**: Pure Cassini (no artifacts) -- the pre-LLM production system

> The circuit breaker triggers Tier 3 if LLM error rate exceeds 5% over a
> 1-minute window. Recovery is automatic once the error rate drops.
"""

# ---------------------------------------------------------------------------
# S4: Formulas & Algorithms
# ---------------------------------------------------------------------------
FORMULAS = """\
## Formulas & Algorithms

### Intent-Affinity Gating

The gating function determines how strongly an artifact's intent signal should
influence candidate scoring:

$$\\text{gate}(d, a) = \\sigma(W_g \\cdot [e_d;\\; e_a;\\; e_d \\odot e_a])$$

where:
- $e_d$ = document embedding
- $e_a$ = artifact (intent) embedding
- $\\odot$ = element-wise product (interaction term)
- $\\sigma$ = sigmoid activation
- $W_g$ = learned gating weights

The gate output is a **soft weight** in $[0, 1]$ that scales the document's L2
ranking score. A gate value of 0.7 means the document's score is multiplied by
0.7 -- not removed, just down-weighted.

### Distance Calibration

Calibrates the proxy model's predictions against the full LLM's output:

$$\\mathcal{L}_{\\text{cal}} = \\sum_{(q,d)} \\text{sign}(y) \\cdot \\|f(q,d) - \\hat{f}_{\\text{proxy}}(q,d)\\|^2$$

where:
- $f(q,d)$ = full LLM artifact score for query-document pair
- $\\hat{f}_{\\text{proxy}}(q,d)$ = proxy model's predicted score
- $\\text{sign}(y)$ = asymmetric penalty based on engagement label $y$

**Smooth approximation**: Since $\\text{sign}$ is non-differentiable at zero, we use:

$$\\text{sign}(y) \\approx \\tanh(\\beta \\cdot y), \\quad \\beta = 5$$

This preserves gradient flow while maintaining asymmetric behavior: penalizing
**over-filtering more than under-filtering** (missing a relevant result is worse
than showing a borderline one).

### Attribution-Aware Diversity

An MMR-style re-ranking objective with an attribution bonus:

$$\\text{score}_{\\text{div}}(d_i) = \\lambda \\cdot \\text{rel}(d_i) - (1-\\lambda) \\cdot \\max_{d_j \\in S} \\text{sim}(d_i, d_j) + \\alpha \\cdot \\text{attr\\_bonus}(d_i)$$

where:
- $\\text{rel}(d_i)$ = relevance score from L2 ranking
- $S$ = set of already-selected documents
- $\\text{sim}(d_i, d_j)$ = content similarity
- $\\text{attr\\_bonus}(d_i)$ = bonus for underrepresented source (seller, category)
- $\\lambda$ = relevance-diversity trade-off parameter
- $\\alpha$ = attribution bonus weight

### MLR Training Objective

Pairwise listwise loss over document sets:

$$\\mathcal{L}_{\\text{MLR}} = -\\sum_{q} \\sum_{(d^+, d^-)} \\log \\sigma\\bigl(s(q, d^+) - s(q, d^-)\\bigr)$$

where $d^+$ ranks higher than $d^-$ in the ground truth, and $s(q, d)$ is the
model's scoring function.
"""

# ---------------------------------------------------------------------------
# S5: Production Constraints
# ---------------------------------------------------------------------------
PRODUCTION_CONSTRAINTS = """\
## Production Constraints

| Metric | Value | Context |
|--------|-------|---------|
| **LLM inference latency** | P50: 35ms, P99: 65ms | Fine-tuned 7B model on dedicated GPU cluster (A10) |
| **LLM throughput** | ~8K inferences/sec across cluster | 4x A10 GPU pods, batch size 16 |
| **Fallback rate** | ~2% of queries fall back to pure Cassini | LLM timeout (80ms) or confidence below threshold |
| **Artifact quality** | 92% intent accuracy (vs 96% for GPT-4 class) | Validated against 10K human-labeled queries monthly |
| **End-to-end search latency** | P50: 120ms, P99: 200ms (with LLM); P50: 80ms (without) | LLM adds ~40ms to search path but measurably improves relevance |
| **Offline learning cycle** | Feature aggregation: near-real-time; Model retrain: daily | Distance calibration updates every 4 hours |
| **Training data volume** | ~50M query-artifact-engagement triples per training cycle | 2-week sliding window aggregation |
| **Storage** | Unified Feature Table: ~2TB (2-week sliding window) | Partitioned by date + query segment |

### Latency Budget Breakdown

```
Total search P99: 200ms
  |- SaaS Orchestrator:    5ms
  |- Context Manager:     10ms
  |- Generator LLM:       65ms (P99)
  |- L1 Retrieval:        30ms
  |- Intent-Affinity Gate: 15ms
  |- L2 Neural Ranking:   50ms
  |- Diversity Scoring:   15ms
  |- Serialization:       10ms
```

### GPU Resource Allocation

- **Cluster**: 4x A10 GPU pods (24GB VRAM each)
- **Model**: 7B parameters, INT8 quantized (~7GB VRAM)
- **Batch size**: 16 queries per batch
- **Scaling**: Horizontal pod autoscaler, target GPU utilization 70%
"""

# ---------------------------------------------------------------------------
# S6: Trade-off Analysis
# ---------------------------------------------------------------------------
TRADEOFFS = """\
## Trade-off Analysis

| Decision | Option A | Option B | Our Choice & Why |
|----------|----------|----------|------------------|
| **LLM model size** | Large (~100B) | Small fine-tuned (~7B) | **Small** -- P99 < 65ms required; fine-tuned achieves 92% intent accuracy |
| **Artifact execution** | LLM directly returns results | LLM -> artifacts -> Cassini executes | **Proxy pattern** -- eliminates hallucination, leverages existing retrieval infrastructure |
| **Calibration frequency** | Daily batch | Near-real-time streaming | **Hybrid** -- streaming for features, 4-hour batch for calibration |
| **Diversity strategy** | Post-hoc MMR | Attribution-aware in ranking | **Attribution-aware** -- considers source provenance, not just content similarity |
| **Fallback strategy** | No artifacts (pure Cassini) | Cached similar-query artifacts | **Tiered** -- (1) LLM, (2) cached, (3) pure Cassini. Zero-downtime guarantee |

### Deep Dive: Model Size Trade-off

The decision between a large foundation model and a small fine-tuned model was
the most consequential architectural choice:

| Factor | Large Model (~100B) | Small Fine-tuned (~7B) |
|--------|--------------------|-----------------------|
| Intent accuracy | ~96% (GPT-4 class) | ~92% |
| Inference latency (P99) | 300-500ms | 65ms |
| GPU cost | 8x A100 ($50K/month) | 4x A10 ($8K/month) |
| Fits in search latency budget? | No (200ms total) | Yes |
| Fine-tuning flexibility | Limited (API-only) | Full control |

The 4% accuracy gap costs us ~0.3% engagement, but the latency savings and cost
reduction make the small model clearly dominant for our use case.

### Deep Dive: Soft vs. Hard Gating

We chose **soft gating** (down-weight by ~30%) over hard gating (remove non-matching):

- **Hard gating risk**: If the LLM's intent is wrong (8% of queries), hard gating
  removes all relevant results. Users see an empty or irrelevant page.
- **Soft gating behavior**: Wrong intent down-weights relevant items but doesn't
  remove them. The L2 neural ranker can still surface them via relevance signals.
- **A/B result**: Soft gating showed neutral engagement on the 8% error queries
  (no harm), while hard gating showed -12% engagement on error queries (significant harm).
"""

# ---------------------------------------------------------------------------
# S7: Adversarial Defense Q&A
# ---------------------------------------------------------------------------
DEFENSE = """\
## Adversarial Defense Q&A

**Q: Your 7B model gets 92% intent accuracy. That means 8% of queries get wrong artifacts piped into Cassini. Isn't that worse than no LLM at all?**

> **Limitation acknowledged:** 8% error rate is real. A wrong intent filter can
> remove relevant results entirely.
>
> **Mitigation:** The Intent-Affinity Gating is a **soft gate**, not a hard filter.
> Wrong intents don't remove results -- they down-weight non-matching candidates
> by ~30% in L2 scoring. The ranking still considers relevance signals independent
> of the artifact. Additionally, we have a confidence threshold: if the LLM's
> intent confidence is < 0.7, we skip the gating entirely and fall back to pure
> Cassini.
>
> **Data:** In A/B testing, the 8% error queries showed neutral engagement (not
> negative) because the soft gating preserved fallback retrieval. The 92% correct
> queries showed +6% click-through and +3% purchase rate. Net: overall +5.2%
> engagement vs. no-LLM baseline.

---

**Q: How do you prevent the LLM from being a single point of failure in the search path?**

> **Limitation acknowledged:** Adding any component to the critical search path
> creates a new failure mode.
>
> **Mitigation:** (1) Circuit breaker: if LLM error rate exceeds 5% over a
> 1-minute window, we automatically bypass LLM for all queries until recovery.
> (2) Async prefetch: for typed queries, LLM starts after 3rd keystroke while
> the user is still typing. (3) The fallback (pure Cassini) is the production
> system that ran for years -- it's not degraded, just not enhanced.
>
> **Data:** LLM service availability: 99.95% (2024 annual). Circuit breaker
> triggered 3 times in 12 months, each for < 5 minutes. User impact during
> breaker: undetectable in engagement metrics.

---

**Q: Distance Calibration with signed learning -- doesn't the sign function make gradients zero almost everywhere?**

> **Limitation acknowledged:** The sign function is indeed non-differentiable
> at zero.
>
> **Mitigation:** We use a smooth approximation:
> $\\text{sign}(y) \\approx \\tanh(\\beta \\cdot y)$ with $\\beta = 5$. This
> preserves gradient flow while maintaining the asymmetric penalty behavior.
> The key insight is that we want to penalize over-filtering MORE than
> under-filtering (missing a relevant result is worse than showing a borderline one).
>
> **Data:** With smooth sign, calibration converges in ~3 epochs. With hard sign,
> it oscillates. The smooth variant achieves 94% calibration correlation vs. 87%
> for symmetric MSE loss.
"""

# ---------------------------------------------------------------------------
# S8: Verbal Outline (3-min & 10-min)
# ---------------------------------------------------------------------------
VERBAL_OUTLINE = """\
## Verbal Outline

### 3-Minute Version

1. **(30s) Problem**: Complex multi-intent queries cannot be served by keyword
   matching alone. Users type natural-language queries expecting semantic
   understanding, but traditional search engines only do lexical matching.

2. **(45s) Key Insight -- Proxy Pattern**: The LLM generates structured artifacts
   (intent tags, filter constraints, query rewrites), and the existing Cassini
   engine executes retrieval. The LLM never touches inventory directly -- it
   only shapes instructions. This eliminates hallucination risk entirely.

3. **(60s) Architecture**: Online path: LLM -> artifacts -> Cassini L1 retrieval
   -> Intent-Affinity Gating (soft, not hard) -> L2 neural ranking -> diversity
   scoring. Offline path: engagement logs -> distance calibration (4-hour cycle)
   -> MLR training (daily) -> model updates.

4. **(30s) Production Reality**: 7B fine-tuned model, P99 65ms on A10 GPUs.
   Soft gating with 0.7 confidence threshold. Circuit breaker at 5% error rate.
   Tiered fallback: LLM -> cached artifacts -> pure Cassini.

5. **(15s) Result**: +5.2% engagement net (including the 8% error queries).
   99.95% availability. Zero-downtime fallback to pre-LLM system.

### 10-Minute Version

1. **(1.5 min) Problem Space**: Why keyword search fails for complex queries.
   Why LLMs cannot do retrieval directly: hallucination (invents products that
   don't exist), latency (300ms+ for large models), freshness (no real-time
   inventory awareness). The gap between understanding and execution.

2. **(2 min) Proxy Pattern Architecture**: LLM generates artifacts, Cassini
   executes. Artifact types: intent/affinity digest, proxy filters, SrpAgentGist.
   Soft gating vs. hard filtering -- why soft gating is critical for error
   tolerance. Confidence threshold design.

3. **(2 min) Offline Learning**: Distance calibration: aligning proxy model with
   full LLM using signed learning. Smooth sign approximation for gradient flow.
   MLR training: pairwise listwise loss on 50M triples. 4-hour calibration cycle
   vs. daily model retrain.

4. **(1.5 min) Production Constraints**: 7B model choice: 92% accuracy at 65ms
   vs. 96% at 300ms. Latency budget breakdown (200ms total, 65ms for LLM).
   GPU cluster sizing: 4x A10, 8K inferences/sec. Fallback strategy and circuit
   breaker mechanics.

5. **(2 min) Trade-offs**: Model size vs. accuracy (the 4% gap analysis). Soft
   vs. hard gating (A/B results on error queries). Calibration frequency
   (streaming features + batch calibration). Attribution-aware diversity vs.
   post-hoc MMR.

6. **(1 min) Results + Retrospective**: +5.2% engagement, +3% purchase rate on
   correct queries. 99.95% availability. What I would do differently: start with
   a smaller artifact set (intent only) before adding filters and rewrites.
   The complexity of multi-artifact coordination was underestimated initially.
"""


def populate_llm_orchestration() -> None:
    """Update the llm-orchestration SystemDesign record with all 8 sections."""
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
            print("Run scripts/seed_system_designs.py first.")
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
        print(f"[DONE] Updated all 8 sections for slug='{SLUG}'.")

        # Verification: re-read and check non-empty
        db.refresh(record)
        fields = [
            "overview", "architecture", "dataflow", "formulas",
            "production_constraints", "tradeoffs", "defense", "verbal_outline",
        ]
        for field in fields:
            value = getattr(record, field)
            if value and len(value) > 50:
                print(f"  [OK] {field}: {len(value)} chars")
            else:
                print(f"  [WARN] {field}: empty or very short")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_llm_orchestration()
