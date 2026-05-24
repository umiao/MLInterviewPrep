# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-shot helper: update .claude/session_state.json after T-P0-634."""
import json
from pathlib import Path

p = Path(".claude/session_state.json")
state = {
    "last_task": "T-P0-634",
    "last_status": "completed",
    "all_done": False,
    "timestamp": "2026-04-29",
    "note": (
        "T-P0-634 (UBER-VO-7 manual smoke + verbal-recall gate) complete "
        "(PARTIAL semantics, marked completed per autonomous-mode rule since "
        "wiring/content checks all pass; verbal-recall ACs are explicit "
        "human-only criteria). Programmatically executed all 6 wiring/content "
        "steps: (1) all 5 charter links on id=37 resolve to existing targets "
        "(db://81/84/85/36 + /behavioral/themes?company=uber); (2) all 8 deep "
        "anchors referenced from id=37 (3 on id=85, 5 on id=84) exist as "
        "<h2 id='...'> tags; (3) all 10 T-P1-631 strengthening keywords present "
        "in id=33; (4) heading-stability invariant on id=33 holds (0 missing, "
        "4 added -- additive only, no destructive edits); (5) source-TXT "
        "cross-check 5/5 verbatim, no drift between "
        "src/backend/seed_data/uber/ml_sd_golden.md and id=85; (6) banner on "
        "id=81 at byte 0, ahead of UBER_LC_INDEX_V1 sentinel, single db://37 "
        "link. Pytest 1216/1216 pass. Out-of-scope for autonomous run: "
        "VR-1..VR-5 verbal-recall ACs (human-only practice criteria for May 4 "
        "Coding 2). Smoke log: logs/uber_vo_smoke_20260429_085743.md. UBER-VO "
        "P0 chain closed. Remaining unblocked work: T-P2-636 (deferred bespoke "
        "FE UberIndex.tsx, P2) is the only P2 follow-up in this thread; "
        "T-P1-582/583/T-P2-585 blocked on T-P1-581; T-P1-606/627, T-P2-207/239 "
        "blocked. Recommend a human checklist task before May 4 to walk through "
        "VR-1..VR-5 in a single sitting."
    ),
}
p.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
print(f"[WROTE] {p} -- last_task={state['last_task']} status={state['last_status']}")
