# docs/ Filing Convention

**Status**: Proposal (T-P0-480, [DOCS-01])
**Adopted**: pending review
**Scope**: All files under `docs/`. Convention proposal only -- no file moves are
performed by this document. Migration is staged as DOCS-02 (company prep) and
DOCS-03 (intermediate / generated content).

## 1. Why a convention

`docs/` currently holds **365 files across 6 informal content categories** mixed at
the same level. A reader cannot tell, from a top-level listing, whether a file is:
a stable study reference, a company-specific drill, a design document, an audit
artifact, a transient generation output, or an archived snapshot. The mess shows
up concretely:

- `docs/google_*.md` (16 files) and `docs/pinterest_sketch_streaming_1pager.md` sit
  next to `docs/prep_bias_variance.md` -- company prep is indistinguishable from
  topic-agnostic study notes.
- `docs/generated/system_designs/` contains 274 sliced-up files
  (`*__overview.md`, `*__dataflow.md`, `*__defense.md`, ...) that dominate any
  recursive listing but are intermediate build output, not reference material.
- `docs/audits/` and `docs/synced/` hold dated, point-in-time artifacts with no
  clear retention policy -- they accumulate indefinitely.

The convention below charters six top-level subdirectories and gives each a
single purpose, naming rule, and lifecycle expectation. Authors can answer "where
does this file go?" by walking the table in §2.

## 2. The six top-level subdirectories

| Subdir            | Purpose                                                           | Lifetime  | Audience              |
| ----------------- | ----------------------------------------------------------------- | --------- | --------------------- |
| `study/`          | Topic-agnostic concept notes (canonical study material)           | Permanent | Self, future sessions |
| `company/<slug>/` | Company-specific prep (drills, BQ, recruiter notes, mock sets)    | Permanent | Self, per loop        |
| `design/`         | System design canonical write-ups (interview-ready, polished)     | Permanent | Self, mock partners   |
| `protocol/`       | Conventions, schemas, format specs (this file lives here)         | Permanent | Self, future agents   |
| `staging/`        | Generation output, audits, syncs, scratch -- TTL-bounded          | <= 30 d   | Build pipelines       |
| `archive/`        | Frozen historical snapshots (pre-migration, pre-deprecation)      | Permanent | Forensics only        |

The `workflow/`, `human_input/`, and `plans/` subdirs already exist and stay
where they are -- they are orthogonal (process, not content). `pinterest/` (an
existing company subdir) folds into `company/pinterest/` during DOCS-02.

### 2.1 study/

Concept-first, company-agnostic study material. A file lives here iff a reader
preparing for *any* ML role would benefit from it. Examples after migration:
`study/prep_bias_variance.md`, `study/prep_ensemble_methods.md`,
`study/prep_ddia_fundamentals.md`, `study/dl_training_pitfalls_1pager.md`.

If a file is named after a company, it does NOT belong here even when the
content is generic -- move it to `company/<slug>/` and link from a study note.

### 2.2 company/&lt;slug&gt;/

Company-specific prep keyed by lowercase slug. One subdir per company:
`company/google/`, `company/uber/`, `company/doordash/`, `company/slack/`,
`company/linkedin/`, `company/adobe/`, `company/pinterest/`. Inside each subdir
the filename **strips the company prefix** -- it is implied by the directory:

```
docs/google_bias_variance_drill.md      -> docs/company/google/bias_variance_drill.md
docs/uber_bps_lc_solutions.md            -> docs/company/uber/bps_lc_solutions.md
docs/pinterest_sketch_streaming_1pager.md -> docs/company/pinterest/sketch_streaming_1pager.md
```

Each company subdir SHOULD have a `README.md` summarizing pipeline stage,
upcoming dates (kept short, link out to memory for authority), and an index of
its drills.

### 2.3 design/

Canonical system design write-ups that are **interview-ready** -- the kind of
doc you would read aloud during a mock. Distinct from `staging/generated/`
which holds the sliced-up build output (`__overview`, `__architecture`, ...).
A `design/<topic>.md` file is the merged, hand-edited promotion of a generated
slice family. Initial inhabitants:
`design/PLAN_system_design_showcase.md`, `design/diffusion_models_canonical.md`,
`design/rope_long_context_canonical.md`, `design/mf_to_two_tower_bridge.md`.

### 2.4 protocol/

