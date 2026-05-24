#!/usr/bin/env python3
# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-off: add 10 golden-marker tasks (6 P1 + 4 P2) into MLInterviewPrep tasks.db.

All depend on T-P1-549 (iota smoke test) or its downstream, so they wait until
ML Fundamentals content is verified before the curation layer is built.

Re-run safe: skip if title already exists.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DB = REPO_ROOT / ".claude" / "hooks" / "task_db.py"
MLIP = REPO_ROOT / "MLInterviewPrep"

SMOKE_TASK = "T-P1-549"  # iota: 27-drawer smoke test — gate for golden batch


def run_task_db(args: list[str]) -> dict:
    cmd = ["python", str(TASK_DB), *args]
    proc = subprocess.run(
        cmd, cwd=str(MLIP), capture_output=True, text=True,
        encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        print(f"[seed] task_db.py failed: {proc.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(proc.stdout.strip().splitlines()[-1])


def list_existing_titles() -> set[str]:
    cmd = ["python", str(TASK_DB), "list"]
    proc = subprocess.run(
        cmd, cwd=str(MLIP), capture_output=True, text=True,
        encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        return set()
    try:
        rows = json.loads(proc.stdout)
        return {r["title"] for r in rows}
    except Exception:
        return set()


TASKS: list[dict] = [
    # --- P1 batch: framework chain (ship first, validate usefulness) ---
    {
        "key": "g01",
        "title": "[T-GOLD-01] Schema + migration: is_golden + golden_at on framework_nodes / behavioral_examples / company_documents + docs/golden_marker.md",
        "priority": "P1", "complexity": "S",
        "description": (
            "Add curation columns to three tables (single Alembic migration or one-shot Python migration script under scripts/ -- follow existing project convention):\n"
            "  - `framework_nodes.is_golden BOOLEAN NOT NULL DEFAULT 0`\n"
            "  - `framework_nodes.golden_at DATETIME NULL`\n"
            "  - `behavioral_examples.is_golden BOOLEAN NOT NULL DEFAULT 0`\n"
            "  - `behavioral_examples.golden_at DATETIME NULL`\n"
            "  - `company_documents.is_golden BOOLEAN NOT NULL DEFAULT 0`\n"
            "  - `company_documents.golden_at DATETIME NULL`\n\n"
            "Update SQLAlchemy models (src/backend/models/framework.py, behavioral.py, company.py) and Pydantic schemas (src/backend/schemas/*.py) so response shapes include `is_golden` + `golden_at`.\n\n"
            "Also produce `docs/golden_marker.md` (1-2 paragraphs):\n"
            "  - feature intent: curation flag, orthogonal to progress status\n"
            "  - decision rule: user's discretion, NO hard criteria in code\n"
            "  - semantics: toggling false->true refreshes golden_at; true->false keeps golden_at untouched (decided at endpoint layer, see T-GOLD-02)\n\n"
            "AC: migration runs clean on a fresh copy of mle_prep.db; all 3 model classes + update schemas expose is_golden/golden_at; docs file exists; commit includes model + schema + migration + doc."
        ),
        "depends_on": SMOKE_TASK,
    },
    {
        "key": "g02",
        "title": "[T-GOLD-02] Backend PUT endpoints accept is_golden; endpoint-layer golden_at auto-refresh on false->true",
        "priority": "P1", "complexity": "S",
        "description": (
            "Extend three existing PUT endpoints (do NOT add new ones):\n"
            "  - PUT /framework/nodes/{node_id}  (routers/framework.py)\n"
            "  - PUT /companies/{company_id}/documents/{doc_id}  (routers/companies.py)\n"
            "  - PUT /behavioral/examples/{example_id}  (routers/behavioral.py)\n\n"
            "For each: accept partial update with optional `is_golden` in the request body. Business rule at endpoint layer (NOT frontend): when `is_golden` flips from False to True, set `golden_at = datetime.utcnow()`; when True -> False, leave `golden_at` unchanged (so we remember the last time it was canonized). Use UTC timestamps; keep consistent with existing project timestamp convention (check `created_at` handling on these models to match).\n\n"
            "Add pytest tests in tests/test_*_api.py per module: (a) false->true sets golden_at to a recent time; (b) re-PUT with is_golden=true but no flip change does NOT overwrite golden_at; (c) true->false keeps golden_at pinned; (d) false->true after an unmark refreshes golden_at to a new later timestamp.\n\n"
            "AC: 3 endpoints + matching tests green; API docs (if FastAPI auto-docs) reflect new optional fields."
        ),
        "depends_on": "g01",
    },
    {
        "key": "g03",
        "title": "[T-GOLD-03] Frontend <GoldenToggleButton> shared component + orange color tokens",
        "priority": "P1", "complexity": "M",
        "description": (
            "Create src/frontend/src/components/ui/GoldenToggleButton.tsx:\n"
            "  Props: { itemType: 'framework_node' | 'behavioral_example' | 'company_document', itemId: number, isGolden: boolean, className?: string }\n"
            "  Renders an outlined star (not golden) or filled orange star (golden). Click toggles via useMutation + api.put to the matching endpoint (routing by itemType).\n"
            "  Optimistic UI: toggle icon immediately, then invalidate the parent query on success. On error: revert + toast.\n"
            "  React-query invalidation keys MUST cover all 3 consumers (add conditionally by itemType):\n"
            "    - framework_node: ['framework', 'tree'], ['framework', 'node', itemId]\n"
            "    - behavioral_example: ['behavioral', 'examples'], ['behavioral', 'example', itemId]\n"
            "    - company_document: ['companies', <companyId>], ['companies', 'document', itemId]  -- may need to pass companyId as an extra prop; check existing drawer interfaces first\n"
            "  Toast: 'Marked as golden' / 'Removed golden mark'.\n\n"
            "Color palette (fixed, inline Tailwind, NO tailwind.config changes):\n"
            "  Inactive: text-gray-300 hover:text-gray-400 (outlined star)\n"
            "  Active: text-orange-500 (filled star) — matches T-GOLD-04's palette\n\n"
            "AC: component renders + clicks + mutates + toasts in Storybook/manual smoke; 3 invalidation keys verified via React DevTools; `npm run build` clean."
        ),
        "depends_on": "g02",
    },
    {
        "key": "g04",
        "title": "[T-GOLD-04] goldenCardClass(isGolden) helper + golden [star] badge for card lists",
        "priority": "P1", "complexity": "S",
        "description": (
            "Create src/frontend/src/utils/goldenStyle.ts exporting:\n"
            "  goldenCardClass(isGolden: boolean): string  -- returns extra Tailwind className when golden is true:\n"
            "    'bg-orange-50 border-orange-300 border-l-4 border-l-orange-500'\n"
            "  Default (non-golden) returns empty string so the caller can concat without clobbering.\n\n"
            "Also export a <GoldenBadge /> tiny pill component: when golden=true, renders a small filled star icon + 'GOLDEN' text in orange-700 on orange-50, with orange-200 border, matching the existing FREQ_BADGE style on MLFundamentals cards.\n\n"
            "Do NOT apply these anywhere yet -- pure shared utilities. T-GOLD-06 consumes them.\n\n"
            "AC: tsc clean, both exports importable, visual snapshot captured (or a manual screenshot committed under docs/ for reference)."
        ),
        "depends_on": "g02",
    },
    {
        "key": "g05",
        "title": "[T-GOLD-05] Integrate GoldenToggleButton into FrameworkNodeDrawer (audit placement first)",
        "priority": "P1", "complexity": "S",
        "description": (
            "BEFORE coding: take a screenshot of the current FrameworkNodeDrawer header (src/frontend/src/components/framework/FrameworkNodeDrawer.tsx) to assess horizontal space. Save screenshot under docs/golden_placement_audit_<date>.png for the commit.\n\n"
            "Decision rule:\n"
            "  - If header has clear room next to the close (X) button: put GoldenToggleButton there, icon-only, 32x32.\n"
            "  - If header is already cramped (title + status badge + confidence + progress + close): put at the drawer's BOTTOM-RIGHT as a full pill 'Mark as golden' / 'Golden ✓' (text + icon), so it's discoverable but doesn't fight the header.\n\n"
            "In either case: pass the framework_node id + current is_golden to the button; let the shared component (T-GOLD-03) handle mutation and invalidation.\n\n"
            "Also: when drawer is open on a golden node, add a thin orange-300 top border inside the drawer header to echo the card visual (uses goldenCardClass pattern from T-GOLD-04).\n\n"
            "AC: manual test in browser -- click star on a framework_node, it flips + toast + drawer top-border echoes state; re-open a different golden node, star renders filled."
        ),
        "depends_on": "g03,g04",
    },
    {
        "key": "g06",
        "title": "[T-GOLD-06] Integrate into MLFundamentals.tsx cards + ?golden=1 URL filter",
        "priority": "P1", "complexity": "S",
        "description": (
            "Edit src/frontend/src/pages/MLFundamentals.tsx:\n"
            "  1. Fetch is_golden + golden_at per leaf -- the /framework/tree endpoint now returns them (per T-GOLD-01). Extend the INVENTORY consumer to merge is_golden from the query.\n"
            "  2. Apply goldenCardClass(isGolden) to each card button's className; render <GoldenBadge /> (from T-GOLD-04) near the freq badge when is_golden=true.\n"
            "  3. Add a 'Golden only' toggle next to the tab bar. Backed by URL param `?golden=1` (matches existing ?cat=, ?slug= pattern). When active, filter categoryItems to only is_golden rows, regardless of active cat. Count shown in tab labels updates to reflect filtered counts.\n"
            "  4. When ?golden=1 and a tab's filtered count drops to 0, keep the tab button visible but show '(0)'; the empty-state message under the grid says 'No golden items in this category yet.'\n\n"
            "No GoldenToggleButton on individual cards -- card click opens drawer, toggling happens in drawer (T-GOLD-05). Card is a pure read-only surface + visual indicator.\n\n"
            "AC: manual test -- mark 2-3 items golden via drawer, reload with ?golden=1 in URL, only those show; ?golden=1&cat=classical_ml further narrows; URL is shareable (golden state persists)."
        ),
        "depends_on": "g05",
    },
    # --- P2 batch: deferred until P1 validates the pattern is actually useful ---
    {
        "key": "g07a",
        "title": "[T-GOLD-07a] Discovery: scan Behavioral UI for drawer + toggle insertion points",
        "priority": "P2", "complexity": "S",
        "description": (
            "Research-only task, NO code writes. Read:\n"
            "  - src/frontend/src/pages/Behavioral*.tsx (all files matching this glob)\n"
            "  - src/frontend/src/components/behavioral/* (if the dir exists)\n"
            "  - src/backend/routers/behavioral.py (to confirm PUT endpoint shape from T-GOLD-02)\n\n"
            "Produce docs/behavioral_golden_integration_plan.md with:\n"
            "  - Does a BehavioralExampleDrawer component exist? Where?\n"
            "  - If yes: which section is best for the toggle (mirroring T-GOLD-05 rules)?\n"
            "  - If no: what's the current 'view a story' UX (modal? inline expand?)? Does it need a new drawer, or can we attach the toggle to the inline view?\n"
            "  - React-query cache keys used today for behavioral queries (for invalidation planning).\n"
            "  - Card list rendering location — where to apply goldenCardClass + GoldenBadge (analogous to T-GOLD-06)?\n"
            "  - Estimated complexity for T-GOLD-07b: S / M / L, with reasoning.\n\n"
            "AC: markdown file with 5 sections answering the above, committed with no other changes."
        ),
        "depends_on": "g06",
    },
    {
        "key": "g07b",
        "title": "[T-GOLD-07b] Behavioral UI integration: drawer toggle + card visuals + filter",
        "priority": "P2", "complexity": "M",
        "description": (
            "Execute the plan from T-GOLD-07a. Expected work surface:\n"
            "  - Add <GoldenToggleButton itemType='behavioral_example' /> to the behavioral story viewer (drawer or inline).\n"
            "  - Apply goldenCardClass + <GoldenBadge /> to behavioral card lists.\n"
            "  - Add ?golden=1 URL filter to whichever page lists behavioral examples.\n\n"
            "Follow the exact visual + interaction pattern from T-GOLD-05/06 so the UX feels consistent across the app. Adjust complexity in flight if 07a surfaces unexpected structure -- the 07a plan is authoritative for this task's scope.\n\n"
            "AC: manual test -- mark a behavioral story golden, see badge on card + filled star in drawer + ?golden=1 filter works."
        ),
        "depends_on": "g07a",
    },
    {
        "key": "g08",
        "title": "[T-GOLD-08] Company docs integration: drawer toggle + card visuals (no filter on index pages)",
        "priority": "P2", "complexity": "S",
        "description": (
            "Add <GoldenToggleButton itemType='company_document' /> to whatever view renders a company_document in full (prep note page / hub doc drawer). Apply goldenCardClass + <GoldenBadge /> to any place where docs are listed as cards (e.g., Prep Notes index per-company).\n\n"
            "DO NOT add ?golden=1 filter here -- company docs are browsed per-company, not across the whole app. The Golden Collection page (T-GOLD-09) is the aggregator.\n\n"
            "Invalidation needs the companyId: pass it as an extra prop to GoldenToggleButton; if T-GOLD-03 didn't already wire this, add the prop now as a follow-up edit.\n\n"
            "AC: mark Google Hub id=53 as golden via UI; star renders filled on reload; other company doc lists show orange-tinted cards for any golden doc."
        ),
        "depends_on": "g07b",
    },
    {
        "key": "g09",
        "title": "[T-GOLD-09] Golden Collection aggregator page (backend /golden endpoint + frontend page)",
        "priority": "P2", "complexity": "M",
        "description": (
            "Backend: add GET /golden router endpoint that unions rows from the 3 tables where is_golden=true, normalized into a uniform response:\n"
            "  [{ id, item_type: 'framework_node'|'behavioral_example'|'company_document', title, preview (first 200 chars of content/description), golden_at, url_path (for deep-linking: e.g. '/ml-fundamentals?cat=...&slug=...' or '/behavioral?id=...' or '/companies/<id>/documents/<id>') }]\n"
            "  Sort by golden_at DESC. Implement in src/backend/routers/golden.py; mount in main.py.\n\n"
            "Frontend: create src/frontend/src/pages/GoldenCollection.tsx. Three tabs (framework_nodes / behavioral / company_docs) + 'All' tab at position 0 (matching MLFundamentals pattern). Each card is clickable and navigates to the url_path from the API. Empty state per tab: 'No items marked golden in this category yet.'\n\n"
            "Sidebar: add { to: '/golden', label: 'Golden' } nav item near the top (above Framework or between Fundamentals and LeetCode).\n\n"
            "AC: mark 3+ items across 3 different tables; /golden page shows all with correct per-tab filtering; clicking a card deep-links to the correct origin page; empty tabs display the friendly message."
        ),
        "depends_on": "g08",
    },
]


def main() -> None:
    existing = list_existing_titles()
    key_to_id: dict[str, str] = {}
    created = 0
    skipped = 0

    # Resolve 'depends_on' strings: if they start with "T-", literal task id; otherwise a key to resolve
    def resolve_dep(dep_field: str | None) -> str | None:
        if not dep_field:
            return None
        parts = [p.strip() for p in dep_field.split(",")]
        resolved = []
        for p in parts:
            if p.startswith("T-"):
                resolved.append(p)
            else:
                if p not in key_to_id:
                    # Maybe the prior task was skipped as a duplicate; try to look up
                    for row in json.loads(subprocess.run(
                        ["python", str(TASK_DB), "list"],
                        cwd=str(MLIP), capture_output=True, text=True,
                        encoding="utf-8", check=False,
                    ).stdout):
                        for spec in TASKS:
                            if row["title"] == spec["title"] and spec["key"] == p:
                                key_to_id[p] = row["id"]
                                resolved.append(row["id"])
                                break
                        if p in key_to_id:
                            break
                if p in key_to_id:
                    resolved.append(key_to_id[p])
                else:
                    print(f"[seed] ERROR: cannot resolve dep key '{p}'", file=sys.stderr)
                    sys.exit(1)
        return ",".join(resolved)

    for spec in TASKS:
        title = spec["title"]
        if title in existing:
            print(f"[seed] skip (exists): {title[:80]}")
            skipped += 1
            continue

        args = [
            "add",
            "--title", title,
            "--priority", spec["priority"],
            "--complexity", spec["complexity"],
            "--description", spec["description"],
        ]
        dep = resolve_dep(spec.get("depends_on"))
        if dep:
            args += ["--depends-on", dep]

        result = run_task_db(args)
        new_id = result["id"]
        key_to_id[spec["key"]] = new_id
        safe_title = title[:80].encode("ascii", "replace").decode("ascii")
        print(f"[seed] created {new_id}: {safe_title}")
        created += 1

    print(f"\n[seed] DONE: {created} created, {skipped} skipped")
    if created:
        print("[seed] chain:")
        for spec in TASKS:
            tid = key_to_id.get(spec["key"], "?")
            dep = spec.get("depends_on", "-")
            print(f"  {spec['key']:6s} -> {tid}  (depends on: {dep})")


if __name__ == "__main__":
    main()
