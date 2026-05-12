# Meta MLSD prep — RecSys 核心模型 + Drawer UX retrofit (2026-05-12)

## Context

User feedback on 2026-05-12 06:36 (Discord msg `1503646926468415548`): 5-task batch from 2026-05-11 (T-P0-837..841) landed but had two UX issues:
1. **Drawer URL hard to follow** (visual prominence不足) — root cause = naked `cd://N` / `sd://slug` in markdown is not visually distinct
2. Wanted single-link consolidation — pushed back, user accepted, but wants the drawer-index UX overhaul

Post-discussion (2026-05-12 06:55), user authorized:
- ✅ New `prep_note` for the RecSys-models technical content
- ✅ Retrofit all 4 existing Meta MLSD surfaces (doc 94 / 95 / 96 + Reels SD id=41) with prominent **Drawer 入口** section at TOP
- ✅ Strict dedupe — same URI must NOT appear in any one doc's Drawer 入口 section twice
- ✅ Markdown-native visual prominence (NO emoji per default + user's "如果你实在想用 emoji 可以事后把对应脚本清理了" reluctance signal)

## Files

| File | Coverage |
|------|----------|
| `source_03_recsys_models.md` | User's verbatim technical content: 8 工作 (DCN v1/v2 / DLRM / CF / 多模态 fusion / multi-task heads / RQ-VAE / HSTU / RankMixer) + 跨工作脉络梳理 — to be the body of T-P0-{A} (new prep_note) |

## Drawer UX Spec (per user 2026-05-12 06:36)

**Position**: TOP of doc (before first H1 prose content; for `system_designs`, prepend to `overview` column).

**Format** (markdown-native, NO emoji):

```markdown
> ## Drawer 入口（点击展开详读）
>
> | 入口 | 内容 | 何时打开 |
> | --- | --- | --- |
> | **[Reels Golden Example (45min 全文)](sd://meta-reels-golden)** | 八段台词 + 4 Strong Moments verbatim | 想看 DLRM/multi-task/multimodal 实战编排 |
> | **[13 题 Family Taxonomy](cd://94)** | Q1-Q12 卡片 + 题型识别 | 拿到新题，30 秒锁定 family |
> | **[Cross-cutting 9 ML 积木](cd://95)** | Two-Tower / IPS / LLM-teacher / Calibration | 套通用 ML 模块 |
> | **[45min Playbook + 4 Strong Moments](cd://96)** | 节奏 + 元结构 + meta-rules | 整体 framework |
> | **[RecSys 核心模型 8 工作](cd://{T-A id})** | DCN/DLRM/HSTU/RankMixer/RQ-VAE/CF | 模型层面 deep-dive |
> | **[通用 RecSys SD Cookbook](sd://interview-recommendation-system)** | Two-Tower + DLRM + MMoE 教科书 | 想看通用 RecSys 而不止 Meta |

---
```

Key design rules:
- **Blockquote wrap** (`> `) → frontend renders left-border, visually distinct from body
- **`## Drawer 入口（点击展开详读）`** H2 inside blockquote → still scannable
- **3-column table**: `入口 / 内容 / 何时打开` — 用户一眼知道点哪个
- **Link text** in `**[bold-label](URI)**` form — NOT naked URI; bold makes the entry conspicuous
- **Horizontal rule `---`** separates Drawer 入口 from body
- **Self-link exclusion**: each doc's Drawer 入口 must NOT list its own URI (no `cd://96` inside doc 96, no `sd://meta-reels-golden` inside SD id=41)
- **Dedupe**: each non-self URI appears at most once in Drawer 入口 section AND any prior drawer-list elsewhere in doc must be removed (or inline prose mention preserved if narrative)

## Task Dependency Graph

```
T-A (new RecSys note) ─────┬──→ T-B (retrofit doc 94, adds cd://<T-A>)
                            ├──→ T-C (retrofit doc 95, adds cd://<T-A>)
                            ├──→ T-D (retrofit doc 96, adds cd://<T-A>, dedupes existing Section 8 drawer list)
                            └──→ T-E (retrofit SD id=41 overview, adds cd://<T-A>)
```

B/C/D/E are parallel after A. Each retrofit task uses dynamic SQL to look up T-A's doc id by title.

## Drawer URI Conventions (per memory `reference_dblc_drawer_links.md`)

- `cd://N` → `CompanyDocDrawer` (company_documents.id)
- `sd://<slug>` → `SystemDesignDrawer` (system_designs.slug, NOT id)
- NEVER `db://N` for company_doc
- NEVER path-form `/system-design/<slug>` (navigates page, not drawer)

## Validation

Per-doc audit (each retrofit + new note):
- Drawer 入口 section present at TOP (before any other H1/H2 in body)
- URI count: each unique URI listed exactly once within Drawer 入口 table
- Self-URI NOT present
- All listed URI resolve (existing DB rows)
- Body content preserved unchanged in retrofit tasks (no destructive edits to existing prose)

Final batch-level: run `scripts/audit_uri_consistency.py` to verify nothing broken.
