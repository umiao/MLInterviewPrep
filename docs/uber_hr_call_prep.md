# Uber MLE -- HR Call Prep Materials

> **Monday 11:10 AM | Recruiter Screen | MLE - Shopping Ranking & Recommendations**
>
> Core mindset: ~25% of candidates are eliminated at this stage. Treat this as "formal interview round 1." Uber recruiters often probe for cultural norm alignment alongside background fit.

---

## Part 0: Call 48hr Checklist

- [x] Review JD, highlight 3-5 key requirement keywords
  - **Team**: Shopping Ranking Team -- enabling eaters to make shopping decisions and find what they need
  - **Key JD keywords**: (1) Ranking & Recommendation ML models, (2) Productionize & deploy, (3) GenAI for shopping ranking, (4) Big-data (Spark/Hive/HDFS), (5) Cross-functional collaboration
  - **Must-have**: 4+ yrs eng + 2+ yrs ML model building/deploying, OOP (Python/Go/Java/C++), big-data stack, PyTorch/TensorFlow/Ray
  - **Preferred (high-signal)**: Production ranking & rec systems, vague business problem -> ML+Optimization formulation, ML system design & architecture, multi-quarter E2E project ownership
  - **GenAI angle**: Team is building "next generation of Generative AI - shopping ranking and recommendation systems"
- [ ] Read Uber Engineering Blog -- focus on Michelangelo, marketplace ML, scaling infrastructure
- [ ] Review Uber's 8 Cultural Norms (see Part 7) -- prepare 1 story per top-4 norm
- [ ] Check recent Uber news (robotaxi partnership, GenAI Gateway, Q4 earnings)
- [ ] Update LinkedIn Profile (consistent with resume, quantified achievements)
- [ ] Prepare quiet environment + wired headphones, resume and JD open on screen
- [ ] Print or have this document open for quick reference during call

---

## Part 1: Self Introduction (60-90 seconds, English)

### Structure

[Current role + years + domain -- 1-2 sentences]

I'm a Machine Learning Engineer at eBay on the Search Science, Ranking & Monetization team, where I've spent the past three years building large-scale ranking and relevance systems serving millions of queries daily.

[Signature projects + quantified results -- 2-3 sentences]

One highlight is designing eBay's Ranking-as-Allocation framework that treats search as a resource allocation problem -- enabling precise multi-objective control over exposure, conversion, and risk at site scale. I also built an end-to-end LLM-based evaluation pipeline that achieved human-comparable agreement while reducing cost by 94% and latency by 90%, now adopted org-wide for Search & Ads experiments.

[Why exploring + why Uber -- 1-2 sentences]

I'm now looking for my next challenge in marketplace ML at greater scale. Uber's Shopping Ranking Team -- building ML-driven ranking and recommendation systems to help eaters find what they need, and pushing into next-gen GenAI for shopping -- is exactly the kind of multi-objective optimization I've been building toward, and I'm excited about the opportunity to work on systems that make 10 million ML predictions per second.

### Self-check

- [ ] Total duration <= 90 seconds (record and time)
- [ ] Contains at least 2 quantified numbers (94% cost reduction, 90% latency reduction, site-scale)
- [ ] Ending naturally transitions to "why Uber" without abrupt stop
- [ ] Pace slightly slower, logical clarity > perfect grammar

---

## Part 2: High-Frequency Questions

> Write 3-5 sentence bullet points per question. Don't memorize full text -- stay natural on the call.

### Q1: Tell me about yourself / Walk me through your background

--> Use Part 1 self-introduction directly.

---

### Q2: Why are you looking / Why leaving?

**Principle: Positive framing, never criticize current employer**

Key points:
I've had a great experience at eBay -- I've grown from intern to owning end-to-end ranking systems at site scale. After three years of deepening my expertise in search ranking, I'm looking for a new challenge in marketplace ML where the optimization surface is even more dynamic -- shopping ranking with real-time personalization, GenAI-powered recommendations, and multi-modal signals. Uber's Shopping Ranking Team presents exactly that level of complexity and innovation.

**Safe phrasing reference:**
- "I've had a great experience at [current company], and after X years of [specific growth], I'm looking for [specific direction] -- more [scale / impact / exposure to Y]."
- Avoid: "bad culture / no raises / manager issues"

---

### Q3: Why Uber / Why this role?

**Must be specific -- not just "big company, lots of data"**

