# Company KG-Internalization Protocol (T-P1-801)

The protocol for migrating per-company prose content into the knowledge graph
(KG) and shared meta-prep nodes, then archiving the company-specific prose
once every claim has a provably equivalent KG/DB target.

This protocol exists because per-company prose (in `companies.prep_notes`,
`companies.notes`, `company_documents.content`) was the historical authoring
surface for everything: behavioral patterns, system-design vocabulary, LC
keyword playbooks, onsite-loop templates, code-pad practices. As the
company set grew past 30, the same patterns ended up duplicated 5-10x with
slight wording drift, with no single re-usable surface. The fix: make the
KG (`framework_nodes` + `meta-prep/*`) the canonical surface, and keep
per-company docs as thin drawer-link indices into it.

The first attempt at this (pre-2026-05) "just rewrite the doc shorter" --
which lost claims silently. The protocol below was distilled from the
KG-INT B-batch (T-P1-795 through T-P2-836) to make the migration
**causal-provable**: every original claim must have a verifiable query
proving it was preserved before the prose row is dropped.

---

## The 7 Steps

### 1. Audit -- inventory the surfaces

Run `scripts/_audit_company_kg_internalization.py` (T-P1-798 / KG-INT B1)
and read `docs/audit/company_kg_internalization_audit_<date>.md` for the
target company. The 6 surfaces in scope:

| Surface | Source | Typical content |
|---|---|---|
| S1 | `companies.prep_notes` | Markdown checklist (research X, mock Y, review Z) |
| S2 | `companies.notes` | Short admin/scheduling notes |
| S3 | `company_documents.content` | Long-form prose study notes (the heavy one) |
| S4 | `problem_company_tags` | Per-company LC tag overrides |
| S5 | `node_company_tags` | Per-company KG-node tag overrides |
| S6 | `behavioral_example_company_tags` | Per-company BQ-story relevance overrides |

Skip companies with `total_bytes < 2000` and `kg_refs == 0` -- they have
nothing to internalize. Skip companies in `applied` status that may
upgrade to `phone_screen`; revisit during T-P2-835 batch.

### 2. Dry-run -- write the archive plan, write nothing to DB

For each candidate company, produce
`docs/archive_plans/B4a-<company>_<date>.md` with five mandatory sections.
The plan is the gate; user reviews and approves before any DB write.

The plan structure:

#### §1 Inventory snapshot

For each of the 6 surfaces: byte count + first 200 chars + topic count
(headings) + drawer-link count + KG-ref count. Lifted directly from the
audit; this section is pure read-back, no interpretation.

#### §2 Migration matrix (4-tuple causal-proof)

The core artifact. One row per archive candidate (a paragraph, a table,
a heading section, or an isolated claim). Each row is a 4-tuple:

| 原 prose 摘要 | 原覆盖 | 现迁移到 | 可验证查询 |
|---|---|---|---|
| (original prose summary, ≤80 chars) | (which surface + char range) | (target URI: `kg://N`, `db://N`, `cd://N`, or `sd://<slug>`) | (SQL or grep that proves the claim is now in the target) |

Rules:
- **Every** archive candidate gets a row. If a paragraph has no migration
  target, do NOT list it as "drop" -- list it in §5 promotion candidates
  or surface it as an open question for the user.
