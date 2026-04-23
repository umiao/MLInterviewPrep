# BQ Golden-Story x Trait Matrix

**Purpose.** Coverage + angle map across 10 high-signal behavioral stories and the
15 canonical themes (`behavioral_themes` table). Drives Phase-B task ordering for
the BQ-DEPTH initiative (T-P0-572 ... T-P2-585).

**How to read a cell.** Each cell names a role + facet:

- `primary` -- this is my lead pick when the interviewer asks for this theme.
- `backup` -- serviceable second choice, or ready to deploy on a follow-up probe.
- `skip` -- story does not carry the theme at a level worth pitching.

Every non-skip cell carries a **facet tag**: the angle of the story I actually
lean on for that theme. Per the BQ-DEPTH plan, facet is a *writing discipline*,
not a DB schema field -- the tag below is how I keep myself honest that the same
story is not retold the same way across three different themes. (Revisit the
schema question in ~6 months; see `.claude/tasks.db` T-P0-572 description.)

**`rewrite_status`.** Tags each story with its protocol-freshness state:

- `fresh` = just rewritten via `docs/workflow/story_rewrite_protocol.md`
  (EX-15 / EX-16 / EX-17 / EX-30, 2026-04-20/21). Safe baseline for probe-notes
  pattern calibration; facet rationale below already matches the rewritten STAR.
- `stale-high-link` = high `question_example_links` count but not rewritten; facet
  rationale below will likely need patching after the Phase-A-II rewrites land
  (EX-01 / EX-02 / EX-14 / EX-33).
- `stable` = rarely linked or already settled enough that protocol refresh is
  not the bottleneck (EX-13 / EX-20).

---

## 1. Story roster (10 rows)

| ID   | Title (short)                                          | rewrite_status     | golden? | Primary themes claimed |
|------|--------------------------------------------------------|--------------------|---------|------------------------|
| EX-01 | Search Diversity -- Intent Collapse Discovery         | stale-high-link    | yes     | data_analysis |
| EX-02 | Team Transfer -- Overcoming Manager Resistance        | stale-high-link    | no      | ownership_accountability |
| EX-13 | Authorship Dispute -- Norm Establishment              | stable             | no      | conflict_disagreement, mentoring_coaching |
| EX-14 | LLM-as-Judge -- Killing the Agentic Mandate with One Week of ROI Math | fresh (2026-04-23) | no      | scope_creep_ambiguous, ambiguity_uncertainty |
| EX-15 | Model Deprecation -- Ownership Transfer Pattern       | fresh (2026-04-20) | yes     | collaboration_teamwork, process_systems, oncall_prod_incident |
| EX-16 | Cross-DC Deployment -- Counterpart Bandwidth Line Item| fresh (2026-04-20) | yes     | code_quality_tech_debt, deadline_pressure |
| EX-17 | Senior IC Feedback -- Reliance vs. Trust              | fresh (2026-04-21) | yes     | -- (backup-heavy)  |
| EX-20 | Seller Risk Fairness -- Ethical Escalation            | stable             | no      | -- (backup-heavy)  |
| EX-30 | Hash Capability Misdesign -- Domain Depth             | fresh (2026-04-21) | yes     | technical_problem_solving, failure_setback |
| EX-33 | MoE -> Allocation Paradigm Shift                      | stale-high-link    | no      | leadership_direction, prioritization_tradeoffs |

Count: 15 primary claims across 15 themes. Some themes are backup-only for every
story (see section 3 if that happens). Each primary is defended with a facet the
other 9 stories do not also claim.

---

## 2. Theme-by-theme detail (15 tables, 10 rows each = 150 cells)

