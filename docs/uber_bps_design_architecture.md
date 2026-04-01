# Uber BPS -- Design & Architecture (D&A) Prep Guide

> **Purpose**: Deep-dive preparation for the D&A segment of the Uber BPS interview.
> The interviewer asks you to walk through a complex past project with a high-level
> diagram. They evaluate system thinking, trade-off reasoning, and communication.
>
> **Time budget**: ~8-10 minutes of a 1hr BPS session (see `uber_phone_screen_prep.md`)
>
> Task: T-P1-245

---

## Table of Contents

1. [D&A Format and Expectations](#1-da-format-and-expectations)
2. [Project Showcase: Ranking-as-Allocation](#2-project-showcase-ranking-as-allocation)
3. [Project Showcase: LLM Evaluation Pipeline](#3-project-showcase-llm-evaluation-pipeline)
4. [Trade-off Discussion Framework](#4-trade-off-discussion-framework)
5. [Uber System Design Patterns](#5-uber-system-design-patterns)
6. [Common D&A Follow-up Questions](#6-common-da-follow-up-questions)
7. [D&A Communication Tips](#7-da-communication-tips)
8. [Practice Checklist](#8-practice-checklist)

---

## 1. D&A Format and Expectations

### What happens in the D&A segment

The interviewer asks: "Tell me about a complex system you designed or contributed to."
You then:
1. Draw a high-level architecture diagram (on HackerRank shared editor or whiteboard)
2. Walk through the system flow end-to-end
3. Explain key design decisions and trade-offs
4. Answer follow-up questions probing depth

### What the interviewer evaluates

| Signal | What they look for |
|--------|-------------------|
| **System thinking** | Can you decompose a complex system into clear components? |
| **Trade-off reasoning** | Do you explain WHY you chose X over Y, not just WHAT you built? |
| **Depth of understanding** | Can you go deeper when probed, or do you only know surface-level? |
| **Communication** | Is the diagram clear? Do you structure the walkthrough logically? |
| **Scope awareness** | Do you understand what's upstream/downstream of your component? |

### How to structure your walkthrough (8-10 min)

| Phase | Time | What to do |
|-------|------|------------|
| Context | 1 min | One sentence: what product, what problem, why it matters |
| Diagram | 2 min | Draw the architecture. Label each component clearly. |
| Flow | 3 min | Walk through a single request/data flow end-to-end |
| Decisions | 2-3 min | Highlight 2-3 key trade-offs you made and why |

---

## 2. Project Showcase: Ranking-as-Allocation

### Context (1 min)

"At my previous company, I worked on the search ranking system for an e-commerce
platform serving millions of daily queries. The core challenge was that traditional
pointwise ranking optimizes per-item scores independently, but business objectives --
like exposure fairness, conversion targets, and risk constraints -- require
session-level coordination. I designed a Ranking-as-Allocation framework that treats
ranking as a constrained resource allocation problem."

### Architecture Diagram

```
                    User Query
                        |
                        v
              +-------------------+
              |   Query Parser    |
              | (intent, filters) |
              +-------------------+
                        |
                        v
              +-------------------+
              |    Retrieval      |
              | (embedding + BM25)|
              | ~1000 candidates  |
              +-------------------+
                        |
                        v
              +-------------------+
              |  Pointwise Scorer |
              | (deep model, MoE) |
              | per-item P(click) |
              +-------------------+
                        |
                        v
        +-------------------------------+
        |   Session-Level Allocator     |
        | (multi-objective optimization)|
        |                               |
        |  Objectives:                  |
        |  - Maximize conversion        |
        |  - Exposure fairness floor    |
        |  - Risk/compliance cap        |
        |  - Diversity target           |
        |                               |
        |  Method: constrained          |
        |  optimization (LP/ILP)        |
        +-------------------------------+
                        |
                        v
              +-------------------+
              |   Re-ranker       |
              | (late-stage MoE)  |
              | final position    |
              +-------------------+
                        |
                        v
              +-------------------+
              |  A/B Experiment   |
              |  Framework        |
              | (diagnostic tools)|
              +-------------------+
                        |
                        v
                  Search Results
```

### End-to-End Flow

1. **Query parsing**: Extract intent, category filters, price range from user query
2. **Retrieval**: Two-stage -- embedding-based (FAISS/ANN) retrieves ~500 semantic matches, BM25 retrieves ~500 lexical matches, merge and deduplicate to ~1000 candidates
3. **Pointwise scoring**: Deep model predicts P(click), P(purchase), P(return) per item. MoE (Mixture of Experts) architecture: different expert towers for different product categories
4. **Session-level allocation**: This is the key innovation. Instead of sorting by score, formulate as constrained optimization:
   - Decision variable: position assignment for each candidate
   - Objective: maximize expected conversion
   - Constraints: minimum exposure per seller tier, maximum risk items per page, diversity across categories
5. **Re-ranking**: Final pass applies business rules (sponsored slots, editorial picks) and ensures the allocation solution translates to a valid ranked list
6. **Experimentation**: A/B framework with metric decomposition: if overall conversion changes, which allocation constraint drove it?

### Key Trade-off Discussions

**Trade-off 1: Pointwise scoring vs. listwise/pairwise**

| Approach | Pros | Cons |
|----------|------|------|
| Pointwise (chosen) | Fast inference, easy to debug per-item, clean separation from allocation layer | Ignores inter-item dependencies |
| Listwise (LambdaMART) | Directly optimizes ranking metrics (NDCG) | Expensive, hard to decompose for diagnostic |
| Pairwise (RankNet) | Captures relative ordering | Quadratic pairs, noisy gradients |

"We chose pointwise because the allocation layer already handles inter-item coordination. Pushing that responsibility into the scorer would create competing optimization objectives and make diagnostics much harder -- when a metric moves, you need to know if it was the scorer or the allocator."

**Trade-off 2: MoE vs. single deep model**

"We started with a single model but observed category-specific patterns (electronics vs. fashion have very different click/purchase funnels). MoE with category-routed experts improved conversion +2.3% without increasing serving latency, because only 2 of 8 experts activate per item."

**Trade-off 3: Hard constraints vs. soft penalties in allocation**

"We initially used soft penalties (Lagrangian relaxation) but found that exposure fairness would be violated during traffic spikes. Switching to hard constraints via LP solver guaranteed compliance but added ~5ms latency. We accepted the latency because the business requirement was non-negotiable."

### Anticipated follow-ups

| Question | Answer sketch |
|----------|--------------|
| "How do you handle latency?" | Retrieval + scoring is parallelized. LP solver runs on pre-filtered top-100. Total P99 < 200ms. |
| "What if constraints conflict?" | Priority ordering: compliance > fairness > diversity. Infeasible? Relax lowest-priority constraint and log. |
| "How do you evaluate offline?" | Counterfactual estimation (IPS-weighted) for allocation; standard AUC/NDCG for scorer. |
| "What would you do differently?" | Would explore contextual bandits for online allocation learning instead of static LP formulation. |

---

## 3. Project Showcase: LLM Evaluation Pipeline

### Context (1 min)

"I built an LLM-based evaluation pipeline that replaced human judges for search
quality assessment. The system reduced evaluation cost by 94% and turnaround time
from 2 weeks to 4 hours, enabling our team to run 3x more experiments per quarter.
It's now used org-wide across Search and Ads teams."

### Architecture Diagram

```
              Experiment Request
              (query set + config)
                      |
                      v
            +-------------------+
            |   Data Pipeline   |
            | sample queries    |
            | retrieve results  |
            | pair with labels  |
            +-------------------+
                      |
                      v
            +-------------------+
            |  Prompt Builder   |
            | task-specific     |
            | templates + few-  |
            | shot examples     |
            +-------------------+
                      |
                      v
            +-------------------+
            |  Calibration      |
            | Module            |
            | - temperature     |
            | - chain-of-thought|
            | - self-consistency|
            | - anchor examples |
            +-------------------+
                      |
                      v
            +-------------------+
            | Batch Inference   |
            | (async, rate-     |
            |  limited, retry)  |
            | ~10K judgments/hr  |
            +-------------------+
                      |
                      v
            +-------------------+
            |  Agreement        |
            |  Analysis         |
            | - vs human judges |
            | - Cohen's kappa   |
            | - per-category    |
            |   breakdown       |
            +-------------------+
                      |
                      v
            +-------------------+
            |  Dashboard        |
            | - experiment      |
            |   comparison      |
            | - confidence      |
            |   intervals       |
            | - failure cases   |
            +-------------------+
```

### End-to-End Flow

1. **Data pipeline**: Given an experiment (e.g., "new ranking model v2"), sample N queries stratified by category/intent, retrieve search results from both control and treatment
2. **Prompt construction**: Task-specific templates (relevance, freshness, intent-match). Few-shot examples from gold-labeled data. Format: "Given query Q and result R, rate relevance on 1-5 scale. Think step-by-step."
3. **Calibration**: Anchor examples with known human labels ensure score distribution alignment. Temperature tuning per task. Self-consistency: sample 3 judgments per pair, take majority vote
4. **Batch inference**: Async API calls with rate limiting, exponential backoff, and result caching. ~10K judgments per hour at ~$0.02/judgment (vs. ~$0.35/judgment for human raters)
5. **Agreement analysis**: Cohen's kappa vs. held-out human labels. Per-category breakdown identifies where LLM disagrees with humans (typically: subjective queries, domain-specific jargon)
6. **Dashboard**: Side-by-side experiment comparison with confidence intervals. Failure case viewer for manual review of high-disagreement items

### Key Trade-off Discussions

**Trade-off 1: LLM-as-judge vs. fine-tuned classifier**

| Approach | Pros | Cons |
|----------|------|------|
| LLM-as-judge (chosen) | Zero-shot generalization, handles new eval dimensions without retraining, explainable via CoT | Higher per-judgment cost, latency, prompt sensitivity |
| Fine-tuned classifier | Fast, cheap, deterministic | Needs labeled data per task, doesn't generalize, opaque |

"We chose LLM-as-judge because our team launches ~3 new eval dimensions per quarter (e.g., 'freshness', 'visual match'). Fine-tuning a new classifier each time was the bottleneck we were trying to eliminate."

**Trade-off 2: Single judgment vs. self-consistency**

"Single judgment is 3x cheaper but has ~8% noise rate. Self-consistency (3 samples, majority vote) reduces noise to ~2% and gives a built-in confidence signal. We use single for screening, self-consistency for final experiment decisions."

**Trade-off 3: Prompt engineering vs. fine-tuning the LLM**

"Prompt engineering is fragile -- a small wording change can shift scores. But fine-tuning requires 5K+ gold labels per task and retraining on each model update. We mitigated prompt fragility through anchor calibration (fixed reference examples that normalize the scale) rather than fine-tuning."

### Anticipated follow-ups

| Question | Answer sketch |
|----------|--------------|
| "How do you handle hallucination?" | CoT + structured output (JSON with reasoning). Flag judgments where reasoning contradicts score. |
| "What about bias?" | Position bias (always favoring result shown first). Mitigation: randomize presentation order, test both orderings. |
| "How reliable is kappa?" | 0.72 kappa overall (substantial agreement). Per-category: navigational queries 0.85, subjective queries 0.55. We don't trust LLM for subjective categories. |
| "Scale to 100K judgments?" | Batch API + result caching. Already cached common query-result pairs. Marginal cost decreasing. |

---

## 4. Trade-off Discussion Framework

When the interviewer asks "Why X over Y?", use this structure:

### STAR-T Framework for Trade-offs

1. **State the options**: "We considered X and Y"
2. **Trade-offs**: "X gives us [benefit] but costs [drawback]. Y gives us [benefit] but costs [drawback]"
3. **Analysis**: "Given our constraints -- [latency budget / team size / data availability / business requirement] -- X was the better fit because..."
4. **Result**: "After deploying X, we observed [metric improvement]"
5. **Reflection (if asked)**: "In hindsight, I would also consider Z because..."

### Common trade-off dimensions at Uber

| Dimension | Option A | Option B | When to pick A | When to pick B |
|-----------|----------|----------|----------------|----------------|
| **Consistency vs. Availability** | Strong consistency (SQL, transactions) | Eventually consistent (NoSQL, event-driven) | Financial data, ride matching | Analytics, user preferences |
| **Latency vs. Accuracy** | Approximate (cached, pre-computed) | Exact (real-time computation) | ETA estimation, driver maps | Pricing, payment |
| **Batch vs. Stream** | Batch processing (Spark, daily) | Stream processing (Kafka, Flink) | Training data, reporting | Fraud detection, surge pricing |
| **Monolith vs. Microservice** | Single service | Separate services | Early-stage, tight coupling | Scale independently, team ownership |
| **Build vs. Buy** | Custom solution | Third-party tool | Core differentiator, unique requirements | Commodity feature, time pressure |
| **Online vs. Offline** | Real-time inference | Pre-computed lookup | Personalization, dynamic context | Static recommendations, cold-start |

---

## 5. Uber System Design Patterns

These are real-world Uber system patterns that may come up as D&A discussion topics
or coding follow-ups. Understanding them demonstrates domain awareness.

### 5.1 Driver Maps (Real-time Geospatial)

**Problem**: Show available drivers on rider's map in real-time.

```
Driver App                          Rider App
    |                                   |
    | GPS update (every 4s)             | Map viewport request
    v                                   v
+----------+                    +----------+
| Location |  -- Kafka -->      | Map Tile |
| Service  |                    | Service  |
| (ingest) |                    | (query)  |
+----------+                    +----------+
    |                                   ^
    v                                   |
+-----------------------------------+   |
|      Geospatial Index             |---+
| (Google S2 cells / H3 hexagons)  |
| - cell resolution ~100m          |
| - in-memory, sharded by region   |
+-----------------------------------+
```

**Key design decisions**:
- **S2/H3 cells vs. geohash**: S2 cells have uniform area at all latitudes (geohash distorts near poles). H3 hexagons have uniform adjacency (6 neighbors always). Uber uses H3.
- **Push vs. pull**: Drivers push location updates; riders pull viewport. Hybrid: push updates to index, pull for rendering.
- **Staleness**: If no update in 30s, driver marked offline. Trade-off: aggressive timeout = fewer ghost cars but may drop drivers in tunnels.

**Follow-up questions**:
- "How do you handle millions of concurrent drivers?" -- Shard by H3 resolution-3 cell (~12K cells globally), each shard fits in memory
- "How accurate is the map?" -- 4s GPS interval + interpolation. Good enough for "driver nearby" UX, not for navigation

### 5.2 Shopping Cart (UberEats)

**Problem**: Manage user's cart across sessions, devices, and concurrent modifications.

```
Mobile App / Web
       |
       v
+---------------+
|  Cart API     |
| (CRUD + rules)|
+---------------+
       |
       v
+---------------+     +---------------+
|  Cart Store   |---->| Menu Service  |
| (per-user     |     | (prices,      |
|  document)    |     |  availability)|
+---------------+     +---------------+
       |
       v
+---------------+     +---------------+
| Pricing       |---->| Promo Engine  |
| Calculator    |     | (coupons,     |
| (surge, fees) |     |  referrals)   |
+---------------+     +---------------+
       |
       v
+---------------+
|  Checkout     |
|  (order       |
|   creation)   |
+---------------+
```

**Key design decisions**:
- **Cart as document vs. normalized rows**: Document (JSON blob per user) is simpler for read/write but harder to query across users. Normalized is better for analytics. Uber uses document for the hot path, syncs to analytics DB asynchronously.
- **Optimistic vs. pessimistic locking**: Optimistic (version field, retry on conflict) because cart conflicts are rare (same user, two devices). Pessimistic would add latency for the common case.
- **Price at add-time vs. checkout-time**: Checkout-time (always re-fetch current price). But show "price changed" warning if delta > threshold. Avoids stale-price orders.

**Follow-up questions**:
- "What if a menu item becomes unavailable?" -- Soft-remove from cart, notify user, don't block checkout for other items
- "How do you handle surge pricing in cart?" -- Prices are not locked until checkout confirmation. Cart shows estimated total with "prices may change" disclaimer

### 5.3 Driver Queue / Dispatch

**Problem**: Match riders to nearest available drivers with fairness and efficiency.

```
Ride Request                    Driver Pool
     |                               |
     v                               v
+-----------+               +-----------+
| Dispatch  |<-- match ---->| Supply    |
| Engine    |               | Index     |
| (matching |               | (H3 cell |
|  + assign)|               |  lookup)  |
+-----------+               +-----------+
     |
     v
+-----------+
| Fairness  |
| Layer     |
| - FIFO    |
| - earnings|
|   balance |
+-----------+
     |
     v
+-----------+
| Offer     |
| Manager   |
| (timeout, |
|  reassign)|
+-----------+
```

**Key design decisions**:
- **Nearest-first vs. FIFO queue**: Pure nearest-first starves drivers in low-demand zones. Pure FIFO ignores rider wait time. Hybrid: nearest within a fairness window (drivers waiting > X minutes get priority boost).
- **Single offer vs. broadcast**: Single offer (one driver at a time, 15s timeout) vs. broadcast (show to multiple, first accept wins). Uber uses single offer for UberX (rider expects specific driver), broadcast for Pool.
- **ETA-based vs. distance-based matching**: ETA accounts for traffic, one-way streets, current speed. More accurate but more expensive to compute. Pre-compute ETA matrix for nearby cells.

### 5.4 ETA Estimation

**Problem**: Predict arrival time for a driver to reach pickup point (or delivery).

```
Route Request (origin, destination)
              |
              v
     +------------------+
     | Graph Engine      |
     | (road network,    |
     |  Dijkstra/A*)     |
     +------------------+
              |
              v
     +------------------+
     | Segment Speed    |
     | Predictor        |
     | (ML model:       |
     |  historical +    |
     |  real-time GPS)  |
     +------------------+
              |
              v
     +------------------+
     | Calibration      |
     | (bias correction |
     |  by city/time)   |
     +------------------+
              |
              v
     +------------------+
     | Post-processing  |
     | (rounding, min   |
     |  floor, display) |
     +------------------+
```

**Key design decisions**:
- **Historical average vs. ML model**: Historical average (same road, same hour, same day-of-week) is a strong baseline. ML adds: real-time traffic from GPS probes, weather, events. ML wins by ~15% MAPE reduction.
- **Pre-computation vs. on-demand**: Pre-compute cell-to-cell ETAs every 5 min. On-demand for exact origin/destination. Two-tier: fast lookup for "nearby" estimate + exact route for confirmed match.
- **Optimistic vs. conservative**: Optimistic ETA improves conversion (rider requests ride) but causes frustration if late. Conservative loses rides but builds trust. Uber calibrates to slight overestimate (~10%).

### 5.5 Food Ordering Pipeline (UberEats)

**Problem**: End-to-end order flow from browse to delivery.

```
User browses         User orders          Restaurant         Courier
     |                    |                   |                  |
     v                    v                   v                  v
+---------+       +-----------+       +-----------+      +-----------+
| Menu &  |       | Order     |       | Restaurant|      | Courier   |
| Search  |       | Service   |------>| Dashboard |      | Matching  |
| Service |       | (payment, |       | (accept/  |      | & Routing |
+---------+       |  validate)|       |  prepare) |      +-----------+
                  +-----------+       +-----------+             |
                        |                   |                   v
                        v                   v            +-----------+
                  +-----------+       +-----------+      | Delivery  |
                  | Payment   |       | Kitchen   |      | Tracking  |
                  | Service   |       | Display   |      | (real-time|
                  +-----------+       | System    |      |  updates) |
                                      +-----------+      +-----------+
```

**Key design decisions**:
- **Synchronous vs. async order flow**: Payment is synchronous (must confirm before sending to restaurant). Restaurant acceptance is async (webhook/push notification). If restaurant doesn't accept in 5 min, auto-cancel and refund.
- **Courier pre-dispatch vs. post-accept**: Pre-dispatch (assign courier before restaurant accepts) reduces delivery time by ~5 min but wastes courier time if restaurant rejects. Post-accept is safer. Uber uses pre-dispatch for high-acceptance restaurants (>95% acceptance rate).
- **Estimated delivery time**: Composed of prep_time (ML model per restaurant) + pickup_wait + travel_time (ETA engine). Each component has uncertainty. Show range, not point estimate.

---

## 6. Common D&A Follow-up Questions

These questions appear frequently in 1p3a BPS reports. Prepare answers for your specific projects.

### General architecture questions

| Question | What they're testing | How to answer |
|----------|---------------------|---------------|
| "Why did you choose X over Y?" | Trade-off reasoning | Use STAR-T framework (Section 4). Never say "it was the standard choice." |
| "What would you do differently?" | Self-awareness, growth | Name one real limitation and a concrete alternative. "If I had more time, I would..." |
| "How did you handle failure cases?" | Resilience thinking | Describe specific failure mode + mitigation. Retry, circuit breaker, fallback, alerting. |
| "How did you scale this?" | Systems knowledge | Horizontal (shard, replicate) vs. vertical. Bottleneck identification. |
| "Walk me through a request lifecycle" | End-to-end understanding | Trace from user action to DB write to response. Include caching, async steps. |

### ML-specific D&A questions

| Question | What they're testing | How to answer |
|----------|---------------------|---------------|
| "How do you monitor model quality in production?" | MLOps maturity | Online metrics (CTR, conversion) + offline eval (holdout). Drift detection. Alerting threshold. |
| "How do you handle data drift?" | Practical ML experience | Feature distribution monitoring, retrain trigger, shadow mode for new model. |
| "How do you do A/B testing for ML models?" | Experiment design | Random traffic split, guardrail metrics, statistical significance, ramp-up plan. |
| "How do you handle cold-start?" | Algorithmic thinking | New users: popularity-based fallback. New items: content-based features. Explore/exploit. |
| "How do you serve models at low latency?" | Infrastructure knowledge | Model optimization (quantization, distillation), caching, batching, async pre-computation. |

### Questions from 1p3a BPS reports

| Question | Context |
|----------|---------|
| "Draw the architecture on the whiteboard" | They literally want you to diagram it on HackerRank editor |
| "What was the most complex technical decision?" | Pick one with clear before/after and measurable impact |
| "How did you convince your team of this approach?" | Communication + data-driven decision making |
| "What metrics did you use to evaluate success?" | Specific numbers: "improved X by Y%" |
| "How long did this take and what was the team?" | Scope awareness: your contribution vs. team effort |
| "What's the bottleneck in this system?" | Show you think about scaling limits, not just happy path |

### Red flags to avoid

| Red flag | Why it's bad | Better approach |
|----------|-------------|-----------------|
| "It took two weeks" | Emphasizes time, not complexity | "The challenge was X, which required solving Y" |
| "I just followed the standard approach" | Shows no critical thinking | "We evaluated A and B. We chose A because [constraint]" |
| "I built the whole thing" | Sounds either dishonest or like a small project | "I owned the [specific component]. The team handled [X, Y]" |
| Only describing happy path | Misses resilience thinking | "The main failure mode was X. We handled it by Y" |
| Vague metrics | "It was faster" | "Reduced P99 latency from 450ms to 180ms" |

---

## 7. D&A Communication Tips

### During the diagram

- **Start with the big picture**: Draw all boxes first, then add arrows and labels
- **Use clear component names**: "Retrieval Service" not "Step 1"
- **Show data flow direction**: Arrows with labels ("query", "candidates", "scores")
- **Mark your component**: Circle or highlight what YOU owned
- **Keep it to 5-7 boxes**: More than that and it's too detailed for 8 minutes

### During the walkthrough

- **Narrate the flow**: "A user query comes in here, gets parsed, then..."
- **Pause at decision points**: "At this stage, we had a choice: X or Y. We chose X because..."
- **Anticipate questions**: "You might wonder why we didn't do Z -- the reason is..."
- **Use concrete numbers**: "This handles ~10K QPS with P99 < 200ms"
- **Acknowledge limitations**: "One thing I'd improve is..." (shows maturity)

### Handling unknown questions

If asked about a component you didn't own:
- "I didn't own that component, but my understanding is [brief explanation]. I can speak in detail about [your component] which interfaces with it through [API/contract]."

---

## 8. Practice Checklist

### Project 1: Ranking-as-Allocation

- [ ] Draw the diagram from memory in under 2 minutes
- [ ] Walk through end-to-end flow in under 3 minutes
- [ ] Explain pointwise vs. listwise trade-off clearly
- [ ] Explain MoE architecture and why it helped
- [ ] Explain allocation constraints with a concrete example
- [ ] Have a metric: "improved conversion by X%"
- [ ] Prepare "what would you do differently" answer

### Project 2: LLM Evaluation Pipeline

- [ ] Draw the diagram from memory in under 2 minutes
- [ ] Walk through end-to-end flow in under 3 minutes
- [ ] Explain LLM-as-judge vs. fine-tuned classifier trade-off
- [ ] Explain calibration methodology
- [ ] Have metrics: "94% cost reduction, 90% latency reduction, 0.72 kappa"
- [ ] Prepare hallucination/bias mitigation answers

### General D&A readiness

- [ ] Practice explaining each project to someone unfamiliar (time yourself)
- [ ] Prepare for "why X over Y" for at least 3 decisions per project
- [ ] Practice drawing diagrams on a plain text editor (not a drawing tool)
- [ ] Review Uber system patterns (Section 5) for domain context
- [ ] Prepare 2-3 specific failure modes and how you handled them
- [ ] Have concrete metrics ready for every claim

---

## Quick Reference: D&A in 60 Seconds

If short on prep time, remember this structure:

```
1. CONTEXT  (10 sec) -- What product, what problem, why it matters
2. DIAGRAM  (60 sec) -- 5-7 boxes, arrows with data flow labels
3. FLOW     (90 sec) -- One request from start to finish
4. DECISION (90 sec) -- "We chose X over Y because [constraint]"
5. METRIC   (30 sec) -- "This improved Z by N%"
6. REFLECT  (30 sec) -- "If I did it again, I'd also consider..."
```

Total: ~5 minutes core, leaving ~3-5 minutes for follow-up Q&A.
