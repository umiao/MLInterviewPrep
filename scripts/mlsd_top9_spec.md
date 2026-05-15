# Meta MLSD Top-9 口播稿 Spec (autorun shared brief)

**Batch context**: cd96 Meta MLSD playbook (45min framework) references a 13-question family in cd94 Family Taxonomy. As of 2026-05-14, 4 of 13 have full `sd://meta-*-golden` walkthroughs (Reels Q13, Top-3 Comments Q1, Weapon Ads Q7, Friend Rec Q3). This batch adds **口播稿 only** rows for the remaining 9 -- 2 anchors (Q9 FB News Feed + Q8 Yelp) inserted manually as calibration; 7 remaining go through autorun inheriting the locked template below.

This row owns only the **solution shape** -- methodology (timing skeleton, vocab YES/NO, 8 rhythm meta-rules, E4/E5 boundary) lives in `cd://96` and must NOT be re-stated.

---

## Template (locked from anchors, N1 = `meta-fb-newsfeed-golden` id=45, N1.5 = `meta-yelp-restaurant-golden` id=46)

Two columns populated per row in `system_designs`:

### `overview` column (~3-4k chars)

#### §1 Problem Definition
- **Objective**: 1-2 sentences. THE optimization target as-it-is for THIS problem (not generic "personalize feed"). Name the actual product objective when it differs from naive engagement (e.g., MSI for FB News Feed, calibrated probability for Ads, conversion-quality matching for Yelp, bilateral matching for PYMK).
- **Input per request**: what the model sees. user_id + context features + which retrieval sources contribute. Be concrete.
- **Output**: what the model emits + to whom downstream (auction / ranker / gating / capacity / notification). The "to whom" is critical -- it determines calibration target.
- **Scale anchor**: DAU + candidate count per request + latency budget split. Plus this line at the end: "Methodology lives in `cd://96`; this row owns only the solution shape."

#### §2 Twists (dominant + interacting constraints; 3-5 total, NOT fixed at 4)
- Lead with **`Twist 1 -- DOMINANT -- <name>`**. This is the reframe that drives all downstream decisions.
- Each additional twist: `Twist N -- <name>` -- generic default it replaces -- unique property of THIS problem -- design implication.
- At least 2 twists name **interactions** with other twists in a "Interacts with #X (...)" clause. Twists are coupled, not orthogonal.
- A weak problem (Q8 Yelp / Q11 Spotify) may only have 3 twists; do NOT pad to 4 with filler. A rich problem (Q9 News Feed / Q4 Ads) may have 4-5.

### `verbal_outline` column (~6-8k chars)

#### §3 Twist-threaded solving (the load-bearing structural feature)
Walks the 45-min skeleton in 6 sections (some problems may merge or skip):
- Framing 0-3 min
- Data / Label 3-12 min
- Retrieval 12-18 / 20 min
- Ranking 18-28 / 30 min
- Bias OR Calibration 28-32 min (may skip if not central)
- Eval 32-38 / 35-40 min
- Wrap 38-45 / 40-45 min

**Every section opens with** `**(driven by Twist N · interacts with M)**` -- this is the structural feature making twist-mapping load-bearing. Reader can trace twist → decision in either direction.

Each section includes at least one **trade-off line** in the form: "**I pick** X over Y **because** Z; **costs**: W; **switches to** V only if ...".

#### §4 Strong Moment slot map (light, no verbatim cue lines)
4 bullets:
- **SM #1 (3-5 min)**: Twist N reframe -- 1 line
- **SM #2 (12-15 min)**: Twist M / interaction -- 1 line
- **SM #3 (25-28 min)**: Twist K production scar / calibration -- 1 line
- **SM #4 (35-40 min)**: zoom-out + top 3 risks anchor

Verbatim 60-word hook phrases are **deferred** to a Tier-4 polish batch. Light slot+content map only here.

#### §5 Drift recovery + 3-way handoff
- 3-4 problem-specific drift lines (interviewer drifts to generic / asks scale early / asks cold-start premature / asks why-not-X). Each names the actual surface of this problem; not generic "deepen X/Y/Z".
- 1 handoff: "Want me to deepen the **A**, the **B**, or the **C**?" -- the 3-way choice maps to this problem's distinct levers.

---

## Positive Quality Rubric (extracted from N1 + N1.5; spot-check criteria)

A row passes spot-check if it satisfies ALL:

