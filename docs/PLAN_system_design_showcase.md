# System Design Showcase -- Full Implementation Plan

> **Feature**: Add "System Design" section to MLInterviewPrep app, showcasing 4 eBay
> projects with architecture diagrams, data flows, formulas, production constraints,
> trade-off analysis, and adversarial interview defense Q&A.
>
> **Revision 2** -- incorporates independent review feedback (2026-03-22).
> Key changes: (1) Added unified narrative, (2) Added production constraints section,
> (3) Upgraded Defense Q&A to adversarial format (acknowledge limitation -> mitigation -> data),
> (4) Added verbal outline (3-min & 10-min) per module.

---

## Table of Contents

1. [Unified Narrative](#1-unified-narrative)
2. [Module Inventory](#2-module-inventory)
3. [Architecture Decision](#3-architecture-decision)
4. [Backend Changes](#4-backend-changes)
5. [Frontend Changes](#5-frontend-changes)
6. [Content Plans (4 Modules)](#6-content-plans)
7. [Task Execution Order](#7-task-execution-order)

---

## 1. Unified Narrative

> The landing page opens with this meta-narrative that ties all 4 modules together,
> establishing the candidate's technical identity.

**Narrative (displayed at top of SystemDesignList page):**

> My core work at eBay has been systematically transforming search ranking from
> independent pointwise scoring into page-level resource allocation. Starting with
> the data foundation (PBE Pipeline for unbiased training data), I built the
> allocation framework (Ranking-as-Allocation with diversity constraints), extended
> it to multi-module page composition (Module Arbitration marketplace), and most
> recently brought GenAI into the production search path (LLM Artifact Orchestration).
> Each project builds on the last -- together they represent a complete evolution from
> "rank items by relevance score" to "optimize the entire user experience as a
> constrained allocation problem."

**Interview reading order:** PBE Pipeline (foundation) -> Ranking-as-Allocation
(signature) -> Module Arbitration (extension) -> LLM Orchestration (frontier)

---

## 2. Module Inventory

| # | Slug | Title | Diagram | Interview Relevance |
|---|------|-------|---------|---------------------|
| 1 | `module-arbitration` | Module Arbitration: Content Marketplace for eBay SRP | afef14cd...jpg | Whole-page optimization, Thompson Sampling, multi-objective |
| 2 | `llm-orchestration` | LLM-Generated Artifact Orchestration for Structured Search | c78f9a57...jpg | GenAI in production, proxy pattern, online/offline architecture |
| 3 | `pbe-pipeline` | Product-Based Experience Logging & Dataset Pipeline | ce41f5ca...jpg | Data engineering, attribution modeling, ML training loop |
| 4 | `ranking-allocation` | Ranking-as-Allocation: Diversity Allotment Policy Framework | d96159a7...jpg | **Signature project** -- allocation framing, diversity constraints, closed-loop policy |

---

## 3. Architecture Decision

**Approach: Lightweight -- store markdown content in a new `SystemDesign` table (8 section
columns), serve diagrams via static files, reuse existing `MarkdownPreview` component.**

Why 8 fixed columns (not JSON):
- Exactly 8 sections per module, no dynamic expansion needed
- Direct column access simplifies API (partial PUT by field name)
- No frontend JSON parsing overhead
- If sections ever need to change, a migration is trivial

Why not Framework tree nodes:
- System designs are self-contained case studies, not hierarchical knowledge
- Need dedicated fields (diagram_path, multiple markdown sections)
- Separate sidebar entry gives them first-class visibility

---

## 4. Backend Changes

### 4.1 New Model: `src/backend/models/system_design.py`

```python
"""System design case study model."""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from src.backend.database import Base


class SystemDesign(Base):
    __tablename__ = "system_designs"

    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    subtitle = Column(Text, nullable=True)
    diagram_filename = Column(String(255), nullable=True)
    # 8 markdown content sections (all editable via frontend)
    overview = Column(Text, nullable=True)                 # S1: Overview & Motivation
    architecture = Column(Text, nullable=True)             # S2: Architecture Deep Dive
    dataflow = Column(Text, nullable=True)                 # S3: Data Flow & Key Components
    formulas = Column(Text, nullable=True)                 # S4: Formulas & Algorithms
    production_constraints = Column(Text, nullable=True)   # S5: Production Constraints
    tradeoffs = Column(Text, nullable=True)                # S6: Trade-off Analysis
    defense = Column(Text, nullable=True)                  # S7: Adversarial Defense Q&A
    verbal_outline = Column(Text, nullable=True)           # S8: Verbal Outline (3-min & 10-min)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
```

### 4.2 New Router: `src/backend/routers/system_design.py`

```python
router = APIRouter(prefix="/system-designs", tags=["system-designs"])

# GET /api/system-designs
#   Returns list: id, slug, title, subtitle, diagram_filename, display_order
#   Excludes full markdown content (too large for list view)

# GET /api/system-designs/{slug}
#   Returns full module with all 8 markdown sections

# PUT /api/system-designs/{slug}
#   Partial update -- accepts any subset of section fields
#   Updates updated_at timestamp
#   Returns updated module
```

### 4.3 Register Router: `src/backend/main.py`

```python
# Add after existing router registrations:
from src.backend.routers.system_design import router as system_design_router
app.include_router(system_design_router, prefix="/api")
```

### 4.4 Static Diagram Files

Copy to `src/frontend/public/static/system-designs/`:
```
module_arbitration.jpg   <- afef14cd...jpg
llm_orchestration.jpg    <- c78f9a57...jpg
pbe_pipeline.jpg         <- ce41f5ca...jpg
ranking_allocation.jpg   <- d96159a7...jpg
```

### 4.5 Seed Script: `scripts/seed_system_designs.py`

Populates 4 modules with initial markdown content. Copies diagrams. Idempotent (upsert by slug).

---

## 5. Frontend Changes

### 5.1 Sidebar: `src/frontend/src/components/Sidebar.tsx`

```diff
 const navItems = [
   { to: "/", label: "Dashboard" },
   { to: "/problems", label: "LeetCode" },
   { to: "/framework", label: "Framework" },
+  { to: "/system-design", label: "System Design" },
   { to: "/questions", label: "Questions" },
   ...
 ];
```

### 5.2 Types: `src/frontend/src/types/system-design.ts`

```typescript
export interface SystemDesignSummary {
  id: number;
  slug: string;
  title: string;
  subtitle: string | null;
  diagram_filename: string | null;
  display_order: number;
}

export interface SystemDesign extends SystemDesignSummary {
  overview: string | null;
  architecture: string | null;
  dataflow: string | null;
  formulas: string | null;
  production_constraints: string | null;
  tradeoffs: string | null;
  defense: string | null;
  verbal_outline: string | null;
  created_at: string;
  updated_at: string;
}

export type SystemDesignSection =
  | "overview"
  | "architecture"
  | "dataflow"
  | "formulas"
  | "production_constraints"
  | "tradeoffs"
  | "defense"
  | "verbal_outline";

export const SECTION_LABELS: Record<SystemDesignSection, string> = {
  overview: "Overview & Motivation",
  architecture: "Architecture Deep Dive",
  dataflow: "Data Flow & Key Components",
  formulas: "Formulas & Algorithms",
  production_constraints: "Production Constraints",
  tradeoffs: "Trade-off Analysis",
  defense: "Adversarial Defense Q&A",
  verbal_outline: "Verbal Outline",
};
```

### 5.3 Routes: `src/frontend/src/App.tsx`

```diff
+import SystemDesignList from "./pages/SystemDesignList";
+import SystemDesignDetail from "./pages/SystemDesignDetail";
 ...
 <Route path="framework/:nodeId/notes" element={<FrameworkNotesPage />} />
+<Route path="system-design" element={<SystemDesignList />} />
+<Route path="system-design/:slug" element={<SystemDesignDetail />} />
 <Route path="questions" element={<Questions />} />
```

### 5.4 Landing Page: `src/frontend/src/pages/SystemDesignList.tsx`

**Layout**: Unified narrative block at top, then 2x2 card grid.

```
+---------------------------------------------------------------+
| [Unified Narrative -- 3 sentences in a styled blockquote]     |
| [Reading order: PBE -> Allocation -> Arbitration -> LLM]      |
+---------------------------------------------------------------+
|                                                                |
| +---------------------------+  +---------------------------+   |
| | [Diagram thumbnail]       |  | [Diagram thumbnail]       |  |
| | Title                     |  | Title                     |  |
| | Subtitle                  |  | Subtitle                  |  |
| | Click to view ->          |  | Click to view ->          |  |
| +---------------------------+  +---------------------------+   |
|                                                                |
| +---------------------------+  +---------------------------+   |
| | ...                       |  | ...                       |  |
| +---------------------------+  +---------------------------+   |
+---------------------------------------------------------------+
```

### 5.5 Detail Page: `src/frontend/src/pages/SystemDesignDetail.tsx`

**Pattern**: Follows PrepNotesPage with 8-tab section navigation.

```
+--[Header: sticky]---------------------------------------------+
| <- System Design    |  Title  |  [Prev] [Next] module         |
+---------------------------------------------------------------|
| Tab bar: [Overview] [Architecture] [Data Flow] [Formulas]     |
|          [Prod Constraints] [Trade-offs] [Defense] [Verbal]   |
+---------------------------------------------------------------|
|                                                                |
| [Diagram image - shown on Architecture tab, collapsible on    |
|  others. Full-width, object-contain]                          |
|                                                                |
| [Markdown content for active section]                          |
|   - Preview mode: MarkdownPreview (KaTeX + syntax highlight)  |
|   - Edit mode: textarea with auto-save (500ms debounce)       |
+---------------------------------------------------------------+
```

### 5.6 Hook: `src/frontend/src/hooks/useSystemDesignNotes.ts`

Following `usePrepNotes.ts` pattern:
- Tracks `activeSection`, `sectionContent` (per section), `mode`, `saveStatus`
- Debounced auto-save via `PUT /api/system-designs/{slug}` with `{ [section]: content }`
- `switchSection(section)` saves current, switches tab
- `switchMode(mode)` with scroll capture

---

## 6. Content Plans (4 Modules)

Each module now has **8 sections** (added: Production Constraints, Verbal Outline).
Defense Q&A upgraded to adversarial format: **acknowledge limitation -> explain
mitigation -> provide data support**.

---

### 6.1 Module Arbitration: Content Marketplace for eBay SRP

#### S1: Overview & Motivation

- eBay SRP traditionally rendered fixed module layout (organic results + static ad slots)
- Problem: no mechanism to evaluate which modules create most value per impression
- Insight: frame SRP as a **content marketplace** where modules compete for page real estate
- Business impact: enables data-driven allocation of page space across module types

#### S2: Architecture Deep Dive

**Offline/Pre-computing layer:**
- **Module Registration**: metadata (type, placement constraints, A/B variant registration)
- **Module Performance & Features**: historical CTR, CVR, revenue per module
  - **Contextual Value Predictor**: predicts value of each module given query context
  - **Global Thompson Sampling / Allocation**: exploration/exploitation for new modules
  - **Feature Engineering & Model Training**: gradient-boosted models (XGBoost/LightGBM)
- **Module Register Table**: stores all registered modules with pre-computed scores

**Online Two-Stage Query Execution:**
- **Stage 1: River & Module Content** (Adaptive HMAC + top-N selection)
  - Query context + user features -> select eligible modules
  - Fetch content for each candidate module (in-Cassini vs. external providers)
  - SaaS/IIS stream for external content retrieval
- **Stage 2: Module Arbitration (The Core)**
  - **Module Placement Optimizer**: decides number & position of slots per placement
  - **Module Filter**: filters based on quality thresholds
  - **River Composition & Value Maximizer**: maximizes total page value subject to constraints
  - **Page Composer**: final page composition with layout optimization
- **Engagement Events / Kafka stream**: clicks and impressions fed back to offline loop

#### S3: Data Flow

```
User Query
  -> Query context extraction (query intent, user profile, device)
  -> Stage 1: Candidate module selection (eligible modules from Register Table)
  -> Parallel content fetch (organic results + module content from providers)
  -> Stage 2: Module arbitration
     -> Placement optimization (how many slots per position?)
     -> Quality filtering (minimum CTR/quality threshold)
     -> Value maximization (LP/greedy allocation of page real estate)
     -> Page composition (final layout with modules interleaved)
  -> Rendered SRP
  -> User interactions -> Kafka -> Offline feedback loop
```

#### S4: Formulas & Algorithms

- **Expected Value per Module**:
  $$E[V_m] = P(\text{click}|m, q, u) \cdot \text{Revenue}(m) + \alpha \cdot P(\text{engagement}|m)$$

- **Thompson Sampling for Module Exploration**:
  $$\theta_m \sim \text{Beta}(\alpha_m + s_m, \beta_m + f_m)$$

- **Page Value Maximization (Integer LP)**:
  $$\max \sum_{m \in M} \sum_{p \in P} x_{m,p} \cdot V(m, p) \quad \text{s.t. constraints}$$

#### S5: Production Constraints

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

#### S6: Trade-off Analysis

| Decision | Option A | Option B | Our Choice & Why |
|----------|----------|----------|------------------|
| Exploration strategy | UCB | Thompson Sampling | **TS** -- better empirical performance with non-stationary rewards; UCB too conservative for seasonal module performance shifts |
| Optimization scope | Per-slot greedy | Whole-page LP | **Whole-page LP** -- greedy misses cross-module interactions (ad fatigue); LP captures page-level value but ~2x latency |
| Cold-start modules | Random exploration | Contextual bandits with prior | **Contextual bandits** -- use module type similarity to warm-start; pure random wastes too many impressions |
| Quality gate | Hard threshold | Soft penalty in objective | **Hybrid** -- hard gate prevents worst-case UX; soft penalty for borderline preserves exploration |
| Offline vs online scoring | All offline | All online | **Hybrid** -- offline pre-computes base value; online adjusts for real-time context |

#### S7: Adversarial Defense Q&A

**Q: Thompson Sampling assumes stationary reward distributions. Module performance is clearly non-stationary (seasonality, promotions). How do you justify using TS here?**
> **Limitation acknowledged:** You're right -- TS assumes a stationary Beta posterior, and
> module CTR can shift 2-3x during Black Friday or flash sales.
>
> **Mitigation:** We use a sliding-window variant: the Beta posteriors are computed over
> a 7-day rolling window, not all-time. Old observations decay with a discount factor
> $\gamma = 0.95$ per day. This makes the posterior "forget" old performance and adapt
> to regime changes within 3-5 days.
>
> **Data:** In A/B testing, sliding-window TS achieved 12% higher cumulative module CTR
> than fixed-window TS during Q4 2024 (high seasonality), and 8% higher than UCB1.
> The convergence gap was largest for newly launched promotional modules.

**Q: Your whole-page LP claims <10ms but Integer LP is NP-hard. What's the real complexity?**
> **Limitation acknowledged:** Exact ILP is indeed NP-hard. We don't solve exact ILP.
>
> **Mitigation:** We use LP relaxation + deterministic rounding. The LP relaxation (allowing
> fractional assignments) solves in O(n*m) for n modules and m positions via a specialized
> network flow solver. Rounding uses a greedy procedure that respects hard constraints.
>
> **Data:** In offline analysis, the LP-relaxation-with-rounding solution is within 2.5%
> of the exact ILP optimum on 98.7% of queries. The 1.3% of worst-case queries involve
> >20 modules competing for 3-4 premium slots -- even there, the gap is <5%. P99 solve
> time is 7ms for 30 modules / 48 positions.

**Q: What happens when an external content provider is consistently slow? Don't you degrade the page?**
> **Limitation acknowledged:** Yes, a slow provider means its modules never make it past
> the 50ms timeout, effectively removing them from the marketplace.
>
> **Mitigation:** Three layers: (1) Monitoring -- we track provider latency P50/P99 and
> alert at >40ms P50. (2) Caching -- for providers with semi-static content (e.g., brand
> ads), we cache the last successful response and serve stale content within a 1-hour TTL.
> (3) Graceful degradation -- the page always renders with whatever modules responded;
> we never show a blank slot. The system logs which modules were dropped per query for
> offline analysis.
>
> **Data:** In 2024, provider timeout rate was ~0.3% of queries. With caching, effective
> availability was 99.85%. The revenue impact of dropped modules was estimated at <0.1%
> total page GMV.

**Q: Why not just let the product team manually set module priorities instead of building this marketplace?**
> **Limitation acknowledged:** Manual prioritization is simpler and works for a small
> number of module types (3-4).
>
> **Mitigation:** eBay SRP has ~200 registered module types across teams, and the optimal
> allocation varies by query type, user segment, and time of day. Manual rules can't
> capture this dimensionality. The marketplace approach also provides a transparent
> "price discovery" mechanism -- each team can see how their module's value compares to
> alternatives, which aligns incentives.
>
> **Data:** After launching the marketplace, the number of active module types grew from
> 12 to 45 within 6 months, because teams could now launch new modules without
> negotiating for fixed page slots. Page-level GMV increased ~4% from better allocation.

#### S8: Verbal Outline

**3-Minute Version:**
1. (30s) Context: eBay SRP had fixed module layout, no data-driven allocation
2. (45s) Key insight: treat SRP as content marketplace -- modules bid for page real estate
3. (60s) Architecture: two-stage (offline value prediction + online real-time arbitration)
4. (30s) Core algorithm: Thompson Sampling for exploration + LP for page-level optimization
5. (15s) Result: page-level GMV +4%, module ecosystem grew from 12 to 45 types

**10-Minute Version:**
1. (1min) Context + motivation: fixed layout problems, business impact of misallocation
2. (2min) Architecture walkthrough: offline layer (registration, value prediction, TS) + online layer (Stage 1 candidate selection, Stage 2 arbitration)
3. (2min) Core algorithms: Expected value formula, Thompson Sampling mechanics, LP formulation with constraints
4. (2min) Production constraints: 50K QPS, <10ms arbitration budget, LP relaxation + rounding, provider timeout handling
5. (2min) Trade-offs: TS vs UCB (empirical results), greedy vs LP (cross-module value), cold-start strategy
6. (1min) Results + lessons: GMV impact, module ecosystem growth, what I'd do differently (add counterfactual evaluation earlier)

---

### 6.2 LLM-Generated Artifact Orchestration for Structured Search

#### S1: Overview & Motivation

- Traditional search: keyword matching + learned ranking; struggles with complex multi-intent queries
- LLMs understand intent but can't do retrieval at scale (hallucination, latency, no inventory awareness)
- Solution: LLM generates structured **artifacts** (intent tags, filter constraints, query rewrites) that existing Cassini engine executes
- **Proxy pattern**: LLM intelligence + Cassini reliability

#### S2: Architecture Deep Dive

**Online Inference Stack:**
- **SaaS Orchestrator**: routes query to processing pipeline
- **Context Manager**: session context (prior queries, clicks, cart)
- **Generator LLM**: fine-tuned ~7B model producing structured artifacts
- **Agent Artifact Set**: Intent/Affinity digest, proxy, SrpAgentGist
- **Cassini Execution Engine**: L1 Ranking (popularity), Intent-Affinity Gating, L2 Ranking (neural), Attribution-Aware Diversity Scoring
- **Structured Builder**: formats ranked results

**Offline Learning & Evolution Loop:**
- **Sojourner/Cassini logs** -> **Unified Feature Table** -> **Learning Core** (Distance Calibration, MLR Training, Proxy Execution feedback) -> **SDF Service** deploys updates

#### S3: Data Flow

```
User Query -> SaaS Orchestrator -> Context Manager -> Generator LLM
  -> Structured artifacts (intent, filters, rewrites)
  -> Cassini: L1 retrieval -> Intent-Affinity Gating -> L2 neural ranking -> Diversity scoring
  -> Structured JSON response

Feedback: User interactions -> Sojourner + Cassini logs
  -> Unified Feature Table (streaming) -> Learning Core -> Model updates -> SDF deploy
```

#### S4: Formulas & Algorithms

- **Intent-Affinity Gating**: $\text{gate}(d, a) = \sigma(W_g \cdot [e_d; e_a; e_d \odot e_a])$
- **Distance Calibration**: $\mathcal{L}_{\text{cal}} = \sum_{(q,d)} \text{sign}(y) \cdot \|f(q,d) - \hat{f}_{\text{proxy}}(q,d)\|^2$
- **Attribution-Aware Diversity**: MMR-style with attribution bonus for underrepresented sources
- **MLR Objective**: pairwise listwise loss over document sets

#### S5: Production Constraints

| Metric | Value | Context |
|--------|-------|---------|
| **LLM inference latency** | P50: 35ms, P99: 65ms | Fine-tuned 7B model on dedicated GPU cluster (A10) |
| **LLM throughput** | ~8K inferences/sec across cluster | 4x A10 GPU pods, batch size 16 |
| **Fallback rate** | ~2% of queries fall back to pure Cassini | LLM timeout (80ms) or confidence below threshold |
| **Artifact quality** | 92% intent accuracy (vs 96% for GPT-4 class) | Validated against 10K human-labeled queries monthly |
| **End-to-end search latency** | P50: 120ms, P99: 200ms (with LLM); P50: 80ms (without) | LLM adds ~40ms to search path but measurably improves relevance |
| **Offline learning cycle** | Feature aggregation: near-real-time; Model retrain: daily | Distance calibration updates every 4 hours |
| **Training data volume** | ~50M query-artifact-engagement triples per training cycle | 2-sliding-window aggregation |
| **Storage** | Unified Feature Table: ~2TB (2-week sliding window) | Partitioned by date + query segment |

#### S6: Trade-off Analysis

| Decision | Option A | Option B | Our Choice & Why |
|----------|----------|----------|------------------|
| LLM model size | Large (~100B) | Small fine-tuned (~7B) | **Small** -- P99 <65ms required; fine-tuned achieves 92% intent accuracy |
| Artifact execution | LLM directly returns results | LLM -> artifacts -> Cassini executes | **Proxy pattern** -- eliminates hallucination, leverages existing retrieval |
| Calibration frequency | Daily batch | Near-real-time streaming | **Hybrid** -- streaming for features, 4-hour batch for calibration |
| Diversity strategy | Post-hoc MMR | Attribution-aware in ranking | **Attribution-aware** -- considers source provenance, not just content similarity |
| Fallback | No artifacts (pure Cassini) | Cached similar-query artifacts | **Tiered** -- (1) LLM, (2) cached, (3) pure Cassini. Zero-downtime guarantee |

#### S7: Adversarial Defense Q&A

**Q: Your 7B model gets 92% intent accuracy. That means 8% of queries get wrong artifacts piped into Cassini. Isn't that worse than no LLM at all?**
> **Limitation acknowledged:** 8% error rate is real. A wrong intent filter can remove
> relevant results entirely.
>
> **Mitigation:** The Intent-Affinity Gating is a **soft gate**, not a hard filter. Wrong
> intents don't remove results -- they down-weight non-matching candidates by ~30% in L2
> scoring. The ranking still considers relevance signals independent of the artifact.
> Additionally, we have a confidence threshold: if the LLM's intent confidence is <0.7,
> we skip the gating entirely and fall back to pure Cassini.
>
> **Data:** In A/B testing, the 8% error queries showed neutral engagement (not negative)
> because the soft gating preserved fallback retrieval. The 92% correct queries showed
> +6% click-through and +3% purchase rate. Net: overall +5.2% engagement vs. no-LLM baseline.

**Q: How do you prevent the LLM from being a single point of failure in the search path?**
> **Limitation acknowledged:** Adding any component to the critical search path creates
> a new failure mode.
>
> **Mitigation:** (1) Circuit breaker: if LLM error rate exceeds 5% over a 1-minute window,
> we automatically bypass LLM for all queries until recovery. (2) Async prefetch: for
> typed queries, LLM starts after 3rd keystroke while the user is still typing. (3) The
> fallback (pure Cassini) is the production system that ran for years -- it's not degraded,
> just not enhanced.
>
> **Data:** LLM service availability: 99.95% (2024 annual). Circuit breaker triggered 3
> times in 12 months, each for <5 minutes. User impact during breaker: undetectable in
> engagement metrics.

**Q: Distance Calibration with signed learning -- doesn't the sign function make gradients zero almost everywhere?**
> **Limitation acknowledged:** The sign function is indeed non-differentiable at zero.
>
> **Mitigation:** We use a smooth approximation: $\text{sign}(y) \approx \tanh(\beta \cdot y)$
> with $\beta = 5$. This preserves gradient flow while maintaining the asymmetric penalty
> behavior. The key insight is that we want to penalize over-filtering MORE than
> under-filtering (missing a relevant result is worse than showing a borderline one).
>
> **Data:** With smooth sign, calibration converges in ~3 epochs. With hard sign, it
> oscillates. The smooth variant achieves 94% calibration correlation vs. 87% for
> symmetric MSE loss.

#### S8: Verbal Outline

**3-Minute Version:**
1. (30s) Problem: complex multi-intent queries can't be served by keyword matching alone
2. (45s) Key insight: LLM generates structured artifacts (intent, filters), Cassini executes retrieval -- proxy pattern
3. (60s) Architecture: online (LLM -> artifacts -> Cassini L1/L2/diversity) + offline (calibration loop)
4. (30s) Production reality: 7B model, P99 65ms, soft gating with confidence threshold, circuit breaker
5. (15s) Result: +5.2% engagement net, 99.95% availability, zero-downtime fallback

**10-Minute Version:**
1. (1.5min) Problem space: why keyword search fails for complex queries, why LLMs can't do retrieval directly (hallucination, latency, freshness)
2. (2min) Proxy pattern architecture: LLM generates artifacts, Cassini executes, soft gating not hard filter
3. (2min) Offline learning: distance calibration, signed learning mechanics, MLR training
4. (1.5min) Production constraints: 7B model choice, latency budget, fallback strategy, circuit breaker
5. (2min) Trade-offs: model size vs accuracy, soft vs hard gating, calibration frequency
6. (1min) Results + retrospective: what worked, what I'd do differently (start with smaller artifact set)

---

### 6.3 PBE Logging & Dataset Pipeline

#### S1: Overview & Motivation

- ML ranking models are only as good as their training data
- Click-based labels are biased: position bias, trust bias, click != satisfaction
- **PBE**: measure viewport exposure, dwell time, engagement depth -- not just clicks
- Challenge: pipeline must be low-latency, high-throughput, and attributable to exact ranking model

#### S2: Architecture Deep Dive

**Online Search Serving:**
- **Search Front End**: trackable IDs injected into HTML attributes (`data-track-id`)
- **Cassini Ranking Engine**: produces ranked results with model attribution metadata
- **PBE Carousel**: enhanced product experience with viewport tracking

**Dual-Stream Data Ingestion:**
- **Stream 1 (Behavioral)**: Sojourner/UBI raw events -> Spark Join for session/ID resolution
- **Stream 2 (Features)**: Kafka Feature Broker -> Spark Streaming -> feature tables

**Offline Processing & Attribution:**
- **Analytics Engine**: exposure, rank, dwell, conversion computation
- **Formal Attribution**: module-level & model-level discount, position bias correction
- **Training Data Materialization**: typed ML/GPU format, partitioned by date + model_version

**ML Loop**: train -> A/B test -> deploy ranking policy -> new logs (closed loop)

#### S3: Data Flow

```
User sees SRP (trackable IDs embedded)
  -> Stream 1: behavioral events -> Sojourner -> Spark Join (session + ID resolution)
  -> Stream 2: product features -> Kafka -> Spark Streaming -> feature tables
  -> Offline: Analytics Engine (exposure + behavioral labels) -> Attribution (position bias correction, module credit) -> Training data materialization
  -> ML Training -> A/B test -> Deploy -> New logs (closed loop)
```

#### S4: Formulas & Algorithms

- **Viewport Exposure**: $\text{exposed}(i) = \mathbb{1}[\text{viewport\_dur}(i) > \tau \land \text{visible\_pct}(i) > 0.5]$
- **Position Bias IPW**: $w_k = 1 / P(\text{examine} | \text{pos} = k)$, estimated via randomization
- **Module Attribution Discount**: $\text{label}_{\text{adj}}(i, m) = \text{label}_{\text{raw}}(i) \cdot \frac{\text{exposure}(i, m)}{\sum_{m'} \text{exposure}(i, m')}$
- **Position-Debiased LambdaMART**: IPW-weighted pairwise loss with NDCG gain

#### S5: Production Constraints

| Metric | Value | Context |
|--------|-------|---------|
| **Impression volume** | ~500M impressions/day, ~2B viewport events/day | Each SRP renders 48-100 trackable items |
| **Click volume** | ~20M clicks/day (~2-5% CTR) | Sparse signal -- why viewport data is essential |
| **Stream 1 throughput** | ~200K events/sec peak (Sojourner) | Spark Join for ID resolution runs at 5-min micro-batches |
| **Stream 2 throughput** | ~50K feature updates/sec (Kafka) | Product features: price, condition, seller score, image quality |
| **Spark Join latency** | ~5 min end-to-end (event -> resolved session) | Acceptable for offline training; not real-time |
| **Attribution processing** | Daily batch, ~4 hours on 500-node Spark cluster | Processes previous day's full session data |
| **Training data size** | ~2TB per daily snapshot (features + labels) | 30-day retention with date partitioning |
| **Model retrain cycle** | Daily for main ranker; weekly for experimental models | Full retrain on 14-day window of attributed data |
| **IPW estimation** | Updated monthly via position randomization experiments | ~0.1% of queries participate in randomization |

#### S6: Trade-off Analysis

| Decision | Option A | Option B | Our Choice & Why |
|----------|----------|----------|------------------|
| Exposure tracking | Click-only | Viewport-based | **Viewport** -- clicks are 2-5% CTR; viewport captures the 95% users saw but didn't click |
| Feature logging | Synchronous | Asynchronous (Kafka) | **Async** -- sync adds 20-50ms to search latency |
| Attribution | Last-touch | Multi-touch with exposure weighting | **Multi-touch** -- items appear in multiple modules |
| Position bias | None | IPW from randomization | **IPW** -- without it, models learn position, not relevance |
| Data freshness | Daily batch | Streaming + batch | **Hybrid** -- streaming for features, batch for session-level attribution |

#### S7: Adversarial Defense Q&A

**Q: IntersectionObserver-based viewport tracking is known to be unreliable on mobile browsers. What's your actual accuracy?**
> **Limitation acknowledged:** Mobile viewport tracking has edge cases: iOS Safari
> delays IntersectionObserver callbacks during momentum scrolling, and some Android
> WebViews don't fire events during fling gestures.
>
> **Mitigation:** We supplement IntersectionObserver with a 200ms scroll-end polling
> fallback: when scrolling stops, we force-check all visible items. We also cross-validate
> viewport logs against server-side "above-the-fold" position heuristics (items at
> positions 1-4 are assumed 100% visible).
>
> **Data:** In an eye-tracking validation study (N=500 sessions), our viewport labels
> agreed with actual eye fixation data at 85% accuracy. The main error mode is fast
> scrolling (items scrolled past in <1s counted as "not exposed" but sometimes seen).
> This is a conservative error -- it under-counts exposure, which is safer than
> over-counting for training purposes.

**Q: Your IPW position bias correction requires randomization experiments. Doesn't randomly reordering results hurt the user experience?**
> **Limitation acknowledged:** Yes, randomization degrades short-term UX for participating queries.
>
> **Mitigation:** We randomize only ~0.1% of queries (low user impact) and only swap
> items within a "quality tier" (items with similar relevance scores). We never put a
> truly irrelevant item at position 1. The randomization is also limited to non-sensitive
> verticals (not health/safety categories).
>
> **Data:** In the 0.1% randomized traffic, CTR drops ~15% compared to ranked traffic.
> But the IPW weights derived from this data improve model quality for the remaining
> 99.9% of traffic. Net impact: +1.8% NDCG improvement in the ranking model, translating
> to +0.5% site-wide GMV. The ROI of randomization is extremely positive.

**Q: 5-minute micro-batch latency for Stream 1 means your "near-real-time" claim is misleading. How does a 5-minute delay affect model quality?**
> **Limitation acknowledged:** 5 minutes is not real-time, and we don't use this data
> for online features.
>
> **Mitigation:** The 5-minute delay only affects offline feature aggregation. The
> training pipeline uses daily batch attribution anyway (requires full session data).
> The streaming layer's value is in making features available for the *next day's*
> training batch 5 hours earlier than a pure daily batch would. This accelerates
> the feedback loop from ~30 hours to ~25 hours.
>
> **Data:** Reducing feedback loop from 30h to 25h improved model responsiveness to
> trend shifts (e.g., new product launches) by ~1 day, measurable in a 0.3% engagement
> lift on trending queries.

**Q: Multi-touch attribution sounds principled but adds significant complexity. Have you measured whether it actually outperforms last-touch?**
> **Limitation acknowledged:** Multi-touch attribution is harder to implement, debug,
> and explain to stakeholders.
>
> **Mitigation:** We ran a 4-week A/B test: models trained on multi-touch labels vs.
> last-touch labels, everything else equal.
>
> **Data:** Multi-touch model showed +0.8% NDCG improvement on organic results and
> +1.2% improvement on module-diverse queries (where items appeared in both organic
> and carousel). For single-module queries (item only in organic), the improvement was
> negligible (+0.1%). So multi-touch attribution pays off specifically for the
> increasingly common multi-module SRP layout, which validates the investment.

#### S8: Verbal Outline

**3-Minute Version:**
1. (30s) Problem: click-based training data is sparse (2-5% CTR) and position-biased
2. (45s) Solution: viewport-based exposure tracking + dual-stream ingestion (behavioral + features)
3. (60s) Pipeline: trackable IDs -> IntersectionObserver -> Spark Join -> attribution (IPW, multi-touch) -> training data
4. (30s) Production: 500M impressions/day, 5-min micro-batch, daily model retrain
5. (15s) Impact: +1.8% NDCG, every ranking model at eBay trains on this pipeline's output

**10-Minute Version:**
1. (1.5min) Why clicks are not enough: sparsity, position bias, click != satisfaction
2. (2min) Viewport tracking: IntersectionObserver, threshold design, mobile edge cases
3. (2min) Dual-stream architecture: behavioral (Sojourner) + features (Kafka), Spark Join
4. (1.5min) Attribution: IPW from randomization, multi-touch vs last-touch, module discount
5. (2min) Production constraints: scale numbers, latency budget, cost justification
6. (1min) Lessons: IPW randomization ROI, multi-touch only pays off for multi-module SRPs

---

### 6.4 Ranking-as-Allocation: Diversity Allotment Policy Framework

> **Signature project** -- deepest coverage, most personal ownership voice.

#### S1: Overview & Motivation

- Pointwise ranking scores items independently -- ignores page-level composition
- Results become homogeneous (same sellers, categories, price ranges)
- Business impact: homogeneity hurts exploration, long-tail sellers, buyer satisfaction
- **Allocation framing**: search page = scarce resource (K slots); ranking = allocating slots
  across competing objectives (relevance, diversity, fairness, revenue)
- Unique: **closed-loop policy management** that auto-adjusts diversity budgets

#### S2: Architecture Deep Dive

**Online Serving Pipeline:**
- **Query Node (QN) Candidate Generation**: first-round retrieval + diversity subProfile/cohort tagging
- **Cassini ORC Late-Stage Ranking**:
  - **Policy Allocation Re-ranking**: re-rank to satisfy allocation constraints
  - **MUS Calibration/Correction**: normalize scores across models
  - **Soft Constraints**: category diversity, price range spread, seller variety
  - **Hard Overrides**: mandatory diversity floors/ceilings, regulatory, brand safety
- **Page Composer**: final page assembly

**Nearline/Offline Closed-Loop:**
- **Cassini Profile Discovery**: query profiles, landing profiles, taste profiles
- **DSBE Paradise Table**: observed diversity vs. target diversity per query segment
- **Adjustment Engine**: compares observed vs. target, adjusts policy parameters
- **Spark Job**: distributes updated policy to serving layer

#### S3: Data Flow

```
Query -> QN: candidate generation with diversity cohort tagging
  -> Cassini ORC:
     -> Base relevance scoring
     -> MUS calibration (normalize cross-model scores)
     -> Policy allocation re-ranking (soft + hard constraints)
     -> Hard overrides (regulatory, safety)
  -> Page Composer -> Rendered SRP -> User interactions

Offline Feedback Loop:
  Interactions -> Profile Discovery (query/taste profiles)
  -> DSBE Paradise Table (observed vs target diversity)
  -> Adjustment Engine (if observed < target: increase budget; if relevance dropping: decrease)
  -> Spark job -> Updated policy -> Next query uses new constraints
```

#### S4: Formulas & Algorithms

- **Allocation Objective**:
  $$\max_{x} \sum_{i=1}^{N} x_i \cdot s_i \quad \text{s.t.} \quad \sum_{i \in G_j} x_i \geq b_j \;\forall j, \quad \sum_i x_i = K$$

- **MUS Calibration**:
  $$\hat{s}_i = \frac{s_i - \mu_m}{\sigma_m} \cdot \sigma_{\text{target}} + \mu_{\text{target}}$$

- **Greedy with Constraint Penalty**:
  $$s'_i = s_i - \lambda \cdot \text{violation\_penalty}(i, \text{placed\_so\_far})$$

- **Closed-Loop Adjustment**:
  $$b_j^{(t+1)} = b_j^{(t)} + \eta \cdot (b_j^{\text{target}} - \bar{d}_j^{(t)})$$

- **Budget Exploration (Thompson Sampling)**:
  $$b_j^{\text{explore}} \sim \mathcal{N}(b_j^{(t)}, \sigma_j^2)$$

#### S5: Production Constraints

| Metric | Value | Context |
|--------|-------|---------|
| **QPS** | ~50K queries/sec at peak | Same traffic as Module Arbitration (shared Cassini path) |
| **Candidate set per query** | 50-200 items after QN retrieval | Diversity re-ranking operates on this set for K=48 page slots |
| **Re-ranking latency** | <3ms (greedy with lookahead) | O(K * N) for K=48, N=200 = ~9600 operations |
| **MUS calibration** | <1ms (simple normalization per query) | Pre-computed $\mu_m, \sigma_m$ per model, refreshed hourly |
| **Hard constraint types** | 8 active constraint categories | Seller cap, category floor, condition diversity, brand safety, etc. |
| **Soft constraint dimensions** | 4 (seller, category, price bucket, condition) | Each has independent budget per query segment |
| **Query segments** | ~2000 segments (query intent x user tier) | Budget targets maintained per segment in DSBE Paradise Table |
| **Policy update frequency** | Daily batch (overnight Spark job) | ~2 hours to process previous day's data and compute new budgets |
| **Closed-loop convergence** | 3-7 days for new budget targets to stabilize | Learning rate $\eta = 0.1$, clamped to [min, max] range |
| **Diversity metric monitoring** | Real-time dashboard (Grafana) | Alerts if any segment's diversity drops >10% from target for 2+ hours |

#### S6: Trade-off Analysis

| Decision | Option A | Option B | Our Choice & Why |
|----------|----------|----------|------------------|
| Ranking paradigm | Pointwise | Allocation (page-level) | **Allocation** -- pointwise ignores composition; two identical items both shown wastes slots |
| Diversity enforcement | Hard only | Soft + hard hybrid | **Hybrid** -- hard for non-negotiables (regulatory); soft for preferences (seller variety) |
| Constraint scope | Per-query | Per-query-segment (clustered) | **Per-segment** -- individual queries too noisy; segments enable stable targets |
| Policy update frequency | Daily batch | Near-real-time | **Daily** -- diversity policy needs careful eval; real-time risks oscillation |
| Score normalization | Raw model scores | MUS calibration | **MUS** -- multiple models contribute scores; raw scores are incomparable |

#### S7: Adversarial Defense Q&A

**Q: Your allocation framing sounds like it adds complexity for marginal gains. Can you quantify the relevance cost of diversity constraints?**
> **Limitation acknowledged:** Diversity constraints do reduce pure-relevance NDCG. Any
> constraint on a maximization problem reduces the optimal value.
>
> **Mitigation:** The key insight is that user satisfaction is not monotonically increasing
> with pointwise relevance. A page of 48 items from the same seller, all highly relevant,
> is a poor experience. We measure page-level engagement (session continuation, purchase
> rate) not just NDCG.
>
> **Data:** With diversity constraints active, pointwise NDCG drops 1.2% but page-level
> purchase rate increases 3.5% and session continuation rate increases 2.8%. The user is
> more likely to buy and more likely to come back. The diversity "cost" measured by NDCG
> is a measurement artifact -- NDCG rewards showing the "most relevant" items, but users
> want variety, not redundancy.

**Q: Your closed-loop adjusts budgets automatically. What prevents it from gaming metrics or drifting to degenerate states?**
> **Limitation acknowledged:** Closed-loop systems can drift, oscillate, or find
> reward-hacking equilibria.
>
> **Mitigation:** Three guardrails: (1) Budget clamping: budgets are clamped to [min, max]
> per constraint type, set by human-reviewed business rules. The system can't set seller
> diversity to 0% or 100%. (2) Conservative learning rate: $\eta = 0.1$ means maximum
> daily budget change is ~10% of the gap. (3) Relevance guardrail: if NDCG drops >2%
> from baseline for any segment, the adjustment engine freezes that segment's budget and
> alerts the team.
>
> **Data:** In 14 months of operation, the adjustment engine froze budgets 7 times (0.5%
> of segment-days). 5 of those were false alarms from seasonality shifts; 2 were genuine
> constraint misconfigurations caught early. No degenerate states reached in production.

**Q: MUS calibration normalizes scores, but different models may have fundamentally different quality levels. Doesn't normalization hide this?**
> **Limitation acknowledged:** Yes, normalization equalizes the scale but not the
> information content of different models.
>
> **Mitigation:** MUS calibration normalizes within the same relevance tier, not globally.
> A high-quality model's score distribution is tighter and more informative, which is
> preserved after normalization -- the calibrated scores still have higher mutual
> information with relevance labels. We also weight models by their offline NDCG
> contribution in the final score combination.
>
> **Data:** After MUS calibration, the ensemble of 3 ranking models (base, freshness,
> personalization) achieved 2.1% higher NDCG than using raw scores from the single
> best model. The calibration enables meaningful score combination.

**Q: Per-segment budgets with 2000 segments -- how do you handle segments with sparse data?**
> **Limitation acknowledged:** Long-tail segments (rare query types + niche user tiers)
> have few observations per day, making budget adjustment noisy.
>
> **Mitigation:** Hierarchical shrinkage: segments with <100 daily queries inherit their
> parent segment's budget (e.g., specific intent inherits from intent category). As
> observation count grows, the segment's own observed diversity gets more weight.
> This is essentially empirical Bayes applied to diversity budgets.
>
> **Data:** 65% of segments have >500 daily queries (reliable individual budgets). 30%
> have 100-500 (partial shrinkage). 5% have <100 (fully inherited from parent). The
> hierarchical approach reduced budget variance on sparse segments by 60% compared to
> per-segment-only estimation.

**Q: This is your signature project. What's the biggest mistake you made, and what would you do differently?**
> **Honest answer:** The biggest mistake was not investing in **counterfactual evaluation**
> from day one. Every policy change required an A/B test, which takes 1-2 weeks and
> consumes traffic. With inverse propensity scoring and doubly-robust estimators, we
> could have evaluated 10+ policy variants offline before committing to a single A/B test.
>
> I eventually built offline evaluation, but by then we'd spent ~3 months running sequential
> A/B tests that could have been parallelized. If I were starting over, I'd build the
> counterfactual evaluation framework in the first sprint, even before the first policy
> constraint.
>
> **Lesson for Uber:** Any ranking system that plans to iterate on policies needs
> offline evaluation infrastructure from day one. A/B tests are for validation, not
> exploration.

#### S8: Verbal Outline

**3-Minute Version:**
1. (30s) Problem: pointwise ranking -> homogeneous results, hurts buyer diversity satisfaction
2. (45s) Key insight: reframe ranking as resource allocation with diversity constraints
3. (60s) Architecture: online (MUS calibration + greedy allocation re-ranking with soft/hard constraints) + offline (closed-loop policy adjustment)
4. (30s) Production: 50K QPS, <3ms re-ranking, 2000 query segments, daily policy updates
5. (15s) Result: +3.5% purchase rate, +2.8% session continuation, allocation paradigm adopted across 3 search verticals

**10-Minute Version:**
1. (1.5min) Motivation: why pointwise fails, homogeneity problem with specific examples
2. (2min) Allocation formulation: objective function, hard vs soft constraints, MUS calibration
3. (2min) Online architecture: QN diversity cohorts, Cassini ORC re-ranking, greedy with lookahead
4. (2min) Closed-loop: DSBE Paradise Table, adjustment engine, convergence behavior, guardrails
5. (1.5min) Production constraints: QPS, latency budget, 2000 segments, sparse data handling
6. (1min) Retrospective: counterfactual evaluation lesson, what I'd tell someone building this at Uber

---

## 7. Task Execution Order

```
Phase 1: Infrastructure (parallel, no dependencies)
  T-P1-158: Backend model (8 section columns) + API + seed script + copy diagrams
  T-P1-159: Frontend sidebar + routes + types (8 sections)

Phase 2: UI Components (depends on Phase 1)
  T-P1-160: Landing page (narrative block + card grid with thumbnails)
  T-P1-161: Detail page template (8-tab section layout with diagram display)

Phase 3: Content (serial, depends on T-P1-161)
  T-P1-162: Module Arbitration writeup (all 8 sections)
  T-P1-163: LLM Orchestration writeup (all 8 sections)
  T-P1-164: PBE Pipeline writeup (all 8 sections)
  T-P1-165: Ranking-as-Allocation writeup (all 8 sections, signature depth)
```

**Total: 8 tasks, 3 phases.**

Phase 1: parallel (backend + frontend independent).
Phase 2: parallel (list page + detail page are separate files sharing types from Phase 1).
Phase 3: serial (each content task seeds DB via script).

---

## Review Checklist (for reviewer)

- [ ] Unified narrative accurately represents the candidate's technical arc
- [ ] Production constraints numbers are realistic (reviewer should flag any that seem off)
- [ ] Adversarial Q&A genuinely attacks weak points (not softballs)
- [ ] Defense answers follow "acknowledge -> mitigate -> data" structure consistently
- [ ] Trade-off tables present real alternatives (not strawmen)
- [ ] Verbal outlines can be delivered within stated time limits
- [ ] 8-section structure is the right granularity (not too many tabs)
- [ ] Model schema covers all needed fields without over-engineering
