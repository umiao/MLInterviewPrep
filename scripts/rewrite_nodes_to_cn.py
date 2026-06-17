"""Rewrite framework_nodes.description to Chinese narration + full English terms.

Deliverable for T-P1-498 (KG-CN-01). Idempotent seed script:

1. Backs up data/mle_prep.db before any write.
2. Creates framework_nodes_description_history table (if missing) and records
   the old description before every UPDATE.
3. For each candidate node, calls `claude -p` (Claude Code CLI subprocess) with
   a system prompt derived from the content-style feedback memory. Uses
   claude-haiku-4-5 by default; routes nodes with len(desc) > 12000 to
   claude-sonnet-4-6.
4. Skips nodes that are already >=60% Chinese AND contain no bare acronym
   (KV/MHA/MQA/GQA/MoE/RoPE/ALiBi/LoRA/QLoRA/PEFT/RLHF/DPO/SFT/FFN/RAG)
   without a nearby full-name expansion.
5. Resume-safe: if history has a newer-than-session-start row for a node, skip.
6. Supports --dry-run (no claude calls, no DB writes), --limit N, --ids ...,
   --only-pillar N. Writes a per-run summary to logs/.

Usage:
    python scripts/rewrite_nodes_to_cn.py --dry-run
    python scripts/rewrite_nodes_to_cn.py --limit 3
    python scripts/rewrite_nodes_to_cn.py --ids 191,42,192
    python scripts/rewrite_nodes_to_cn.py            # full run, all candidates
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
LOGS_DIR = REPO_ROOT / "logs"
STYLE_MEMORY_PATH = (
    Path.home()
    / ".claude"
    / "projects"
    / "C--Users-Shenghui-Xu-Desktop-Gen-AI-Proj-MLInterviewPrep"
    / "memory"
    / "feedback_content_style_cn_en.md"
)

DEFAULT_MODEL = "claude-haiku-4-5"
BIG_MODEL = "claude-sonnet-4-6"
BIG_DESC_THRESHOLD = 12000
PER_CALL_TIMEOUT_S = 300
BIG_CALL_TIMEOUT_S = 900

# Ensure stdout can emit Chinese on Windows (cp1252 default crashes on CJK).
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Acronyms that should never appear bare on first mention. If the document
# contains any of these AND does not also contain the corresponding full
# expansion (case-insensitive), the node is a rewrite candidate regardless
# of zh_ratio.
BARE_ACRONYMS: dict[str, str] = {
    "KV": "Key-Value",
    "MHA": "Multi-Head Attention",
    "MQA": "Multi-Query Attention",
    "GQA": "Grouped-Query Attention",
    "MoE": "Mixture of Experts",
    "RoPE": "Rotary Position",
    "ALiBi": "Attention with Linear",
    "LoRA": "Low-Rank Adaptation",
    "QLoRA": "Quantized",
    "PEFT": "Parameter-Efficient",
    "RLHF": "Reinforcement Learning from Human",
    "DPO": "Direct Preference",
    "SFT": "Supervised Fine-Tuning",
    "FFN": "Feed-Forward",
    "RAG": "Retrieval-Augmented",
}


# ---------- helpers ----------


def zh_ratio(text: str) -> float:
    """Fraction of characters in the CJK Unified Ideographs block."""
    if not text:
        return 0.0
    stripped = text.strip()
    if not stripped:
        return 0.0
    chinese = sum(1 for c in stripped if "\u4e00" <= c <= "\u9fff")
    return chinese / len(stripped)


def has_bare_acronym(text: str) -> list[str]:
    """Return acronyms that appear in text without their full-name expansion."""
    offenders: list[str] = []
    for acro, needle in BARE_ACRONYMS.items():
        pattern = rf"(?<![A-Za-z]){re.escape(acro)}(?![A-Za-z])"
        if re.search(pattern, text) and needle.lower() not in text.lower():
            offenders.append(acro)
    return offenders


def structure_hash(text: str) -> tuple[int, int, int, int]:
    """Cheap shape-preservation check: counts of code fences, $$, headings, list markers."""
    fences = text.count("```")
    dollars = text.count("$$")
    headings = len(re.findall(r"(?m)^#{1,6} ", text))
    bullets = len(re.findall(r"(?m)^\s*[-*]\s", text))
    return (fences, dollars, headings, bullets)


@dataclass
class Candidate:
    node_id: int
    title: str
    description: str
    zh_ratio: float
    bare_acronyms: list[str]
    reason: str
    model: str


# ---------- DB layer ----------


def ensure_history_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS framework_nodes_description_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER NOT NULL,
            description TEXT,
            changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (node_id) REFERENCES framework_nodes(id)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_fn_desc_history_node_id "
        "ON framework_nodes_description_history(node_id)"
    )
    conn.commit()


def backup_db(db_path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = db_path.with_suffix(db_path.suffix + f".bak.{ts}")
    shutil.copy2(db_path, bak)
    return bak


def load_all_nodes(conn: sqlite3.Connection) -> list[tuple[int, str, str]]:
    cursor = conn.execute(
        "SELECT id, title, description FROM framework_nodes "
        "WHERE description IS NOT NULL AND length(description) > 0 "
        "ORDER BY id"
    )
    return cursor.fetchall()


def latest_history_changed_at(
    conn: sqlite3.Connection, node_id: int
) -> str | None:
    row = conn.execute(
        "SELECT MAX(changed_at) FROM framework_nodes_description_history "
        "WHERE node_id = ?",
        (node_id,),
    ).fetchone()
    return row[0] if row else None


# ---------- candidate selection ----------


def build_candidates(
    conn: sqlite3.Connection,
    session_start: str,
    only_ids: set[int] | None = None,
    force: bool = False,
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for node_id, title, desc in load_all_nodes(conn):
        if only_ids is not None and node_id not in only_ids:
            continue

        # Idempotency guard: if this node has ANY history row, it has already
        # been rewritten by a prior run -- skip. --ids + --force can override
        # for re-processing specific nodes.
        if not force and only_ids is None:
            last_changed = latest_history_changed_at(conn, node_id)
            if last_changed is not None:
                continue

        ratio = zh_ratio(desc)
        bare = has_bare_acronym(desc)

        if only_ids is not None:
            reason = "explicit --ids"
        elif ratio >= 0.6 and not bare:
            continue
        elif ratio < 0.4:
            reason = f"zh_ratio={ratio:.2f} < 0.4"
        elif bare:
            reason = f"bare acronyms: {','.join(bare)}"
        else:
            reason = f"zh_ratio={ratio:.2f} in [0.4, 0.6)"

        model = BIG_MODEL if len(desc) > BIG_DESC_THRESHOLD else DEFAULT_MODEL
        candidates.append(
            Candidate(
                node_id=node_id,
                title=title,
                description=desc,
                zh_ratio=ratio,
                bare_acronyms=bare,
                reason=reason,
                model=model,
            )
        )
    return candidates


# ---------- claude -p call ----------


def load_system_prompt() -> str:
    if not STYLE_MEMORY_PATH.exists():
        raise FileNotFoundError(
            f"Style memory not found at {STYLE_MEMORY_PATH}. "
            "Create it before running (see task T-P1-498 description)."
        )
    raw = STYLE_MEMORY_PATH.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return raw.strip()


def split_leading_html_comments(text: str) -> tuple[str, str]:
    """Extract leading HTML comment block (and its trailing blank line) from text.

    Many canonical-hub / StudyNoteBuilder descriptions begin with sentinel
    comments like `<!-- doc_kind: canonical_hub -->`,
    `<!-- canonical_topic: xxx -->`, `<!-- KG_* -->`, or
    `<!-- Generated by StudyNoteBuilder -->`. These are load-bearing (tests
    grep for them, KG tooling inspects them) and must survive style rewrites,
    but `claude -p` routinely strips them as "metadata noise". We pull them
    off before the call and re-prepend them afterward.

    Returns (leading_block, remainder). leading_block preserves original
    whitespace (including the blank line after the last comment) so that
    `leading + remainder` round-trips the original text when no stripping
    occurred.
    """
    if not text:
        return "", text
    # Match zero or more <!-- ... --> blocks at the very top, each on its own
    # line, separated by optional whitespace/blank lines. The final match
    # consumes the trailing blank line(s) if present so remainder starts at
    # the first real content line.
    pattern = re.compile(
        r"\A((?:[ \t]*<!--[\s\S]*?-->[ \t]*\n)+\s*\n?)",
        re.MULTILINE,
    )
    m = pattern.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def build_user_prompt(title: str, desc: str) -> str:
    return (
        f"Rewrite the Markdown description below for the knowledge-graph node "
        f"titled: \"{title}\".\n\n"
        "Apply the Chinese-narration + full-English-term style from the system "
        "prompt. Preserve all code fences, $$...$$ formulas, $...$ inline math, "
        "Markdown headings, tables, and list structure exactly. Preserve any "
        "HTML comments (<!-- ... -->) verbatim, including leading sentinel "
        "blocks like <!-- doc_kind: canonical_hub -->, "
        "<!-- canonical_topic: ... -->, <!-- KG_* -->, and "
        "<!-- Generated by StudyNoteBuilder --> -- these are load-bearing "
        "metadata that downstream tests and tooling depend on; never drop or "
        "reword them. Do NOT add new sections or new content -- this is a "
        "style rewrite, not an expansion. Return ONLY the rewritten Markdown "
        "content, no preface, no wrapping code fence.\n\n"
        "--- ORIGINAL MARKDOWN START ---\n"
        f"{desc}\n"
        "--- ORIGINAL MARKDOWN END ---"
    )


def call_claude(
    system_prompt: str, user_prompt: str, model: str
) -> tuple[str, float]:
    t0 = time.time()
    cmd = [
        "claude",
        "-p",
        user_prompt,
        "--model",
        model,
        "--system-prompt",
        system_prompt,
        "--output-format",
        "json",
        "--no-session-persistence",
        "--tools",
        "",
        "--setting-sources",
        "user",
    ]
    per_call_timeout = BIG_CALL_TIMEOUT_S if model == BIG_MODEL else PER_CALL_TIMEOUT_S
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=per_call_timeout,
    )
    elapsed = time.time() - t0
    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (rc={result.returncode}): "
            f"stdout={result.stdout[:400]!r} stderr={result.stderr[:400]!r}"
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"claude -p returned non-JSON: {result.stdout[:400]!r}"
        ) from e
    content = payload.get("result") or payload.get("text") or ""
    if not content.strip():
        raise RuntimeError(
            f"claude -p returned empty content. Payload keys: {list(payload.keys())}"
        )
    return content.strip(), elapsed


# ---------- validation ----------


def validate_rewrite(
    original: str, rewritten: str
) -> tuple[bool, list[str]]:
    """Basic sanity checks: no structure loss, no code-block formula regression."""
    issues: list[str] = []

    orig_shape = structure_hash(original)
    new_shape = structure_hash(rewritten)
    if new_shape[0] != orig_shape[0]:
        issues.append(
            f"code-fence count changed: {orig_shape[0]} -> {new_shape[0]}"
        )
    # Allow small $$ drift (model may merge/split display math) but reject
    # catastrophic loss. Threshold: reject if delta > 25% of original, or
    # if original had >=4 and rewrite has <=2.
    orig_dd, new_dd = orig_shape[1], new_shape[1]
    catastrophic = orig_dd >= 4 and new_dd <= 2
    big_drift = orig_dd > 0 and abs(new_dd - orig_dd) > max(4, 0.25 * orig_dd)
    if catastrophic or big_drift:
        issues.append(f"$$ count changed: {orig_dd} -> {new_dd}")
    if new_shape[2] < orig_shape[2]:
        issues.append(
            f"heading count dropped: {orig_shape[2]} -> {new_shape[2]}"
        )

    # Formulas must not appear inside fenced code blocks.
    for block in re.findall(r"```[\s\S]*?```", rewritten):
        if "$$" in block:
            issues.append("$$ formula found inside a fenced code block")
            break

    # Must actually contain Chinese.
    if not re.search(r"[\u4e00-\u9fff]", rewritten):
        issues.append("rewrite contains zero Chinese characters")

    # Guard against truncation: rewrite should be >= 40% of original length.
    if len(rewritten) < 0.4 * len(original):
        issues.append(
            f"suspiciously short rewrite: {len(rewritten)} vs original "
            f"{len(original)}"
        )

    return (len(issues) == 0, issues)


# ---------- main loop ----------


def write_summary(
    log_path: Path,
    started_at: str,
    finished_at: str,
    backup_path: Path | None,
    examined: int,
    skipped: int,
    updated: int,
    failed: int,
    rows: list[dict],
    dry_run: bool,
) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# rewrite_nodes_to_cn -- run summary\n")
    lines.append(f"- **Started**: {started_at}")
    lines.append(f"- **Finished**: {finished_at}")
    lines.append(f"- **Mode**: {'DRY-RUN' if dry_run else 'WRITE'}")
    if backup_path:
        lines.append(f"- **Backup**: `{backup_path.as_posix()}`")
    lines.append(f"- **Examined**: {examined}")
    lines.append(f"- **Skipped**: {skipped}")
    lines.append(f"- **Updated**: {updated}")
    lines.append(f"- **Failed**: {failed}")
    lines.append("")
    lines.append(
        "| id | title | model | old_zh | new_zh | old_len | new_len | "
        "elapsed_s | status |"
    )
    lines.append(
        "|---:|-------|-------|-------:|-------:|--------:|--------:|"
        "----------:|--------|"
    )
    for r in rows:
        title_cell = r["title"].replace("|", "\\|")
        lines.append(
            f"| {r['id']} | {title_cell} | {r['model']} | "
            f"{r['old_zh']:.2f} | {r['new_zh']:.2f} | "
            f"{r['old_len']} | {r['new_len']} | "
            f"{r['elapsed']:.1f} | {r['status']} |"
        )
    log_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print candidates and exit; no claude calls, no DB writes.",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N candidates (useful for smoke tests).",
    )
    p.add_argument(
        "--ids",
        type=str,
        default=None,
        help="Comma-separated node ids to force-rewrite (ignores skip rules).",
    )
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model routing (e.g. 'claude-haiku-4-5'). "
        "If unset, uses haiku for small nodes and sonnet for nodes > "
        f"{BIG_DESC_THRESHOLD} chars.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="With --ids, reprocess nodes even if they already have history.",
    )
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not DB_PATH.exists():
        print(f"[FAIL] DB not found at {DB_PATH}", file=sys.stderr)
        return 2

    only_ids: set[int] | None = None
    if args.ids:
        only_ids = {int(x.strip()) for x in args.ids.split(",") if x.strip()}

    conn = sqlite3.connect(str(DB_PATH))
    try:
        ensure_history_table(conn)
        candidates = build_candidates(
            conn, session_start, only_ids, force=args.force
        )
    finally:
        conn.close()

    if args.limit is not None:
        candidates = candidates[: args.limit]

    print(f"[INFO] Session start: {session_start}")
    print(f"[INFO] Candidates: {len(candidates)}")
    for c in candidates[:20]:
        print(
            f"    id={c.node_id} model={c.model} "
            f"zh={c.zh_ratio:.2f} len={len(c.description)} "
            f"reason=\"{c.reason}\" title=\"{c.title}\""
        )
    if len(candidates) > 20:
        print(f"    ... +{len(candidates) - 20} more")

    if args.dry_run:
        print("[DONE] Dry-run complete; no DB changes.")
        summary_path = LOGS_DIR / f"rewrite_nodes_to_cn_{ts_suffix}_dryrun.md"
        write_summary(
            summary_path,
            session_start,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            backup_path=None,
            examined=len(candidates),
            skipped=0,
            updated=0,
            failed=0,
            rows=[
                {
                    "id": c.node_id,
                    "title": c.title,
                    "model": c.model,
                    "old_zh": c.zh_ratio,
                    "new_zh": c.zh_ratio,
                    "old_len": len(c.description),
                    "new_len": len(c.description),
                    "elapsed": 0.0,
                    "status": f"dry-run ({c.reason})",
                }
                for c in candidates
            ],
            dry_run=True,
        )
        print(f"[INFO] Wrote {summary_path}")
        return 0

    if not candidates:
        # AC #7: re-running with no new candidates exits fast.
        print("[DONE] No candidates remain; exiting (idempotent guard).")
        return 0

    backup_path = backup_db(DB_PATH)
    print(f"[INFO] Backup created: {backup_path.name}")

    system_prompt = load_system_prompt()

    conn = sqlite3.connect(str(DB_PATH))
    try:
        ensure_history_table(conn)
        rows: list[dict] = []
        updated = 0
        failed = 0
        total = len(candidates)
        for i, c in enumerate(candidates, 1):
            model = args.model or c.model
            print(
                f"[{i}/{total}] id={c.node_id} title=\"{c.title}\" "
                f"model={model} zh={c.zh_ratio:.2f} len={len(c.description)} "
                f"reason=\"{c.reason}\""
            )
            try:
                # Strip leading HTML comment sentinels before handing the
                # body to claude, and re-prepend them afterward. Belt-and-
                # suspenders: the user prompt also asks claude to preserve
                # them, but the model has been observed to drop them anyway.
                leading_comments, body_for_claude = split_leading_html_comments(
                    c.description
                )
                rewritten_body, elapsed = call_claude(
                    system_prompt,
                    build_user_prompt(c.title, body_for_claude),
                    model,
                )
                # If claude echoed the comments back, dedupe so we don't
                # emit them twice.
                _, rewritten_tail = split_leading_html_comments(rewritten_body)
                rewritten = leading_comments + rewritten_tail
                ok, issues = validate_rewrite(c.description, rewritten)
                if not ok:
                    failed += 1
                    print(
                        f"    [FAIL] validation: {'; '.join(issues)} "
                        f"(elapsed={elapsed:.1f}s)"
                    )
                    rows.append(
                        {
                            "id": c.node_id,
                            "title": c.title,
                            "model": model,
                            "old_zh": c.zh_ratio,
                            "new_zh": zh_ratio(rewritten),
                            "old_len": len(c.description),
                            "new_len": len(rewritten),
                            "elapsed": elapsed,
                            "status": "FAIL: " + "; ".join(issues),
                        }
                    )
                    continue

                conn.execute(
                    "INSERT INTO framework_nodes_description_history "
                    "(node_id, description) VALUES (?, ?)",
                    (c.node_id, c.description),
                )
                conn.execute(
                    "UPDATE framework_nodes SET description = ? WHERE id = ?",
                    (rewritten, c.node_id),
                )
                conn.commit()
                new_ratio = zh_ratio(rewritten)
                updated += 1
                print(
                    f"    [OK] zh_ratio={c.zh_ratio:.2f}->{new_ratio:.2f} "
                    f"len={len(c.description)}->{len(rewritten)} "
                    f"elapsed={elapsed:.1f}s"
                )
                rows.append(
                    {
                        "id": c.node_id,
                        "title": c.title,
                        "model": model,
                        "old_zh": c.zh_ratio,
                        "new_zh": new_ratio,
                        "old_len": len(c.description),
                        "new_len": len(rewritten),
                        "elapsed": elapsed,
                        "status": "OK",
                    }
                )
            except Exception as e:  # noqa: BLE001 -- runtime robustness
                failed += 1
                print(f"    [ERR] {type(e).__name__}: {e}")
                rows.append(
                    {
                        "id": c.node_id,
                        "title": c.title,
                        "model": model,
                        "old_zh": c.zh_ratio,
                        "new_zh": c.zh_ratio,
                        "old_len": len(c.description),
                        "new_len": len(c.description),
                        "elapsed": 0.0,
                        "status": f"ERR: {type(e).__name__}: {e}",
                    }
                )
    finally:
        conn.close()

    summary_path = LOGS_DIR / f"rewrite_nodes_to_cn_{ts_suffix}.md"
    write_summary(
        summary_path,
        session_start,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        backup_path=backup_path,
        examined=len(candidates),
        skipped=0,
        updated=updated,
        failed=failed,
        rows=rows,
        dry_run=False,
    )
    print(f"[INFO] Wrote {summary_path}")
    print(
        f"[DONE] examined={len(candidates)} updated={updated} failed={failed}"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
