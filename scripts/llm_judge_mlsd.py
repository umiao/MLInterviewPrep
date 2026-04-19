"""Gate 10 LLM-as-judge for MLSD V2 rewrites (per id=18 Appendix A.1 + A.1.v2).

Given V1 and V2 text files for the same section, asks Claude (Sonnet 4.6) to
score each on four 0-10 dimensions (A.1.v2 added the 4th):

  - Readability    : Does it flow as a coherent spoken narrative?
  - Triage         : Can a reader derive pick / reason / alternatives (>=3) /
                     switch-trigger from prose alone for every tech choice?
  - Density        : Does every sentence carry load (no fillers)?
  - Follow-up      : Does each tech-choice block preempt the 3 most-likely
                     interviewer follow-ups (common-question block)?

Pass condition: V2 must score STRICTLY GREATER than V1 on all four
dimensions. Ties fail.

Backward compat: responses missing the 4th dimension (legacy judge output)
are tolerated only when `--legacy-3-dim` is passed. Default is 4-dim strict.

Usage:
    python scripts/llm_judge_mlsd.py --v1-text path/to/v1.md --v2-text path/to/v2.md
    python scripts/llm_judge_mlsd.py --v1-text v1.md --v2-text v2.md --model claude-sonnet-4-6
    python scripts/llm_judge_mlsd.py --v1-text v1.md --v2-text v2.md --legacy-3-dim

Exit codes:
    0  V2 > V1 on all required dimensions (4 by default, 3 with --legacy-3-dim)
    1  V2 tied or worse on at least one dimension (FAIL)
    2  infra error (bad args, subprocess failure, unparseable response)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_MODEL = "claude-sonnet-4-6"
PER_CALL_TIMEOUT_S = 600

RUBRIC_SYSTEM_PROMPT = """You are a senior ML systems interviewer grading two versions of the same interview-answer section (V1 and V2) on prose quality. The material is L5-level ML system design, written in Chinese narration with English technical terms.

Score each version on four dimensions (0-10 integers only):

1. Readability: Does the text flow as a coherent spoken narrative? A senior interviewer listening to a candidate speak this aloud should follow without confusion — no awkward jumps from bullet to bullet, no missing connective tissue.

2. Triage completeness: For every tech choice (product, algorithm, protocol) named in the text, can the reader derive all required elements from the PROSE ALONE (not just from a tradeoff table): (a) what is picked, (b) the concrete reason, (c) **at least three named alternatives each with an explicit why-not**, (d) a switch trigger for changing picks. The 3-alternative bar (A.1.v2 tightening) is mandatory; 1-2 alternatives is a 4 at most.

3. Information density: Is every sentence carrying load — teaching, justifying, or connecting? Or are there filler sentences like "值得注意", "具体来说", "需要指出" that don't deliver follow-through?

4. Follow-up preemption coverage: For each tech choice, is there a "常见追问" or equivalent block preempting the 3 most-likely interviewer follow-ups? Surface mentions = low score; concrete numbers + tradeoff reasoning in the preempt = high score. A tech choice with zero preempted follow-ups is a 3 at most, regardless of how good the triage is.

Rubric anchors (0-10 integer scale):
  0-2  : incoherent / padded / empty / no preempt
  3-4  : weak but readable / sparse preempt
  5-6  : competent but patchy / partial preempt
  7-8  : solid L5-ready prose / 3+ preempts per choice
  9-10 : gold-standard, ready-to-ship / exhaustive preempt with quantitative reasoning

Return ONLY a single JSON object on one line:
{"readability": {"v1": N, "v2": N}, "triage": {"v1": N, "v2": N}, "density": {"v1": N, "v2": N}, "preemption": {"v1": N, "v2": N}, "verdict": "PASS|FAIL", "notes": "<one sentence>"}

