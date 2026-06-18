# BQ-DEPTH-10 (T-P1-581) -- Top-40 Primary-Story Assignments

> **Status: AWAITING USER APPROVAL before DB write.** Each row sets
> `question_example_links.is_primary=1` for one (question, example) pair.
> The partial unique index `ux_qel_primary_per_question` guarantees at most
> one primary per question.
>
> **Flow** (human-as-verifier): Claude drafted 40 -> DeepSeek QA judged each
> (keep / swap / flag, `deepseek-v4-pro`, temp 0) -> Claude accept-default
> review -> **you approve** -> idempotent `.bak`-guarded seed `--apply`.
>
> Selection = top-40 high-probability questions (company overlap + asked
> frequency) across all 9 categories; each primary chosen from that question's
> already-linked candidates, guided by `docs/bq_golden_trait_matrix.md`.

**Review tally:** 26 kept as drafted (DeepSeek concurred), 5 swapped on DeepSeek's advice, 9 overrode DeepSeek (kept draft, reason in note). All 40 primaries are verified existing links.

| # | Question | FINAL primary | Draft | DeepSeek | Decision |
|---|----------|---------------|-------|----------|----------|
| 1 | **OWN-1** Give an example of a time when you took complete ownership of a failure. | `EX-15` | `EX-15` | KEEP | keep |
| 2 | **OWN-2** Describe a situation where you went above and beyond to meet a deadline. | `EX-23` | `EX-23` | FLAG | keep |
| 3 | **OWN-6** Tell me about a time when you took a bold risk at work. | `EX-33` (was `EX-16`) | `EX-16` | SWAP->EX-33 | ACCEPT swap |
| 4 | **OWN-8** Describe a situation where you were moving fast and made a mistake. | `EX-30` | `EX-30` | KEEP | keep |
| 5 | **OWN-11** Tell me about a time when you took ownership of a challenging situation. | `EX-02` | `EX-02` | SWAP->EX-01 | OVERRIDE |
| 6 | **ADP-5** Describe a time when you made a mistake. How did you handle it, and what did you learn? | `EX-30` | `EX-30` | KEEP | keep |
| 7 | **ADP-19** What's the most challenging piece of feedback you've received? | `EX-17` | `EX-17` | KEEP | keep |
| 8 | **ADP-11** Describe a major setback you experienced and how you overcame it. | `EX-15` | `EX-15` | KEEP | keep |
| 9 | **ADP-10** Describe a time when you created a plan in a highly ambiguous environment. | `EX-14` | `EX-14` | KEEP | keep |
| 10 | **ADP-1** Tell me about a time when you had to quickly learn a new technology or skill. | `EX-14` | `EX-14` | KEEP | keep |
| 11 | **ADP-15** What's the biggest lesson you've learned from a failed project? | `EX-33B` | `EX-33B` | KEEP | keep |
| 12 | **IMP-11** Describe a time when you faced an ethical dilemma in your work. | `EX-20` | `EX-20` | SWAP->EX-34 | OVERRIDE |
| 13 | **IMP-2** Describe a time when you prioritized user experience in a technical decision. | `EX-01` | `EX-01` | KEEP | keep |
| 14 | **IMP-3** How do you balance technical debt with feature delivery? | `EX-21` | `EX-21` | KEEP | keep |
| 15 | **IMP-10** Give an example of a project where you focused on long-term impact. | `EX-06` | `EX-06` | KEEP | keep |
| 16 | **INN-4** Describe a time when you implemented an innovative solution. | `EX-09` | `EX-09` | KEEP | keep |
| 17 | **INN-2** Tell me about a project or idea you started on your own. | `EX-01` | `EX-01` | KEEP | keep |
| 18 | **INN-8** Describe a time when you questioned a traditional approach and proposed something new. | `EX-03` (was `EX-33`) | `EX-33` | SWAP->EX-03 | ACCEPT swap |
| 19 | **INN-5** Tell me about a time when you improved an inefficient process. | `EX-12B` | `EX-12B` | KEEP | keep |
| 20 | **PS-1** Walk me through a difficult technical decision you had to make. | `EX-05` | `EX-05` | KEEP | keep |
| 21 | **PS-6** Describe a time when you took a calculated risk. What was the outcome? | `EX-16` | `EX-16` | SWAP->EX-33 | OVERRIDE |
| 22 | **PS-11** Describe a time when you used data to make a key decision. | `EX-01` | `EX-01` | KEEP | keep |
| 23 | **PS-2** Describe a time when you solved a problem creatively. | `EX-09` | `EX-09` | SWAP->EX-01 | OVERRIDE |
| 24 | **PS-4** Give an example of a time when you analyzed a complex problem and broke it down. | `EX-03` | `EX-03` | SWAP->EX-05 | OVERRIDE |
| 25 | **PS-10** Describe a situation where you had to make a tough trade-off to keep a project moving forward. | `EX-05` | `EX-05` | KEEP | keep |
| 26 | **EXE-5** Tell me about a time when you managed a large-scale project with tight deadlines. | `EX-23` | `EX-23` | KEEP | keep |
| 27 | **EXE-3** Explain a complex technical problem you solved and your approach. | `EX-05` | `EX-05` | KEEP | keep |
| 28 | **EXE-9** Describe a time when you dealt with a major project setback and how you recovered. | `EX-33B` | `EX-33B` | SWAP->EX-23 | OVERRIDE |
| 29 | **EXE-13** How do you balance immediate tasks with longer-term projects? | `EX-21` | `EX-21` | KEEP | keep |
| 30 | **LDR-1** Describe a time when you coached or mentored someone. | `EX-12` | `EX-12` | SWAP->EX-11 | OVERRIDE |
| 31 | **LDR-3** Tell me about a time you had to make a tough call as a leader. | `BLOG-04` (was `EX-13`) | `EX-13` | SWAP->BLOG-04 | ACCEPT swap |
| 32 | **LDR-6** How do you decide when to delegate vs. handle tasks yourself? | `EX-22` | `EX-22` | KEEP | keep |
| 33 | **LDR-2** How do you handle performance issues with junior team members? | `EX-11` | `EX-11` | KEEP | keep |
| 34 | **COL-1** Describe a time when you disagreed with a team member. How did you resolve it? | `EX-13` | `EX-13` | SWAP->BLOG-01 | OVERRIDE |
| 35 | **COL-3** Tell me about a time you worked with a cross-functional team to achieve a common goal. | `EX-12B` (was `BLOG-03`) | `BLOG-03` | SWAP->EX-12B | ACCEPT swap |
| 36 | **COL-5** How do you align different teams or stakeholders on a shared goal? | `BLOG-03` (was `EX-33`) | `EX-33` | SWAP->BLOG-03 | ACCEPT swap |
| 37 | **COL-6** Describe a time when you had to communicate a complex technical concept to an executive. | `EX-24` | `EX-24` | KEEP | keep |
| 38 | **COM-1** How do you explain complex technical details to a non-technical stakeholder? | `EX-19` | `EX-19` | KEEP | keep |
| 39 | **COM-2** Describe a time when you had to persuade others to change direction. | `EX-14` | `EX-14` | KEEP | keep |
| 40 | **COM-3** Tell me about a time when you had to deliver bad news to a team. | `EX-08` | `EX-08` | SWAP->EX-15 | OVERRIDE |

