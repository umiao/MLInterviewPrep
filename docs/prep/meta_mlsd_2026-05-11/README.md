# Meta MLSD 加面 Prep — Raw Source (2026-05-11)

## Context

2026-05-11 用户得知 Meta 临时安排 ML Design interview 加面。本目录存放原始复习材料（用户笔记），下游 5 个任务 (T-P0-829 .. T-P0-833) 将这些 raw 文本结构化进 `data/mle_prep.db`。

## Files

| File | Bytes | Coverage |
|------|-------|----------|
| `source_01_pacing_golden.md` | 32 083 | 45min 节奏理论 + 4 strong moment 框架 + Reels Golden Example 完整 8 段台词 + ML-native vocab 规则 + 题目家族列表 (lines 1-138 节奏理论; 139-362 Reels Golden Example 全文; 367-441 题目家族 raw 列表) |
| `source_02_family_taxonomy.md` | 17 034 | 13 题 family taxonomy 表 + 9 个 cross-cutting 积木 + Q1-Q12 per-question cards（Q13 Reels 引用 source_01）|

## Target DB Layout

新内容分四块（per 用户 2026-05-11 22:00 确认）：

1. **Reels Golden Example** → `system_designs` row, slug `meta-reels-golden`, display_order=130, title 明确标识 "Meta MLSD Golden Example" (T-P0-829)
2. **Family Taxonomy + 13 Cards** → `company_documents` row, company_id=31, doc_kind='prep_note' (T-P0-830)
3. **Cross-cutting 积木库** → `company_documents` row, company_id=31, doc_kind='prep_note' (T-P0-831)
4. **Main Hub Page** → `company_documents` row, company_id=31, doc_kind='prep_note'，引用上述三个 drawer URI (T-P0-832)
5. **Golden 置顶切换** → 新 hub `is_golden=1`，旧 doc 82 demote `is_golden=0` (T-P0-833)

## Drawer URI Conventions (per memory `reference_dblc_drawer_links.md`)

- `cd://N` → `CompanyDocDrawer`（用于 company_documents 行）
- `sd://<slug>` → `SystemDesignDrawer`（用于 system_designs 行，slug 寻址，**不是 id**）
- **绝不**用 `db://N` 引用 company_document（那是 problem drawer）
- **绝不**用 path-form `/system-design/<slug>`（会导航离开页面，不是 drawer）

## Style Rules (per memory `feedback_content_style_cn_en.md` + `feedback_match_golden_voice.md`)

- 中文叙述 + English 术语
- First-occurrence: `**English** (acronym, 中文)`
- 金句台词（如 strong moment 4 段、面试现场金句）保留**英文原文**——面试就这么说
- 表格直接 markdown 渲染
- 不要 AI 解释 voice；匹配用户原文 sentence-fragment / spoken 节奏

## Validation Pattern

每个任务自带 sanity check（query DB → 行存在 / 内容长度匹配 / 链接 reachable）。T-P0-833 收尾跑 `scripts/audit_uri_consistency.py` 确保 drawer URI 全部 reachable。

## Why Not Inline Inside CLAUDE.md

不在 CLAUDE.md / hub doc 内嵌全文是有意为之：
- 主 hub 要保持 ~6 KB 高密度 summary，重内容下沉 drawer（用户明确要求）
- Raw source 保留在 docs/prep/ 给 inner agent 做 stable input
- 完成后这两个 source_*.md 可保留为 archive（不会作为 user-facing 页面渲染）

## Task Dependency Graph

```
T-P0-829 (Reels SD)  ┐
T-P0-830 (Cards doc) ├──→ T-P0-832 (Main hub, needs all 3 drawer URIs) ──→ T-P0-833 (Promote is_golden)
T-P0-831 (积木 doc)  ┘
```

A/B/C 三个并行可拣；D 等三者完成；E 等 D 完成。autonomous_run picker 按 priority + dep 自动调度。
