"""One-off: queue T-P1-357 — populate EX-30 with Hash Misdesign, create EX-33 for MoE Allocation.

The task description below is the full spec the autonomous runner will execute.
STAR fields are intentionally English-only (per user directive 2026-04-11); the
source bank at <staging>/bq_story_bank_moe_allocation.md
has Chinese bridging commentary that does NOT enter the DB.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_DB = ROOT / ".claude" / "hooks" / "task_db.py"


DESC = """\
# Behavioral: populate EX-30 with Hash Misdesign + create EX-33 for MoE->Allocation paradigm shift

## Context
Source material: `<staging>/bq_story_bank_moe_allocation.md` (user's local staging area)
The user wrote a comprehensive story bank covering one raw set of events
(MoE failure -> Allocation paradigm shift) in four framings (A/B/C/D) plus
a distinct pure-failure story (Version E: Hash Capability Misdesign).
STAR fields below are pre-drafted, user-reviewed, and pure English.
Bridging/analysis commentary in the source doc stays in Chinese and does NOT
enter the DB row.

## Part 1 - Populate EX-30 (currently [NEEDS-INPUT] placeholder from T-P0-351)

### Field writes
- title: `Hash Capability Misdesign - Expert Frame Blind Spot`
  (strip the `[NEEDS-INPUT]` prefix)
- source_project: `eBay search - diversity/hash features`
- principle_tags: `["failure", "learning", "expert_blind_spot", "cross_functional", "humility", "consulted_prior_art"]`
- analogy: `Shipping a hash function turned out to be shipping an analytical artifact - I optimized the math-object standard and ignored who the real consumer was.`
- tech_terms: `["Hash function", "Prime multiplication", "Entropy metric", "Diversity metric", "SQL/Hive", "Stable ID", "Analytical pipeline"]`

### Situation
At eBay search I was in an unusually high-momentum collaboration with a PM,
shipping a series of diversity-related features and metrics with almost no
friction. I personally had a feeling of invincibility - needs identified,
design fast, ship faster, PM driving launch, and the loop turned fast enough
that I stopped looking for blockers. I was the deep-expertise IC on hash and
diversity inside our group.

### Task
PM and I identified a new capability need: compute facet hash and entropy-based
diversity metric on the real-time page-rendering path, as the foundation for a
new round of diversity experiments. As the hash-domain IC, I owned the design.

### Action
**(1) Wrong first decision - elegant but single-framed design.**
I designed a math-elegant real-time hash: large-prime multiplication plus
high-bit extraction. Uniformity was good, performance was high, extension was
clean. I shipped it as an optional feature. My team's internal testing all
passed and I was confident in the quality. Looking back, the root cause was not
technical - I evaluated "good" by the hash-as-math-object standard (quality,
uniformity, performance), and I never asked a more basic question: who outside
my team will consume this, and what will they use it for.

**(2) Failure surfaces.**
Weeks after launch, confusion began escalating back from two or three
downstream teams - mostly data science and analytics/product. They were stuck
preparing launch analysis. My hash was implicit at the SQL/Hive layer with no
stable identity, so DS could not track "which bucket corresponds to which
facet" in their analytical queries, and they could not build explainable
launch-decision support on top of it. The moment that escalation landed back on
my desk was when this failure became real for me. I realized I had not shipped
a hash function - I had shipped an analytical artifact, and I had designed it
with zero analytical-consumer perspective.

**(3) Wrong second decision - sunk-cost rescue attempt.**
My first instinct was to propose a "correct" fix: modify search lower infra so
hash became a first-class operator, plus matching changes to the data pipeline,
the A/B test platform, and Hive SQL, so my elegant hash could be properly
tracked end-to-end. I quickly realized this was a cross-four-team,
multi-quarter infra change. The proposal did not go through. Looking back that
is the right outcome, because it was using larger infra investment to rescue
a framing error rather than admitting the framing itself was wrong.

**(4) Right third decision - consult and adopt prior art.**
I went to the indexing team and asked how their analytics pipeline adaptively
absorbs new features and metrics. The answer was humbling: they already had a
mature practice I had no idea existed. I followed their work. The final
solution was an explicit cache of diversity aspect plus stable ID assignment.
By my hash-expert standard this was "worse" - lower efficiency, no elegant
scaling, zero math beauty. By the cross-functional standard it was "better",
because it served what DS actually needed: traceable, explainable, auditable.

### Result
Downstream confusion was resolved and launch analysis could proceed. But I
have to be honest: this is not a happy ending. Two or three downstream teams
had several weeks of analysis time burned by my design choice. My proposed
infra rescue was rejected. The fix was not something I cleverly invented - it
came from asking someone else who had the answer the whole time. The
reputational cost was real: as the hash-domain expert, I shipped something in
my own domain that confused the downstream consumers of my own work.

### risk_statement
Cost was externalized to two or three downstream DS/product teams whose
analysis time was burned. Personal reputational cost inside my own expert
domain. The failure was unambiguous: no ship of the original design, proposed
rescue rejected, final fix sourced from prior art I had simply never asked
about. Use this story for failure-type questions; it does not have a
success-tail to soften it.

### evidence_quotes (JSON array of strings)
- "I had a feeling of invincibility - the collaboration loop was so smooth I stopped looking for blockers."
- "The escalation landed on my desk and I realized I had not shipped a hash function, I had shipped an analytical artifact."
- "Expertise had taught me to design first. I should have asked first."

### Link changes for EX-30
- PRESERVE existing 5 links from T-P0-351: OWN-1, OWN-8, ADP-5, ADP-18, EXE-2
  (UPDATE each row's relevance_note from `[PLACEHOLDER] ...` to a real per-link
  semantic note >= 30 chars; DO NOT delete or recreate the rows)
- ADD 1 new link: ADP-15 "What's the biggest lesson you've learned from a
  failed project?" - perfect fit. Relevance note: "The cleanest unambiguous
  failure in my story pool; no success-tail, clear mental-model lesson
  (expert frame blind spot)."
- All 6 links total after this task.

### Theme tags for EX-30 (via example_theme_tags table from T-P1-353)
- `failure_setback` (primary)
- `mentoring_coaching` (learning-from-indexing-team angle)
- `scope_creep_ambiguous` (implicit vs explicit identity framing)
- `conflict_disagreement` (cross-team friction when the escalation came back)

## Part 2 - Create EX-33 (new row) for MoE -> Allocation Paradigm Shift

### Rationale
Per the user's own doc warning (Version D section): this is a success story
with a failure chapter, NOT suitable for failure-type questions. Use it for
"drove organizational change", "influence without authority", "calculated
risk", "challenged convention". Version A (drove org change) is the primary
STAR shape. Version B (influence) and Version C (calculated risk) are
alternate framings of the same raw events - stash them in evidence_quotes
rather than creating separate rows EX-34/EX-35, which would double-count
the event in theme frequency.

### Field writes
- example_id: `EX-33` (next in sequence after EX-32)
- title: `MoE -> Allocation Paradigm Shift - Org-Level Reframe via Honest Negative Result`
- source_project: `eBay search - ranking to allocation paradigm`
- principle_tags: `["organizational_change", "long_term_bet", "influence_without_authority", "calculated_risk", "paradigm_shift", "evidence_based_advocacy", "coalition_building"]`
- analogy: `A wrapped success cannot convince anyone. A credibly honest negative result was the last chip that flipped the org's paradigm.`
- tech_terms: `["MoE (Mixture of Experts)", "Neural ranking", "Pairwise ranking", "Whole-page optimization", "Reranking", "Allocation policy", "MRR", "Expert routing", "Item-level ranker"]`

### Situation
In the eBay search org, the dominant paradigm was pairwise distributed
ranking - each item scored independently and then sorted. The industry had
moved toward whole-page optimization and reranking, and several senior ICs,
my manager, and I had been calling out this gap for several quarters. The
org agreed with the direction at the abstract level, but nobody had a concrete
path. It was a shared-vision, no-path situation.

### Task
Leadership assigned me ownership of a high-visibility project: migrate search
from boosting to neural ranking plus MoE, consuming about 80 GPU nodes, which
was nearly all the org-wide headroom, shared with the cross-org AI intake. On
the surface this was a ranker upgrade. In my head it was also a critical
empirical test of the ranker-centric paradigm itself: if even the most
sophisticated ranker architecture could not solve the diversity and discovery
problems we were seeing, that would be the strongest possible evidence for
reframing the paradigm.

### Action
**(1) Framing decision at project launch - "start test", not "test and launch".**
Against org convention, my manager and I labeled the project scope as
"start test" rather than "test and launch". Convention would have allowed us
to wrap a failure as "carry over to next quarter", which protects the IC's
track record but destroys the credibility of any paradigm-level signal the
project produces. I gave up that protection on purpose - a wrapped success
cannot convince anyone, and if I wanted this project to function as a
paradigm test, the result had to be credible either way.

**(2) Moment of realization mid-execution.**
While adding a new expert to handle abandonment and exploration, I noticed
that it and the conversion expert were frequently co-activated but contributed
in opposite directions. I first attributed this to under-training and added
more training rounds, but the behavior stayed. Then I realized it was
structural - these two goal sets were orthogonal to conversion in a way that
a single item-level ranker could not reconcile. More disturbing was a second
finding: by our org's launch criteria (MRR up, revenue neutral) this expert
was actually launchable, yet users were not being served better and homogeneity
had gotten worse. That gap made me first question MRR itself as a
self-fulfilling prophecy - the ranker training objective and the metric shared
the same assumptions, so a "win" on the metric did not independently validate
user outcome.

**(3) Converting failure into a reframe proposal.**
I wrote a detailed proposal arguing three things: (a) the ranker architecture
cannot handle goals that are structurally orthogonal to conversion, such as
diversity, abandonment, and exploration; (b) the org's metric system was
masking this blind spot; (c) the right direction was to make the business
tradeoff explicit as an allocation policy, letting the model unleash its power
inside a defined policy frame, instead of asking the ranker to carry both
optimization and tradeoff on the same head. The proposal was accepted because
the several-quarter pre-work from me, the senior ICs, and my manager had
prepared the org psychologically. MoE's negative result was the last
undeniable empirical chip.

### Result
The MoE direction was officially deprecated and did not ship. But three
org-level outcomes followed. First, the team was renamed from "ranking
modeling" to "policy learning" and eventually to the "Allocation team",
reflecting the full paradigm shift. Second, allocation policy became the
team's new main line of work. Third, that new direction later shipped over
200M in annualized GMB. The outcome I care about most is not the GMB number:
it is that the org's default planning question shifted from "how do we train
a better ranker" to "what user problem are we solving and is a ranker the
right tool for it". That mental-model change is irreversible.

### risk_statement
I staked my personal track record as collateral when I refused the carry-over
convention. If MoE had been wrapped, the failure would have been invisible but
so would the paradigm lesson. Real costs were personal (no carry-over
protection for my record), team (mindset adjustment away from "we are launching
something"), and political (signaling to leadership that a top-down strategic
project might not work). DO NOT use this story for pure-failure questions -
the 200M+ tail will make the interviewer feel the story is a disguised success,
which backfires. For failure questions use EX-30 instead.

### evidence_quotes (JSON array of strings)
- "A wrapped success cannot convince anyone. A credibly honest negative result was the last undeniable empirical chip."
- "I used 'start test' framing instead of 'test and launch', which gave up my carry-over protection on purpose."
- "MRR was a self-fulfilling prophecy because the ranker's training objective and the evaluation metric shared the same assumptions."
- "Alt framing B (Influence Without Authority): coalition + risk-taking + opponents-language + evidence-based advocacy over several quarters."
- "Alt framing C (Calculated Risk): short-term personal cost traded for long-term organizational value; used my track record as collateral for a paradigm bet."

### Link list for EX-33 (12 new rows in question_example_links)
All with relevance_note >= 30 chars explaining version match:

| question_id | version | why |
|---|---|---|
| OWN-6  | C | Bold risk at work - start-test framing staked personal record on a paradigm bet |
| PS-6   | C | Calculated risk - short-term personal cost traded for long-term org value |
| OWN-10 | A | Long-term impact - multi-quarter paradigm push across the org |
| IMP-10 | A | Long-term impact example - full Allocation policy 200M+ GMB arc |
| IMP-9  | A | Short-term vs long-term tradeoff - forgoing carry-over protection for org value |
| INN-6  | A | New process/strategy with major improvement - allocation policy proposal |
| INN-8  | A | Questioned a traditional approach and proposed something new - ranker -> allocation |
| COM-2  | B | Persuade others to change direction - core influence-without-authority match |
| COL-5  | B | Align teams/stakeholders on shared goal - coalition building over several quarters |
| IMP-4  | A | Improved a process/system adding significant value - 200M GMB + mental-model shift |
| INN-1  | A | Identified an opportunity for improvement - paradigm gap identification |
| OWN-9  | A | Innovate without all the information - empirical test as the way forward under uncertainty |

### Theme tags for EX-33 (via example_theme_tags)
- `leadership_direction` (primary)
- `ownership_accountability`
- `prioritization_tradeoffs`
- `technical_problem_solving`
- `failure_setback` (partial - the MoE chapter only)
- `ambiguity_uncertainty`

## Scenario matrix
| Condition | Expected |
|---|---|
| EX-30 row exists as placeholder | UPDATE in place, do not INSERT |
| EX-33 row does not exist | INSERT with example_id='EX-33' |
| EX-30 title no longer starts with [NEEDS-INPUT] | Frontend needs-input badge disappears; STAR renders real content |
| EX-30 existing 5 links | PRESERVED, relevance_note updated from [PLACEHOLDER] prefix to real semantic note |
| ADP-15 added to EX-30 | New row, relevance_note >= 30 chars |
| EX-33 gets 12 new links | All from the table above; each relevance_note >= 30 chars |
| Re-run script | Idempotent - UPDATEs are idempotent; INSERTs gated by existence check |
| example_theme_tags updated | EX-30 and EX-33 both tagged with theme rows per the lists above |

## Acceptance criteria
- [ ] `scripts/_populate_hash_and_moe_examples.py` (new) performs all the above changes in one transaction and is idempotent
- [ ] EX-30 row: title no longer starts with `[NEEDS-INPUT]`; situation/task/action/result all populated with the English STAR above; principle_tags/analogy/tech_terms updated; evidence_quotes populated
- [ ] EX-30 still has the original 5 question links from T-P0-351 PLUS 1 new ADP-15 link = 6 total
- [ ] Every EX-30 link row has a real relevance_note (no more `[PLACEHOLDER]` prefix)
- [ ] EX-33 row inserted with example_id='EX-33', all STAR fields populated, principle_tags/analogy/tech_terms/evidence_quotes/risk_statement set
- [ ] EX-33 has exactly 12 question_example_links rows per the table above
- [ ] example_theme_tags contains the EX-30 and EX-33 theme assignments from the lists above (use the table populated in T-P1-353)
- [ ] Consumer-path verification (per CLAUDE.md):
  - `curl /api/behavioral/examples/by-example-id/EX-30` returns populated STAR, no [NEEDS-INPUT] in title, 6 linked_questions
  - `curl /api/behavioral/examples/by-example-id/EX-33` returns populated STAR, 12 linked_questions
  - `curl /api/behavioral/questions?theme=failure_setback` includes both EX-30's linked Qs and EX-33's Qs that are in that theme
- [ ] `npm run build` passes (tsc -b + vite build)
- [ ] Frontend Needs-Input badge is absent on EX-30 card and drawer (visual check via dev server)

## Manual smoke test
1. `scripts/dev.py` -> wait for "Application startup complete"
2. Navigate to BehavioralQuestions -> click ADP-15 ("biggest lesson from a failed project")
3. Linked examples list includes BOTH EX-30 (real Hash Misdesign content, no [NEEDS-INPUT] badge) AND EX-32 (still placeholder)
4. Click EX-30 -> drawer opens with populated STAR, no (missing - pending) fallback, real analogy and tech_terms
5. Navigate to OWN-6 ("took a bold risk") -> linked examples include EX-33 with Version C framing evidence quotes visible
6. Theme filter sidebar: select `failure_setback` -> both EX-30-linked and EX-33-linked Qs visible. Select `leadership_direction` -> EX-33-linked Qs visible.

## Consumer audit
No new field added, but relevance_note prefix changes may affect any UI rendering that filtered by `[PLACEHOLDER]` marker. Grep for `[PLACEHOLDER]` across `src/frontend/` and confirm nothing depends on that prefix remaining.

## Dependencies
T-P1-353 (completed) - theme_tags tables must exist.
T-P0-351 (completed) - EX-30 placeholder row and its 5 links must exist.
"""


def main() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(TASK_DB),
            "add",
            "--title",
            "Behavioral: populate EX-30 with Hash Misdesign + create EX-33 for MoE->Allocation",
            "--priority",
            "P1",
            "--complexity",
            "M",
            "--description",
            DESC,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    result.check_returncode()


if __name__ == "__main__":
    main()