Format specs, schemas, naming conventions, and meta-rules that other docs and
scripts depend on. Already present: `protocol/kg_markdown_conventions.md`. New
additions land here: `protocol/docs_filing_convention.md` (this file),
`protocol/framework_node_template.md` (when the current
`framework_content_template.md` is promoted), etc. Files in `protocol/` are
authoritative -- changes require explicit review and a commit message that
calls out the protocol bump.

### 2.5 staging/

Everything transient: build output, audits, syncs, exploratory analysis. Files
here have a 30-day soft TTL (see §4). Subdirs after DOCS-03:
`staging/generated/system_designs/` (274 sliced files),
`staging/audits/` (dated audit artifacts), `staging/synced/` (sync-from-other-repo
copies), `staging/analysis/` (exploratory). A `staging/README.md` documents the
TTL policy. Anything in `staging/` should never be referenced by long-lived
study or company prep -- if a study note links into staging, that is a
graduation signal (see §4).

### 2.6 archive/

Frozen pre-migration / pre-deprecation snapshots. Already present:
`archive/completed_tasks.md`, `archive/progress_log.md`. New additions are
date-stamped subdirs: `archive/pre_kg/20260416/`, `archive/pre_docs_migration/`.
Files here are read-only by convention -- never edit, never reorganize. If you
need a current view, copy out to `study/` or `staging/`.

## 3. Filename conventions per subdir

| Subdir            | Case         | Date stamp                       | Language               |
| ----------------- | ------------ | -------------------------------- | ---------------------- |
| `study/`          | `snake_case` | None (timeless)                  | Chinese-first prose OK |
| `company/<slug>/` | `snake_case` | None (drill name conveys topic)  | Per company memory     |
| `design/`         | `snake_case` | None (canonical, name = topic)   | Chinese-first prose OK |
| `protocol/`       | `snake_case` | None (versioned via §3 of body)  | English (parser hits)  |
| `staging/`        | `snake_case` | `_YYYYMMDD` suffix REQUIRED      | Any                    |
| `archive/`        | `snake_case` | Subdir = `YYYYMMDD/`             | Frozen as-of date      |

The date-stamp rule for `staging/` lets the TTL sweep find expired files with a
single glob. The rule for `archive/` keeps snapshots cleanly grouped by event
(`pre_kg/`, `pre_docs_migration/`) without polluting filenames.

## 4. Graduation rules (staging/ TTL)

Staging is a holding pen, not a long-term home. Two graduation paths:

1. **Promote up** -- if a `staging/*` file is referenced by a `study/`,
   `company/`, `design/`, or `protocol/` doc, the staged file MUST be merged
   into the consumer (or moved to its own canonical home) within the next
   editing session. Long-lived references into `staging/` are a code smell.
2. **Sweep out** -- files older than **30 days** (per the `_YYYYMMDD` suffix)
   that have no inbound references are candidates for deletion. The owning
   author confirms; otherwise they move to `archive/<YYYYMMDD>/`.

A scheduled task (out of scope for DOCS-01 -- expected as DOCS-04) walks
`staging/` weekly, lists expired files, and posts the report to PROGRESS.md.

The 30-day window is a heuristic chosen so audits from a current interview loop
(typical loop: 2-3 weeks) survive the loop, but stale generation output from
prior loops does not accumulate.

## 5. Anti-patterns

Do not commit any of the following. Each example is taken from the current
state of the repo and points at why the convention exists.

### 5.1 Company prep at the top level

```
docs/google_bias_variance_drill.md            <!-- WRONG: floats next to study/ notes -->
docs/uber_phone_screen_prep.md                <!-- WRONG: 8 sibling uber_* files -->
docs/pinterest_sketch_streaming_1pager.md     <!-- WRONG: pinterest/ subdir already exists -->
```

Correct:

```
docs/company/google/bias_variance_drill.md
docs/company/uber/phone_screen_prep.md
docs/company/pinterest/sketch_streaming_1pager.md
```

### 5.2 Generated build output at the top of docs/

```
docs/generated/system_designs/database_comparison__architecture.md   <!-- WRONG: 274 such files -->
```

`generated/` is build output, not curated content. It must live under
`staging/generated/` so a recursive listing of `study/`, `company/`, `design/`
is not drowned out by 274 slice files.

Correct:

```
docs/staging/generated/system_designs/database_comparison__architecture.md
```

The promoted, merged version (after hand-editing the 8 slices into one canonical
write-up) lives at:

```
docs/design/database_comparison.md
```

### 5.3 Undated audits accumulating in audits/

```
docs/audits/qe_link_spotcheck_2026-04-11.md            <!-- date in name, but in audits/ not staging/ -->
docs/audits/tech_depth_data_driven_2026-04.md          <!-- date in name, no graduation policy -->
```

