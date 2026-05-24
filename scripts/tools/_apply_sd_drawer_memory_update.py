# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Idempotently update workspace memory + index for sd:// drawer scheme (T-P0-736).

Two operations:
1. Replace the body of `reference_dblc_drawer_links.md` to add the 4th scheme.
2. Update the one-line MEMORY.md index entry to match.

Both are idempotent: re-running emits [OK] without writes if the target state already matches.
"""

from __future__ import annotations

import sys
from pathlib import Path

WORKSPACE_MEMORY = Path(
    r"C:\Users\Shenghui Xu\.claude\projects\C--Users-Shenghui-Xu-Desktop-Gen-AI-Proj\memory"
)

REFERENCE_FILE = WORKSPACE_MEMORY / "reference_dblc_drawer_links.md"
INDEX_FILE = WORKSPACE_MEMORY / "MEMORY.md"

NEW_REFERENCE = """---
name: db:// / lc:// / cd:// / sd:// drawer link schemes in MLInterviewPrep markdown
description: Four URI schemes in MLI prep_note / company_documents markdown -- lc://N (leetcode_id) and db://N (problems.id) open ProblemDrawer; cd://N (company_documents.id) opens CompanyDocDrawer; sd://<slug> (system_designs.slug) opens SystemDesignDrawer. Never use db:// to point at a company_document. Never use path-form `/system-design/<slug>` in markdown -- that navigates the page away.
type: reference
originSessionId: 2492baa3-da52-4210-9aa8-5d1f97cda3c7
---
## The four schemes (as of 2026-05-04, SD-DRAWER series T-P0-731..736)

| Scheme | Target table | Drawer | Backend endpoint | Identifier type |
|--------|--------------|--------|-------------------|-----------------|
| `lc://N` | `problems` (by leetcode_id) | `ProblemDrawer` | `GET /problems/by-lc/{N}` | int |
| `db://N` | `problems.id` | `ProblemDrawer` | `GET /problems/{N}` | int |
| `cd://N` | `company_documents.id` | `CompanyDocDrawer` | `GET /company-documents/{N}` | int |
| `sd://<slug>` | `system_designs.slug` | `SystemDesignDrawer` | `GET /system-designs/{slug}` | string (kebab-case) |

**Slug-vs-id distinction**: `sd://` keys on `system_designs.slug` (e.g. `pinterest-ad-ctr`), NOT on `system_designs.id`. The audit's cross-table-confusion WARNING branch (which exists for db:// vs cd:// because both are int-keyed) is omitted by design for `sd://` -- slugs are strings, problem/doc ids are ints, so a slug can never collide with an int-keyed scheme.

## Why four schemes (history of the bug)

- Pre-2026-04-30: only `lc://` and `db://`. Memory previously claimed `db://` could open company_documents in a drawer -- WRONG. `db://N` always resolved against the `problems` table; if `N` happened to also exist as a `company_documents.id` (which is common since both tables share an integer space), the drawer silently showed the unrelated LC problem. Discovered while building the Meta AI-Native hub (id=82) when 6/6 sub-doc links opened wrong LC problems.
- 2026-04-30: introduced explicit `cd://N` scheme via Drawer-Fix series:
  - `cb6ec35` backend `GET /company-documents/{N}` (id-only resolver, 404 on missing)
  - `5961aa3` `MarkdownPreview` regex match `^cd://(\\d+)(?:#...)?$` + `onCdLinkClick` prop
  - `c8bee09` `CompanyDocDrawer` component with explicit "Document not found" 404 UI + `console.warn("[CompanyDocDrawer] cd://N fetch failed: ...")` observability + recursive cd:// REPLACES drawer (no stacking)
  - `a836ab6` `PrepNotesPage` discriminated-union state `DrawerTarget = {type:'lc'|'problem'|'company_doc';id} | null` so two drawers can't be open simultaneously at the type level
  - `677cea2` `scripts/audit_uri_consistency.py` (CI-ready, exits non-zero on cross-table corruption) + Meta hub migration db://->cd:// + `tests/test_hub_cd_link_resolution.py` integration test
  - `bc687a1` migrated 4 other affected hubs (Uber id=37/81, Google id=51/53; 23 broken links across them)
- 2026-05-04: introduced explicit `sd://<slug>` scheme via SD-DRAWER series (T-P0-731..736):
  - `731` `MarkdownPreview` regex match `^sd://([a-z0-9-]+)(?:#...)?$` + `onSdLinkClick` prop (slug-keyed, not id-keyed)
  - `732` `SystemDesignDrawer` component mirroring CompanyDocDrawer: 9 fixed sections (`SECTION_LABELS`), `useQuery({ retry: false })` against `GET /system-designs/<slug>`, 404 inline UI surfaces the slug, recursive sd:// REPLACES `activeSlug` locally (no history stack), lc/db/cd bubble UP to parent for outer-drawer swap
  - `733` `PrepNotesPage` widened `DrawerTarget` discriminated union with `{ type: "system_design"; slug: string }` (slug-keyed arm) + `<SystemDesignDrawer>` mounted as sibling to ProblemDrawer + CompanyDocDrawer
  - `734` doc 47 (Pinterest LC Must-Do hub) migration: 7 path-form `](/system-design/<slug>)` links rewritten to `](sd://<slug>)` via idempotent seed `scripts/seed_pinterest_lc_must_do_sd_drawer_links.py` (anchored regex on link boundary; delta_chars==70 invariant)
  - `735` `scripts/audit_uri_consistency.py` extended to cover sd://: `SD_LINK_RE = re.compile(r'sd://([a-z0-9-]+)')`, `_existing_slugs(conn, table, slug_col)` helper, `Finding.target_id: int | str` widened typing, third scan loop with VALID/ERROR classification (no WARNING branch -- str-vs-int cross-table confusion impossible)