## Per-row reasoning

### OWN-1 -> `EX-15` (ownership)
- *DeepSeek (keep):* Personal failure with clear ownership taken end-to-end.
- *Claude decision (keep):* Matrix oncall/ownership anchor; already the existing primary.

### OWN-2 -> `EX-23` (ownership)
- *DeepSeek (flag):* Story leans problem-solving over extra-effort-for-deadline; emphasize how analysis averted delay.
- *Claude decision (keep):* Sole linked story; the flag is a delivery tip, not a swap. Keep.

### OWN-6 -> `EX-33` (ownership)
- *DeepSeek (swap->EX-33):* EX-16 is reactive risk; EX-33 is a deliberate chosen risk (gave up carry-over protection) -- better fits 'bold risk'.
- *Claude decision (accept-swap):* Accept: EX-33 is a stronger deliberate bold-risk AND frees EX-16 to be PS-6's calculated-risk (removes the OWN-6/PS-6 duplicate).

### OWN-8 -> `EX-30` (ownership)
- *DeepSeek (keep):* Directly answers moving fast + making a mistake with clear ownership.
- *Claude decision (keep):* Canonical move-fast-broke-it ownership story.

### OWN-11 -> `EX-02` (ownership)
- *DeepSeek (swap->EX-01):* EX-01 shows direct personal ownership of diagnosing+solving a silent search issue.
- *Claude decision (override):* Override: matrix designates EX-02 ('problem follows the person') as the ownership_accountability primary; EX-01 already leads IMP-2/INN-2/PS-11.

### ADP-5 -> `EX-30` (adaptability)
- *DeepSeek (keep):* Directly addresses a personal design mistake and the handling.
- *Claude decision (keep):* Matrix failure_setback primary; already the existing primary.