### 2.1 `technical_problem_solving` -- Diagnosing and solving complex technical problems

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | backup  | root-cause diagnosis : item-scoring in isolation creates page-level homogeneity, traced from abandon logs to model mechanics |
| EX-02 | skip    | -- org move, not a tech diagnosis |
| EX-13 | skip    | -- authorship conflict, not technical |
| EX-14 | backup  | feasibility-first : killed agentic search path via 1-week QPS/latency/cost math before committing |
| EX-15 | backup  | dependency-graph reasoning : reframed deprecation from compliance to ownership transfer after reading the actual consumer graph |
| EX-16 | backup  | incident RCA under hood : declarative artifactory wrapping compiled C++ discovered mid-rollback |
| EX-17 | skip    | -- CI failure is the trigger, not the substance |
| EX-20 | skip    | -- fairness framing, tech is secondary |
| EX-30 | primary | misdesign post-mortem : hash was mathematically correct by domain standard but wrong by consumer-surface standard -- `domain depth is not design authority` |
| EX-33 | backup  | paradigm-level diagnosis : pairwise ranking could not express allocation objectives, named the ceiling not just a defect |

### 2.2 `collaboration_teamwork` -- Working with teammates and cross-functional partners

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | skip    | -- solo Hacker Week |
| EX-02 | backup  | cross-team relocation : negotiated transfer to Final Ranking team without burning bridges at prior team |
| EX-13 | backup  | intern-protection collaboration : partnered with intern to assemble ethics-guideline evidence pack |
| EX-14 | skip    | -- solo exploration |
| EX-15 | primary | cross-team governance : 3-4 blocked teams absorbed without blame, then converted recurring zero-sum fight into an ownership-transfer option |
| EX-16 | backup  | counterpart-trust rebuild : senior IC from the destabilized team jumped into RCA with me; I treated their bandwidth as a line-item, not a favor |
| EX-17 | backup  | reviewer-ownership boundary : declined manager's offer to explain on my behalf so the senior IC's relationship with me stays intact |
| EX-20 | backup  | legal + research + PM triangulation : PayPal precedent + platform liability + recommerce narrative aligned three stakeholder groups |
| EX-30 | skip    | -- solo design; PM relationship covered by mentoring_coaching |
| EX-33 | skip    | -- paradigm reframe story; collaboration is thin |

### 2.3 `leadership_direction` -- Setting direction, tough calls, leading without authority

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | backup  | self-initiated direction : chose which problem to work on without an assignment |
| EX-02 | backup  | org-structure call : transferring teams as a leadership move, not a career move |
| EX-13 | backup  | norm-setting : first-authorship rule held for all subsequent papers |
| EX-14 | backup  | exploration-to-product pivot : talked manager into abandoning agentic search for the higher-value LLM-as-Judge path |
| EX-15 | backup  | absorb-then-reframe : the 1-week credibility buy-in came first, governance change came second |
| EX-16 | skip    | -- incident recovery, not directional |
| EX-17 | skip    | -- individual reflection story |
| EX-20 | backup  | ethical escalation as leadership : escalation goal is not to win, it is to ensure the decision is made with full information |
| EX-30 | skip    | -- too self-critical to be a leadership pitch |
| EX-33 | primary | paradigm-level reframe : staked my own track-record protection (refused carry-over wrap) so the negative result could reach org-level leadership as credible signal |

### 2.4 `process_systems` -- Designing processes, establishing standards, improving workflows

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | backup  | methodology-as-process : diversity-blending became the default vertical launch template |
| EX-02 | skip    | -- one-time org move |
| EX-13 | backup  | authorship rule : written norm, applied in subsequent publications |
| EX-14 | backup  | LLM-as-Judge evaluation harness : solo exploration became org-wide measurement infra for ads + other teams |
| EX-15 | primary | governance-pattern creation : ownership-transfer option for legacy models is still the policy, ended a recurring zero-sum fight |
| EX-16 | backup  | cross-team change policy : every cross-team change in search engine still routes through the counterpart-bandwidth line-item rule |
| EX-17 | backup  | engineer-researcher ownership boundary : explicit team practice after the incident |
| EX-20 | backup  | precision-modeling guardrail : blanket-penalty disallowed, listing-quality cross-modeling adopted |
| EX-30 | skip    | -- I explicitly did NOT drive team-level process change (per probe_qa) |
| EX-33 | backup  | team rename + carry-over semantics : three org-level follow-throughs from the honest negative result |

