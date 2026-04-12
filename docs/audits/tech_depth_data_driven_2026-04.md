# Audit: technical_problem_solving -- Data-Driven Evidence Check

**Date**: 2026-04-11
**Task**: T-P2-365
**Scope**: All 28 examples tagged with `technical_problem_solving` (theme_id=1)
**Auditor**: Automated + manual review

## Summary

| Verdict | Count | Examples |
|---------|-------|----------|
| PASS | 8 | BLOG-01B, BLOG-03, EX-01, EX-02, EX-05, EX-06, EX-08, EX-33 |
| NEEDS-NOTE | 13 | BLOG-01, EX-03, EX-04, EX-07, EX-09, EX-09B, EX-10, EX-14, EX-19, EX-20, EX-21, EX-22, EX-23 |
| RECOMMEND-UNTAG | 7 | EX-11, EX-12, EX-15, EX-16, EX-17, EX-18, EX-24 |

**Total**: 28 examples audited (task description estimated 27)

## Criteria

- **(a)** Quantitative number in the Result section (e.g., "+1% GMB", "200M+", "p99 latency dropped 30%")
- **(b)** Metric name and direction-of-change in the Action section
- **(a)+(b)** together = bar for real data-driven story
- **(c)** A/B test reference (strong supporting evidence)
- **(d)** Data-derived hypothesis (strong supporting evidence)
- If (c) or (d) present + only one of (a)/(b): NEEDS-NOTE rather than RECOMMEND-UNTAG

## Verdicts

### PASS (8)

#### BLOG-01B: Brand Recall: Deep Dive -- Challenging the Evaluation Blind Spot
- **(a)** YES: "~95%+ of business value", "~2% of transactions drove 50%+ of GMV"
- **(b)** YES: Action analyzes price variance, GMV vs frequency calibration
- **(d)** YES: Data-derived hypothesis that frequency != value
- **Verdict**: PASS

#### BLOG-03: Cross-Org Boundary Defense via LLM Relevance Pipeline
- **(a)** YES: "~18K high-quality labeled judgments per day at ~$500", "1.5% GMB lift"
- **(b)** YES: Action describes relevance signal design with cost/volume metrics
- **Verdict**: PASS

#### EX-01: Search Diversity: Intent Collapse Discovery
- **(a)** YES: "200M+ annualized impact"
- **(b)** YES: Action analyzes "hundreds of high-volume queries" with intent collapse pattern, purchase data validation
- **(d)** YES: Data-derived hypothesis about page-level homogeneity
- **Verdict**: PASS

#### EX-02: Overcoming Manager Resistance via Proactive Team Transfer
- **(a)** YES: "+1% GMB", "200M+ annualized impact"
- **(b)** YES: Action reframes diversity as ranking allocation with clear metric targets
- **Verdict**: PASS

#### EX-05: Relevance Filtering: Deployment Feasibility Under Latency Constraints
- **(a)** YES: "+4-6% GMB on null/low-intent queries", "<=1% latency target"
- **(b)** YES: Action analyzes "80%+ of candidate items obviously irrelevant", latency budgets, tree count analysis
- **(d)** YES: Data-derived insight about traffic distribution
- **Verdict**: PASS

#### EX-06: Allocation Framework as Reusable Platform Primitive -- 200M+ Impact
- **(a)** YES: "+0.6%+ independent GMB gain" per reuse, "200M+ annualized"
- **(b)** YES: Action describes unified GMB bidding dimension replacing LTR scoring paradigm
- **Verdict**: PASS

#### EX-08: Module Proliferation Prod Degradation -- Escalation to VP
- **(a)** YES: "200M+ annualized impact" (downstream outcome)
- **(b)** YES: Action quantifies "significant GMB regression", modules "4-6x the space", historical vs current baselines
- **(d)** YES: Data-derived finding about interaction effects
- **Verdict**: PASS

#### EX-33: MoE -> Allocation Paradigm Shift
- **(a)** YES: "200M in annualized GMB"
- **(b)** YES: Action analyzes "MRR up, revenue neutral" launch criteria, co-activation patterns, metric self-fulfilling prophecy
- **(c)** YES: Implicit experiment framework (MoE test)
- **(d)** YES: Data-derived paradigm reframe
- **Verdict**: PASS

---

### NEEDS-NOTE (13)

These examples have partial data-driven evidence or strong supporting signals (c/d) that compensate for gaps. A relevance_note should explain why this story still belongs under technical_problem_solving.

#### BLOG-01: Brand Recall: Influence -- Changing the Researcher-Engineer Dynamic
- **(a)** WEAK: "~95% business value" appears in Action, not Result. Result says "launched on time meeting all criteria" (no number)
- **(b)** PARTIAL: Action mentions compression attempts and GMV-based pruning but no explicit metric+direction
- **(d)** YES: Data-derived pivot from frequency to GMV-based pruning
- **Gap**: Result lacks quantitative outcome
- **Recommendation**: Add a quantitative result number or add a relevance_note explaining this is primarily a collaboration/influence story with technical depth as supporting element