- "现迁移到" must be a concrete URI, not a description. `kg://meta-prep/sd-must-knows/HNSW`
  is invalid (paths aren't URIs); use `kg://N` where N = the framework_nodes.id.
- "可验证查询" must be runnable. SQL preferred (`SELECT description FROM
  framework_nodes WHERE id = N`); grep acceptable when the claim is in
  a markdown file (`grep -l "two-tower" docs/workflow/*.md`).
- If the same claim appears in 3+ companies, route to a `meta-prep/*`
  node and tag the row with `[PROMOTION]` for §5.

This is the causal-proof: if every row has a passing verifiable query,
the prose can be dropped without losing information. The matrix is the
audit trail forever; do not delete it after archive.

#### §3 Skeleton preview

The full markdown of the replacement thin drawer-link doc (i.e., what
`company_documents.content` will become after archive). Pattern:

```markdown
# <Company> Prep Index

Cross-references into the KG. Per-company specifics live in tags
([S4](db://...), [S5](kg://...), [S6](db://...)). Shared substrate
lives in `meta-prep/*` nodes.

## Behavioral
- [Failure / setback cluster](kg://N) -- `<company>_failure` tag
- ... (one bullet per relevant meta-prep node, with company tag)

## System Design
- [Two-tower retrieval](kg://N) -- `<company>` flavour notes in node tags
- ...

## LC Keywords
- [HNSW family](kg://N) (S4 tag set: see problems with `<company>` tag)
- ...

## Onsite Loop
- [Standard 4-round VO](kg://N) -- last refreshed `<date>`
```

The skeleton MUST render in the existing CompanyDrawer.Notes view without
markup errors. Test by mounting it on a sandbox doc id before commit.

#### §4 Hard-archive checklist

The exact write sequence, in order. Each step is a discrete artifact:

1. **DB backup**: `data/mle_prep.db.bak.<timestamp>_pre_<company>_archive`
2. **DELETE rows**: `DELETE FROM company_documents WHERE id IN (...)` --
   list ids explicitly
3. **UPDATE clears**: `UPDATE companies SET prep_notes = NULL,
   notes = NULL WHERE id = N` (or replace with the §3 skeleton if S3
   is the surface being archived)
4. **Seed script moves**: `git mv scripts/seed_<company>_*.py
   archive/seed_scripts/<date>/`
5. **restore.sql generation**: `pg_dump`-style INSERT statements for
   every deleted/updated row, written to
   `archive/company_internalized/<company>_<date>/restore.sql`. This
   is the rollback artifact.

The script that applies §4 is the standard idempotent seed pattern (see
`docs/workflow/seed_smoke_test_protocol.md`): backup-before-write,
sentinel idempotency check, single transaction, verbose diff output.

#### §5 Promotion candidates flagged for meta-prep

Patterns spotted in this company that meet the
`promotion_criteria.md` threshold (>=3 of 11 P0+P1 companies AND
de-companiable wording). One bullet per candidate with:
- pattern name
- which companies (so far) have it
- proposed `meta-prep/*` target node
- 1-line excerpt of the de-companied wording

T-P1-821 (`B4-promotion`) consolidates §5 across all B4a plans and
authors the final meta-prep updates. This section is just the input.

### 3. Discord ping for review

The plan path is sent via Discord (the user's review surface) with a
1-line tldr. User reviews §2 and §5 specifically -- those are the rows
that determine information loss vs. promotion accuracy. Approval
gate: explicit "ok 执行" or equivalent green light.

Plan B writes do not start without this gate. Per `story_rewrite_protocol.md`:
"silence is not the gate."

### 4. Apply atomically (the actual archive)

Run the §4 checklist in order. The seed script is written to
`scripts/_archive_<company>_<date>.py` (underscore prefix == throwaway,
since each archive is one-time per company). It must:

- DB backup before any write (named per the §4 spec)
- Sentinel idempotency: re-run prints `[SKIP]`, never duplicates
- Single transaction wrapping the deletes + updates
- Verbose diff: print row counts, byte deltas, and the §3 skeleton hash
- Generate the restore.sql artifact

If any §2 row has a failing verifiable query, the seed aborts BEFORE
writing. This is the causal-proof gate enforced at apply time.

### 5. Re-audit

Re-run `scripts/audit_uri_consistency.py` (T-P0-735 / T-P1-802) to
confirm:

- Zero ERRORs (no dangling `kg://N`, `db://N`, `cd://N`, `sd://<slug>`)
- The replacement doc's drawer links all resolve
- No regression in the other 30 companies' surfaces (same audit, full scope)

Re-run `scripts/_audit_company_kg_internalization.py` and confirm
the company's row in the roll-up summary now matches the post-archive
expected shape (S3 byte count == skeleton size; KG refs > 0 if the
skeleton has any drawer links).

### 6. Verify end-to-end (manual smoke)

Three gates before marking the task done:

- **Idempotency re-run**: archive seed prints `[SKIP]` on second run
- **DB read-back**: `SELECT title, content_hash FROM company_documents
  WHERE company_id = N` matches the §3 skeleton hash
- **Frontend smoke**: `npm run dev` in `src/frontend/`, navigate to
  `/companies/<company>`, confirm the CompanyDrawer.Notes renders the
  skeleton with all drawer links clickable. Spot-click 2 KG links,
  2 DB links, 1 SD link.

### 7. Promotion pass (deferred to T-P1-821)

After every B4a archive plan exists, T-P1-821 (`B4-promotion`) reads
the §5 sections, deduplicates, and authors the meta-prep updates.
The order matters: archive FIRST (the audit reveals what's promotable),
promote SECOND (avoids rewriting meta-prep nodes for a single
company's idiosyncratic wording).

---

## Anti-patterns observed

- **Rewrite-and-rename**: shortening the prose without proving every
  claim has a KG target. Information loss is silent and unrecoverable
  without restore.sql. The §2 matrix is the only defense.
- **Promotion-first**: writing meta-prep nodes from one company's prose
  before scanning all 11. Wording stays company-flavoured ("Pinterest's
  HNSW playbook") instead of de-companied.
- **Skipping the dry-run gate**: the user has caught >=3 archive
  mistakes during §2 review that would have lost claims. The plan IS
  the protocol; the apply is mechanical.
- **Forgetting upstream seeds**: company-specific seeds in
  `scripts/seed_<company>_*.py` will silently undo the archive on next
  run. Step 4.4 (`git mv` to `archive/seed_scripts/`) is mandatory.

## When NOT to apply the full protocol

- Companies in `applied` status -- batch-process via T-P2-835 (KG-extraction
  only, no archive)
- Companies with `total_bytes < 2000` and `kg_refs == 0` -- nothing to
  internalize
- A surface that is structurally not prose (S4/S5/S6 tag tables) -- the
  protocol is about prose-to-KG migration; tag tables stay as-is

---

## File conventions

| Path | Purpose | Lifecycle |
|---|---|---|
| `docs/archive_plans/B4a-<company>_<date>.md` | Per-company dry-run plan | Permanent (audit trail) |
| `archive/company_internalized/<company>_<date>/restore.sql` | Rollback INSERT statements | Permanent |
| `archive/seed_scripts/<date>/seed_<company>_*.py` | Moved canonical seeds | Permanent |
| `scripts/_archive_<company>_<date>.py` | One-shot archive seed | Throwaway after first apply |

`docs/archive_plans/` is the §2 matrix archive; never delete. Even if
a future migration reverses an archive, the plan stays as the historical
record of what the prose said and where it went.
