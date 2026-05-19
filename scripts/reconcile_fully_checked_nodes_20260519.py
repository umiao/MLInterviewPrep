"""Table-wide reconcile sweep for fully-checked KG-Framework leaves.

Source: review of the 2026-05-19 node-44 drift class (Discord) + the
T-P0-914 root-cause note (``logs/review/T-P0-914_drift_rootcause_
20260519.md``). An automated full-table write needs a
``--dry-run -> diff -> human review -> --apply -> audit log`` lifecycle,
because the 911 blast radius (every drifted leaf, table-wide) is orders
of magnitude above the single node-44 fix.

What this tool does (and does NOT do)
-------------------------------------
It promotes every **fully-checked leaf whose status was never derived to
``mastered``** -- the unambiguous "Class A / visual-lag" drift (e.g.
nodes 111, 114; node 44 was already fixed by the dedicated script). It
delegates 100% of the reconcile logic to
``scripts.lib.framework_progress.reconcile_all_fully_checked`` (the
single tested T-P0-910 helper); there is **zero inline reconcile logic**
here -- this file is only a dry-run/apply driver, a diff renderer, an
AC2 scope guard, and an audit-log writer.

Scope is pinned (T-P0-911 AC2, Review point B, verbatim). The sweep
**MUST NOT** mutate the ambiguous drift classes:

* **reverse** -- ``progress_pct > 0`` with **0** boxes checked (the
  115/171 shape). Origin is an untraceable pre-Invariant-3 direct write
  (T-P0-914 AC3); silently zeroing it is itself data loss. **Out.**
* **partial-stale** -- ``0 < checked < total`` (e.g. node 92, 7/15).
  Not terminal; reconciling it would *promote-only* but the batch class
  is deliberately fully-checked-only. **Out.**
* **no-checklist drift** -- ``0/0`` boxes with drifted status (node 69).
  No checkbox dimension to reconcile from. **Out.**

These exclusions are not merely documented: :func:`assert_scope_pinned`
hard-asserts (in code, before any commit) that the changed leaf set is a
subset of the deterministic fully-checked signature and disjoint from
all three excluded classes. ``tests/test_reconcile_fully_checked_
sweep.py`` proves it.

Modes
-----
* ``--dry-run`` (DEFAULT): computes the would-change diff inside an
  uncommitted transaction, **rolls back** (zero DB writes), and writes a
  human-readable diff report to ``logs/review/``. This is the *only*
  mode T-P0-911 runs; reviewing that report gates the human-approved
  apply (T-P0-915).
* ``--apply``: timestamped ``mle_prep.db`` ``.bak`` -> commit ->
  append a structured JSONL audit record. **Reserved for the
  human-gated T-P0-915; not run by T-P0-911.**

Not hardcoded (AC5): the would-change set is discovered by *signature
over the whole table* via the shared helper -- node ids 111/114 are
never enumerated literally; a newly-drifted node is picked up
automatically and a fixed node stops matching.

Idempotent (AC6): a re-run after a hypothetical apply finds zero
fully-checked-unreconciled leaves, so the diff is empty and the report
says "nothing to reconcile".

Run (dry-run, the T-P0-911 deliverable)::

    python scripts/reconcile_fully_checked_nodes_20260519.py --dry-run

Run (apply -- T-P0-915 only, human-gated)::

    python scripts/reconcile_fully_checked_nodes_20260519.py --apply
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib.framework_progress import (  # noqa: E402
    count_checkboxes,
    reconcile_all_fully_checked,
)

from src.backend.config import get_settings  # noqa: E402
from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402

REPORT_DIR = PROJECT_ROOT / "logs" / "review"
# Fixed (dated) name so an idempotent re-run overwrites the same committed
# deliverable instead of spamming timestamped copies (matches the
# T-P0-914 logs/review/*_20260519.md naming convention).
REPORT_PATH = REPORT_DIR / "reconcile_fully_checked_dryrun_20260519.md"
AUDIT_PATH = PROJECT_ROOT / "logs" / "reconcile_fully_checked_audit.jsonl"


class ScopeViolationError(RuntimeError):
    """Raised when the changed leaf set escapes the AC2 pinned scope.

    A defense-in-depth tripwire: if the shared helper ever regressed and
    touched a reverse / partial-stale / no-checklist node, this aborts
    the run *before* any commit so the ambiguous classes can never be
    silently mutated by the sweep.
    """


@dataclass(frozen=True)
class NodeState:
    """Immutable snapshot of one framework node's reconcile-relevant state.

    Attributes:
        status: ``framework_nodes.status`` at snapshot time.
        progress_pct: ``framework_nodes.progress_pct`` (``None`` coerced
            to ``0.0`` on capture so diffs compare cleanly).
        started_at: ISO string of ``started_at`` or ``None``.
        completed_at: ISO string of ``completed_at`` or ``None``.
        checked: Number of checked checkboxes in the description.
        total: Total checkboxes (checked + unchecked).
        path: ``framework_nodes.path`` (for human-readable reporting).
        is_leaf: ``True`` if no other node lists this node as its
            parent. A parent node legitimately carries a rolled-up
            status via ``_propagate_upward`` -- that is NOT drift, so
            the no-checklist class is leaf-only (matches T-P0-914,
            which names exactly node 69).
    """

    status: str
    progress_pct: float
    started_at: str | None
    completed_at: str | None
    checked: int
    total: int
    path: str
    is_leaf: bool


def resolve_db_path() -> Path:
    """Resolve the live SQLite file from ``settings.DATABASE_URL``.

    Used only for the ``--apply`` ``.bak`` (AC4); the dry-run never
    touches the file. Falls back to the canonical ``data/mle_prep.db``
    if the URL is not a recognizable ``sqlite:///`` path.

    Returns:
        Absolute path to the SQLite database file.
    """
    url = get_settings().DATABASE_URL
    prefix = "sqlite:///"
    if url.startswith(prefix):
        raw = url[len(prefix):]
        p = Path(raw)
        return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()
    return (PROJECT_ROOT / "data" / "mle_prep.db").resolve()


def _iso(value: object) -> str | None:
    """Render a datetime-ish column value as an ISO string or ``None``."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def snapshot_states(db) -> dict[int, NodeState]:
    """Capture every framework node's reconcile-relevant state.

    Returns immutable :class:`NodeState` copies so a snapshot taken
    *before* :func:`reconcile_all_fully_checked` is unaffected by the
    in-session mutation that follows.

    Args:
        db: An active SQLAlchemy session.

    Returns:
        Mapping ``node_id -> NodeState``.
    """
    nodes = db.query(FrameworkNode).order_by(FrameworkNode.id).all()
    parent_ids = {n.parent_id for n in nodes if n.parent_id is not None}
    out: dict[int, NodeState] = {}
    for n in nodes:
        checked, total = count_checkboxes(n.description)
        out[n.id] = NodeState(
            status=n.status,
            progress_pct=float(n.progress_pct or 0.0),
            started_at=_iso(n.started_at),
            completed_at=_iso(n.completed_at),
            checked=checked,
            total=total,
            path=n.path,
            is_leaf=n.id not in parent_ids,
        )
    return out


