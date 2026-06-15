#!/usr/bin/env python3
"""Plan validation CLI: deterministic L0 gate for planning output.

Not a hook -- standalone script called at the end of a planning session, or by
the /plan-review skill before the LLM review layer. This is the L0 objective
gate of the plan-review pipeline (TASK_PLAN_plan_review_pipeline.md, "bearing
wall"): the machine OWNS only objective, fail-closed checks; subjective
preferences are never judged here (they are surfaced/routed by L1/L2).

Objective checks (FAIL = exit 1):
1. Tasks were created/updated during the planning window (--since).
2. Each window task has all required spec sections (non-empty).
3. Each window task has >=1 acceptance-criteria item (`- [ ]`).
4. Each window task declares a Verification field (presence + non-empty ONLY,
   never sufficiency): a pytest/test_*.py reference, a `## Verification`
   section, or an explicit `no-test: <reason>`.
5. Each repo-resident Grounding Assets path exists (conceptual / memory /
   external references are exempt).
6. TASKS.md was regenerated after the planning window.

Advisory checks (WARN, never block):
- EARS: AC items lacking trigger/response phrasing.

Bearing-wall note (T-P0-386): "has a Verification field" is objective (presence,
L0 owns); "is the Verification sufficient" is subjective (L0 must NOT judge).

Usage:
    python .claude/hooks/plan_validate.py
    python .claude/hooks/plan_validate.py --since "2026-06-13T00:00:00"

Exit codes:
    0 = all objective checks pass (warnings allowed)
    1 = one or more objective failures
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TASKS_DB = PROJECT_ROOT / ".claude" / "tasks.db"
TASKS_MD = PROJECT_ROOT / "TASKS.md"
STATE_FILE = PROJECT_ROOT / ".claude" / "state.json"

# Required sections in task description (case-insensitive matching).
REQUIRED_SECTIONS = [
    "summary",
    "context",
    "acceptance criteria",
    "technical approach",
    "edge cases",
    "complexity",
    "dependencies",
]

# Minimum content length (chars, after the header) for a section to count as
# non-empty. "dependencies" and "complexity" are relaxed because "None" / "T-X"
# and a bare "S" / "M" / "L" are valid short bodies -- the dependency EDGES live
# in task_dependencies (not the prose), and complexity is an enum-ish value
# (T-P0-386 AC1: do not false-trip a short-but-valid section).
DEFAULT_SECTION_MIN_LENGTH = 10
SECTION_MIN_LENGTH = {
    "dependencies": 1,
    "complexity": 1,
}

# File-extension suffixes that mark a Grounding entry as a repo-resident path
# (existence-checked). Entries without a slash and without one of these
# suffixes are treated as conceptual / external references and are exempt.
PATH_SUFFIXES = (
    ".py", ".md", ".toml", ".json", ".sh", ".yaml", ".yml", ".txt",
    ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".cfg", ".ini", ".sql",
)

# EARS-ish trigger/response markers (advisory only).
EARS_MARKERS = (
    "when ", "if ", "given ", "while ", "once ", "then ", "->", "→",
    " shall ", "exits", "returns", "exit code",
)


def _get_plan_start_time() -> float:
    """Get the plan activation timestamp (unix epoch) from state.json.

    Returns:
        Unix timestamp of plan activation, or 0 if not found.
    """
    if not STATE_FILE.exists():
        return 0.0
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return float(state.get("activated_at", 0))
    except (json.JSONDecodeError, OSError, ValueError):
        return 0.0


def _normalize_since(since_iso: str | None) -> tuple[str | None, float]:
    """Resolve the planning window start into a (naive-UTC ISO, epoch) pair.

    The tasks table stores ``created_at`` / ``updated_at`` as NAIVE ISO strings
    that represent UTC. The historical bug (T-P0-386 AC6) was
    ``fromisoformat(s).timestamp()`` (treats a naive string as LOCAL time) then
    ``fromtimestamp(ts, UTC)`` (re-projects to UTC) -- a round-trip that shifted
    the window by the local UTC offset and missed tasks. The fix: keep the
    comparison in naive-UTC space (lexical ISO compare against created_at), and
    derive the file-mtime epoch separately and correctly.

    Args:
        since_iso: ISO timestamp string, or None to read state.json.

    Returns:
        (iso_since, since_ts): ``iso_since`` is a naive-UTC ISO string for
        string-comparison against created_at (or None if no window), and
        ``since_ts`` is the matching unix epoch for file-mtime comparison.
    """
    if since_iso:
        dt = datetime.fromisoformat(since_iso)
        if dt.tzinfo is not None:
            dt = dt.astimezone(UTC).replace(tzinfo=None)
        # dt is now naive, interpreted as UTC.
        iso_since = dt.isoformat()
        since_ts = dt.replace(tzinfo=UTC).timestamp()
        return iso_since, since_ts

    ts = _get_plan_start_time()
    if ts == 0:
        return None, 0.0
    iso_since = datetime.fromtimestamp(ts, tz=UTC).replace(tzinfo=None).isoformat()
    return iso_since, ts


def _get_tasks_since(iso_since: str | None) -> list[dict]:
    """Query tasks created or updated at/after a naive-UTC ISO boundary.

    Args:
        iso_since: Naive-UTC ISO string boundary, or None for no window.

    Returns:
        List of task dicts (id, title, description, created_at, updated_at).
        Empty when no window is known (callers must not retro-scan the table).
    """
    if not TASKS_DB.exists() or iso_since is None:
        return []

    conn = sqlite3.connect(str(TASKS_DB))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT id, title, description, created_at, updated_at "
            "FROM tasks WHERE created_at >= ? OR updated_at >= ?",
            (iso_since, iso_since),
        )
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def _section_content(description: str, section: str) -> str | None:
    """Return the trimmed body of one required section, or None if absent.

    Looks for ``## Section`` / ``**Section**`` / ``Section:`` headers and takes
    the text up to the next required-section header.

    Args:
        description: Task description markdown.
        section: Lower-case section name from REQUIRED_SECTIONS.

    Returns:
        The section body (stripped), or None if the header is not present.
    """
    desc_lower = description.lower()
    for pattern in (f"## {section}", f"**{section}**", f"{section}:"):
        idx = desc_lower.find(pattern)
        if idx < 0:
            continue
        after = description[idx + len(pattern):]
        next_section = len(after)
        for other in REQUIRED_SECTIONS:
            for p in (f"## {other}", f"**{other}**", f"{other}:"):
                pos = after.lower().find(p)
                if pos > 0:
                    next_section = min(next_section, pos)
        return after[:next_section].strip()
    return None


def _check_spec_sections(description: str) -> list[str]:
    """Find required sections that are missing or too short.

    Args:
        description: Task description markdown.

    Returns:
        List of section names that are absent or below their min length.
    """
    if not description:
        return list(REQUIRED_SECTIONS)
    missing = []
    for section in REQUIRED_SECTIONS:
        content = _section_content(description, section)
        min_len = SECTION_MIN_LENGTH.get(section, DEFAULT_SECTION_MIN_LENGTH)
        if content is None or len(content) < min_len:
            missing.append(section)
    return missing


def _check_min_ac(description: str) -> bool:
    """True iff the description has at least one acceptance-criteria item.

    An AC item is a markdown task checkbox: ``- [ ]`` / ``- [x]``.

    Args:
        description: Task description markdown.

    Returns:
        True if >=1 AC item is present.
    """
    return bool(re.search(r"-\s*\[\s*[xX ]?\s*\]", description or ""))


def _check_verification(description: str) -> bool:
    """True iff the description declares a Verification field (presence only).

    Accepts ANY of: a non-empty ``## Verification`` / ``**Verification**`` /
    ``Verification:`` section; a pytest or ``test_*.py`` / ``*_test.py``
    reference; or an explicit ``no-test: <reason>``. This checks PRESENCE +
    non-empty ONLY -- never whether the verification is *sufficient* (that is a
    subjective judgement the human owns; bearing wall).

    Args:
        description: Task description markdown.

    Returns:
        True if a verification field is present.
    """
    d = description or ""
    dl = d.lower()

    for pattern in ("## verification", "**verification**", "verification:"):
        idx = dl.find(pattern)
        if idx < 0:
            continue
        after = d[idx + len(pattern):]
        nxt = after.find("\n##")
        content = (after[:nxt] if nxt > 0 else after).strip()
        if len(content) >= 1:
            return True

    if re.search(r"\bpytest\b", d, re.I):
        return True
    if re.search(r"\btest_[a-z0-9_]+\.py\b", d, re.I):
        return True
    if re.search(r"\b[a-z0-9_]+_test\.py\b", d, re.I):
        return True

    m = re.search(r"no-test:\s*(\S.*)", d, re.I)
    if m and m.group(1).strip():
        return True

    return False


def _looks_like_repo_path(token: str) -> bool:
    """Heuristic: does a Grounding entry name a repo-resident path?

    Repo paths contain a ``/`` or end with a known source/doc suffix. URLs,
    ``memory <slug>`` references, and conceptual artifacts ("T3 findings JSON
    contract") are external and exempt from existence checking.

    Args:
        token: The text of a Grounding entry before its ``(tag/role)``.

    Returns:
        True if the token should be existence-checked.
    """
    t = token.strip().strip("`").strip()
    if not t:
        return False
    tl = t.lower()
    if tl.startswith(("http://", "https://")):
        return False
    if tl.startswith("memory "):
        return False
    if " " in t and "/" not in t:
        # Multi-word non-path conceptual reference (e.g. "T3 findings JSON contract").
        return t.endswith(PATH_SUFFIXES)
    return "/" in t or t.endswith(PATH_SUFFIXES)


def _check_grounding_paths(description: str) -> list[str]:
    """Find repo-resident Grounding Assets paths that do not exist.

    Args:
        description: Task description markdown.

    Returns:
        List of non-existent repo-resident paths (empty if the section is
        absent -- that case is reported by the section-completeness check).
    """
    section = _section_content(description, "grounding assets")
    if not section:
        return []

    missing = []
    for entry in re.split(r"[;\n]", section):
        entry = entry.strip()
        if not entry:
            continue
        token = entry.split("(")[0].strip().strip("`").rstrip(",. ")
        if not token:
            continue
        if _looks_like_repo_path(token):
            if not (PROJECT_ROOT / token).exists():
                missing.append(token)
    return missing


def _check_ears(description: str) -> int:
    """Count AC items lacking EARS trigger/response phrasing (advisory).

    Args:
        description: Task description markdown.

    Returns:
        Number of AC items with no recognizable trigger/response marker.
    """
    section = _section_content(description, "acceptance criteria")
    if not section:
        return 0
    count = 0
    for line in section.splitlines():
        if not re.search(r"-\s*\[\s*[xX ]?\s*\]", line):
            continue
        low = line.lower()
        if not any(marker in low for marker in EARS_MARKERS):
            count += 1
    return count


def validate_description(task_id: str, description: str) -> tuple[list[str], list[str]]:
    """Run all per-task objective + advisory checks on one task description.

    Args:
        task_id: The task id (for messages).
        description: Task description markdown.

    Returns:
        (failures, warnings): lists of human-readable messages, each naming the
        offending task.
    """
    failures: list[str] = []
    warnings: list[str] = []

    missing = _check_spec_sections(description)
    if missing:
        failures.append(f"{task_id}: missing/empty section(s): {', '.join(missing)}")

    if not _check_min_ac(description):
        failures.append(f"{task_id}: no acceptance-criteria item (`- [ ]`) found")

    if not _check_verification(description):
        failures.append(
            f"{task_id}: no Verification field "
            "(need a pytest/test_*.py ref, a `## Verification` section, "
            "or `no-test: <reason>`)"
        )

    bad_paths = _check_grounding_paths(description)
    if bad_paths:
        failures.append(
            f"{task_id}: Grounding Assets path(s) do not exist: {', '.join(bad_paths)}"
        )

    ears_gaps = _check_ears(description)
    if ears_gaps:
        warnings.append(
            f"{task_id}: {ears_gaps} AC item(s) may lack EARS trigger/response phrasing"
        )

    return failures, warnings


def _find_cycle(adj: dict, nodes) -> list[str] | None:
    """Return one dependency cycle as an ordered path (x -> ... -> x), or None.

    Iterative DFS over upstream->downstream edges; on a back edge to a node
    still on the active stack, reconstructs the cycle via the parent chain.

    Args:
        adj: adjacency map upstream_id -> [downstream_id, ...].
        nodes: iterable of all node ids to start from.

    Returns:
        Ordered cycle path (first == last), or None if acyclic.
    """
    WHITE, GREY, BLACK = 0, 1, 2
    color: dict = {n: WHITE for n in nodes}
    parent: dict = {}

    def visit(start: str) -> list[str] | None:
        color[start] = GREY
        stack = [(start, iter(adj.get(start, [])))]
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if color.get(nxt, WHITE) == WHITE:
                    color[nxt] = GREY
                    parent[nxt] = node
                    stack.append((nxt, iter(adj.get(nxt, []))))
                    advanced = True
                    break
                if color.get(nxt) == GREY:
                    path = [node]
                    x = node
                    while x != nxt:
                        x = parent[x]
                        path.append(x)
                    path.reverse()
                    path.append(nxt)
                    return path
            if not advanced:
                color[node] = BLACK
                stack.pop()
        return None

    for n in nodes:
        if color.get(n, WHITE) == WHITE:
            found = visit(n)
            if found:
                return found
    return None


def _check_topology(
    task_ids: set, edges: list, window_ids: set
) -> tuple[list[str], list[str]]:
    """Deterministic dependency-graph checks (T-P0-387).

    Cycle and dangling edges are objective illegalities -> FAIL. Orphans
    (window tasks with no edges) are a recall-biased connectivity flag ->
    WARN only, scoped to this session's tasks; never auto-add an edge, never
    hard-block.

    Args:
        task_ids: all existing task ids.
        edges: list of (upstream_id, downstream_id) dependency edges.
        window_ids: ids of tasks created/updated this planning session.

    Returns:
        (failures, warnings) message lists.
    """
    failures: list[str] = []
    warnings: list[str] = []

    dangling = [(u, v) for (u, v) in edges if u not in task_ids or v not in task_ids]
    if dangling:
        pretty = ", ".join(f"{u}->{v}" for u, v in dangling)
        failures.append(
            f"dangling dependency edge(s) to non-existent task(s): {pretty}"
        )

    adj: dict = defaultdict(list)
    deg: dict = defaultdict(int)
    for u, v in edges:
        if u in task_ids and v in task_ids:
            adj[u].append(v)
            deg[u] += 1
            deg[v] += 1

    cycle = _find_cycle(adj, task_ids)
    if cycle:
        failures.append("dependency cycle: " + " -> ".join(cycle))

    for tid in sorted(window_ids):
        if tid in task_ids and deg.get(tid, 0) == 0:
            warnings.append(
                f"{tid}: orphan (no dependency edges) -- add a real edge if it "
                "depends on / blocks another task, or confirm it is standalone"
            )

    return failures, warnings


def _check_topology_db(window_ids: set) -> tuple[list[str], list[str]]:
    """Load the dependency graph from tasks.db and run _check_topology.

    Args:
        window_ids: ids of tasks in the current planning window.

    Returns:
        (failures, warnings) message lists.
    """
    if not TASKS_DB.exists():
        return [], []
    conn = sqlite3.connect(str(TASKS_DB))
    try:
        task_ids = {r[0] for r in conn.execute("SELECT id FROM tasks")}
        try:
            edges = [
                (r[0], r[1])
                for r in conn.execute(
                    "SELECT upstream_id, downstream_id FROM task_dependencies"
                )
            ]
        except sqlite3.OperationalError:
            edges = []
    finally:
        conn.close()
    return _check_topology(task_ids, edges, window_ids)


def _check_tasks_md_freshness(since_ts: float) -> bool:
    """Check if TASKS.md was modified at/after the plan window start.

    Args:
        since_ts: Unix epoch to compare against.

    Returns:
        True if TASKS.md exists and was modified at/after since_ts.
    """
    if not TASKS_MD.exists():
        return False
    return os.path.getmtime(str(TASKS_MD)) >= since_ts


def validate(since_iso: str | None = None) -> int:
    """Run the L0 gate over the planning window.

    Args:
        since_iso: Optional ISO timestamp string for the window start. If None,
            reads state.json; if neither is available, per-task spec checks are
            SKIPPED (no whole-table retro-scan, T-P0-386 edge case).

    Returns:
        0 if all objective checks pass, 1 if any fail.
    """
    iso_since, since_ts = _normalize_since(since_iso)
    failures: list[str] = []
    warnings: list[str] = []

    if iso_since is None:
        print("[WARN] No plan window (--since/state.json). Skipping per-task "
              "spec checks (no retro-scan).")
        # Only the freshness check is meaningful without a window.
        if _check_tasks_md_freshness(0.0):
            print("[OK] TASKS.md exists.")
        print("\n[PASS] Planning validation complete (no-window mode).")
        return 0

    tasks = _get_tasks_since(iso_since)
    if not tasks:
        failures.append("No tasks were created or updated during this planning window.")
    else:
        print(f"[OK] {len(tasks)} task(s) created/updated in window (since {iso_since}).")

    for task in tasks:
        f, w = validate_description(task["id"], task.get("description", ""))
        failures.extend(f)
        warnings.extend(w)

    # Deterministic dependency-graph checks (cycle/dangling FAIL, orphan WARN).
    top_failures, top_warnings = _check_topology_db({t["id"] for t in tasks})
    failures.extend(top_failures)
    warnings.extend(top_warnings)

    if warnings:
        print(f"[WARN] {len(warnings)} advisory note(s):")
        for w in warnings:
            print(f"  {w}")
    elif tasks:
        print("[OK] No advisory notes.")

    if _check_tasks_md_freshness(since_ts):
        print("[OK] TASKS.md was regenerated.")
    else:
        failures.append("TASKS.md was not regenerated after planning. Run task_db.py project.")

    if failures:
        print(f"\n[FAIL] {len(failures)} failure(s):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\n[PASS] Planning validation complete.")
    return 0


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate planning session output (L0 gate).")
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="ISO timestamp for the planning window start (default: state.json)",
    )
    args = parser.parse_args()
    sys.exit(validate(args.since))


if __name__ == "__main__":
    main()