#### EX-03: Challenging Sale NDCG Proxy -- First Principles Rethinking
- **(a)** WEAK: Result says "significant GMB uplift" -- no specific number
- **(b)** YES: Action deeply analyzes price bias, calibration trap, BM25-inspired transformation
- **(d)** YES: Data-derived hypothesis about proxy selection
- **Gap**: Result should include specific uplift percentage
- **Recommendation**: Add specific GMB uplift number to result, or note that this example's value is in the method/insight rather than the outcome magnitude

#### EX-04: MRR Paradox -- Educating Stakeholders on Metric Limitations
- **(a)** NO: Result says "fundamental shift" -- no numbers
- **(b)** YES: Action uses "GMB + purchase data", "abandonment rate decrease" as evidence
- **(c)** IMPLICIT: References experiment results
- **Gap**: Result has no quantitative metric
- **Recommendation**: Add specific metric improvement to result (e.g., abandonment rate delta), or note that this example's technical depth is in the metric limitation analysis

#### EX-07: Relevance Dataset Bias -- Challenging the Self-Fulfilling Prophecy
- **(a)** NO: Result says "prevented wasted engineering cycles" -- no numbers
- **(b)** YES: Action identifies pairwise dataset bias, survivorship bias
- **(d)** YES: Data-derived hypothesis about self-fulfilling evaluation loop
- **Gap**: No quantitative outcome -- this is a "prevented a wrong direction" story
- **Recommendation**: Add note explaining this is a prevention/redirection story where the data-driven value is in the diagnosis, not a launch metric

#### EX-09: Conversational Search -- Proxy Item Breakthrough
- **(a)** NO: Result says "strong results" -- no number
- **(b)** NO: Action describes proxy item approach but no explicit metric+direction
- **Gap**: Both (a) and (b) missing. Story has deep technical insight but no quantitative evidence
- **Recommendation**: Add specific retrieval quality metrics (e.g., recall@k, click-through improvement) or add relevance_note explaining why this qualifies despite no numbers (architectural innovation significance)

#### EX-09B: Conversational Search Privacy: Proxy Item Generation
- **(a)** NO: No quantitative number in result
- **(b)** NO: Action is privacy-focused, no metric+direction
- **(d)** YES: Privacy-by-design architecture analysis
- **Gap**: This is a privacy/architecture story, not a metric-driven one
- **Recommendation**: Add relevance_note explaining technical depth is in the architectural privacy guarantee (ELIMINATE vs MITIGATE principle), not in quantitative outcome

#### EX-10: Experimental Rigor -- Designing Debiased Evaluation Framework
- **(a)** WEAK: Result says "consistent results" with no specific number, but mentions "GMB rise" generally
- **(b)** YES: Action has "debiased curve (A/B lift minus A/A lift)", "GMB rise + JSD distance decrease + abandonment decrease"
- **(c)** YES: Entire story is about A/B test framework design
- **(d)** YES: Bucketing drift discovery from data
- **Gap**: Result should include specific metric numbers
- **Recommendation**: Add specific GMB lift percentage or JSD improvement to result. Strong (b)(c)(d) presence makes this clearly technical -- just needs a number

#### EX-14: LLM Exploration -- From Vague AI Mandate to Pragmatic LLM-as-Judge
- **(a)** WEAK: Result says "won across multiple relevance metrics, delivered GMB improvement" -- no specific numbers
- **(b)** PARTIAL: Action describes feasibility analysis ("tens of QPS vs 40K peak") but main action is pivot strategy
- **(d)** YES: Data-derived diagnosis of dataset quality issue
- **Gap**: Result should include specific metric wins
- **Recommendation**: Add specific relevance metric improvement and GMB number

#### EX-19: Explaining A/B Test Confounder to PM
- **(a)** NO: Result describes agreement on methodology, no numbers
- **(b)** PARTIAL: Action analyzes same-page contamination confounder
- **(c)** YES: Entire story is about A/B test design
- **(d)** YES: Data-derived confounder identification
- **Gap**: This is a communication/methodology story; numbers would be about what was prevented, not achieved
- **Recommendation**: Add relevance_note: technical depth is in the experimental design rigor (identifying confounder that would have invalidated results)

#### EX-20: Seller Risk Modeling Fairness -- Ethical Dilemma and Escalation
- **(a)** NO: No quantitative number in result
- **(b)** PARTIAL: Action references "false-positive blocking vs fraud prevention" tradeoff
- **(d)** YES: Research-backed analysis of legal and fairness implications
- **Gap**: Story is primarily about ethical escalation, not technical metrics
- **Recommendation**: Add relevance_note: technical depth is in the precision-modeling alternative and legal framework research, not in quantitative outcome

#### EX-21: Tech Debt Balance -- Declarative Artifactory Proof of Concept
- **(a)** NO: Result says "shipped on time" -- no number
- **(b)** YES: Action has "parity tests proving expressions were identical"
- **Gap**: No quantitative business outcome
- **Recommendation**: Add GMB or latency impact of the feature, or note that technical depth is in the architectural boundary analysis (core vs peripheral)

