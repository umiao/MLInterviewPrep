# KG Markdown Link Conventions

**Status**: Adopted 2026-04-16 (T-P0-472, [KG-P1-03])
**Scope**: All `framework_nodes.description` and `company_documents.content` markdown bodies.
**Parser target**: `> \*\*(正典|也见|前置|后续)\*\* \[.*?\]\(/framework/(\d+)\)`

## 1. Why a convention

The knowledge graph (KG) treats `framework_nodes` as canonical concept hubs and `company_documents` as drills / prep notes that reference those hubs. Today the same concept may be mentioned informally in dozens of places with prose like "详见 LLM Serving 节点" or "参见 doc《Two-Tower Retrieval Deep Dive》". Those mentions are invisible to machines.

This convention standardizes every cross-reference so a future scraper can extract edges into the `concept_links` table (KG-P1-01) with a single regex. The authoring rules below are cheap to follow and produce unambiguous pointers.

## 2. The four canonical tag families

All cross-references MUST sit on their own markdown **blockquote line** (line starts with `> `). The tag is bold-wrapped in `**...**`. The label text is a plain markdown link. The link target uses the in-app URL `/framework/{node_id}` (or `/companies/{slug}/documents/{doc_id}` for document targets -- see §5).

| Tag           | Semantics                                                    | Typical context              |
| ------------- | ------------------------------------------------------------ | ---------------------------- |
| `**正典**`    | "Canonical" -- single source of truth pointer                | Drill refs its hub           |
| `**也见**`    | "See also" -- adjacent or related concept                    | Cross-pillar link            |
| `**前置**`    | "Prerequisite" -- must understand X before current node      | Top of node body             |
| `**后续**`    | "Follow-up" -- natural next step in the learning path        | Bottom of node body          |

### 2.1 Canonical pointer (`正典`)

Use when a drill, prep note, or secondary doc defers to a hub for the definitive treatment. Exactly one `正典` per topic per document is the norm; multiple canonicals are a smell (the drill is drifting into its own hub).

```markdown
> **正典** [Bias-Variance Tradeoff (pillar7.probability_statistics.bias_variance)](/framework/56)
```

The label convention is `Title (path)`. The path suffix keeps the anchor legible when the DB is not available (e.g., diff review).

### 2.2 Mentions / see-also (`也见`)

Use for lateral links where the current node does NOT defer its treatment, but a reader interested in adjacent territory should know about the other node.

```markdown
> **也见** [A/B Testing](/framework/104)
> **也见** [Exploration / Exploitation](/framework/105)
```

Multiple `也见` lines are fine. Order by most-relevant-first.

### 2.3 Prerequisite (`前置`)

Place at the top of the node body, before the first `##` heading. Signals the minimum prior knowledge the current node assumes. Keeps long bodies self-contained without re-deriving basics.

```markdown
> **前置** [Linear Algebra Refresher](/framework/12)
> **前置** [Gradient Descent](/framework/18)
```

### 2.4 Follow-up (`后续`)

Place near the bottom, typically after `## Key Takeaways`. Signals the natural next concept. Helps the study-path generator (future work) build paths without manual curation.

```markdown
> **后续** [Regularization](/framework/195)
> **后续** [Model Selection](/framework/24)
```

## 3. Composed-of (canonical_hub listing)

When a `doc_kind='canonical_hub'` document lists its constituent concepts, use an unordered **list**, not a blockquote. Each item is a single markdown link followed by an em-dash and a one-sentence role description.

```markdown
## Components

- [Bias-Variance Tradeoff](/framework/56) -- bedrock for any model-selection discussion.
- [Regularization (L1/L2/ElasticNet)](/framework/195) -- controls variance once the hypothesis class is chosen.
- [Learning Curves](/framework/77) -- the diagnostic you reach for when "why is my model bad?" is the question.
```

This form is distinct from the blockquote tags because the parser treats composition as a container relationship (`relation='composed_of'`), not a pointer.

## 4. Parser contract

The scraper that populates `concept_links` uses this regex (Python syntax, `re.MULTILINE`):

