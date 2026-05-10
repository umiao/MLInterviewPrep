# Red-Dot Threshold EDA -- 2026-05-10

Task: T-P1-795 [KG-INT A0]. Goal: data-driven recommendation for
the `has_meaningful_note` cutoff used by A1 (T-P1-796) /
A2 (T-P1-797) to drive the company-card red dot. Default proposed
by the umbrella plan was 50/100/20 chars (per-surface). This report
validates or revises those values from current DB state.

## Methodology

- Source DB: `data/mle_prep.db`
- Length unit: Python `len(text)` (Unicode code points; CJK = 1 each).
- Percentile method: nearest-rank on sorted population.
- Placeholder heuristic: empty / whitespace-only / <5 chars OR
  body <80 chars containing one of:
  `tbd, todo, to do, n/a, na, placeholder, stub, fill me in, fill in, [ ], lorem ipsum`.
- Status buckets:
  - applied-bucket: `['applied', 'rejected']` (not actively interviewing)
  - active-bucket: `['offer', 'onsite', 'phone_screen']` (phone_screen / onsite / offer)

## Surface: `companies.prep_notes`

- Total rows: **32**
- Non-empty: **5**
- Real (non-placeholder): **5** (15.6%)
- Placeholder: **27** (84.4%)

| Slice | N | min | P25 | P50 | P75 | P95 | max | mean |
|-------|---|-----|-----|-----|-----|-----|-----|------|
| all rows | 32 | 0 | 0 | 0 | 0 | 2757 | 24340 | 1041 |
| non-empty only | 5 | 730 | 1333 | 2757 | 4159 | 24340 | 24340 | 6664 |
| real (non-placeholder) | 5 | 730 | 1333 | 2757 | 4159 | 24340 | 24340 | 6664 |
| placeholder only | 27 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real & applied-bucket | 1 | 730 | 730 | 730 | 730 | 730 | 730 | 730 |
| real & active-bucket | 4 | 1333 | 2757 | 4159 | 4159 | 24340 | 24340 | 8147 |

## Surface: `companies.notes`

- Total rows: **32**
- Non-empty: **25**
- Real (non-placeholder): **23** (71.9%)
- Placeholder: **9** (28.1%)

| Slice | N | min | P25 | P50 | P75 | P95 | max | mean |
|-------|---|-----|-----|-----|-----|-----|-----|------|
| all rows | 32 | 0 | 28 | 66 | 108 | 372 | 523 | 100 |
| non-empty only | 25 | 25 | 55 | 87 | 126 | 446 | 523 | 128 |
| real (non-placeholder) | 23 | 28 | 60 | 98 | 126 | 446 | 523 | 135 |
| placeholder only | 9 | 0 | 0 | 0 | 0 | 72 | 72 | 11 |
| real & applied-bucket | 17 | 28 | 54 | 66 | 105 | 132 | 196 | 81 |
| real & active-bucket | 6 | 86 | 126 | 168 | 446 | 523 | 523 | 287 |

## Surface: `company_documents.content`

- Total rows: **78**
- Non-empty: **78**
- Real (non-placeholder): **78** (100.0%)
- Placeholder: **0** (0.0%)

| Slice | N | min | P25 | P50 | P75 | P95 | max | mean |
|-------|---|-----|-----|-----|-----|-----|-----|------|
| all rows | 78 | 528 | 7158 | 10707 | 19604 | 125521 | 185703 | 23207 |
| non-empty only | 78 | 528 | 7158 | 10707 | 19604 | 125521 | 185703 | 23207 |
| real (non-placeholder) | 78 | 528 | 7158 | 10707 | 19604 | 125521 | 185703 | 23207 |
| placeholder only | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real & applied-bucket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real & active-bucket | 78 | 528 | 7158 | 10707 | 19604 | 125521 | 185703 | 23207 |

## Surface: `problem_company_tags.notes`

- Total rows: **28**
- Non-empty: **17**
- Real (non-placeholder): **9** (32.1%)
- Placeholder: **19** (67.9%)

| Slice | N | min | P25 | P50 | P75 | P95 | max | mean |
|-------|---|-----|-----|-----|-----|-----|-----|------|
| all rows | 28 | 0 | 0 | 23 | 42 | 42 | 74 | 21 |
| non-empty only | 17 | 18 | 25 | 42 | 42 | 42 | 74 | 35 |
| real (non-placeholder) | 9 | 18 | 22 | 25 | 27 | 74 | 74 | 29 |
| placeholder only | 19 | 0 | 0 | 0 | 42 | 42 | 42 | 18 |
| real & applied-bucket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real & active-bucket | 9 | 18 | 22 | 25 | 27 | 74 | 74 | 29 |

## Surface: `node_company_tags.notes`

- Total rows: **5**
- Non-empty: **0**
- Real (non-placeholder): **0** (0.0%)
- Placeholder: **5** (100.0%)

| Slice | N | min | P25 | P50 | P75 | P95 | max | mean |
|-------|---|-----|-----|-----|-----|-----|-----|------|
| all rows | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| non-empty only | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real (non-placeholder) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| placeholder only | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real & applied-bucket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real & active-bucket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Surface: `behavioral_example_company_tags.notes`