def classify_excluded(before: dict[int, NodeState]) -> dict[str, list[int]]:
    """Enumerate the three explicitly out-of-scope drift classes.

    Reported for transparency (so a reviewer can see the sweep *saw*
    these nodes and deliberately left them) and reused by
    :func:`assert_scope_pinned` as disjointness oracles.

    Args:
        before: Pre-reconcile snapshot from :func:`snapshot_states`.

    Returns:
        ``{"reverse": [...], "partial_stale": [...],
        "no_checklist_drift": [...]}`` -- sorted node-id lists.
    """
    reverse: list[int] = []
    partial_stale: list[int] = []
    no_checklist_drift: list[int] = []
    for nid, s in before.items():
        if not s.is_leaf:
            # Parent nodes carry a propagated rollup status; that is not
            # drift and is irrelevant to a leaf-signature sweep.
            continue
        if s.total > 0 and s.checked == 0 and s.progress_pct > 0:
            reverse.append(nid)
        elif 0 < s.checked < s.total:
            partial_stale.append(nid)
        elif s.total == 0 and s.progress_pct >= 100:
            # T-P0-914 node-69 signature: pct=100 with NO checklist is
            # un-earnable via the checkbox path -> a direct-write drift.
            # (A 0/0 leaf with pct<100 and a manual status is merely a
            # checklist-free node the user advanced, NOT this drift
            # class, and is naturally out of a fully-checked sweep.)
            no_checklist_drift.append(nid)
    return {
        "reverse": sorted(reverse),
        "partial_stale": sorted(partial_stale),
        "no_checklist_drift": sorted(no_checklist_drift),
    }