PASS iff v2 > v1 on ALL four dimensions (strictly greater; ties fail). No preamble, no code fences, no explanation outside the JSON."""


def call_claude(v1_text: str, v2_text: str, model: str) -> dict:
    user_prompt = (
        "Score these two versions per the rubric.\n\n"
        "--- V1 START ---\n"
        f"{v1_text}\n"
        "--- V1 END ---\n\n"
        "--- V2 START ---\n"
        f"{v2_text}\n"
        "--- V2 END ---"
    )
    # Pipe the prompt via stdin so payloads >8K chars don't exceed the
    # Windows CreateProcess command-line limit (encountered on full-doc
    # V1 vs V2 judging where the combined text runs ~35K chars).
    cmd = [
        "claude",
        "-p",
        "--model",
        model,
        "--system-prompt",
        RUBRIC_SYSTEM_PROMPT,
        "--output-format",
        "json",
        "--no-session-persistence",
        "--tools",
        "",
        "--setting-sources",
        "user",
    ]
    result = subprocess.run(
        cmd,
        input=user_prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=PER_CALL_TIMEOUT_S,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (rc={result.returncode}): "
            f"stdout={result.stdout[:400]!r} stderr={result.stderr[:400]!r}"
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"claude -p returned non-JSON: {result.stdout[:400]!r}") from e
    content = payload.get("result") or payload.get("text") or ""
    if not content.strip():
        raise RuntimeError(f"claude -p empty content. keys={list(payload.keys())}")

    # The rubric returns JSON-only; tolerate a surrounding code fence.
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(l for l in lines if not l.startswith("```"))
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"judge returned non-JSON content: {text[:400]!r}") from e


DEFAULT_DIMENSIONS = ("readability", "triage", "density", "preemption")
LEGACY_DIMENSIONS = ("readability", "triage", "density")


def verify(judgment: dict, dimensions: tuple[str, ...] = DEFAULT_DIMENSIONS) -> tuple[bool, list[str]]:
    problems: list[str] = []
    for dim in dimensions:
        d = judgment.get(dim)
        if not isinstance(d, dict) or "v1" not in d or "v2" not in d:
            problems.append(f"missing/malformed dimension: {dim}")
            continue
        v1, v2 = d["v1"], d["v2"]
        if not (isinstance(v1, int) and isinstance(v2, int)):
            problems.append(f"{dim} scores not int: v1={v1!r} v2={v2!r}")
            continue
        if v2 <= v1:
            problems.append(f"{dim}: v1={v1} v2={v2} (need v2 > v1)")
    return (not problems), problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1-text", required=True, type=Path)
    ap.add_argument("--v2-text", required=True, type=Path)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument(
        "--legacy-3-dim",
        action="store_true",
        help="verify only the 3 legacy dimensions (skip preemption); "
             "new callers should omit this and use the A.1.v2 4-dim rubric",
    )
    args = ap.parse_args(argv)
    dims = LEGACY_DIMENSIONS if args.legacy_3_dim else DEFAULT_DIMENSIONS

    if not args.v1_text.exists():
        print(f"[FAIL] V1 file not found: {args.v1_text}", file=sys.stderr)
        return 2
    if not args.v2_text.exists():
        print(f"[FAIL] V2 file not found: {args.v2_text}", file=sys.stderr)
        return 2

    v1 = args.v1_text.read_text(encoding="utf-8")
    v2 = args.v2_text.read_text(encoding="utf-8")

    print(f"[INFO] V1 {len(v1)} chars, V2 {len(v2)} chars, model={args.model}")
    try:
        judgment = call_claude(v1, v2, args.model)
    except Exception as exc:
        print(f"[FAIL] judge call failed: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(judgment, ensure_ascii=False, indent=2))
    ok, problems = verify(judgment, dims)

    verdict_str = judgment.get("verdict", "")
    if ok and verdict_str != "PASS":
        print(f"[WARN] scores pass but judge verdict = {verdict_str!r}")
    if not ok:
        print(f"[FAIL] V2 did not strictly beat V1 on all {len(dims)} dimensions:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"[PASS] V2 > V1 on {', '.join(dims)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