```
^\s*> \*\*(正典|也见|前置|后续)\*\* \[(.*?)\]\(/framework/(\d+)\)\s*$
```

Capture groups:
1. Tag word (`正典` / `也见` / `前置` / `后续`)
2. Link label text (free-form, NOT used for graph edges)
3. Target framework_node id (integer)

Edges inserted into `concept_links`:

| Tag     | relation    | direction                        |
| ------- | ----------- | -------------------------------- |
| 正典    | `canonical` | current_doc -> target_node       |
| 也见    | `mentions`  | current_doc -> target_node       |
| 前置    | `prereq`    | target_node -> current_doc       |
| 后续    | `followup`  | current_doc -> target_node       |

The `composed_of` list-style links (§3) use a separate regex scoped to hub docs.

## 5. Document targets

When the target is a `company_documents` row rather than a framework_node, use the same tag family but with URL `/companies/{slug}/documents/{doc_id}`:

```markdown
> **也见** [Google Bias-Variance Drill](/companies/google/documents/56)
```

This is less common -- prefer to link TO a canonical framework_node and let that node list its drills via `composed_of`. Direct doc-to-doc references are allowed but the parser inserts them as `mentions` with `dst_kind='company_document'`.

## 6. Anti-patterns

Do NOT write any of the following. They either break the parser or produce ambiguous edges.

### 6.1 Inline prose references (no blockquote)

```markdown
详见 LLM Serving 节点。   <!-- WRONG: no blockquote, no link, untrackable -->
```

Correct form:

```markdown
> **也见** [LLM Serving](/framework/132)
```

### 6.2 Missing tag family word

```markdown
> [Bias-Variance](/framework/56)   <!-- WRONG: parser ignores -->
```

Correct:

```markdown
> **正典** [Bias-Variance (pillar7.probability_statistics.bias_variance)](/framework/56)
```

### 6.3 Blockquote with trailing prose on the same line

```markdown
> **正典** [Bias-Variance](/framework/56) -- and some extra commentary.   <!-- WRONG -->
```

The parser regex anchors to end-of-line (`$`). Commentary belongs on the next line (non-blockquote) or inside the link label itself:

```markdown
> **正典** [Bias-Variance (bedrock for any model-selection discussion)](/framework/56)
```

### 6.4 Using a tag to point at external URLs

```markdown
> **正典** [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)   <!-- WRONG: not a KG edge -->
```

External references are plain markdown links without tags. The KG only tracks internal edges.

### 6.5 Chinese punctuation or full-width characters in the tag

```markdown
> **正典**：[Bias-Variance](/framework/56)   <!-- WRONG: extra colon breaks regex -->
> **正典 **[Bias-Variance](/framework/56)    <!-- WRONG: space inside the bold -->
```

The spec requires exactly `> **<tag>** [label](url)` with a single ASCII space between the closing `**` and the opening `[`.

### 6.6 Duplicate canonicals

Two `正典` lines pointing at different nodes in the same document is a sign the document is actually a hub, not a drill. Promote the document to a hub or split it.

## 7. Authoring checklist

When adding or revising a node/doc:

1. Every informal reference ("详见 X 节点", "参见 doc《Y》", "as discussed in Z") -> rewrite as a blockquote tag.
2. Place `前置` lines at top, `后续` lines at bottom, `正典`/`也见` wherever they read naturally.
3. If the reference is the first or only mention of the target, prefer `正典`. Otherwise `也见`.
4. Keep each tagged line short -- the label is a summary, the blockquote is not a paragraph.
5. Re-scan with `grep -nE '^> \*\*(正典|也见|前置|后续)\*\*'` to confirm the blockquotes exist before committing.

## 8. Migration policy

Existing content is migrated opportunistically, not in a big-bang pass. When a task touches a node for any reason (content edit, length trim, consolidation), the author should upgrade any informal references in that node as part of the edit.

The POC patch in T-P0-472 upgrades nodes **130 (Model Serving Systems)** and **133 (Latency Optimization)** -- both reference the LLM Serving node (id 132) as plain prose today. They become the first two canonical-tag users in the corpus.