def assert_scope_pinned(
    before: dict[int, NodeState], changed_leaf_ids: list[int]
) -> None:
    """Hard-assert the changed leaf set obeys the AC2 pinned scope.

    Every changed leaf MUST match the deterministic fully-checked
    signature (``total > 0 and checked == total``) in the *pre*-reconcile
    snapshot, and the changed set MUST be disjoint from the reverse,
    partial-stale, and no-checklist drift classes. A violation means the
    shared helper regressed; abort before any commit.

    Args:
        before: Pre-reconcile snapshot.
        changed_leaf_ids: Leaf ids the helper reports as changed.

    Raises:
        ScopeViolationError: If any changed leaf is not fully-checked, or
            intersects an excluded class.
    """
    excluded = classify_excluded(before)
    excluded_all = (
        set(excluded["reverse"])
        | set(excluded["partial_stale"])
        | set(excluded["no_checklist_drift"])
    )
    for nid in changed_leaf_ids:
        s = before.get(nid)
        if s is None:
            raise ScopeViolationError(
                f"changed leaf {nid} absent from pre-reconcile snapshot"
            )
        if not (s.total > 0 and s.checked == s.total):
            raise ScopeViolationError(
                f"changed leaf {nid} ({s.path}) is NOT fully-checked "
                f"({s.checked}/{s.total}) -- AC2 scope breach"
            )
        if nid in excluded_all:
            raise ScopeViolationError(
                f"changed leaf {nid} ({s.path}) intersects an excluded "
                f"drift class -- AC2 scope breach"
            )


@dataclass(frozen=True)
class NodeDelta:
    """One node that would change, with before/after and a kind tag.

    Attributes:
        node_id: ``framework_nodes.id``.
        path: Node path (human-readable).
        kind: ``"reconciled-leaf"`` (matched the fully-checked
            signature) or ``"propagated-ancestor"`` (changed only as a
            ``_propagate_upward`` rollup side-effect).
        before: Pre-reconcile :class:`NodeState`.
        after: Post-reconcile :class:`NodeState`.
    """

    node_id: int
    path: str
    kind: str
    before: NodeState
    after: NodeState


@dataclass(frozen=True)
class ReconcileDiff:
    """Full result of a (rolled-back or to-be-committed) reconcile pass.

    Attributes:
        changed_leaf_ids: Leaf ids the helper reconciled by signature.
        deltas: Every node whose state changed (leaves + propagated
            ancestors), sorted by id.
        excluded: Out-of-scope class -> node ids (transparency).
        total_nodes: Total framework node count scanned.
    """

    changed_leaf_ids: list[int]
    deltas: list[NodeDelta]
    excluded: dict[str, list[int]]
    total_nodes: int


def compute_reconcile_diff(db) -> ReconcileDiff:
    """Run the shared helper inside the caller's transaction; build a diff.

    Snapshots before, calls the single tested
    :func:`reconcile_all_fully_checked`, snapshots after, runs the AC2
    scope guard, and classifies every changed node. Does **NOT** commit
    or roll back -- the caller (dry-run vs apply) owns that decision.

    Args:
        db: An active, uncommitted SQLAlchemy session.

    Returns:
        The :class:`ReconcileDiff` describing what would (or did) change.

    Raises:
        ScopeViolationError: Propagated from :func:`assert_scope_pinned`.
    """
    before = snapshot_states(db)
    excluded = classify_excluded(before)

    changed_leaf_ids = reconcile_all_fully_checked(db)  # ALL reconcile logic
    db.flush()  # make propagated ancestor rows visible to the after-snapshot

    assert_scope_pinned(before, changed_leaf_ids)  # AC2 tripwire, pre-commit

    after = snapshot_states(db)
    changed_set = set(changed_leaf_ids)
    deltas: list[NodeDelta] = []
    for nid in sorted(before):
        b = before[nid]
        a = after[nid]
        if (b.status, b.progress_pct, b.started_at, b.completed_at) != (
            a.status,
            a.progress_pct,
            a.started_at,
            a.completed_at,
        ):
            deltas.append(
                NodeDelta(
                    node_id=nid,
                    path=b.path,
                    kind=(
                        "reconciled-leaf"
                        if nid in changed_set
                        else "propagated-ancestor"
                    ),
                    before=b,
                    after=a,
                )
            )
    return ReconcileDiff(
        changed_leaf_ids=sorted(changed_leaf_ids),
        deltas=deltas,
        excluded=excluded,
        total_nodes=len(before),
    )