### 2.5 `failure_setback` -- Mistakes, setbacks, and recovery

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | skip    | -- success story, no setback hook |
| EX-02 | backup  | political setback : own-acknowledged gap (should have translated to OKR language earlier, found ranking sponsor sooner) |
| EX-13 | skip    | -- resolved in my favor, not a failure |
| EX-14 | skip    | -- no failure arc |
| EX-15 | backup  | triggered the incident myself : ran the traffic scan, still missed the pipelines -- ate the rollback personally |
| EX-16 | backup  | second-DC panic + lost 1/3 of a quarter : the honest personal cost sits in the Result |
| EX-17 | backup  | merged a broken PR : senior IC's anger was correct, I conflated manager-instruction with my own gate |
| EX-20 | skip    | -- ended in alignment, not a failure |
| EX-30 | primary | rescue-was-self-centered : my proposed fix protected my design credit but offloaded cost onto 4 teams -- only caught it when the proposal was rejected |
| EX-33 | backup  | MoE deprecated, did not ship : the negative result was the chip, but it is a real failure on the project card |

### 2.6 `prioritization_tradeoffs` -- Balancing competing priorities and tradeoffs

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | skip    | -- week-1 all-in on one problem, no tradeoff tension |
| EX-02 | skip    | -- single-axis org move |
| EX-13 | backup  | escalate-vs-absorb tradeoff : accepting gift authorship would have been easier short-term; I paid the conflict cost for a lasting norm |
| EX-14 | backup  | feasibility-first prioritization : killed high-visibility agentic path for the unglamorous but tractable LLM-as-Judge backlog |
| EX-15 | backup  | rollback-now-then-reform : absorbed the rollback first to buy the standing for the governance change |
| EX-16 | backup  | solo-vs-delay tradeoff : manager couldn't get PD quota, chose solo-solo instead of waiting |
| EX-17 | skip    | -- tradeoff was not prioritization; it was identity (reliance vs. trust) |
| EX-20 | backup  | false-positive vs. fraud-prevention : named the tradeoff as inherent to compliance, not a bug |
| EX-30 | skip    | -- the tradeoff ("fix with more engineering vs. rebuild") got short-circuited by the rejection |
| EX-33 | primary | carry-over vs. paradigm signal : I gave up personal track-record protection so the negative result would reach the org as paradigm evidence, not a wrapped failure |

### 2.7 `ownership_accountability` -- Taking responsibility and delivering end-to-end

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | backup  | self-assigned -> end-to-end prototype : data pipeline, blending algo, experiment framework in one week |
| EX-02 | primary | ownership-follows-person : transferred teams to own the problem rather than accept structural constraint -- "the problem follows the person" |
| EX-13 | backup  | norm-owner : carried the authorship fight to management mediation |
| EX-14 | skip    | -- closer to ambiguity/scope than ownership |
| EX-15 | backup  | on-call-ownership : picked up a long-deferred ticket and owned the fallout |
| EX-16 | backup  | solo end-to-end incident ownership : manager couldn't get PD quota, I still owned the 3-DC rollout + RCA |
| EX-17 | backup  | declined the air-cover : "If she explained it, the story would be about her, not me" |
| EX-20 | backup  | escalation-ownership : after design-review rejection, kept driving up the chain until legal got involved |
| EX-30 | backup  | orphan-capability ownership : accepted responsibility for the leak, did not frame as "should have been integrated earlier by someone else" |
| EX-33 | backup  | paradigm-level ownership : refused the carry-over wrap so the paradigm signal would be legible |

### 2.8 `data_analysis` -- Using data and metrics to drive decisions

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | primary | invisible-to-standard-metrics : abandon-log slice exposed intent collapse the dashboard masked, then purchase-data proof the blending works |
| EX-02 | skip    | -- relies on EX-01's numbers, no new analysis |
| EX-13 | skip    | -- norm story |
| EX-14 | backup  | ROI-math killed the hype path : QPS, latency, cost numbers disqualified real-time agentic search |
| EX-15 | skip    | -- consumer-graph reading, not data-driven in the metric sense |
| EX-16 | backup  | RCA-by-evidence : traced second-DC panic back to the compiled-C++ layer through log + load signal |
| EX-17 | skip    | -- interpersonal story |
| EX-20 | backup  | industry-case evidence : PayPal + platform liability case research backed the fairness argument |
| EX-30 | skip    | -- post-rescue analytics showed confounding later, but story pitches design, not analysis |
| EX-33 | backup  | offline-win + online-flat read : the explicit signal that pairwise distributed ranking had hit a ceiling |