#### EX-22: Delegation Decision -- Hashing Algorithm for Experiment Platform
- **(a)** NO: No specific number in result
- **(b)** YES: Action specifies "uniform distribution, performance benchmarks, latency budget"
- **(d)** YES: Data-derived bug discovery (ItemID distribution non-uniformity)
- **Gap**: No quantitative business outcome
- **Recommendation**: Add note that technical depth is in the acceptance framework design and latent bug discovery through data analysis

#### EX-23: Large-Scale Project with Tight Deadlines -- NYC C2C Policy Launch
- **(a)** NO: Result says "delivered within VP's deadline" -- no number
- **(b)** YES: Action identifies "control effectiveness below expectations", silent test failure from upstream overwrite
- **(c)** YES: A/B test integrity investigation
- **(d)** YES: Data-derived discovery of policy interaction effects
- **Gap**: No quantitative outcome in result
- **Recommendation**: Add specific policy ROI numbers or GMB lift, or note that technical depth is in the experimental integrity investigation and policy interaction discovery

---

### RECOMMEND-UNTAG (7)

These examples lack both (a) quantitative results and (b) metric-driven action sections. Their primary narratives are not about technical problem solving with data-driven evidence. They belong under other themes (leadership, mentoring, failure/resilience, communication).

#### EX-11: Mentoring Intern on Overpromise / Goal Visibility
- **(a)** NO: "significantly improved", "received return offer" -- no numbers
- **(b)** NO: Action is coaching-focused, no metrics
- **Primary theme**: Mentoring / leadership development
- **Why untag**: Story has zero data-driven or technical problem-solving content. Entirely about communication coaching.

#### EX-12: Helping PhD Interns Transition from Notebook to Production Stack
- **(a)** NO: "successfully adapted" -- no numbers
- **(b)** NO: Action describes template creation, no metric analysis
- **Primary theme**: Mentoring / onboarding
- **Why untag**: While the template class involves technical content, the story is about people management and onboarding process. No data-driven evidence or metric-driven technical decisions.

#### EX-15: Model Deprecation Incident -- Resilience and Process Improvement
- **(a)** NO: "one week on redeployment" -- timeline, not impact metric
- **(b)** NO: Action is incident-response focused, no data analysis
- **Primary theme**: Failure / resilience / process improvement
- **Why untag**: Incident response story with process improvement. No data-driven hypothesis or metric-driven technical decision-making.

#### EX-16: Cross-Datacenter Deployment Incident
- **(a)** NO: "quickly stabilized" -- no numbers
- **(b)** NO: Action is incident-coordination focused
- **Primary theme**: Failure / stretching beyond comfort zone
- **Why untag**: Cross-boundary deployment incident. Technical in setting but not in methodology -- no data-driven analysis or metric reasoning.

#### EX-17: Difficult Feedback from Senior IC -- Building Credibility
- **(a)** NO: "built mutual respect" -- no numbers
- **(b)** NO: Action is interpersonal, no metrics
- **Primary theme**: Feedback / credibility / process integrity
- **Why untag**: Interpersonal credibility story. The technical context (PR review) is incidental to the narrative about process integrity and trust-building.

#### EX-18: Pushing Back on Unreasonable Scope -- Distributed Training
- **(a)** NO: "deprioritized distributed training" -- no impact number
- **(b)** NO: Action provides analysis but no metric with direction
- **Primary theme**: Pushback / scope management / leadership
- **Why untag**: Story is about managing unreasonable expectations and multi-manager conflict. Technical analysis (distributed training pros/cons) is supporting evidence for a scope decision, not the core narrative.

#### EX-24: Explaining Allocation Problem to VP -- C2C Policy Launch Communication
- **(a)** NO: "VP accepted analysis" -- no numbers
- **(b)** NO: Action is communication-focused (conclusion-first, VP-accessible framing)
- **Primary theme**: Technical communication / stakeholder management
- **Why untag**: This is the communication cut of EX-23. The technical content is about framing and persuasion, not about data-driven problem solving. EX-23 (which has NEEDS-NOTE) covers the technical depth angle of the same project.

---

## Observations

1. **PASS examples cluster around the allocation/ranking domain** (EX-01, EX-02, EX-05, EX-06, EX-08, EX-33) where quantitative GMB metrics are naturally embedded in the narrative.

2. **NEEDS-NOTE examples often have strong (b)/(c)/(d)** but lack a specific number in the Result section. Several could be upgraded to PASS by adding one concrete metric to the result.

3. **RECOMMEND-UNTAG examples are primarily interpersonal/process stories** (mentoring, incident response, communication, scope management) where technical context is setting, not substance.

4. **The schema lacks a `relevance_note` column** on `example_theme_tags`. The task description references this field, but it does not exist. Adding NEEDS-NOTE annotations would require either adding this column or documenting the notes externally.

5. **EX-09 and EX-09B** are an interesting pair: EX-09 is the technical breakthrough cut, EX-09B is the privacy cut. Neither has quantitative results, suggesting the underlying project's metrics should be back-filled into at least EX-09.
