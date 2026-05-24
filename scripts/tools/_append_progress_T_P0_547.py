# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Throwaway: append T-P0-547 progress entry idempotently."""
from pathlib import Path

ENTRY = """
## 2026-04-20 HH:MM -- [T-P0-547] [T-MLF-07] MLFundamentals.tsx page + ?cat=&slug= deep-link
- **What I did**: Created `src/frontend/src/pages/MLFundamentals.tsx` modeled on `QuickIndex.tsx` -- 6-category tab bar (classical_ml, eval_data, unsupervised, dl_training, attention_transformer, llm_stats), a grid of 27 question cards showing `#id`, `title_zh`, `title_en`, and an `interview_freq` badge (red=high / amber=mid / gray=low), and a `FrameworkNodeDrawer` that opens when a slug is present in the URL. URL state via `useSearchParams`: `?cat=<cat_slug>&slug=<question_slug>` -- a slug outside the currently-selected cat auto-redirects to its owning cat; tab click preserves the slug if it belongs to the new cat and clears it otherwise; closing the drawer drops slug while keeping cat; navigating to `/ml-fundamentals?slug=bias-variance-tradeoff` with no `cat` param resolves cat from the inventory map. The 27-item inventory (title_zh / title_en / category / interview_freq) is inlined as a typed const that mirrors `data/ml_fundamentals_inventory.yaml`. Drawer wiring: `buildSlugToNodeId` walks the `/framework/tree` response under path `ml-fundamentals` and builds a `slug -> node_id` map so the drawer fetches the canonical `framework_nodes` row. Footer cross-link points to `/quick-index?section=ml_system_design` labelled `延伸: MLSD pillar` (per spec). Route `/ml-fundamentals` registered in `src/frontend/src/App.tsx` immediately below `/quick-index`, with the import added alongside `QuickIndex`. Sidebar nav item is deliberately left to T-P0-548.
- **Deliverables**:
  - ADDED `src/frontend/src/pages/MLFundamentals.tsx` (~200 lines: typed inventory + category tab bar + card grid + drawer wiring + URL state sync)
  - MODIFIED `src/frontend/src/App.tsx` (+1 import, +1 `<Route>` for `/ml-fundamentals`)
- **Sanity check result**: `npm run build` in `src/frontend/` -> 0 TypeScript errors, Vite emitted `dist/` in ~1.05s (pre-existing >500kB chunk-size warning unchanged). DB cross-check: 27 rows under `path LIKE 'ml-fundamentals/%/%'` in `data/mle_prep.db` match the 27 slugs in the inlined INVENTORY const (verified via sqlite3 dump), so every card resolves to a real `framework_nodes.id` at runtime. Visual verification of KaTeX rendering + per-drawer content is the explicit scope of the downstream smoke task T-P1-549 (dev-server review of all 27 drawers), not this task.
- **Status**: [DONE]
- **Request**: `task_db.py update T-P0-547 --status completed`
"""

p = Path("PROGRESS.md")
s = p.read_text(encoding="utf-8")
if "[T-P0-547]" in s:
    print("already present")
else:
    p.write_text(s + ENTRY, encoding="utf-8")
    print("appended")
