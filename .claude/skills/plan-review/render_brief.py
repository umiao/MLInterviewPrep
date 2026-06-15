#!/usr/bin/env python3
"""Deterministic guidance-brief renderer for plan-review axis-2 (T-P1-389 AC4).

T4 (axis-2) runs in the context-RICH main session: Claude audits the round-1
findings against evidence (marks each kept / discarded(hallucination) / added),
does the global/topology pass, and writes an *adjudicated* findings doc. THIS
script then renders that doc into the human-friendly guidance brief
deterministically -- Claude judges, the renderer formats. Keeping rendering
deterministic means the brief's structure (task-level default, AC drill-down on
concerns, route-to-human section, explicit 'no action needed') is unit-testable
and never drifts with prose mood.

Bearing wall: the renderer surfaces + routes, it NEVER pronounces a terminal
verdict on a subjective item -- those land in the 'needs your decision' section
with evidence + options, no machine verdict (AC4). Discarded (hallucination)
findings are excluded entirely (not in the brief, not in the T0 denominator).
harden-L0 items feed T1's oracle, not the human -- they appear only as a count
note (AC5: objective items already owned by L0 are not duplicated into the brief).

The brief's signal-to-noise (acceptance_rate, T0 DR) is named as the primary
system metric in the footer (AC6).

Adjudicated input = findings doc (round=2) where each finding may additionally
carry:
    "adjudication": "kept" | "discarded" | "added"   (default "kept")
    "audit_note":  free text (why discarded / why added)

Usage:
    python render_brief.py adjudicated.json [-o brief.md]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRIMARY_METRIC_NOTE = (
    "本简报的**信噪比 (signal-to-noise = 接受率 accepted/(accepted+dismissed))** 是本系统的"
    "主指标 (T0 DR)。被审计弃掉的幻觉 concern 不进本简报、不入分母。持续低接受率会触发"
    "可逆 quarantine。"
)


def _adj(f: dict) -> str:
    """Return a finding's adjudication state, defaulting to 'kept'."""
    return f.get("adjudication", "kept")


def _human_findings(findings: list[dict]) -> list[dict]:
    """Findings that belong in the human brief: kept/added AND route='human'.

    Excludes discarded (hallucination) and harden-L0 (feeds T1 oracle, AC5).
    """
    return [
        f for f in findings
        if _adj(f) != "discarded" and f.get("route") == "human"
    ]


GLOBAL_LABEL = "(全局/跨任务)"


def _by_task(findings: list[dict]) -> dict[str, list[dict]]:
    """Group findings by task id, preserving first-seen task order.

    A null task (a global/cross-task finding from T4's global pass) is grouped
    under GLOBAL_LABEL.
    """
    out: dict[str, list[dict]] = {}
    for f in findings:
        out.setdefault(f.get("task") or GLOBAL_LABEL, []).append(f)
    return out


