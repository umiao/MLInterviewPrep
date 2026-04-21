# BQ Link Prune Log (T-P0-574)

Run timestamp: `20260421_015609`
Mode: **APPLIED**
Backup: `mle_prep.db.bak.20260421_015609_pre_link_prune`
Script: `scripts/_prune_bq_links_20260421.py`
Audit input: `docs/bq_link_audit_20260421.md`

## Counts

- Links before: **266**
- Links after:  **258**
- Net deleted:  **8**

- Candidates matched by rule 1 (brand-recall placeholder): 11
  - DELETE: 8
  - SKIP_GOLDEN: 0
  - SKIP_ORPHAN: 3
  - SKIP_ALREADY_GONE: 0

## Deletions applied (8)

| link_id | question | story | note | rule |
|--------:|----------|-------|------|------|
| 179 | `COM-2` | `BLOG-01` | Brand recall two-part story | rule 1 (brand-recall placeholder) + rule 3 (question retains 13 links) + rule 4 (example is not golden) |
| 180 | `PS-2` | `BLOG-01` | Brand recall two-part story | rule 1 (brand-recall placeholder) + rule 3 (question retains 5 links) + rule 4 (example is not golden) |
| 183 | `LDR-1` | `BLOG-01` | Brand recall two-part story | rule 1 (brand-recall placeholder) + rule 3 (question retains 2 links) + rule 4 (example is not golden) |
| 186 | `IMP-4` | `BLOG-01` | Brand recall two-part story | rule 1 (brand-recall placeholder) + rule 3 (question retains 4 links) + rule 4 (example is not golden) |
| 187 | `PS-1` | `BLOG-01B` | Brand recall deep dive story | rule 1 (brand-recall placeholder) + rule 3 (question retains 6 links) + rule 4 (example is not golden) |
| 188 | `PS-4` | `BLOG-01B` | Brand recall deep dive story | rule 1 (brand-recall placeholder) + rule 3 (question retains 3 links) + rule 4 (example is not golden) |
| 190 | `COM-2` | `BLOG-01B` | Brand recall deep dive story | rule 1 (brand-recall placeholder) + rule 3 (question retains 13 links) + rule 4 (example is not golden) |
| 191 | `PS-2` | `BLOG-01B` | Brand recall deep dive story | rule 1 (brand-recall placeholder) + rule 3 (question retains 5 links) + rule 4 (example is not golden) |

## Skipped -- golden story (rule 4) (0)

_None._ No candidate links point to a golden example. (EX-01 is golden and has 16 question links, none of which carry the brand-recall placeholder note.)

## Skipped -- would orphan question (rule 3) (3)

These three questions have only 2 total links, so dropping the single placeholder link would leave just 1 -- below the `MIN_LINKS_POST_PRUNE=2` floor. They are surfaced here for follow-up: either UPDATE-NOTE the placeholder to a real facet lock, or add a second non-placeholder link from a relevant story, then re-run the prune.

| link_id | question | story | note | rule |
|--------:|----------|-------|------|------|
| 181 | `PS-3` | `BLOG-01` | Brand recall two-part story | rule 3 (question PS-3 has 2 links; dropping 1 placeholder(s) would leave 1 < 2) |
| 184 | `ADP-3` | `BLOG-01` | Brand recall two-part story | rule 3 (question ADP-3 has 2 links; dropping 1 placeholder(s) would leave 1 < 2) |
| 189 | `IMP-1` | `BLOG-01B` | Brand recall deep dive story | rule 3 (question IMP-1 has 2 links; dropping 1 placeholder(s) would leave 1 < 2) |

## Skipped -- already deleted in earlier run (0)

_None in the authoritative (first apply) run._

## Idempotency verification

A second invocation of `scripts/_prune_bq_links_20260421.py` at `20260421_015636` on the already-pruned DB produced:

    [SCAN] 3 candidate(s) match rule 1
    [PLAN] DELETE=0  SKIP_GOLDEN=0  SKIP_ORPHAN=3  SKIP_ALREADY_GONE=0

The 8 deleted rows no longer appear in the candidate query (they are truly gone), and the 3 orphan-protected placeholders continue to SKIP. Net delete on re-run: 0.

## Post-prune invariants (verified on live DB)

- `question_example_links` row count: **258** (266 - 8)
- Questions with 0 links: **0** (no orphans)
- `EX-01` (is_golden=1) total question links: **16** (unchanged; all golden links preserved)
- Remaining rows matching `relevance_note LIKE 'Brand recall%story%'`: **3** (exactly the three rule-3 skips above)

## Revert recipe

Each DELETE row above can be reverted by re-inserting the triple `(question_id, example_id, relevance_note)`. The question/example numeric IDs are recoverable via the question_code/example_code in the table: look them up in `behavioral_questions.question_id` and `behavioral_examples.example_id` respectively. To revert the whole run, restore the backup file listed above (`data/mle_prep.db.bak.20260421_015609_pre_link_prune`).