### 2.9 `conflict_disagreement` -- Disagreements, pushback, interpersonal tension

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | skip    | -- no direct opposition |
| EX-02 | backup  | manager-disagreement : reframed to the manager's OKR language, then exited when reframe failed |
| EX-13 | primary | authorship-conflict : multiple private conversations + escalation to joint-manager mediation, holding the contribution-based principle |
| EX-14 | backup  | leadership-pushback : talked leadership out of its stated "agentic search" mandate into a pragmatic pivot |
| EX-15 | backup  | cross-team-blame-avoidance : resisted the "who followed the right process" frame, absorbed the rollback without ceding the governance argument |
| EX-16 | skip    | -- destabilized a team but there was no dispute, only recovery |
| EX-17 | backup  | senior-IC-feedback : refused my manager's air-cover so the senior IC's trust could reset directly with me |
| EX-20 | backup  | principal-researcher opposition : design-review opposition from a senior PI, escalated without losing the relationship |
| EX-30 | backup  | pushed-back-and-lost : proposal-rejection was the conflict; I initially read it as unreasonable before reframing to accept the cost math |
| EX-33 | skip    | -- paradigm disagreement lived at org-structure level, not between named people |

### 2.10 `deadline_pressure` -- Tight deadlines and high-stakes delivery

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | backup  | one-week Hacker Week : end-to-end prototype, data pipeline + algo + experiment framework |
| EX-02 | skip    | -- no acute deadline |
| EX-13 | skip    | -- sustained conflict, not deadline |
| EX-14 | skip    | -- 1-week feasibility was a self-imposed timebox, not external pressure |
| EX-15 | backup  | within-a-week recovery : pipelines restored inside a week to buy standing for the governance change |
| EX-16 | primary | same-day DC recovery : minutes-window admin approval, same-day pipeline restoration, clean crisp description in channel |
| EX-17 | backup  | mid-launch only-merge-rights : teammate went on unexpected leave, I was the single gating resource -- produced both the urgency and the later trust-reset story |
| EX-20 | skip    | -- sustained investigation, not deadline |
| EX-30 | skip    | -- no time pressure dominant |
| EX-33 | skip    | -- quarter-level, not deadline-shaped |

### 2.11 `mentoring_coaching` -- Developing juniors, mentoring interns, coaching peers

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | skip    | -- solo |
| EX-02 | skip    | -- self-directed |
| EX-13 | primary | intern-protection : refused gift authorship not to win credit but to keep the intern's substantial contribution unambiguous and to set the norm for future juniors |
| EX-14 | skip    | -- individual contribution |
| EX-15 | skip    | -- peer governance, not mentoring |
| EX-16 | skip    | -- peer-level incident |
| EX-17 | backup  | reverse-mentoring : received hard feedback from senior IC, rebuilt reviewer trust in 2 months -- I was the one being coached |
| EX-20 | skip    | -- stakeholder-facing, not coaching |
| EX-30 | backup  | PM-relationship coaching through recovery : high-velocity PM loop survived my design failure because I owned the cost instead of deflecting |
| EX-33 | skip    | -- paradigm-level, individual contribution |