## 9. Future scope (out of scope for T-P0-472)

- Automatic scraper that walks framework_nodes + company_documents and populates `concept_links` -- separate task.
- Frontend rendering: the FrameworkNodeDrawer should surface `前置` / `后续` as clickable breadcrumb chips.
- Bidirectional link validation: enforce that every `正典` has an inverse edge from the target node back to the source doc.
- Composition parser (§3 list form) with a separate regex scoped to `doc_kind='canonical_hub'`.

## 10. `framework_nodes.path` separator convention

**Status**: Adopted 2026-04-25 (T-P0-612, [KG-FIX-04]) after the slash-path KG bug
postmortem (see `LESSONS.md` 2026-04-25 entry).

### 10.1 The rule

`framework_nodes.path` uses the **dot** (`.`) separator for taxonomy segments.

```
pillar2.feature_engineering.scaling_normalization     <-- correct
pillar7.probability_statistics.bias_variance          <-- correct
```

The first dot-segment is the **pillar key** and is the load-bearing prefix for
KG rendering. The backend `src/backend/routers/kg.py::_pillar_of()` walks
`parent_id` to depth=0 and reads the root path; the frontend
`PILLAR_STYLES` (`src/frontend/src/components/kg/kgStyles.ts`) and
`PILLAR_ORDER` (`src/frontend/src/components/kg/useKgLayout.ts`) map that key
to colour and lane order.

### 10.2 Known historical exception: `ml-fundamentals/*`

The `ml-fundamentals` subtree (35 nodes, seeded 2026-04-2x) was authored with
**slash** (`/`) separators:

```
ml-fundamentals/classical_ml/bias-variance-tradeoff   <-- exception
ml-fundamentals/optimization/sgd-vs-adam              <-- exception
```

This single root is whitelisted in `tests/test_framework_path_convention.py`
(`WHITELIST = {"ml-fundamentals"}`). The exception is governed by **T-P2-614
(KG-DESIGN-DUAL-VIEW)** -- when that design task closes, either (a) the
subtree gets migrated to dot-separator and the whitelist is emptied, or
(b) the dual-root pattern is ratified and the whitelist enforcement is
replaced by a permanent rule. The schema invariant test fails once T-P2-614
is marked completed while the whitelist is still non-empty, forcing the
cleanup.

### 10.3 Adding a new top-level taxonomy

Any new top-level taxonomy (a new pillar, or any new depth=0 root) **MUST**
land **all four** of the following in the same change:

1. **WHITELIST entry** in `tests/test_framework_path_convention.py` if the
   new root uses slash separators (preferred: use dots and skip this step).
2. **`PILLAR_ORDER` entry** in `src/frontend/src/components/kg/useKgLayout.ts`
   with a step=10 rank (or an adjacent decimal if inserting between existing
   ranks -- see the insertion-convention comment in that file).
3. **`PILLAR_STYLES` entry** in `src/frontend/src/components/kg/kgStyles.ts`
   with a unique border colour (no collision with existing pillar hues).
4. **Convention test update**: extend the parameterized known-pillars list
   in `src/frontend/src/components/kg/kgStyles.test.ts` and
   `useKgLayout.test.ts` so the new key is covered by the
   `FALLBACK_STYLE`/`UNKNOWN_PILLAR_RANK` invariants.

Skipping any of the four reproduces the original "Other" bucket bug (every
node in the new taxonomy gets bucketed grey + sorted to the end of the lane
order).

### 10.4 Why a separator convention at all

The KG layout pipeline groups nodes into swimlanes by their pillar key.
Mixing separators silently breaks any code that splits on a single delimiter
(`path.split(".")[0]`), which is the easy / wrong way to derive the pillar.
The dot-separator rule plus the parent_id walk in `_pillar_of()` make the
backend separator-agnostic, but the frontend lane order/colour still keys
off the literal pillar string. The whitelist + invariant test are the
checkpoint that prevents another silent slash-root from slipping in.