| Dimension | My points |
|-----------|-----------|
| JD keyword alignment | Shopping ranking & recommendation, ML model productionization, GenAI for shopping, big-data (Spark/Hive), cross-functional collaboration |
| My experience match | 3 years building ranking systems at eBay scale, multi-objective optimization, LLM evaluation, E2E model productionization |
| Uber tech attraction | Michelangelo platform, 10M predictions/sec, 5000+ production models, GenAI evolution |
| Recent tech awareness | Shopping Ranking Team building next-gen GenAI shopping systems; Michelangelo's evolution from predictive to generative AI |

**Draft:**
```
Three things specifically draw me to this role.

First, the problem space -- Uber's Shopping Ranking is a multi-stakeholder
optimization challenge very similar to what I've built at eBay. Helping eaters
find what they need requires balancing relevance, personalization, and business
objectives at scale -- exactly the kind of multi-objective ranking I've built
with my Ranking-as-Allocation framework.

Second, the infrastructure scale -- Michelangelo serving 10 million predictions
per second with 5000+ models in production is the kind of engineering environment
where I can both contribute and grow. The evolution from predictive ML to generative
AI that I read about on the engineering blog shows the team is pushing boundaries.

Third, Uber's culture of ownership -- the "Act Like Owners" norm resonates with
how I work. At eBay, I didn't wait for specs -- I identified the relevance filtering
gap and drove it from proposal to site-wide launch. I want to bring that same
ownership mentality to Uber's ranking challenges.
```

---

### Q4: What do you enjoy most about your current role?

**Principle: Pick something highly relevant to the target role**

```
I enjoy the end-to-end ownership -- from identifying a gap (like the lack of
model-based relevance filtering), to designing the system, running experiments,
and shipping to production. The feedback loop of seeing A/B test results validate
a hypothesis is extremely rewarding.

Our org's leadership worked hard to ensure ML engineers are embedded in each team,
working closely with researchers, and focused on launching production features
that bring value to customers.
```

---

### Q5: What kind of work are you looking for next?

**Principle: Show clear direction but remain flexible**

```
I'm looking for a role where I can own impactful ranking and recommendation
features end-to-end at marketplace scale, with room to push modeling boundaries
when the product problem demands it. I'm most excited about systems where ML
directly drives business metrics -- like matching efficiency, conversion, or
user satisfaction -- and where I can leverage both classical ML and emerging
LLM capabilities.
```

---

### Q6: How would your manager describe you?

```
Ownership -- I don't wait for specs; I identified the relevance filtering gap
and drove it from proposal to site-wide launch.

Reliable delivery -- I consistently ship production-quality systems on time,
including the LLM eval pipeline that went from prototype to deployed in one quarter.

Data-driven -- Every design decision is backed by offline metrics and A/B results;
I built diagnostic tooling specifically to catch hidden confounders.
```

Tip: Pick 2-3 words (ownership, data-driven, reliable), each with one short example.

---

### Q7: Compensation expectations

**Strategy A -- Defer (recommended first choice):**
> "I'd prefer to learn more about the role's scope and level before discussing specific numbers -- is that something we can revisit later in the process?"

**Strategy B -- Give range (fallback if recruiter insists):**
> "For total compensation, I'm generally targeting around $___K - $___K, depending on level and scope."

```
My expectation at this stage is something not below my current compensation. ~250K.
Primary strategy: defer with Strategy A.
```

---

### Q8: Timeline / Other processes

```
"I'm targeting making a decision within 4-6 weeks. I'm in early-stage conversations
with a few other ML roles in the Bay Area, nothing at offer stage yet."
```

---

### Q9: Visa / Relocation / Location

| Item | Details |
|------|---------|
| Visa status | H1B, need transfer sponsorship |
| Location preference | Sunnyvale preferred (current base) |
| Work mode | Hybrid OK |
| Earliest start | 2-week notice after offer acceptance |

---

### Q10: Do you have any questions for me?

--> See Part 3 for Uber-specific reverse questions.

---

## Part 3: Reverse Questions (Prepare 5, Ask 3-4)

### About Team & Business

1. "Could you give me a sense of what ML systems the Ranking & Recommendations team owns end-to-end -- for example, the matching algorithm, ETA prediction, or pricing models?"

2. "What does success look like for this role in the first 6 months?"

### About Engineering Practices

3. "How does the team leverage Michelangelo in day-to-day work -- is it the primary platform for model training, serving, and monitoring, or do teams also build custom infrastructure?"