### 2.12 `scope_creep_ambiguous` -- Scope changes, rescoping, ambiguous requirements

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | backup  | ambiguous-assignment : no one assigned Hacker Week scope; I defined the problem myself |
| EX-02 | backup  | charter-mismatch scope : the project scope contradicted the team's OKRs -- a scope that could not be fixed by scoping, only by relocation |
| EX-13 | skip    | -- scope is well-defined |
| EX-14 | primary | vague-AI-mandate : "upgrade to GenAI" with no requirements, no precedent, no integration path -- I scoped it through feasibility, not brainstorming |
| EX-15 | skip    | -- scope was clear; execution was the tension |
| EX-16 | skip    | -- scope was clear (3-DC rollout) |
| EX-17 | backup  | inherited-scope : picked up a remote branch mid-launch with a half-visible context -- policy gap was the real scope leak |
| EX-20 | skip    | -- well-scoped from the start |
| EX-30 | backup  | orphan-capability scope : hash was shipped inside diversity team's scope but its real consumer surface (DS launch analysis) was outside the scope I had defined |
| EX-33 | skip    | -- paradigm scope is leadership_direction territory |

### 2.13 `code_quality_tech_debt` -- Balancing code quality, maintainability, tech debt

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | skip    | -- prototype code, no debt conversation |
| EX-02 | skip    | -- org story |
| EX-13 | skip    | -- norm story |
| EX-14 | backup  | infra-integration debt : LLM could not plug into indexing pipeline -- the debt is architectural, not codebase |
| EX-15 | backup  | legacy-model debt : deprecation target was real tech debt; the novelty was letting consumers fork and own it |
| EX-16 | primary | half-done migration as hidden debt : declarative artifactory wrapping compiled C++ -- the hazard lived in the fact that the migration was partial |
| EX-17 | skip    | -- CI failure is symptom, not debt |
| EX-20 | skip    | -- model behavior, not debt |
| EX-30 | backup  | orphan capability as debt : unintegrated foundational primitive is tech debt in a new shape |
| EX-33 | skip    | -- paradigm debt, not code debt |