def _delta_row(d: NodeDelta) -> str:
    """Render one :class:`NodeDelta` as a markdown table row."""
    b, a = d.before, d.after
    return (
        f"| {d.node_id} | `{d.path}` | {d.kind} | "
        f"{b.status} -> {a.status} | "
        f"{b.progress_pct} -> {a.progress_pct} | "
        f"{b.checked}/{b.total} |"
    )


def render_report(
    diff: ReconcileDiff, mode: str, generated_at: datetime
) -> str:
    """Render the human-readable diff report (markdown).

    Args:
        diff: The computed :class:`ReconcileDiff`.
        mode: ``"dry-run"`` or ``"apply"`` (recorded in the header).
        generated_at: Report generation timestamp.

    Returns:
        The full markdown document as a string.
    """
    ts = generated_at.strftime("%Y-%m-%d %H:%M:%S")
    leaves = [d for d in diff.deltas if d.kind == "reconciled-leaf"]
    ancestors = [d for d in diff.deltas if d.kind == "propagated-ancestor"]
    lines: list[str] = []
    lines.append(
        "# Reconcile sweep -- fully-checked leaves (T-P0-911 dry-run)"
    )
    lines.append("")
    lines.append(f"- **Generated**: {ts}")
    lines.append(f"- **Mode**: {mode} (dry-run = ZERO DB writes)")
    lines.append(
        "- **Reconcile logic**: `scripts.lib.framework_progress."
        "reconcile_all_fully_checked` (T-P0-910 shared helper -- NO "
        "inline logic in this tool)"
    )
    lines.append(f"- **Nodes scanned**: {diff.total_nodes}")
    lines.append(
        f"- **Leaves that WOULD change** (fully-checked signature): "
        f"{diff.changed_leaf_ids or 'none'}"
    )
    lines.append("")
    lines.append("## Would-change: reconciled leaves")
    lines.append("")
    if leaves:
        lines.append(
            "| node | path | kind | status | progress_pct | boxes |"
        )
        lines.append("|---:|---|---|---|---|---:|")
        lines.extend(_delta_row(d) for d in leaves)
    else:
        lines.append(
            "_None. Every fully-checked leaf is already `mastered`/100 "
            "(idempotent re-run -- AC6)._"
        )
    lines.append("")
    lines.append("## Would-change: propagated ancestors (rollup side-effect)")
    lines.append("")
    lines.append(
        "These change only because `_propagate_upward` recomputed them "
        "from the reconciled leaves (production rollup, not a direct "
        "signature match)."
    )
    lines.append("")
    if ancestors:
        lines.append(
            "| node | path | kind | status | progress_pct | boxes |"
        )
        lines.append("|---:|---|---|---|---|---:|")
        lines.extend(_delta_row(d) for d in ancestors)
    else:
        lines.append("_None._")
    lines.append("")
    lines.append("## OUT OF SCOPE -- deliberately NOT touched (AC2, Review B)")
    lines.append("")
    lines.append(
        "The sweep saw these and left them untouched. Pinned scope is "
        "asserted in code (`assert_scope_pinned`) and tested "
        "(`tests/test_reconcile_fully_checked_sweep.py`)."
    )
    lines.append("")
    lines.append(
        f"- **reverse** (pct>0, 0 checked -- 115/171 shape): "
        f"{diff.excluded['reverse'] or 'none'}"
    )
    lines.append(
        f"- **partial-stale** (0 < checked < total -- e.g. node 92): "
        f"{diff.excluded['partial_stale'] or 'none'}"
    )
    lines.append(
        f"- **no-checklist drift** (0/0 boxes, drifted status -- node "
        f"69): {diff.excluded['no_checklist_drift'] or 'none'}"
    )
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "This is the T-P0-911 deliverable: tool + dry-run report only. "
        "Applying the change (`--apply`: timestamped `.bak` -> commit -> "
        "JSONL audit) is the separate human-gated **T-P0-915**. No "
        "`--apply` was run here."
    )
    lines.append("")
    return "\n".join(lines)


