#!/usr/bin/env python3
"""plan-review L3 (T-P1-390): routing + provenance writeback + T0 signal.

At /plan-review close, this turns the adjudicated findings into governance
actions, reusing the existing gates rather than inventing new ones:

- AC1/AC4 routing: a task carrying >=1 (kept|added) route=human finding is gated
  human_review=1 (via ``task_db.py mark-review`` -- NOT park; it stays pickable
  for the user's decision). A task whose findings are all pass / no route=human
  stays ready (released).
- AC2 provenance: each surfaced concern appends ONE events.jsonl line (reusing
  scripts/lib/events.py) carrying {artifact_hash, model_ver, prompt_ver, ts,
  verdict, evidence, ...}. The provenance field set is sized for T6 incremental
  re-review; if T6 is downgraded, slim this to a lightweight event log.
- AC3 lifecycle: an undecided concern defaults to fail-open-with-record -- the
  plan proceeds, the concern stays logged (disposition='pending') and visible,
  owned by its hr=1 task; it never silently drops.
- AC5 hardline: this module NEVER completes a task. It only sets the gate +
  records. Finishing an hr=1 task stays the user's ``complete --reviewer`` action
  (enforced by task_store.complete_task / update).
- AC6 T0 signal: the user's accept/reject of a surfaced concern is appended as a
  later concern line (disposition accepted|dismissed); ``summary`` derives the
  rolling acceptance_rate as a by-product -- no separate labelling step.

The DECISION (which task routes where) is pure + unit-tested (``plan_routing``);
the EFFECTS (shell mark-review, append events) are thin wrappers over the public
CLI / the shared events lib.

CLI:
    route <adjudicated.json> [--prompt-ver V] [--model-ver V]   # AC1/AC2/AC3
    record-disposition <run> <task> <ac|-> <accepted|dismissed> # AC6
    summary [--json]                                            # T0 signal
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

# plan-review lives at .claude/skills/plan-review/ -> root is parents[3].
ROOT = Path(__file__).resolve().parents[3]
TASK_DB = ROOT / ".claude" / "hooks" / "task_db.py"
CONCERN_KIND = "plan_review_concern"

# T0 kill-criterion hyperparameters (DR-plan-review-T0 §4); explicit + tunable.
TAU = 0.30   # acceptance-rate trip threshold
W = 3        # window = last W qualifying runs
S = 10       # significance floor = >= S decided concerns in the window

DECIDED = {"accepted", "dismissed"}


def content_hash(text: str) -> str:
    """SHA-256 hex of a task description (provenance + T6 cache key)."""
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _kept(f: dict) -> bool:
    """A finding that survived T4 adjudication (kept or added, not discarded)."""
    return f.get("adjudication", "kept") != "discarded"


# --------------------------------------------------------------------------- #
# AC1 / AC4 -- pure routing decision
# --------------------------------------------------------------------------- #
def plan_routing(adjudicated: dict) -> dict:
    """Decide routing from adjudicated findings (pure; no side effects).

    Args:
        adjudicated: the round-2 adjudicated findings doc.

    Returns:
        {
          "tasks_to_review": [task_id, ...],   # AC1: have a kept route=human
          "tasks_released":  [task_id, ...],   # AC4 else: reviewed, no route=human
          "concerns":        [finding, ...],   # kept route=human (incl. global)
        }
    All lists are sorted / order-stable for deterministic tests.
    """
    findings = adjudicated.get("findings", []) if isinstance(adjudicated, dict) else []
    reviewed = list(adjudicated.get("tasks_reviewed", []) or [])

    concerns = [f for f in findings if _kept(f) and f.get("route") == "human"]
    tasks_to_review = sorted({
        f["task"] for f in concerns
        if f.get("task")  # global (task=null) concerns have no single owner
    })
    review_set = set(tasks_to_review)
    # AC4 else-branch: a reviewed task with no route=human finding is released.
    tasks_released = sorted(t for t in set(reviewed) if t and t not in review_set)
    return {
        "tasks_to_review": tasks_to_review,
        "tasks_released": tasks_released,
        "concerns": concerns,
    }


# --------------------------------------------------------------------------- #
# AC2 / AC3 / AC6 -- events
# --------------------------------------------------------------------------- #
def concern_event(
    run_id: str,
    finding: dict,
    *,
    ts: str,
    disposition: str,
    prompt_ver: str,
    model_ver: str,
    artifact_hash: str | None,
    project_id: str = "root",
    actor: str = "plan-review",
) -> dict:
    """Build one events.jsonl payload for a surfaced concern (pure).

    Carries the events.py REQUIRED_FIELDS (ts/project_id/task_id/from_state/
    to_state/actor) plus the plan-review provenance fields. to_state = the
    concern's disposition so the line reads as a state transition; kind tags it.
    A global (task=null) concern uses task_id='PLAN' so the required field is
    present and the event is queryable.
    """
    return {
        "ts": ts,
        "project_id": project_id,
        "task_id": finding.get("task") or "PLAN",
        "from_state": None,
        "to_state": disposition,
        "actor": actor,
        "kind": CONCERN_KIND,
        "run_id": run_id,
        "ac_ref": finding.get("ac"),
        "dimension": finding.get("dimension"),
        "verdict": finding.get("verdict"),
        "severity": finding.get("severity"),
        "evidence": finding.get("evidence"),
        "disposition": disposition,
        "artifact_hash": artifact_hash,
        "prompt_ver": prompt_ver,
        "model_ver": model_ver,
    }


def _events_append(root: Path, payload: dict) -> None:
    """Append one line via the shared events lib (raises on hard failure -- AC edge)."""
    sys.path.insert(0, str(root / "scripts"))
    try:
        from lib import events  # noqa: PLC0415
    finally:
        try:
            sys.path.remove(str(root / "scripts"))
        except ValueError:
            pass
    events.append(root, payload)


def _now_iso(root: Path) -> str:
    sys.path.insert(0, str(root / "scripts"))
    try:
        from lib import events  # noqa: PLC0415
        return events.now_iso()
    finally:
        try:
            sys.path.remove(str(root / "scripts"))
        except ValueError:
            pass


# --------------------------------------------------------------------------- #
# T0 signal summary (DR-plan-review-T0)
# --------------------------------------------------------------------------- #
def _concern_key(evt: dict) -> tuple:
    return (evt.get("run_id"), evt.get("task_id"), evt.get("ac_ref"))


def summarize_events(events_iter, *, tau: float = TAU, w: int = W, s: int = S) -> dict:
    """Compute the T0 acceptance-rate + kill-criterion verdict (pure).

    Args:
        events_iter: iterable of event dicts (chronological).
        tau/w/s: kill-criterion hyperparameters (DR §4).

    Returns:
        {acceptance_rate|None, decided, accepted, dismissed, runs_in_window,
         status in {working, insufficient_data, quarantine_trip}, tau, w, s}.

    The LATEST disposition per concern key wins (a later accept/reject overrides
    the initial 'pending'); 'pending' concerns are not counted (fail-open, AC3).
    Window = the last `w` QUALIFYING runs (a run with >=1 decided concern).
    """
    # latest disposition per concern, in first-seen run order.
    latest: "OrderedDict[tuple, str]" = OrderedDict()
    run_order: "OrderedDict[str, None]" = OrderedDict()
    for evt in events_iter:
        if evt.get("kind") != CONCERN_KIND:
            continue
        run_order.setdefault(evt.get("run_id"), None)
        latest[_concern_key(evt)] = evt.get("disposition")

    # group decided concerns by run.
    per_run: "OrderedDict[str, list[str]]" = OrderedDict((r, []) for r in run_order)
    for (run_id, _t, _a), disp in latest.items():
        if disp in DECIDED:
            per_run.setdefault(run_id, []).append(disp)

    qualifying = [r for r in run_order if per_run.get(r)]
    window_runs = qualifying[-w:]
    window = [d for r in window_runs for d in per_run.get(r, [])]

    accepted = sum(1 for d in window if d == "accepted")
    dismissed = sum(1 for d in window if d == "dismissed")
    decided = accepted + dismissed

    out = {
        "tau": tau, "w": w, "s": s,
        "runs_in_window": len(window_runs),
        "accepted": accepted, "dismissed": dismissed, "decided": decided,
        "acceptance_rate": None, "status": "insufficient_data",
    }
    if decided < s:
        return out  # AC edge: never render sample-too-small as false green.
    rate = accepted / decided
    out["acceptance_rate"] = round(rate, 4)
    out["status"] = "working" if rate >= tau else "quarantine_trip"
    return out


def summary(root: Path, *, tau: float = TAU, w: int = W, s: int = S) -> dict:
    """Read events.jsonl and summarize the T0 signal."""
    sys.path.insert(0, str(root / "scripts"))
    try:
        from lib import events  # noqa: PLC0415
        it = events.iter_events(root, include_rotated=True)
        return summarize_events(it, tau=tau, w=w, s=s)
    finally:
        try:
            sys.path.remove(str(root / "scripts"))
        except ValueError:
            pass


# --------------------------------------------------------------------------- #
# Effects (thin wrappers over the public CLI / events lib)
# --------------------------------------------------------------------------- #
def set_human_review(root: Path, task_id: str) -> dict:
    """Gate a task hr=1 via the public CLI (AC1 'call task_db.py').

    Requires the `mark-review` verb (and task_store.mark_for_review). That lives
    in the canonical root task_db.py/task_store.py, which are deliberately NOT
    propagated by the plan-review pattern (deferred to the task_db unification,
    T-P2-321). So in a sub-project that predates them, this returns ok=False and
    L3 routing is inert there until task_db catches up -- L0/L1/L2 still work.
    The failure is surfaced (ok=False), never silently swallowed.
    """
    proc = subprocess.run(
        [sys.executable, str(TASK_DB), "mark-review", task_id],
        capture_output=True, text=True, cwd=str(root),
    )
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {"ok": False, "task_id": task_id, "raw": proc.stdout, "err": proc.stderr}


def apply_routing(
    root: Path, adjudicated: dict, *, prompt_ver: str, model_ver: str,
) -> dict:
    """Execute routing: gate hr=1 tasks + append a pending concern line each."""
    plan = plan_routing(adjudicated)
    run_id = adjudicated.get("run_id", "?")
    ts = _now_iso(root)
    descriptions = adjudicated.get("task_descriptions", {}) or {}

    gated = [set_human_review(root, t) for t in plan["tasks_to_review"]]
    for f in plan["concerns"]:
        ah = content_hash(descriptions.get(f.get("task"), "")) if f.get("task") else None
        _events_append(root, concern_event(
            run_id, f, ts=ts, disposition="pending",
            prompt_ver=prompt_ver, model_ver=model_ver, artifact_hash=ah,
        ))
    return {
        "run_id": run_id,
        "gated": gated,
        "released": plan["tasks_released"],
        "concerns_recorded": len(plan["concerns"]),
    }


def record_disposition(
    root: Path, run_id: str, task: str | None, ac: str | None, disposition: str,
    *, prompt_ver: str = "", model_ver: str = "",
) -> None:
    """Append the user's accept/reject of a concern (AC6 -> feeds T0)."""
    if disposition not in DECIDED:
        raise ValueError(f"disposition must be one of {sorted(DECIDED)}, got {disposition!r}")
    finding = {"task": task, "ac": ac, "verdict": "concern"}
    _events_append(root, concern_event(
        run_id, finding, ts=_now_iso(root), disposition=disposition,
        prompt_ver=prompt_ver, model_ver=model_ver, artifact_hash=None,
    ))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="plan-review L3 routing + signal.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("route", help="gate hr=1 + record concern events")
    pr.add_argument("adjudicated", help="adjudicated findings JSON")
    pr.add_argument("--prompt-ver", default="axis1-v1")
    pr.add_argument("--model-ver", default="claude-opus-4-8")

    pd = sub.add_parser("record-disposition", help="record a user accept/reject")
    pd.add_argument("run_id")
    pd.add_argument("task", help="task id, or '-' for a global concern")
    pd.add_argument("ac", help="AC ref, or '-' for task-level")
    pd.add_argument("disposition", choices=sorted(DECIDED))

    ps = sub.add_parser("summary", help="T0 acceptance-rate + kill-criterion verdict")
    ps.add_argument("--json", action="store_true")

    args = ap.parse_args()

    if args.cmd == "route":
        adjudicated = json.loads(Path(args.adjudicated).read_text(encoding="utf-8"))
        out = apply_routing(ROOT, adjudicated,
                            prompt_ver=args.prompt_ver, model_ver=args.model_ver)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif args.cmd == "record-disposition":
        record_disposition(
            ROOT, args.run_id,
            None if args.task == "-" else args.task,
            None if args.ac == "-" else args.ac,
            args.disposition,
        )
        print(json.dumps({"ok": True, "recorded": args.disposition}))
    elif args.cmd == "summary":
        out = summary(ROOT)
        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print(f"acceptance_rate: {out['acceptance_rate']} "
                  f"({out['accepted']}/{out['decided']} decided, "
                  f"{out['runs_in_window']} run(s) in window)")
            print(f"status: {out['status']}  (tau={out['tau']} W={out['w']} S={out['s']})")


if __name__ == "__main__":
    main()