- Total rows: **3**
- Non-empty: **0**
- Real (non-placeholder): **0** (0.0%)
- Placeholder: **3** (100.0%)

| Slice | N | min | P25 | P50 | P75 | P95 | max | mean |
|-------|---|-----|-----|-----|-----|-----|-----|------|
| all rows | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| non-empty only | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real (non-placeholder) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| placeholder only | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real & applied-bucket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| real & active-bucket | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Surface: `framework_nodes.description`

- Total rows: **238**
- Non-empty: **189**
- Real (non-placeholder): **189** (79.4%)
- Placeholder: **49** (20.6%)

| Slice | N | min | P25 | P50 | P75 | P95 | max | mean |
|-------|---|-----|-----|-----|-----|-----|-----|------|
| all rows | 238 | 0 | 2600 | 4844 | 6372 | 15637 | 35591 | 5411 |
| non-empty only | 189 | 233 | 4084 | 5866 | 6743 | 19739 | 35591 | 6814 |
| real (non-placeholder) | 189 | 233 | 4084 | 5866 | 6743 | 19739 | 35591 | 6814 |
| placeholder only | 49 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Recommendation

Recommendation rule: for each surface, set the `has_meaningful_note`
cutoff to `max(20, min(plan_default, real_content_P25))`. Rationale:

- `plan_default` is the umbrella plan's intent: the minimum length we
  consider 'sign of real prep'. We don't want to raise it just because
  current real content happens to be long -- that would penalize a
  legitimate-but-short future entry (e.g. a brief `notes` line).
- `real_content_P25`: if 25% of real entries already sit below the
  default, the default is too aggressive (would red-dot legitimate
  entries). In that case, drop the cutoff to that data-driven floor.
- The `max(20, ...)` clamp prevents the cutoff from collapsing into
  the trivial-string range.
- Surfaces with no real-content evidence yet (e.g. `node_company_tags.notes`
  is currently 100% placeholders) fall back to the plan default.

**The placeholder filter (heuristic above) is independent of the length**
**cutoff and applies in addition to it.** Any entry matching the
placeholder-shape rules counts as 'no meaningful note' regardless of
its length.

| Surface | Plan default | Real-content P25 | Real min | Placeholder max | Recommended | Real N | Placeholder N |
|---------|--------------|------------------|----------|-----------------|-------------|--------|---------------|
| `companies.prep_notes` | 50 | 1333 | 730 | 0 | **50** | 5 | 27 |
| `companies.notes` | 50 | 60 | 28 | 72 | **50** | 23 | 9 |
| `company_documents.content` | 100 | 7158 | 528 | 0 | **100** | 78 | 0 |
| `problem_company_tags.notes` | 20 | 22 | 18 | 42 | **20** | 9 | 19 |
| `node_company_tags.notes` | 20 | 0 | 0 | 0 | **20** | 0 | 5 |
| `behavioral_example_company_tags.notes` | 20 | 0 | 0 | 0 | **20** | 0 | 3 |
| `framework_nodes.description` | 50 | 4084 | 233 | 0 | **50** | 189 | 49 |

### Aggregate `has_meaningful_note` rule (for A1)

A company is `has_meaningful_note=true` if ANY of the per-surface
conditions below holds for that company_id:

- `length(companies.prep_notes) >= 50` AND not placeholder-shaped
- `length(companies.notes) >= 50` AND not placeholder-shaped
- `length(company_documents.content) >= 100` AND not placeholder-shaped
- `length(problem_company_tags.notes) >= 20` AND not placeholder-shaped
- `length(node_company_tags.notes) >= 20` AND not placeholder-shaped
- `length(behavioral_example_company_tags.notes) >= 20` AND not placeholder-shaped

Placeholder-shape filter is applied identically to the EDA heuristic
above. The intent: a company with only `TBD`/`TODO`/empty cells should
show the red dot regardless of how long those cells are.

## Per-company simulation

Apply the aggregate rule against current DB state and bucket by status.

- Total companies: **32**
- Would show red dot OFF (has_meaningful_note=true): **25** (78.1%)
- Would show red dot ON (has_meaningful_note=false): **7** (21.9%)

By status -- has_meaningful_note=true:

  - `applied`: 15
  - `onsite`: 4
  - `phone_screen`: 6

By status -- has_meaningful_note=false (red dot ON):

  - `applied`: 7

## Decision summary (for A1 / T-P1-796 to consume)

```python
# Per-surface cutoffs (chars) -- copy into A1 implementation.
RED_DOT_CUTOFFS = {
    "companies.prep_notes": 50,
    "companies.notes": 50,
    "company_documents.content": 100,
    "problem_company_tags.notes": 20,
    "node_company_tags.notes": 20,
    "behavioral_example_company_tags.notes": 20,
}

# A company has has_meaningful_note=True iff at least one of its
# six surfaces meets its cutoff AND is not placeholder-shaped.
```

Cross-reference: this report is the source of truth for the cutoff
values listed above. T-P1-796 (A1) acceptance criterion: 'A1 references
report's recommended values' -- this section IS that reference.