4. "What are the biggest technical challenges the team is focused on right now -- things like real-time feature serving latency, multi-objective trade-offs in matching, or scaling to new markets?"

### About Interview Process

5. "Could you walk me through the remaining interview stages and what each round focuses on?"

### Backup Questions

6. "How does the team approach model iteration -- what's the typical experiment cycle from hypothesis to A/B test to production?"

7. "I read about Michelangelo's evolution from predictive to generative AI -- how is the team incorporating LLMs or generative models into ranking and recommendation workflows?"

---

## Part 4: Project Elevator Pitches (3 Projects)

### Project 1: Ranking-as-Allocation Framework

**30-second Pitch:**
> At eBay, search ranking was done point-wise -- each query-item pair scored independently. I proposed a Ranking-as-Allocation framework that treats the entire search session as an allocation problem, enabling precise control over exposure, conversion, and risk across the full result page. With ranking scores calibrated into probability of sales with full page context, we successfully realized GMB as a ranking objective. I advanced this with late-stage re-ranking and Mixture-of-Experts architectures.

**STARR Outline:**

| Element | Content |
|---------|---------|
| Situation | eBay search ranked items independently; no session-level or multi-objective control |
| Task | Evolve ranking to support full-session context-aware optimization with exposure/conversion/risk constraints |
| Action | Designed allocation framework; built MoE architecture for late-stage re-ranking; ran multi-sided A/B experiments with diagnostic tooling |
| Result | Enabled precise multi-objective control at site scale; reduced marketplace rule-to-production latency from 7 days to <1 day |
| Reflection | Marketplace ranking is resource allocation, not just relevance. **Directly applicable to Uber's rider-driver matching and surge pricing** -- balancing wait time, driver utilization, and platform revenue requires the same multi-objective allocation thinking |

---

### Project 2: LLM-Based Relevance Evaluation Pipeline

**30-second Pitch:**
> eBay's search and ads experimentation relied on crowd-sourced human judges for relevance labels -- expensive, slow, and hard to scale. I led the end-to-end development of an LLM-based evaluation pipeline that achieved human-comparable agreement while cutting cost by 94% and generation latency by 90%. This became the standard evaluation framework for search and ads experiments across the organization.

**STARR Outline:**

| Element | Content |
|---------|---------|
| Situation | Crowd-sourced relevance judging was the bottleneck for experiment velocity -- high cost, multi-day turnaround |
| Task | Build scalable, reliable automated relevance evaluation with human-comparable quality |
| Action | Designed prompt engineering + calibration pipeline; benchmarked against human judges; deployed production-grade async system |
| Result | 94% cost reduction, 90% latency reduction, human-comparable agreement; adopted org-wide |
| Reflection | LLM-as-judge needs careful calibration and failure-mode analysis. **At Uber, this approach could accelerate evaluation of matching quality, ETA accuracy, or content recommendation relevance** -- especially as Michelangelo evolves toward generative AI |

---

### Project 3: Site-Wide Model-Based Relevance Filtering

**30-second Pitch:**
> eBay's organic search had no unified model-based relevance filtering -- irrelevant results hurt buyer trust. I designed and launched the first site-wide filtering framework on Best Match, with tailored variants for deterministic sorting, embedding-based retrieval, and Focused Categories. This improved search quality across millions of listings while balancing precision against recall.

**STARR Outline:**

| Element | Content |
|---------|---------|
| Situation | No model-based relevance gate in organic search; irrelevant listings degraded buyer experience |
| Task | Build a unified yet flexible filtering framework deployable across multiple ranking pipelines |
| Action | Designed modular architecture with variant configs per retrieval type; engineered features; tuned precision-recall tradeoffs per vertical |
| Result | First site-wide model-based relevance filter on Best Match; measurable quality improvement across millions of listings |
| Reflection | Filtering is high-stakes (false positive = lost revenue). **At Uber, similar precision-recall thinking applies to driver-rider matching quality, fraud detection, and content moderation** -- you need guardrails and gradual rollout |

---

## Part 5: Call Notes Area

> The recruiter will share useful info -- jot it down for later interview rounds.

| Item | Notes |
|------|-------|
| Interview rounds & order | |
| Expected timeline | |
| Interviewer roles/names | |
| Key evaluation dimensions | |
| Team/org name | |
| Next action items | |
| Level discussion | |
| Other useful info | |

---

## Part 6: Execution Plan (Weekend Prep)

### Saturday Evening (~2 hours)