Audits are inherently dated and short-lived -- they belong in `staging/` so the
TTL sweep can manage them. Long-lived findings extracted FROM an audit become
either a `study/` note (if generic) or a `protocol/` rule (if a new convention).

Correct:

```
docs/staging/audits/qe_link_spotcheck_20260411.md
```

### 5.4 Mixing template and concept content

```
docs/framework_content_template.md                     <!-- WRONG: template -> protocol/ -->
docs/framework_node_content_template_20260416.md       <!-- WRONG: dated template at top level -->
```

Templates are specs (every author follows them) -- they belong in `protocol/`.
Multiple dated copies of the same template are a smell; the convention is
`protocol/<name>.md` plus a Status line at the top noting the last revision
date (see this file's header).

### 5.5 Dated planning docs at the top level

```
docs/google_2026-04-17_prep.md                <!-- WRONG: dated event-specific doc at top level -->
docs/knowledge_graph_design_20260416.md       <!-- WRONG: design proposal mixed with study/ -->
```

Event-specific prep belongs under `company/<slug>/` (the date is part of the
filename if multiple loops). Design proposals belong in `design/` or, if still
in flux, `staging/`. The KG design doc graduates to `design/knowledge_graph.md`
once stable.

## 6. Migration map preview

Per the prior audit (T-P0-447 inventory) and the listing taken on 2026-04-16,
the 365 files in `docs/` redistribute approximately as follows. Counts are
*targets*; the exact moves happen in DOCS-02 / DOCS-03 and may shift by a few
files as edge cases surface.

| Destination          | File count | Source pattern                                                   |
| -------------------- | ---------- | ---------------------------------------------------------------- |
| `study/`             | ~30        | `prep_*.md`, `*_1pager.md`, `classical_model_pitches.md`, etc.   |
| `company/<slug>/`    | ~52        | `google_*` (16), `uber_*` (8), `doordash_*` (7), `slack_*` (1), `pinterest_*` + `pinterest/` (10), `linkedin_*` and `adobe_*` (if any), plus existing `pinterest/` contents |
| `design/`            | ~6         | `PLAN_system_design_showcase.md`, `diffusion_models_canonical.md`, `rope_long_context_canonical.md`, `mf_to_two_tower_bridge.md`, etc. |
| `protocol/`          | ~7         | Existing `protocol/kg_markdown_conventions.md`, this file, promoted templates, `chinese_conversion_spec.md`. |
| `staging/`           | ~284       | `generated/system_designs/` (274), `audits/` (4), `synced/` (3), `analysis/` (1), plus future generation runs. |
| `archive/`           | remainder  | Already present `archive/completed_tasks.md`, `archive/progress_log.md`, plus pre-migration snapshots taken during DOCS-02/03. |

The `workflow/`, `human_input/`, and `plans/` subdirs are out of scope for
migration -- they keep their current locations.

## 7. Open questions (to resolve before DOCS-02)

1. **Slug for Adobe doc 19 / 28?** Doc 19 is "Adobe MLE Prep All-in-One",
   doc 28 is "Uber ML Fundamentals From-Scratch" but currently lives under
   `adobe/` slug in the DB. Cross-check with `company_documents.company_id`
   before creating `company/adobe/` vs folding into `company/uber/`.
2. **`bq_*.md` files (3 at top level)** -- generic behavioral stories, not
   company-specific. Proposal: `study/bq/` subdir, or fold into
   `company/<slug>/bq.md` per loop. DOCS-02 author decides.
3. **`ml_cost_sensitive_selection.md`** -- single ML topic at top level.
   Proposal: `study/ml_cost_sensitive_selection.md`. Trivial.
4. **Symlink shim?** -- whether to leave a transition-period symlink at the old
   path so external bookmarks (Notion, browser tabs) keep working. Default:
   no shims; rely on `git mv` history and a one-time PROGRESS.md note.

## 8. Out of scope for DOCS-01

This document is a convention proposal only. It does NOT:

- Move any files (DOCS-02, DOCS-03 do that).
- Modify any seed scripts that reference current paths (those are part of the
  migration tasks).
- Change `framework_nodes` / `company_documents` content (KG tasks own that).
- Rewrite `pinterest/` subdocs (already in the right shape, just becomes
  `company/pinterest/`).

The deliverable is this file plus the migration-map preview. DOCS-02 and
DOCS-03 cite §2-§4 of this document as the contract they implement.