1. **§1 has all 4 elements**: objective sentence (with domain-specific target, not "personalize"), input (per-request), output (what + to whom), scale anchor.
2. **§2 lists 3-5 twists, ONE marked DOMINANT** at top. Not all equal-weight.
3. **At least 2 twists carry "Interacts with #N (...)" clauses.** Twists are coupled.
4. **§3 has 5-7 sections** roughly aligned to 45-min skeleton (Framing / Data-Label / Retrieval / Ranking / Bias-or-Calibration / Eval / Wrap). Skip/merge OK if problem family permits.
5. **Every §3 section opens with `**(driven by Twist N · interacts with M)**`** -- this is non-negotiable.
6. **Every §3 section has at least one trade-off line** in "**I pick** X over Y **because** Z; **costs**: W" form.
7. **§4 is 4 bullets**: SM# + minute range + twist + 1-line content. NO verbatim 60-word hook phrases.
8. **§5 has 3-4 drift lines + 1 handoff**. Drift lines are problem-specific (named surface), not generic.
9. **Concrete vocab**: name actual techniques (HNSW M=32, MMoE, IPS, Thompson sampling, BCE+calibration, cluster-randomized A/B). NOT generic ("model class", "deep learning", "feature engineering" without specifics).
10. **Cross-refs allowed and encouraged**: "structurally the same cascade pattern as Weapon Ads", "shares retrieval pattern with V2V Search", `cd://96` for methodology.
11. **Total length 8k-12k chars across overview + verbal_outline**. Anchors landed at ~10.7k and ~10.9k -- aim for that ballpark, not 4-5k.

---

## Mechanical Validation (only these; NO quality regex per user directive)

After insert, run:
```bash
sqlite3 data/mle_prep.db "SELECT length(overview)+length(verbal_outline), slug FROM system_designs WHERE slug='<your-slug>';"
# Expect: total between 8000 and 13000, slug exactly as specified
```

That's it. Quality is human spot-check ONLY -- do NOT add causal-density regex, "because" count, or any prose-level lints. Those are anti-patterns per user judgment 2026-05-14.

---

## Commit Contract

- `EXPECTED_FILES=data/mle_prep.db` (only DB changes; if you wrote a one-shot insert script, also include `scripts/insert_<topic>.py`)
- Commit message format: `[T-PX-NNN] [Meta-MLSD] Add meta-<topic>-golden 口播稿 row (twist-threaded solving + SM slot map)`
- No `git add .` -- explicit paths only (workspace `no_wildcard_add.py` hook).

---

## Reference Anchors

Read these BEFORE drafting yours:

```bash
sqlite3 data/mle_prep.db "SELECT overview FROM system_designs WHERE slug='meta-fb-newsfeed-golden';"
sqlite3 data/mle_prep.db "SELECT verbal_outline FROM system_designs WHERE slug='meta-fb-newsfeed-golden';"
sqlite3 data/mle_prep.db "SELECT overview FROM system_designs WHERE slug='meta-yelp-restaurant-golden';"
sqlite3 data/mle_prep.db "SELECT verbal_outline FROM system_designs WHERE slug='meta-yelp-restaurant-golden';"
```

cd94 source for the per-question twist seeds:
```bash
sqlite3 data/mle_prep.db "SELECT content FROM company_documents WHERE id=94;"
```

Then find `### Q<N>.` block for YOUR problem and use cd94's headline-twist + puzzle-pieces + anti-patterns as the seed -- but EXPAND with the interacting-constraints twists already enumerated in PROGRESS.md 2026-05-14.

---

## Per-Problem Twist Seeds (from PROGRESS.md 2026-05-14)

Each autorun task has the 4 twists for ITS problem in the task description. Paste those verbatim as the §2 starting point, then expand each into the [generic default → unique property → design implication] structure with at least 2 interaction clauses.

---

## Out of Scope (do NOT do)

- Do NOT populate `architecture`, `dataflow`, `formulas`, `production_constraints`, `tradeoffs`, `defense`, `cheat_sheet`, `diagram_filename` columns. Leave NULL.
- Do NOT write verbatim 60-word SM hook phrases. Light slot map only.
- Do NOT update cd94 family table -- that's the final wire-up task (depends on all 7).
- Do NOT update cd96 -- methodology layer is stable, this batch is solution layer only.
- Do NOT add causal-density regex, "because" count, or any prose-level validation.
