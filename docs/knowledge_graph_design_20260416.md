# Knowledge Graph Design — MLInterviewPrep

**Status**: Design v1, pending user review
**Author**: Claude (design-mode)
**Date**: 2026-04-16
**Goal**: Systematic, visualizable knowledge graph unifying company-specific interview prep content atop canonical ML concepts. Link, don't duplicate.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Current-State Audit (Evidence)](#2-current-state-audit-evidence)
3. [Target Data Model](#3-target-data-model)
4. [Link Convention](#4-link-convention)
5. [Visualization Approach](#5-visualization-approach)
6. [Migration Strategy (4 phases)](#6-migration-strategy-4-phases)
7. [Risk Register & Non-Goals](#7-risk-register--non-goals)
8. [Success Metrics](#8-success-metrics)
9. [Open Questions for User Decision](#9-open-questions-for-user-decision)
10. [Appendix: Duplication Hotspot Catalog (preliminary)](#10-appendix-duplication-hotspot-catalog-preliminary)

---

## 1. Problem Statement

The prep corpus has grown organically. 57 `company_documents` totaling ~1.75M bytes + 47 `framework_nodes` that are meant to be the canonical concept tree. Three concrete pains:

- **Redundant content**: the same concept (Bias-Variance, Loss, Optimizer, NDCG, …) is re-derived in multiple company docs — byte-for-byte in at least one confirmed case (§2.2).
- **Terminology drift**: the same symbol is given different definitions across communities within the same codebase (e.g., "HLL" as family vs Flajolet-2007 instance — the motivating case that led to T-P0-241).
- **No single source of truth**: when a fact changes (better pitch line, corrected formula), there is no discipline for propagating the change to every duplicate.

The user has articulated the target shape clearly: **one canonical entry per concept + company-specific compositions that link back**. This document proposes how to get there incrementally, with user review gates at every phase.

---

## 2. Current-State Audit (Evidence)

### 2.1 Scale

| Company | Docs | Total bytes | Notes |
|---|---|---|---|
| LinkedIn | 6 | **465,839** | Heavy 合集 ("ML 理论 + 手写实现" 186k, "算法题解" 141k, "概率统计" 67k, "System Design" 60k) |
| Adobe | 10 | **400,899** | Multi-day prep ("All-in-One Day 1-8" 125k, "Diffusion Day1" 39k) |
| Uber | 11 | **374,365** | "BPS Custom Solutions" 71k, "BPS LC Solutions" 36k |
| DoorDash | 9 | **314,399** | ML Domain master (152k) + case studies |
| Google | 14 | 151,594 | **11 EN drills + 3 ZH** (hub, recruiter, interview note) |
| Pinterest | 6 | 25,888 | Already compact; card_index + sketch 1-pager |
| Slack | 1 | 13,791 | HR call prep |
| **Total** | **57** | **~1.75M** | |

And 47 `framework_nodes` in 8 pillars, most with descriptions 0–7kb (room to absorb migrated content).

### 2.2 Confirmed duplication

The cleanest case: `company_document.id=28` (Uber) and `id=29` (Adobe) share the **same SHA256** content_hash `3f2db8f9287fc95d91e462577166ca5934a2b2096d5c206fc657ed4b7ef31d51` — literally the same 151,774-byte file `ML Fundamentals From-Scratch 完整指南 (8大主题合并)` copied under two companies. Same first 300 chars byte-for-byte.

This is **the smoking gun**: the current workflow invites byte-level copy across companies. A KG with canonical source would make this impossible by construction.

### 2.3 Suspected (un-audited) duplication — examples

- `Google doc 56 Bias-Variance + Overfitting Diagnosis Drill` (7,166b) ↔ `framework_node 67 Bias-Variance Tradeoff` (6,103b) ↔ `framework_node 195 Bias-Variance & L1/L2 Geometric View` (7,543b) ↔ LinkedIn doc 27 "ML 理论 + 手写实现" (186kb, likely contains BV section).
- `Google doc 55 Regularization Deep Dive` (8,396b) ↔ `framework_node 69 Regularization` (7,888b) ↔ `framework_node 194 Regularization` (sibling) ↔ LinkedIn doc 27.
- `Google doc 62 Calibration Drill` (11,631b) ↔ `framework_node 88 Calibration` (6,081b).
- `Google doc 60 LambdaRank/LambdaMART Drill` (8,910b) — likely unique (specialized topic), but verify.
- `Pinterest doc 58 Sketch/Streaming 1-Pager` (3,817b) ↔ `framework_node 196 streaming_topk` (7,924b) ↔ `framework_node 197` ↔ `framework_node 103` — already identified; **T-P0-241 addresses this**.

A full audit (concept × doc matrix) is the deliverable of migration Phase 2 — not this design doc.

### 2.4 Language heterogeneity (Google R1)

Of Google's 14 docs, **11 are English**, 3 Chinese. Per user convention (`feedback_lc_notes_chinese.md`): prose Chinese, code/LaTeX/algorithm names English. 11 drills currently violate this. Separate concern from the KG architecture; tracked as a sibling task candidate (§9 open questions).

---

## 3. Target Data Model

### 3.1 Entity roles

| Table | Role | What it holds |
|---|---|---|
| `framework_nodes` | **Canonical** (the fact) | One node per concept; description is the authoritative text; Prerequisites + Key Terms enforce consistency. Already exists — use it. |
| `company_documents` | **Composition** (how a company applies it) | Company-specific angle, pitch, drill, or hub page. Must link to canonical(s) at first concept mention. |
| `concept_links` (NEW, optional) | **Cross-ref index** | Materialized M:N map: `(doc_id, node_id, relation, anchor_text, created_at)`. Enables back-links on framework_node pages and a graph view without string-parsing docs. |

### 3.2 `doc_kind` taxonomy (expanded from current 3 values)

| Value | Meaning | Example | Rewrite policy |
|---|---|---|---|
| `canonical_hub` | Aggregator across multiple canonical nodes | "Everything about Bias-Variance" spanning nodes 67/195 | New kind |
| `composition` | Company-specific angle with pointer to canonical | "Google NDCG drill" (Pinterest MP lens of node 70) | Replaces most `prep_note` after migration |
| `drill` | Intentional memorization card; may repeat primitives | "Staging 13 Flashcards" (Google doc 57) | **Explicitly protected** from collapse |
| `prep_note` | Legacy (current default) | Anything seeded before this design | Migrate to `composition` or `canonical_hub` per-concept |
| `hub_doc` | Company landing page | "Google 2026-04-17 Prep Hub" (doc 53) | Unchanged |
| `card_index` | Pinterest-style LC index | doc 66 | Unchanged |

### 3.3 `concept_links` table (proposed, user-confirmable)

```sql
CREATE TABLE concept_links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id      INTEGER NOT NULL REFERENCES company_documents(id) ON DELETE CASCADE,
    node_id     INTEGER NOT NULL REFERENCES framework_nodes(id) ON DELETE CASCADE,
    relation    TEXT NOT NULL CHECK (relation IN ('primary', 'reference', 'extends', 'drill_of')),
    anchor_text TEXT,            -- e.g. "Section 3: Bias-Variance"
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doc_id, node_id, relation)
);
CREATE INDEX idx_concept_links_node ON concept_links(node_id);
CREATE INDEX idx_concept_links_doc ON concept_links(doc_id);
```

**Why a table instead of parsing markdown**:
- Back-link rendering on framework_node page becomes a simple join (no content re-scan per page view).
- Graph visualization reads edges directly.
- Dead-link detection on doc edit becomes a trivial integrity check.

**Alternative (simpler)**: keep links inline in markdown only, extract at render time. Faster to ship, but every framework_node page must re-scan every doc to find back-refs. OK for small scale; becomes O(docs) per page view as corpus grows.

Recommendation: **add the table**. Migration cost is small (one ALTER + one backfill pass).

---

## 4. Link Convention

### 4.1 Syntax (markdown inside `company_document.content`)

At first mention of any canonical concept in a document, the author (human or seed script) inserts:

```markdown
> **正典** [Bias-Variance Tradeoff (pillar2.supervised_learning.bias_variance)](/framework/67)
```

Format rules:
- Opens with `> **正典**` (blockquote + bold label) so it renders visually distinct.
- Link text = canonical node title + path in parentheses.
- URL = `/framework/{node_id}` (existing route).
- Placed **at first mention in each document**, not repeated per section.
- Multiple concepts in one section = multiple consecutive blockquotes.

### 4.2 Author semantics (relation types)

| relation | Meaning | When to use |
|---|---|---|
| `primary` | This doc is the canonical-hub for the concept | Only for `doc_kind='canonical_hub'` |
| `reference` | Doc uses the concept but doesn't re-derive | Default for `composition` |
| `extends` | Doc adds a novel angle not in canonical | Signals canonical should absorb the delta on next revision |
| `drill_of` | Doc is a memorization/drill for the concept | Protects the doc from collapse |

### 4.3 Back-link rendering (framework_node page)

On every `/framework/{node_id}` page, render a panel below the description:

```
### Also discussed in
- [LinkedIn — ML 理论 + 手写实现, §3 Bias-Variance](...)
- [Google R1 — Bias-Variance Diagnosis Drill](...)   [drill]
- [DoorDash ML Domain Prep Master](...)
```

Data source: `SELECT d.company_id, c.name, d.title, l.anchor_text, l.relation FROM concept_links l JOIN company_documents d ... WHERE l.node_id = ?`

### 4.4 Migration helper

Provide a CLI helper to insert a canonical block:

```bash
python scripts/kg_link_insert.py --doc-id 60 --node-id 70 --relation reference --anchor "Section 2 NDCG definition"
```

The helper (a) updates the doc content with the blockquote at the anchor position, (b) upserts the `concept_links` row, (c) is idempotent (skip if block already present).

---

## 5. Visualization Approach

### 5.1 What to render

Two views, one page at `/kg`:

**A. Concept graph (primary)**
- Nodes = framework_nodes (sized by `SUM(byte_length(description))` + `COUNT(*) concept_links`).
- Edges:
  - Solid = Prerequisite (existing `parent_id` → child).
  - Dashed = Cross-doc reference (from `concept_links`, weighted by edge count).
- Filters: by pillar (pillar1–8), by company (show only edges whose doc.company_id matches), by density threshold.

**B. Company lens (secondary)**
- Pick a company → highlight which framework_nodes they touch → show uncovered nodes as ghost nodes with "gap" label.

### 5.2 Tech stack candidates

| Library | Pros | Cons | Recommendation |
|---|---|---|---|
| **React Flow** | Mature, node/edge customization, good TS types, React-native | Manual layout (or dagre plugin) | **Lean here** — existing frontend is React+TS |
| **Cytoscape.js** | Powerful layouts (cose-bilkent), scales to 1k+ nodes | React wrapper less mature, more CSS fight | Backup |
| **vis-network** | Zero-config force layout | Looks dated, less ergonomic in React | Not recommended |
| **D3 force** | Infinitely customizable | High implementation cost for low marginal gain here | Not recommended |

**Recommendation**: React Flow + dagre layout plugin. Estimated implementation: 1 feature-sized task (Phase 4).

### 5.3 Page route + component sketch

```
/kg
  <KnowledgeGraphPage>
    <GraphControls filters={pillarFilter, companyFilter} />
    <GraphCanvas nodes={...} edges={...} />  // React Flow
    <NodeDetailDrawer selectedNodeId={...} />  // existing drawer pattern
```

API endpoint proposal:
- `GET /api/kg/graph?pillar=2&company=3` → `{nodes: [...], edges: [...]}`
- Backed by two queries: framework_nodes + concept_links joined.

### 5.4 What visualization is NOT

- **Not** a replacement for framework_node detail pages. The graph is navigation.
- **Not** auto-generated inference ("concept A similar to concept B"). All edges come from explicit data (parent_id or concept_links).

---

## 6. Migration Strategy (4 phases)

Each phase has a visible user-review gate. Never proceed to the next phase without user sign-off.

### Phase 0 — Design Review (CURRENT)

- **Deliverable**: This document.
- **User action**: Review, annotate, approve or revise Open Questions in §9.
- **Gate**: User explicit approval before Phase 1.
- **Reversibility**: Trivial — the doc is the only artifact.

### Phase 1 — Convention & Schema (no content rewrite)

- **Scope**:
  - Add `doc_kind` values `composition`, `canonical_hub`, `drill` to schema CHECK constraint.
  - Create `concept_links` table + indexes.
  - Add `/api/kg/graph` stub endpoint (returns empty graph for now).
  - Add `kg_link_insert.py` helper script.
  - Backfill **obvious existing links**: parent/child framework_node edges into `concept_links` (relation='extends') so the table has initial data.
- **Visible output**: `/kg` page scaffolded but mostly empty; framework_node pages render empty "Also discussed in" panel.
- **Effort**: 1 feature task (S-M).
- **Reversibility**: DROP TABLE + one schema rollback migration.

### Phase 2 — High-Value Manual Consolidation (3 concepts)

- **Scope**: Pick **3 highest-value duplicated concepts** from audit, do full consolidation:
  1. **Sketch family** — already in flight as T-P0-241 (use as reference template).
  2. **Bias-Variance tradeoff** — node 67 + 195 canonical; collapse Google doc 56 to composition; add pointers from LinkedIn doc 27.
  3. **One more TBD by user** (candidates: Regularization / LambdaRank / Calibration / Feature Engineering).
- **Visible output**:
  - These 3 concepts' framework_node pages are the undisputed canonical.
  - Company docs that previously duplicated now link with a crisp "See canonical …" panel.
  - Total duplicate-bytes reduced measurably.
- **Effort**: 3 tasks, each M-complexity (similar to T-P0-241).
- **Reversibility**: Per-concept seed scripts are idempotent + archive originals before rewrite.
- **Gate**: User reviews 3 consolidated concepts → approve Phase 3.

### Phase 3 — Systematic Migration (remaining concepts)

- **Scope**: Based on Phase 2 signal + T-P0-243-style duplication map, spawn ~10-15 per-concept consolidation tasks. Prioritize by (duplication bytes × concept frequency in interviews).
- **Visible output**: Duplication rate metric drops; framework_node back-link panels populate steadily.
- **Effort**: 10-15 M-complexity tasks, ideally run serially via `autonomous_run.sh`.
- **Gate**: Halt if Phase 2 signal is poor; reshape approach first.

### Phase 4 — Visualization

- **Scope**: Implement `/kg` page with React Flow; integrate filters + detail drawer.
- **Prerequisite**: `concept_links` populated (Phases 1-3).
- **Effort**: 1 L-complexity task (frontend + backend endpoint).
- **Visible output**: Click `/kg`, see the whole concept forest with company overlays.

---

## 7. Risk Register & Non-Goals

### Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Collapsing a drill doc that was intentional repetition | Medium | `doc_kind='drill'` explicit exemption; user reviews every Phase 2 collapse |
| Consolidation destroys useful company-specific context | Medium | Every consolidation seed archives original content to `archive/pre_kg/doc_{id}_{timestamp}.md` before rewrite |
| Translation of Google R1 drills introduces subtle errors before R1 | **High (deadline)** | Separate task; backup originals before rewrite; bilingual diff review by user |
| `concept_links` table becomes stale vs inline links | Low | Phase 1 provides helper script; later a nightly validator can reconcile |
| Scope creep — user wants to migrate non-ML content | Low | This design explicitly scopes to ML prep content only |

### Non-Goals (explicit)

- **Not** migrating LC problem notes (`problems.notes`) — they already have their own per-problem scope.
- **Not** auto-inferring edges by embedding similarity — all edges come from explicit authoring.
- **Not** collapsing drill-format docs (Staging 13 Flashcards et al).
- **Not** handling non-ML content (behavioral, SQL, OOD).
- **Not** merging canonical content from OTHER projects (helixos, homestead) — single-repo scope.

---

## 8. Success Metrics

Measurable outcomes to gate phase progression:

| Metric | Baseline (today) | Target after Phase 3 | Measurement |
|---|---|---|---|
| **Duplication rate** | Unknown, estimated 30-45% of company_document bytes duplicate canonical content | < 10% | Byte-shingling Jaccard between each company_document and all framework_node.description |
| **Back-linked concepts** | 0 of 47 nodes have back-links today | ≥ 40 of 47 nodes have ≥ 1 back-link | `SELECT COUNT(DISTINCT node_id) FROM concept_links` |
| **Terminology variance** | ≥ 2 "HLL" definitions (family vs instance) without grounding | 0 ungrounded mentions | grep `HLL` across all content; require co-occurrence with "family" or "Flajolet" in same paragraph at first mention |
| **Orphan concepts** | Most framework_nodes have < 3 back-links | Top-20 concepts each have ≥ 2 compositions | Same COUNT as above, grouped |
| **Stale-link count** | N/A | 0 | Integrity check: every `concept_links` row's `node_id` and `doc_id` still exist |
| **User time-to-find** | ~ (currently have to search 6 companies to find all Bias-Variance content) | Single click from /framework/67 back-link panel | Manual test |

---

## 9. Open Questions for User Decision

Numbered for easy reply. **Recommended default in bold.**

1. **Data model**: Add the `concept_links` table (§3.3) or keep links markdown-only?
   - **Default: add table** (small cost, large downstream payoff for back-links + graph)
2. **doc_kind taxonomy**: Is `{canonical_hub, composition, drill, prep_note, hub_doc, card_index}` the right set, or add/remove?
   - **Default: accept as proposed**
3. **Link syntax**: Is `> **正典** [...](/framework/N)` the right marker, or prefer something else (e.g., `[[canonical:67]]` wiki-style, or HTML `<canonical-ref>` tag)?
   - **Default: blockquote markdown** (renders on current UI without frontend changes)
4. **Visualization library**: React Flow vs Cytoscape.js vs other?
   - **Default: React Flow + dagre** (fits existing React+TS stack)
5. **Phase 2 concept selection**: Sketch family (already in flight as T-P0-241) + Bias-Variance confirmed. **User picks the 3rd**: Regularization / LambdaRank / Calibration / Feature Engineering / Transformer Attention / other?
   - **Default: Regularization** (very high cross-company duplication)
6. **Google R1 translation timing**: Run translation task (11 EN drills → Chinese prose) **before** or **after** Phase 1? R1 is 2026-04-17 (< 24h).
   - **Default: BEFORE Phase 1** (deadline-driven; translation and KG work are orthogonal)
7. **Legacy 合集 docs** (LinkedIn doc 21/22/26/27, Adobe doc 19, Uber doc 28/29/30/31): keep as-is while decomposing into canonicals + compositions, or archive after decomposition?
   - **Default: keep as-is during migration**; reassess after Phase 3
8. **Archive policy**: Before every consolidation, copy original content to `archive/pre_kg/doc_{id}_{iso8601}.md` committed to git?
   - **Default: yes** (reversibility insurance)
9. **Migration execution**: Continue serial via `autonomous_run.sh`, or bring some tasks into user-reviewed sessions?
   - **Default: serial autonomous_run.sh** for Phase 2-3 content work; user review sessions for Phase 1 (schema) and Phase 4 (frontend)
10. **Scope of "canonical"**: Only ML concepts in pillar2/3/4/6, or include pillar7 (Math/Stats) and pillar1 (Coding)?
    - **Default: start with pillar2/3/4/6 ML-core** (where the duplication lives); pillar1/7 Phase 3+ if signal supports

---

## 10. Appendix: Duplication Hotspot Catalog (preliminary)

Preliminary candidates for Phase 2 and Phase 3. Exact priorities set after full audit (T-P0-243 deferred until after design approval).

| Concept | Canonical node(s) | Suspected duplicates | Est. collapsible bytes |
|---|---|---|---|
| Sketch family (CMS/HLL/SS) | 196, 197, 103 | Pinterest doc 58 | ~3k (in flight T-P0-241) |
| Bias-Variance | 67, 195 | Google doc 56, LinkedIn doc 27 §? | ~8-15k |
| Regularization | 69, 194, 195 | Google doc 55, LinkedIn doc 27 §? | ~15-25k |
| Calibration | 88 | Google doc 62 | ~10k |
| NDCG / MAP / MRR | 70 | Google doc 61 | ~10k |
| LambdaRank / LambdaMART | 65 (Tree Models) | Google doc 60 | ~8k |
| Two-Tower retrieval | 98 | Google doc 64, Pinterest? | ~15k |
| Multi-objective ranking (DPP/MMR) | 99 (Multi-Stage Ranking) | Google doc 65 | ~20k |
| IPS / counterfactual eval | 70-adjacent, new node? | Google doc 63 | ~13k |
| A/B testing | 104 | Google doc 67, DoorDash ? | ~12k |
| Feature engineering primitives | 78-83 | LinkedIn doc 27, DoorDash master | ~25k+ |
| Gradient descent / Optimizers | 74 | **doc 28 = doc 29 confirmed dup** (Uber ↔ Adobe), LinkedIn doc 27 | ~50k+ |
| Attention / Transformer | 141-147 | Adobe doc 19 (All-in-One), LinkedIn doc 27 | ~30k+ |
| Diffusion models | new node needed | Adobe doc 18 (Day1 39k) | Low dup (niche) |

**Total preliminary collapsible estimate: 200-300kb of bytes** = ~15% of total corpus, consistent with baseline estimate in §8. After Phase 3, expect further reduction as canonical nodes absorb variants.

---

## Revision Log

- **v1 (2026-04-16)**: Initial design. Awaiting user review on §9 open questions.