### 2.14 `ambiguity_uncertainty` -- Operating with incomplete information, unclear goals

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | backup  | problem-framing before stakeholder persuasion : the intent-collapse framing had to exist before anyone would sponsor the work |
| EX-02 | skip    | -- once scoped, path was clear |
| EX-13 | backup  | ambiguous-norm : authorship norm was ill-defined; the conflict forced the definition |
| EX-14 | primary | no-precedent GenAI mandate : leadership said "upgrade", no requirements, no LLM precedent in our stack -- feasibility study replaced requirements |
| EX-15 | skip    | -- well-defined problem |
| EX-16 | skip    | -- well-defined incident |
| EX-17 | backup  | identity-level ambiguity : "being relied on" vs. "being trusted" was the ambiguity; the resolution reshaped my default model |
| EX-20 | backup  | fairness-vs-precision ambiguity : no policy existed on seller fairness at the time; I had to build the case from outside the company |
| EX-30 | skip    | -- the ambiguity was mine (I didn't see the consumer surface); story pitches as failure_setback |
| EX-33 | backup  | paradigm-uncertainty : MoE as hedge was hedging; I refused the hedge, staked the honest read |

### 2.15 `oncall_prod_incident` -- On-call rotations, outages, production incident response

| Story | Role    | Facet : one-line rationale |
|-------|---------|----------------------------|
| EX-01 | skip    | -- research project |
| EX-02 | skip    | -- org story |
| EX-13 | skip    | -- norm story |
| EX-14 | skip    | -- exploration, no incident |
| EX-15 | primary | on-call-caused incident : I was the on-call; I ran the scan, I missed the pipelines, I absorbed the rollback and converted it into governance |
| EX-16 | backup  | cross-DC incident : second-DC panic triggered minutes-window rollback, admin approval, and RCA with senior IC from destabilized team |
| EX-17 | backup  | CI-level incident : merged PR broke CI, senior IC refused to continue reviewing -- not a prod outage, but an on-call-adjacent reviewer-contract incident |
| EX-20 | skip    | -- model-behavior story, not incident |
| EX-30 | skip    | -- DS launch-analysis block is adjacent, not an incident response |
| EX-33 | skip    | -- paradigm work, not incident |

---

## 3. Compact matrix (quick-scan summary)

Legend: `P` = primary, `b` = backup, `.` = skip.

Theme column order (display_order 1..15):
1. tech_problem_solving, 2. collab_teamwork, 3. leadership_direction,
4. process_systems, 5. failure_setback, 6. prioritization_tradeoffs,
7. ownership_accountability, 8. data_analysis, 9. conflict_disagreement,
10. deadline_pressure, 11. mentoring_coaching, 12. scope_creep_ambiguous,
13. code_quality_tech_debt, 14. ambiguity_uncertainty, 15. oncall_prod_incident

| Story | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|-------|---|---|---|---|---|---|---|---|---|----|----|----|----|----|----|
| EX-01 | b | . | b | b | . | . | b | P | . | b  | .  | b  | .  | b  | .  |
| EX-02 | . | b | b | . | b | . | P | . | b | .  | .  | b  | .  | .  | .  |
| EX-13 | . | b | b | b | . | b | b | . | P | .  | P  | .  | .  | b  | .  |
| EX-14 | b | . | b | b | . | b | . | b | b | .  | .  | P  | b  | P  | .  |
| EX-15 | b | P | b | P | b | b | b | . | b | b  | .  | .  | b  | .  | P  |
| EX-16 | b | b | . | b | b | b | b | b | . | P  | .  | .  | P  | .  | b  |
| EX-17 | . | b | . | b | b | . | b | . | b | b  | b  | b  | .  | b  | b  |
| EX-20 | . | b | b | b | . | b | b | b | b | .  | .  | .  | .  | b  | .  |
| EX-30 | P | . | . | . | P | . | b | . | b | .  | b  | b  | b  | .  | .  |
| EX-33 | b | . | P | b | b | P | b | b | . | .  | .  | .  | .  | b  | .  |

Primary count per theme (should be 1-2 each; `0` is a coverage gap):

| Theme | Primary count | Primary stories |
|-------|---------------|-----------------|
| 1. technical_problem_solving  | 1 | EX-30 |
| 2. collaboration_teamwork     | 1 | EX-15 |
| 3. leadership_direction       | 1 | EX-33 |
| 4. process_systems            | 1 | EX-15 |
| 5. failure_setback            | 1 | EX-30 |
| 6. prioritization_tradeoffs   | 1 | EX-33 |
| 7. ownership_accountability   | 1 | EX-02 |
| 8. data_analysis              | 1 | EX-01 |
| 9. conflict_disagreement      | 1 | EX-13 |
| 10. deadline_pressure         | 1 | EX-16 |
| 11. mentoring_coaching        | 1 | EX-13 |
| 12. scope_creep_ambiguous     | 1 | EX-14 |
| 13. code_quality_tech_debt    | 1 | EX-16 |
| 14. ambiguity_uncertainty     | 1 | EX-14 |
| 15. oncall_prod_incident      | 1 | EX-15 |

No coverage gaps. EX-17 and EX-20 carry no primary claims -- both are backup-heavy
by design (EX-17 is a reflection piece; EX-20 is an escalation piece). That is
fine as long as downstream question-link mapping does not treat them as lead
anchors for any theme.

---

## 4. Free lunch -- Phase-B probe-notes pattern calibration targets

**EX-15 / EX-16 / EX-17 / EX-30** were rewritten through
`docs/workflow/story_rewrite_protocol.md` during 2026-04-20/21. Their STAR
fields, titles, KEY-FACTS pills, principle tags, and frontend pre-renders are
all in a consistent state right now -- *this is the window where probe_notes can
be authored against stable source content and will not need re-drafting when
upstream stories shift.*

Phase-B plan (T-P1-580) uses these four stories to calibrate the 4-field
probe_notes schema (`core_signal` / `what_good_looks_like` / `what_L5_adds` /
`common_failure_modes`). Pick the top-Q linked probe per story:

- **EX-15** -- governance-pattern probe (ownership-transfer option facet).
- **EX-16** -- counterpart-bandwidth probe (line-item-not-favor facet).
- **EX-17** -- reliance-vs-trust probe (declined-air-cover facet).
- **EX-30** -- domain-depth probe (design-authority facet).

Notes calibrated on these four should encode the *pattern* (field shape, voice,
length) -- not the story-specific content -- so bulk authoring in T-P1-582 can
proceed without re-calibration drift.

**Link to planning:** `.claude/tasks.db` T-P1-579 adds the schema, T-P1-580
does the 4 calibration samples, T-P1-582 does the bulk.

---

## 5. Stale-high-link -- protocol-refresh targets

**EX-01 / EX-02 / EX-14 / EX-33** have high `question_example_links` count but
have NOT been refreshed through the current `story_rewrite_protocol.md`. Their
facet rationales in section 2 are written against the *current* STAR content in
`bq_improved_stories.md` / `behavioral_examples`, but downstream propagation
surfaces (KEY-FACTS pills, principle tags, question relevance notes,
`cn_elevator_pitch`, frontend pre-renders) may tell a slightly older version of
the same story. Expect rationale-level patches after each rewrite lands.

Phase-A-II plan (T-P0-575 ... T-P0-578) refreshes these in this order:

- **T-P0-575 / EX-01** (L complexity) -- highest link volume, largest
  propagation surface; the intent-collapse vocabulary is load-bearing for
  data_analysis primary and ambiguity_uncertainty backup.
- **T-P0-576 / EX-02** (M) -- depends on EX-01's vocabulary; ownership_
  accountability primary hinges on `the problem follows the person` framing.
- **T-P0-577 / EX-14** (M) -- scope_creep_ambiguous and ambiguity_uncertainty
  primaries both live here; most fragile if rewrite shifts the vocabulary.
- **T-P0-578 / EX-33** (M) -- leadership_direction and
  prioritization_tradeoffs primaries; `start-test vs. test-and-launch` framing
  must survive the rewrite.

**Gating.** T-P0-574 (link pruning) lands before any rewrite so rationale-level
patches don't have to touch pruned links. T-P1-579 (schema uplift) only starts
after all four rewrites land.

**Post-rewrite check.** Re-read section 2 cells mentioning EX-01/02/14/33 and
verify the facet rationale still matches the rewritten STAR. Patch in place if
not.

---

## 6. Facet vocabulary (what `angle_label` would be -- if it existed)

Per the BQ-DEPTH plan, `angle_label` is deliberately NOT a DB field. This
section captures the facet vocabulary as writing discipline so probe_notes
authors (T-P1-580 / T-P1-582) can stay honest that they are not retelling the
same story three different ways.

Facets used above (by story):

- **EX-01**: intent-collapse framing, abandon-log evidence, item-vs-page
  scoring, self-initiated direction.
- **EX-02**: OKR-language translation, problem-follows-person, proactive
  relocation.
- **EX-13**: authorship-as-contribution (not as gift), intern protection,
  norm-by-mediation.
- **EX-14**: feasibility-first, agentic-search-killed, LLM-as-Judge pivot,
  no-precedent scoping.
- **EX-15**: ownership-transfer option, absorb-then-reframe, consumer-graph
  reading, governance-pattern.
- **EX-16**: counterpart-bandwidth-as-line-item, same-day recovery, half-done
  migration, compiled-C++-under-declarative.
- **EX-17**: reliance-vs-trust, declined air-cover, reviewer-ownership
  boundary, merged-a-broken-PR.
- **EX-20**: escalation-not-winning, false-positive-vs-fraud tradeoff,
  legal+research+PM triangulation.
- **EX-30**: domain-depth-is-not-design-authority, orphan-capability leak,
  rescue-was-self-centered.
- **EX-33**: start-test-not-test-and-launch, refused-carry-over wrap,
  paradigm-level ownership, honest-negative-result.

When writing probe_notes, name the facet in `core_signal` and verify the chosen
facet is not already the lead in another theme for the same story. Revisit
formalizing this as a DB field in ~6 months if probe-notes drift detection
(T-P2-585) shows repeated facet collisions.

---

## 7. Change log

| Date       | What                                                         | By             |
|------------|--------------------------------------------------------------|----------------|
| 2026-04-21 | Initial matrix created (T-P0-572 / BQ-DEPTH-01).             | autonomous run |