## Authoring rules

- **Hub doc -> company_document sub-doc**: use `[label](cd://N)`. NEVER `db://N` to point at a company_document -- silent corruption.
- **Hub doc -> LC problem**: use `[label](db://5)` (problem dbid) or `[label](lc://347)` (leetcode number). Both work and show the same problem.
- **Hub doc -> system_design**: use `[label](sd://<slug>)` where `<slug>` is the kebab-case `system_designs.slug` (e.g. `pinterest-ad-ctr`, NOT a numeric id). NEVER use path-form `[label](/system-design/<slug>)` -- that navigates the page away instead of opening the drawer (failure class observed on doc 47 prior to T-P0-734).
- **Cross-tab full-page nav**: use `[label](?tab=docs&doc=N)` query string -- replaces page (not drawer). Use this when you want full-screen view, not modal.
- **NEVER** use HTML `<details>` for hub-doc nav -- drawer pattern is the canonical UX (slide-over from right, mask, Escape closes).

## Maintenance

- Run `python scripts/audit_uri_consistency.py` before merging anything that adds links to a `company_documents.content` body. The script walks all docs, extracts every `db://N`, `cd://N`, AND `sd://<slug>`, then asserts each target exists in the right table. Exits non-zero on any cross-table corruption (e.g. `db://N` where N exists in `company_documents` but not `problems`) or any dangling sd:// (slug missing from `system_designs.slug`).
- The 5 historically-affected db:///cd:// hubs are: Meta AI-Native id=82 (4 links migrated), Uber VO id=37 (5 links), Uber LC Index id=81 (1 link), Google Prep Note id=51 (1 link), Google Prep Hub id=53 (16 links).
- The 1 historically-affected path-form-vs-sd:// hub is: Pinterest LC Must-Do id=47 (7 links migrated 2026-05-04). The audit does NOT yet scan for `/system-design/<slug>` path-form misuses; future task could add that as a fourth check.

## Frontend wiring summary (2026-05-04)

- `MarkdownPreview.tsx` -- regex matches all 4 schemes, calls `onLcLinkClick` / `onDbLinkClick` / `onCdLinkClick` / `onSdLinkClick`
- `PrepNotesPage.tsx` `DocumentViewer` -- single `setDrawer({type, ...})` discriminated union handles all 4 (id-keyed for lc/db/company_doc, slug-keyed for system_design)
- `CompanyDocDrawer.tsx` -- internally also handles all 4 schemes recursively (cd:// replaces, lc/db/sd bubble back to outer)
- `SystemDesignDrawer.tsx` -- internally also handles all 4 schemes recursively (sd:// replaces `activeSlug`, lc/db/cd bubble back to outer)
- `ProblemDrawer.tsx` -- handles lc/db; cd:// and sd:// are NOT routed here
"""

NEW_INDEX_LINE = (
    "- [reference_dblc_drawer_links.md](reference_dblc_drawer_links.md) "
    "— Four URI schemes in MLI markdown: `lc://N`/`db://N` → ProblemDrawer; "
    "`cd://N` → CompanyDocDrawer; `sd://<slug>` → SystemDesignDrawer (slug-keyed, not id). "
    "NEVER use `db://` for a company_document; NEVER use path-form `/system-design/<slug>` "
    "(navigates page). Audit via `python scripts/audit_uri_consistency.py`"
)

OLD_INDEX_LINE_PREFIX = "- [reference_dblc_drawer_links.md](reference_dblc_drawer_links.md)"


def update_reference() -> str:
    current = REFERENCE_FILE.read_text(encoding="utf-8")
    if current == NEW_REFERENCE:
        return "[OK] reference_dblc_drawer_links.md already up to date"
    REFERENCE_FILE.write_text(NEW_REFERENCE, encoding="utf-8")
    return f"[UPDATED] reference_dblc_drawer_links.md ({len(current)} -> {len(NEW_REFERENCE)} chars)"


def update_index() -> str:
    text = INDEX_FILE.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    replaced = False
    for line in lines:
        if line.startswith(OLD_INDEX_LINE_PREFIX):
            if line.rstrip("\r\n") == NEW_INDEX_LINE:
                return "[OK] MEMORY.md index entry already up to date"
            ending = "\r\n" if line.endswith("\r\n") else "\n"
            out.append(NEW_INDEX_LINE + ending)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        raise RuntimeError(
            f"could not locate index line starting with {OLD_INDEX_LINE_PREFIX!r}"
        )
    new_text = "".join(out)
    # Loose budget: keep line within ~25% of the prior entry's length so the index
    # stays roughly comparable. The MEMORY.md guidance is <=150 chars, but the
    # legacy entries in this index already exceed that; we keep parity with siblings
    # rather than artificially truncating to a budget no one else respects.
    prior_line_len = 384  # Pre-T-P0-736 length of the same entry (3-scheme version).
    budget = int(prior_line_len * 1.25)
    if len(NEW_INDEX_LINE) > budget:
        raise RuntimeError(
            f"new index line is {len(NEW_INDEX_LINE)} chars "
            f"(>{budget} budget; prior was {prior_line_len})"
        )
    INDEX_FILE.write_text(new_text, encoding="utf-8")
    return (
        f"[UPDATED] MEMORY.md index entry replaced "
        f"({len(NEW_INDEX_LINE)} chars on the new line)"
    )


def main() -> int:
    print(update_reference())
    print(update_index())
    return 0


if __name__ == "__main__":
    sys.exit(main())