- [ ] **Self-intro**: Write English version -> record -> listen -> refine to <= 90 sec and natural
- [ ] **Why Uber + Why this role**: Read JD + Engineering Blog -> finalize Q3 draft
- [ ] **Cultural Norms**: Read Part 7, prepare 1 STAR story per top-4 norm
- [ ] **Comp strategy**: Confirm Strategy A (defer); if B, check levels.fyi for Uber MLE range
- [ ] **Visa / timeline**: Confirm talking points

### Sunday Evening (~1.5 hours)

- [ ] **Project pitches**: Practice 3 projects, each 30-sec pitch + STARR
- [ ] **Q2-Q6 drafts**: Review and internalize key points (don't memorize)
- [ ] **Reverse questions**: Select 4-5 from Part 3, write on a card
- [ ] **Michelangelo deep dive**: Re-read Part 7 Uber background section
- [ ] **Mock run-through**: Do a full 15-min practice run (intro -> questions -> reverse questions)

### Monday Morning (30 min before call)

- [ ] Re-read this document
- [ ] Open JD + resume side by side
- [ ] Test audio setup
- [ ] Have water ready

---

## Part 7: Uber Deep Background

### 7.1 Uber's 8 Cultural Norms + Your Story Mapping

Uber CEO Dara Khosrowshahi replaced the original 14 values with 8 cultural norms in 2017. **Map your behavioral answers to these:**

| Cultural Norm | What it Means | Your Story |
|--------------|---------------|------------|
| **We Act Like Owners** | Seek out problems and solve them; bias for action | You identified the relevance filtering gap at eBay and drove it from proposal to site-wide launch without being asked |
| **We Are Customer Obsessed** | Deliver experiences that exceed expectations | Your filtering work was driven by buyer trust -- removing irrelevant results to protect the user experience |
| **We Make Big Bold Bets** | Sometimes fail, but failure makes us smarter | Ranking-as-Allocation was a 0-to-1 paradigm shift from pointwise to session-level ranking |
| **We Value Ideas Over Hierarchy** | Best ideas from anywhere; candid debate | You drove LLM eval adoption across Search & Ads orgs, working cross-functionally to standardize the framework |
| **We Persevere** | Power of grit; seek tough challenges | Multi-objective ranking required iterating through multiple architectures (pointwise -> listwise -> MoE) |
| **We Build Globally, We Live Locally** | Global scale + local connection | eBay search serves diverse markets with different relevance expectations per vertical |
| **We Celebrate Differences** | Diversity and inclusion | Cross-team collaboration between ML engineers and researchers with different expertise |
| **We Do the Right Thing** | Ethical standards | Building guardrails and gradual rollout for filtering to prevent false positives (seller revenue protection) |

**Mission Statement:** "We ignite opportunity by setting the world in motion."

---

### 7.2 Michelangelo -- Uber's ML Platform (Three Phases)

**Phase 1 (2016-2019): Predictive Analytics**
- Tree-based models (XGBoost) for ETA, risk, pricing
- Key components:
  - **Palette** -- Feature store for feature management and serving
  - **Gallery** -- Metadata registry for model lineage tracking
  - **Manifold** -- Visual debugging and model interpretation tool
- Focus: Standardize ML workflow across teams

**Phase 2 (2019-2023): Deep Learning**
- Model Excellence Score (MES) for quality tracking across all models
- Project tiering (Tier 1-4) by business impact
- **Canvas** framework -- "model iteration as code"
- **Horovod** for distributed training on GPU clusters
- **Triton** for high-performance model serving
- Scale: 20K+ model training jobs per month

**Phase 3 (2023-Present): Generative AI**
- Gen AI Gateway for unified LLM access (external + in-house models)
- LLM fine-tuning via Hugging Face integration
- Model parallelism via DeepSpeed
- Prompt engineering toolkit with version control
- H100 GPUs for latency-sensitive GenAI; A10 GPUs for serving
- 4x network upgrades (25Gb/s -> 100Gb/s) nearly doubled LLM training speed

**Key stat:** Uber makes **10 million real-time ML predictions per second** at peak, with **5,000+ models in production**.

---

### 7.3 Key Open-Source Projects from Uber

| Project | Purpose | Your Relevance |
|---------|---------|---------------|
| **Michelangelo** | End-to-end ML platform (data -> training -> deployment -> monitoring) | Analogous to your full-stack ranking pipeline at eBay |
| **Horovod** | Distributed deep learning training on GPU clusters | Relevant if discussing training infrastructure scaling |
| **Ludwig** | Declarative deep learning / AutoML framework | Low-code model building, interesting for rapid experimentation |
| **Pyro** | Probabilistic programming built on PyTorch | Relevant for uncertainty quantification in ETA/pricing |
| **Fiber** | Distributed computing framework for AI | Cluster management for large-scale training |

---

### 7.4 Marketplace ML -- Core Scenarios

| Scenario | ML Challenge | Connection to Your Work |
|----------|-------------|------------------------|
| **ETA Prediction** | Real-time regression with geospatial + temporal features; accuracy directly impacts rider trust | Similar to relevance scoring -- prediction quality drives user satisfaction |
| **Dynamic Pricing (Surge)** | Supply/demand equilibrium; multi-objective (rider wait time vs driver earnings vs platform margin) | Direct parallel to your Ranking-as-Allocation multi-objective framework |
| **Driver-Rider Matching** | Bipartite matching optimization under latency constraints; fairness across drivers | Allocation problem -- your framework treats ranking as resource allocation |
| **Fraud Detection** | Real-time classification with high precision requirements; adversarial environment | Similar precision-recall tradeoffs as your relevance filtering work |
| **Search & Recommendations** | Restaurant/destination ranking; personalization with sparse user history | Your core domain -- search ranking and recommendation systems |

---

### 7.5 Engineering Blog Highlights (Relevant to Your Background)

**1. "From Predictive to Generative AI: The Evolution of Michelangelo"**
- Chronicles the platform's journey across 3 phases
- Key insight: Uber's ML infrastructure had to evolve from supporting simple tree models to serving LLMs -- same trajectory as eBay's search stack
- **Your angle:** You've lived this evolution at eBay (XGBoost -> deep ranking -> LLM eval)

**2. "Scaling AI/ML Infrastructure at Uber"**
- Cloud migration, GPU optimization, Kubernetes orchestration
- 4x network upgrade dramatically improved training throughput
- DeepSpeed memory offload: 2x model flops utilization, 34% less GPU usage
- **Your angle:** Understanding infrastructure constraints when designing ranking systems

**3. "ML Education at Uber"**
- Internal ML training program to scale ML adoption across engineering
- Emphasizes ML as an engineering discipline, not just research
- **Your angle:** Aligns with your experience embedding ML engineers into product teams

**4. Marketplace Optimization Series**
- Real-time matching, pricing algorithms, driver incentive design
- Multi-objective optimization is a recurring theme
- **Your angle:** Directly maps to your Ranking-as-Allocation framework

---

### 7.6 MLE Interview Process Overview

For Machine Learning Engineer roles, Uber typically runs:

| Stage | Focus |
|-------|-------|
| Recruiter Screen | Background fit, motivation, logistics (YOU ARE HERE) |
| Technical Screen | Coding ability, ML fundamentals |
| Final Loop (4-5 rounds) | See below |

**Final Loop Rounds:**
1. **Coding & Data** -- Algorithm implementation, data manipulation
2. **Applied ML** -- Model selection, feature engineering, evaluation metrics, trade-offs
3. **System Design** -- End-to-end ML system architecture (training, serving, monitoring)
4. **Product & Collaboration** -- Translating business problems to ML solutions, cross-functional communication
5. **Behavioral** -- Cultural norm alignment, leadership, conflict resolution

**What Uber evaluates:**
- **Production Ownership** -- Systems that work under latency constraints and data imperfections
- **Trade-off Reasoning** -- Accuracy vs latency vs cost vs marketplace stability
- **Operational Maturity** -- Model drift, monitoring, debugging, graceful degradation
- **Cross-functional Communication** -- Explaining technical decisions to non-technical stakeholders

---

## Appendix: Common Pitfalls Quick Reference

| Avoid | Do Instead |
|-------|-----------|
| Criticize current company/manager | "Seeking new challenges / broader impact" |
| "I'm open to anything" (compensation) | Give a range or defer |
| "What's your culture like?" (reverse Q) | Ask specific team technical challenges or success criteria |
| Talk too much detail (5-min project story) | HR call: project pitch in 30 sec - 2 min |
| Don't mention other interviews at all | "Early stages with a few other ML roles" |
| Speak too fast to prove English fluency | Deliberately slow down; clarity > fluency |
| Generic "I like ML" for Why Uber | Reference Michelangelo, marketplace ML, specific blog posts |