### ADP-19 -> `EX-17` (adaptability)
- *DeepSeek (keep):* Only story provided; directly addresses receiving challenging feedback.
- *Claude decision (keep):* Already the existing primary; matrix reliance-vs-trust anchor.

### ADP-11 -> `EX-15` (adaptability)
- *DeepSeek (keep):* Sole option; full STAR of a major setback and its recovery.
- *Claude decision (keep):* Recovered-within-a-week-then-reformed arc.

### ADP-10 -> `EX-14` (adaptability)
- *DeepSeek (keep):* Shows building a data-driven feasibility plan under a no-precedent mandate.
- *Claude decision (keep):* Matrix ambiguity primary.

### ADP-1 -> `EX-14` (adaptability)
- *DeepSeek (keep):* Directly demonstrates rapidly learning GenAI in a week.
- *Claude decision (keep):* Learn-new-tech facet of EX-14.

### ADP-15 -> `EX-33B` (adaptability)
- *DeepSeek (keep):* Clear failure with a strong personal KPI-humility lesson.
- *Claude decision (keep):* Lesson-from-a-project-that-did-not-ship.

### IMP-11 -> `EX-20` (impact)
- *DeepSeek (swap->EX-34):* EX-34 shows an ethical dilemma via personal conflict with a superior.
- *Claude decision (override):* Override: EX-20 is the richer ethical dilemma (new-seller fairness trap, PayPal/legal precedent); EX-34 reads more as a policy disagreement, better held for IMP-13 later.

### IMP-2 -> `EX-01` (impact)
- *DeepSeek (keep):* Prioritized UX by diagnosing user intent harm invisible to dashboards.
- *Claude decision (keep):* Sole linked story.

### IMP-3 -> `EX-21` (impact)
- *DeepSeek (keep):* Balances core-vs-peripheral to ship on time with no residual debt.
- *Claude decision (keep):* Sole linked debt story.

### IMP-10 -> `EX-06` (impact)
- *DeepSeek (keep):* Crystallized a single experiment into a reusable allocation platform -- long-term vision.
- *Claude decision (keep):* Platform-primitive long-term-value story.

### INN-4 -> `EX-09` (innovation)
- *DeepSeek (keep):* Novel proxy-item method that maximized infra reuse.
- *Claude decision (keep):* Proxy-item breakthrough.

### INN-2 -> `EX-01` (innovation)
- *DeepSeek (keep):* Directly answers self-initiated project + demonstrates innovation.
- *Claude decision (keep):* Self-initiated Hacker Week prototype (sole linked).

### INN-8 -> `EX-03` (innovation)
- *DeepSeek (swap->EX-03):* EX-03 directly challenges the core metric and proposes a new proxy -- a more precise match; EX-33 is about test method, not the traditional approach itself.
- *Claude decision (accept-swap):* Accept: EX-03 ('questioned NDCG, proposed GMB') is squarely 'questioned a traditional approach'; EX-33 better serves COL-5/leadership.

### INN-5 -> `EX-12B` (innovation)
- *DeepSeek (keep):* Shows the process waste (<5% utilization) and a measurable improvement; complete arc.
- *Claude decision (keep):* Notebook->platform migration.

### PS-1 -> `EX-05` (problem_solving)
- *DeepSeek (keep):* Real technical decision with constraints, alternatives, and quantified result.
- *Claude decision (keep):* Latency-budget deployment tradeoff.

### PS-6 -> `EX-16` (problem_solving)
- *DeepSeek (swap->EX-33):* EX-33 shows a deliberate calculated risk (gave up carry-over protection); EX-16 reads as reactive crisis response.
- *Claude decision (override):* Override: keep EX-16 as the clean calculated-risk (named the risk + bandwidth line-item, already the existing primary); EX-33 now leads OWN-6's bold-risk.

### PS-11 -> `EX-01` (problem_solving)
- *DeepSeek (keep):* Data-driven diagnosis (abandon-log slice) driving the decision.
- *Claude decision (keep):* Matrix data_analysis primary.

### PS-2 -> `EX-09` (problem_solving)
- *DeepSeek (swap->EX-01):* EX-01 combines creative diagnosis with strong data-driven insights.
- *Claude decision (override):* Override: EX-09 (proxy-item generation) is the more distinctly *creative* solution; EX-01 already leads three other rows.

### PS-4 -> `EX-03` (problem_solving)
- *DeepSeek (swap->EX-05):* EX-05 shows explicit structured decomposition vs EX-03's metric analysis.
- *Claude decision (override):* Override: EX-03 is a solid complex-problem analysis (calibration trap); EX-05 already leads PS-1/PS-10/EXE-3 (avoid 4x concentration).