def write_report(content: str) -> Path:
    """Write the diff report to the fixed ``logs/review/`` deliverable.

    Args:
        content: Rendered markdown from :func:`render_report`.

    Returns:
        Path to the written report.
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")
    return REPORT_PATH


def backup_db(db_path: Path) -> Path:
    """Copy the live DB to a timestamped ``.bak`` (AC4, ``--apply`` only).

    Args:
        db_path: Path to the live SQLite file.

    Returns:
        Path to the backup copy.
    """
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = db_path.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(db_path, dst)
    return dst


def append_audit_record(
    diff: ReconcileDiff, applied_at: datetime, backup: Path
) -> None:
    """Append one structured JSONL audit record (AC4, ``--apply`` only).

    Records ts, the changed node ids, every before/after status+pct, and
    the ``.bak`` path -- a grep-friendly, append-only trail.

    Args:
        diff: The applied :class:`ReconcileDiff`.
        applied_at: Commit timestamp.
        backup: Path returned by :func:`backup_db`.
    """
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": applied_at.isoformat(),
        "tool": "reconcile_fully_checked_nodes_20260519.py",
        "task": "T-P0-915",
        "backup": str(backup),
        "changed_leaf_ids": diff.changed_leaf_ids,
        "deltas": [
            {
                "node_id": d.node_id,
                "path": d.path,
                "kind": d.kind,
                "before": {
                    "status": d.before.status,
                    "progress_pct": d.before.progress_pct,
                },
                "after": {
                    "status": d.after.status,
                    "progress_pct": d.after.progress_pct,
                },
            }
            for d in diff.deltas
        ],
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _print_summary(diff: ReconcileDiff, mode: str) -> None:
    """Print a one-screen console summary of the diff."""
    print(f"[INFO] mode={mode} nodes_scanned={diff.total_nodes}")
    print(
        f"[INFO] would-change leaves (fully-checked signature): "
        f"{diff.changed_leaf_ids or 'none'}"
    )
    for d in diff.deltas:
        print(
            f"[DIFF] {d.node_id} {d.path} [{d.kind}] "
            f"status {d.before.status}->{d.after.status} "
            f"pct {d.before.progress_pct}->{d.after.progress_pct}"
        )
    print(
        f"[INFO] OUT OF SCOPE (untouched) reverse={diff.excluded['reverse']} "
        f"partial_stale={diff.excluded['partial_stale']} "
        f"no_checklist={diff.excluded['no_checklist_drift']}"
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    ``--dry-run`` (default) computes the diff in an uncommitted
    transaction, rolls back (zero DB writes), and writes the
    ``logs/review/`` report. ``--apply`` (T-P0-915 only) backs up the
    DB, commits, and appends a JSONL audit record.

    Args:
        argv: Optional argv override (for tests). Defaults to
            ``sys.argv[1:]``.

    Returns:
        Process exit code (0 success, 1 failure).
    """
    parser = argparse.ArgumentParser(
        description=(
            "Reconcile fully-checked KG-Framework leaves whose status "
            "was never derived to 'mastered'. Dry-run first; apply is "
            "the human-gated T-P0-915."
        )
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="(default) compute + report the diff; ZERO DB writes",
    )
    group.add_argument(
        "--apply",
        action="store_true",
        help="T-P0-915 only: .bak -> commit -> audit log",
    )
    args = parser.parse_args(argv)
    apply = bool(args.apply)
    mode = "apply" if apply else "dry-run"

    init_db()
    db = SessionLocal()
    try:
        try:
            diff = compute_reconcile_diff(db)
        except ScopeViolationError as exc:
            db.rollback()
            print(f"[FAIL] AC2 scope violation -- aborted, no write: {exc}")
            return 1

        now = datetime.now()
        if apply:
            db_path = resolve_db_path()
            if not db_path.exists():
                db.rollback()
                print(f"[FAIL] DB not found for backup: {db_path}")
                return 1
            backup = backup_db(db_path)
            print(f"[INFO] DB backup -> {backup.name}")
            db.commit()
            append_audit_record(diff, now, backup)
            print(f"[INFO] audit appended -> {AUDIT_PATH.name}")
        else:
            db.rollback()  # dry-run: guarantee ZERO DB writes

        report = render_report(diff, mode, now)
        path = write_report(report)
        _print_summary(diff, mode)
        print(f"[PASS] {mode} report written -> {path}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
