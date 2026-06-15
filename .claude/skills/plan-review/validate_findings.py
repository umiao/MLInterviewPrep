#!/usr/bin/env python3
"""Deterministic validator for plan-review axis-1 findings JSON (T-P0-388 AC1).

The /plan-review skill spawns a FRESH context-free subagent per task (axis-1,
refute-by-default). Each subagent returns AC-level findings JSON. This module is
the deterministic contract gate between that LLM output and the rest of the
pipeline (T4 adjudication, T5 events.jsonl writeback, T6 incremental review):
LLM judgement in, machine-checkable shape out. It owns ONLY objective structural
checks (bearing wall) -- it never judges whether a concern is *correct* (that is
T4's audit + the user's call).

Contract (mirrors findings_schema.json):
- top level: {run_id:str, round:int in {1,2}, findings:[...]}
- each finding: {task, ac, dimension, verdict, severity, confidence, evidence,
  suggested_fix, route}; task may be null ONLY for a global/cross-task finding
  (added by T4's global pass), ac may be null for a task-level finding.
- verdict terminal set = {pass, concern} (AC1). 'defer' is the NON-terminal
  sentinel reserved for subjective items (AC5) -- the machine must not pronounce
  a terminal verdict on a subjective matter. No 'fail' (objective fail -> L0;
  subjective fail does not exist).
- dimension is the NATURE of a finding {objective, subjective}; harden-L0 is a
  ROUTE, not a dimension -- a harden-L0 item is an OBJECTIVE defect L0 missed
  (AC6: "a reviewer-found OBJECTIVE defect ... gets route=harden-L0").
- coupling invariants encode T3 AC5 / AC6:
    subjective  <=> verdict=defer  AND route=human
    objective    => verdict in {pass,concern}
    route=harden-L0 => dimension=objective AND verdict=concern  (AC6)
    verdict=pass    => route=none ; verdict=concern => route in {human,harden-L0}

Usage:
    python validate_findings.py findings.json        # exit 0 valid / 1 invalid
    python validate_findings.py findings.json --json  # machine-readable report

Importable:
    errs = validate_findings(obj)            # list[str], empty == valid
    obj, errs = load_and_validate(path)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VERDICTS = {"pass", "concern", "defer"}
TERMINAL_VERDICTS = {"pass", "concern"}
SEVERITIES = {"low", "med", "high"}
CONFIDENCES = {"low", "med", "high"}
DIMENSIONS = {"objective", "subjective"}
ROUTES = {"none", "human", "harden-L0"}
REQUIRED_FINDING_KEYS = {
    "task", "ac", "dimension", "verdict", "severity",
    "confidence", "evidence", "suggested_fix", "route",
}


def validate_finding(f: object, idx: int) -> list[str]:
    """Validate one finding dict; return human-readable error messages.

    Args:
        f: The finding (expected dict).
        idx: Position in findings[] (for messages).

    Returns:
        List of error strings (empty == valid).
    """
    where = f"findings[{idx}]"
    if not isinstance(f, dict):
        return [f"{where}: not an object"]

    errs: list[str] = []
    missing = REQUIRED_FINDING_KEYS - set(f.keys())
    if missing:
        errs.append(f"{where}: missing key(s): {', '.join(sorted(missing))}")
        # Without the full key set, downstream coupling checks are unsafe.
        return errs

    task = f["task"]
    # task is null ONLY for a genuinely plan-level / cross-task (global) finding
    # (added by T4's global pass); axis-1 per-task findings always set it.
    if task is not None and (not isinstance(task, str) or not task.strip()):
        errs.append(f"{where}.task: must be null (global) or a non-empty string")

    ac = f["ac"]
    if ac is not None and (not isinstance(ac, str) or not ac.strip()):
        errs.append(f"{where}.ac: must be null or a non-empty string")

    dim = f["dimension"]
    if dim not in DIMENSIONS:
        errs.append(f"{where}.dimension: {dim!r} not in {sorted(DIMENSIONS)}")

    verdict = f["verdict"]
    if verdict not in VERDICTS:
        errs.append(
            f"{where}.verdict: {verdict!r} not in {sorted(VERDICTS)} "
            "(note: 'fail' is intentionally absent)"
        )

    if f["severity"] not in SEVERITIES:
        errs.append(f"{where}.severity: {f['severity']!r} not in {sorted(SEVERITIES)}")

    if f["confidence"] not in CONFIDENCES:
        errs.append(f"{where}.confidence: {f['confidence']!r} not in {sorted(CONFIDENCES)}")

    route = f["route"]
    if route not in ROUTES:
        errs.append(f"{where}.route: {route!r} not in {sorted(ROUTES)}")

    evidence = f["evidence"]
    if not isinstance(evidence, str) or not evidence.strip():
        errs.append(f"{where}.evidence: must be a non-empty string (cite a concrete AC/Verification)")

    sfix = f["suggested_fix"]
    if not isinstance(sfix, str):
        errs.append(f"{where}.suggested_fix: must be a string")

    # ---- coupling invariants (only run when enums are individually valid) ----
    enums_ok = dim in DIMENSIONS and verdict in VERDICTS and route in ROUTES
    if not enums_ok:
        return errs

    if dim == "subjective":
        if verdict != "defer":
            errs.append(
                f"{where}: dimension=subjective requires verdict='defer' "
                "(no terminal verdict on a subjective matter, AC5)"
            )
        if route != "human":
            errs.append(f"{where}: dimension=subjective requires route='human' (AC5)")
    else:
        if verdict == "defer":
            errs.append(
                f"{where}: verdict='defer' is reserved for dimension=subjective "
                f"(got dimension={dim!r})"
            )

    # harden-L0 is a ROUTE, not a dimension: an OBJECTIVE defect L0 missed (AC6).
    if route == "harden-L0":
        if dim != "objective":
            errs.append(f"{where}: route=harden-L0 requires dimension=objective (AC6)")
        if verdict != "concern":
            errs.append(f"{where}: route=harden-L0 requires verdict=concern (AC6)")

    if verdict == "pass" and route != "none":
        errs.append(f"{where}: verdict='pass' must have route='none', got {route!r}")
    if verdict == "concern" and route not in {"human", "harden-L0"}:
        errs.append(f"{where}: verdict='concern' must route to 'human' or 'harden-L0', got {route!r}")

    if verdict in {"concern", "defer"} and isinstance(sfix, str) and not sfix.strip():
        errs.append(f"{where}: verdict={verdict!r} requires a non-empty suggested_fix")

    return errs


def validate_findings(obj: object) -> list[str]:
    """Validate a full findings document; return all error messages.

    Args:
        obj: Parsed JSON (expected the top-level findings object).

    Returns:
        List of error strings (empty == valid).
    """
    if not isinstance(obj, dict):
        return ["top-level: not an object"]

    errs: list[str] = []

    run_id = obj.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("run_id: must be a non-empty string")

    rnd = obj.get("round")
    if rnd not in (1, 2):
        errs.append(f"round: {rnd!r} must be 1 or 2")

    findings = obj.get("findings")
    if not isinstance(findings, list):
        errs.append("findings: must be a list")
        return errs

    tr = obj.get("tasks_reviewed")
    if tr is not None and not (isinstance(tr, list) and all(isinstance(x, str) for x in tr)):
        errs.append("tasks_reviewed: must be a list of strings when present")

    for i, f in enumerate(findings):
        errs.extend(validate_finding(f, i))

    return errs


def load_and_validate(path: str | Path) -> tuple[object, list[str]]:
    """Load JSON from path and validate it.

    Args:
        path: Path to a findings JSON file.

    Returns:
        (parsed_obj_or_None, errors). A parse/IO failure yields (None, [msg]).
    """
    p = Path(path)
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"file not found: {p}"]
    except json.JSONDecodeError as e:
        return None, [f"invalid JSON: {e}"]
    except OSError as e:
        return None, [f"cannot read {p}: {e}"]
    return obj, validate_findings(obj)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Validate plan-review findings JSON (L1 contract).")
    ap.add_argument("path", help="findings JSON file")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args()

    obj, errs = load_and_validate(args.path)
    if args.json:
        print(json.dumps({"ok": not errs, "errors": errs}, ensure_ascii=False, indent=2))
    else:
        if errs:
            print(f"[FAIL] {len(errs)} error(s):")
            for e in errs:
                print(f"  - {e}")
        else:
            n = len(obj.get("findings", [])) if isinstance(obj, dict) else 0
            print(f"[PASS] findings valid ({n} finding(s)).")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