### PS-10 -> `EX-05` (problem_solving)
- *DeepSeek (keep):* Sole story; directly a tough latency trade-off.
- *Claude decision (keep):* Cost-vs-quality tradeoff.

### EXE-5 -> `EX-23` (execution)
- *DeepSeek (keep):* Fits 'large-scale project with tight deadline' directly.
- *Claude decision (keep):* NYC cross-org launch (30+ people).

### EXE-3 -> `EX-05` (execution)
- *DeepSeek (keep):* STAR-complete; answers complexity + approach.
- *Claude decision (keep):* Sole linked story.

### EXE-9 -> `EX-33B` (execution)
- *DeepSeek (swap->EX-23):* EX-33B lacks a project-rescue arc (never shipped); EX-23 shows locating the control failure and recovering item-by-item.
- *Claude decision (override):* Override (judgment): an honest did-not-ship setback with a strong lesson is a valid 'major setback' answer and preserves diversity; EX-23 already leads OWN-2/EXE-5. DeepSeek's recovery point is noted as a delivery caveat.

### EXE-13 -> `EX-21` (execution)
- *DeepSeek (keep):* Explicitly balances an urgent feature against longer-term debt.
- *Claude decision (keep):* Immediate-vs-long-term execution tradeoff.

### LDR-1 -> `EX-12` (leadership)
- *DeepSeek (swap->EX-11):* EX-11 is a clearer 1:1 coaching example with a specific communication framework.
- *Claude decision (override):* Override: keep EX-12 (onboarding/enablement mentoring) here and reserve EX-11 for LDR-2 (performance coaching) so both stories are used and distinct.

### LDR-3 -> `BLOG-04` (leadership)
- *DeepSeek (swap->BLOG-04):* BLOG-04 is a clearer tough call: knowingly accept a short-term metric drop to fix the system.
- *Claude decision (accept-swap):* Accept: a deliberate tough leadership call with an owned cost; frees EX-13 to be COL-1's conflict primary.

### LDR-6 -> `EX-22` (leadership)
- *DeepSeek (keep):* Shows the delegate-vs-do-it-myself decision (maintainability vs intuition).
- *Claude decision (keep):* Delegation-decision story.

### LDR-2 -> `EX-11` (leadership)
- *DeepSeek (keep):* Directly addresses a junior's performance/communication gap.
- *Claude decision (keep):* Performance-coaching facet (paired with LDR-1=EX-12).

### COL-1 -> `EX-13` (collaboration)
- *DeepSeek (swap->BLOG-01):* BLOG-01 exemplifies cross-functional collaboration with a joint technical resolution.
- *Claude decision (override):* Override: COL-1 is about *disagreement* with a team member; EX-13 (authorship dispute) is the direct fit and the matrix conflict_disagreement primary. BLOG-01 is collaboration, not disagreement.

### COL-3 -> `EX-12B` (collaboration)
- *DeepSeek (swap->EX-12B):* EX-12B shows research/Infra two-team direct collaboration to a shared 5%->40% goal -- a better cross-functional-team fit than a one-sided firefighting pipeline.
- *Claude decision (accept-swap):* Accept: genuine cross-functional teamwork; frees BLOG-03 to lead COL-5's stakeholder-alignment.

### COL-5 -> `BLOG-03` (collaboration)
- *DeepSeek (swap->BLOG-03):* BLOG-03 directly demonstrates aligning cross-org stakeholders by resolving conflict and building shared infra.
- *Claude decision (accept-swap):* Accept: 'align different teams/stakeholders' is exactly BLOG-03's arc.

### COL-6 -> `EX-24` (collaboration)
- *DeepSeek (keep):* Matches the prompt: a complex technical concept (zero-sum allocation) explained to a VP.
- *Claude decision (keep):* Conclusion-first VP explanation.

### COM-1 -> `EX-19` (communication)
- *DeepSeek (keep):* Concrete analogy explains a technical confounder to a non-technical PM.
- *Claude decision (keep):* A/B confounder explained to a PM.

### COM-2 -> `EX-14` (communication)
- *DeepSeek (keep):* Persuaded leadership to abandon an agentic GenAI path based on ROI -- a clear, well-structured direction change.
- *Claude decision (keep):* Highest-link persuasion question; EX-14 is the cleanest 'change direction' story.

### COM-3 -> `EX-08` (communication)
- *DeepSeek (swap->EX-15):* EX-15 involves owning a mistake, informing affected teams (bad news), and managing it.
- *Claude decision (override):* Override: EX-08 (surfacing an unnoticed degradation + VP escalation) is a valid deliver-bad-news story and keeps diversity; EX-15 already leads OWN-1/ADP-11.