def build_brief(adjudicated: dict) -> str:
    """Render the human-facing guidance brief markdown.

    Args:
        adjudicated: The round-2 adjudicated findings doc.

    Returns:
        Markdown brief string. For a clean plan it is an explicit
        'no action needed' note, never an empty document (edge case).
    """
    findings = adjudicated.get("findings", []) if isinstance(adjudicated, dict) else []
    run_id = adjudicated.get("run_id", "?") if isinstance(adjudicated, dict) else "?"

    human = _human_findings(findings)
    objective = [f for f in human if f.get("dimension") == "objective"]
    subjective = [f for f in human if f.get("dimension") == "subjective"]
    discarded = [f for f in findings if _adj(f) == "discarded"]
    harden = [f for f in findings if f.get("route") == "harden-L0" and _adj(f) != "discarded"]

    lines: list[str] = []
    lines.append("# /plan-review — 评审简报 (guidance brief)")
    lines.append("")
    lines.append(f"> run: `{run_id}` · 默认按任务聚合,仅在有 concern 处下钻到 AC 级。")
    lines.append("")

    if not human:
        # Edge case: perfect plan -> explicit message, never an empty file.
        lines.append("## ✅ 无需你处理 (no action needed from you)")
        lines.append("")
        lines.append("本轮评审未发现需要你裁决的主观项,也无需修正的 objective concern。")
        if discarded:
            lines.append("")
            lines.append(f"(审计弃掉 {len(discarded)} 条证据不足/幻觉 concern,已不计入信噪比分母。)")
        if harden:
            lines.append("")
            lines.append(f"({len(harden)} 条 objective 缺口回流 L0 oracle,机器侧处理,不需你介入。)")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(PRIMARY_METRIC_NOTE)
        return "\n".join(lines) + "\n"

    # Audit-and-discard buffer transparency (T0 §7) -- surfaced up front.
    lines.append(
        f"**本轮**:需修正 {len(objective)} 项 · 需你裁决 {len(subjective)} 项 · "
        f"审计弃掉 {len(discarded)} 项(不入分母)· 回流 L0 {len(harden)} 项。"
    )
    lines.append("")

    if objective:
        lines.append("## 需修正项 (objective concern)")
        lines.append("")
        lines.append("机器认为客观上欠妥;按任务聚合,下钻到具体 AC。修了再放行即可。")
        for task, items in _by_task(objective).items():
            lines.append("")
            lines.append(f"### `{task}` — {len(items)} 项")
            for f in items:
                ac = f.get("ac") or "(task 级)"
                sev = f.get("severity", "?")
                lines.append(f"- **{ac}** · severity={sev}")
                lines.append(f"  - 证据: {f.get('evidence', '').strip()}")
                fix = f.get("suggested_fix", "").strip()
                if fix:
                    lines.append(f"  - 建议: {fix}")
                if _adj(f) == "added":
                    note = f.get("audit_note", "").strip()
                    lines.append(f"  - _(全局补充{': ' + note if note else ''})_")
        lines.append("")

    if subjective:
        lines.append("## 需你裁决 (subjective — 机器不下终判)")
        lines.append("")
        lines.append("以下涉及 *该不该做 / scope / 意图 / 不可逆 / 安全*,无客观金标准。"
                     "机器只给证据与选项,**由你拍板**。")
        for task, items in _by_task(subjective).items():
            lines.append("")
            lines.append(f"### `{task}` — {len(items)} 项")
            for f in items:
                ac = f.get("ac") or "(task 级)"
                lines.append(f"- **{ac}** · severity={f.get('severity', '?')}")
                lines.append(f"  - 证据: {f.get('evidence', '').strip()}")
                opt = f.get("suggested_fix", "").strip()
                if opt:
                    lines.append(f"  - 选项: {opt}")
                if _adj(f) == "added":
                    note = f.get("audit_note", "").strip()
                    lines.append(f"  - _(全局补充{': ' + note if note else ''})_")
        lines.append("")

    if harden:
        lines.append("## L0 加固回流 (harden-L0 — 不需你处理)")
        lines.append("")
        lines.append(f"{len(harden)} 条 objective 缺口本应被 L0 拦下;已回流 T1 oracle,机器侧加固,"
                     "**不占用你的注意力**(故不在上面的裁决清单)。")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(PRIMARY_METRIC_NOTE)
    return "\n".join(lines) + "\n"


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Render plan-review guidance brief from adjudicated findings.")
    ap.add_argument("path", help="adjudicated findings JSON (round=2)")
    ap.add_argument("-o", "--out", default=None, help="output markdown path (default: stdout)")
    args = ap.parse_args()

    try:
        adjudicated = json.loads(Path(args.path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"[ERROR] cannot load {args.path}: {e}", file=sys.stderr)
        sys.exit(1)

    brief = build_brief(adjudicated)
    if args.out:
        Path(args.out).write_text(brief, encoding="utf-8")
        print(Path(args.out).resolve())
    else:
        sys.stdout.write(brief)


if __name__ == "__main__":
    main()
