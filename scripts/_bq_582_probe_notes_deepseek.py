"""T-P1-582 BQ-DEPTH-11: DeepSeek probe_notes generator for the top-40 BQ tail.

One-off (prefix ``_``) generation tool, NOT a DB writer. It:
  1. Reads the live DB for a batch of questions that still lack ``probe_notes``.
  2. For each, pulls full per-question context: question text + category, the
     ``is_primary`` linked example's full STAR detail (the DB is the source of
     truth for which example is primary -- post-T-P1-581 approval, NOT the 581
     draft), and a one-line pitch of every other linked candidate.
  3. Feeds DeepSeek (temperature 0) the BQ-DEPTH-09 calibration entries verbatim
     as the locked golden-voice few-shot, then asks for the 4-field probe_notes
     JSON for each target question.
  4. Writes a JSON sidecar (the seed script consumes it after user approval) plus
     a self-contained review HTML for human spot-check.

Schema (locked by BQ-DEPTH-09 calibration):
  {core_signal: str,
   what_good_looks_like: [str, ...],     # MUST reference the is_primary EX-NN story
   what_L5_adds: [str, ...],
   common_failure_modes: [str, ...]}
Content rules: 中文叙述 + 英文术语; all 4 fields required; no angle_label
(angle lives in prose); reference the is_primary story in what_good_looks_like.

Run from a SUPERVISED session (it needs scripts/lib/.env.deepseek):
  PYTHONUTF8=1 /c/Anaconda/python.exe scripts/_bq_582_probe_notes_deepseek.py --batch 1
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import deepseek_creds  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mle_prep.db"
DOCS = ROOT / "docs"

# 36-question tail (top-40 minus the 4 BQ-DEPTH-09 calibration entries), split
# into 4 sub-batches of 9 per the task spec (user spot-checks between batches).
BATCHES: dict[int, list[str]] = {
    1: ["OWN-2", "OWN-6", "OWN-8", "OWN-11", "ADP-11", "ADP-10", "ADP-1", "ADP-15", "IMP-11"],
    2: ["IMP-2", "IMP-3", "IMP-10", "INN-4", "INN-2", "INN-8", "INN-5", "PS-1", "PS-11"],
    3: ["PS-2", "PS-4", "PS-10", "EXE-5", "EXE-3", "EXE-9", "EXE-13", "LDR-1", "LDR-3"],
    4: ["LDR-6", "LDR-2", "COL-1", "COL-3", "COL-5", "COL-6", "COM-1", "COM-2", "COM-3"],
}
# BQ-DEPTH-09 calibration entries -- the locked golden-voice exemplars.
CALIBRATION = ["OWN-1", "ADP-5", "PS-6", "ADP-19"]

GEN_SYSTEM = (
    "你是资深 FAANG 行为面试 (behavioral interview) 教练, 正在为一道 BQ 题撰写 "
    "probe_notes -- 一份给候选人自己用的备考 crib: 拆解『这道题真正在 probe 什么』、"
    "『一个好答案长什么样 (结合候选人指定的 primary STAR story)』、『L5 比 L4 多给出什么』、"
    "以及『常见 failure modes』。\n\n"
    "严格内容规则 (与 BQ-DEPTH-09 calibration 锁定一致):\n"
    "1. 中文叙述 + 英文术语 (例如 first-person ownership / L5 bar / blast radius / "
    "frame pivot / default shift), 与示例 voice 完全一致, 不要翻译腔。\n"
    "1a. 标点口径 (硬性, 与 calibration 完全一致): 句末用全角句号 '。' (这是 calibration 唯一"
    "保留的全角符号); 其余标点一律半角 ', ' ': ' '; ' '(' ')' '?' '!' (绝不用全角 ',' ':' "
    "';' '(' ')' '?' '!'); 列举不用顿号 '、', 改用 '/'; 破折号用 ASCII '--' (不用 '—'); "
    "中英文之间、英文术语两侧留一个半角空格 (写 'principal researcher 的反对', 不写 "
    "'principal researcher的反对'); 引用候选人原话用直引号 'like this'。\n"
    "2. 输出 JSON, 恰好 4 个字段, 无多余字段:\n"
    "   - core_signal: 一个字符串。固定句式开头『这题本质在问: ...』, 并点明『L5 bar 是 ...』。\n"
    "   - what_good_looks_like: 字符串数组 (4 条)。其中必须有至少一条显式引用候选人的 "
    "is_primary story (用它的 EX 编号 + 一个具体动作/原话), 例如『EX-15 primary 动作: ...』。\n"
    "   - what_L5_adds: 字符串数组 (3 条)。讲 L5 相对 L4 多出来的 frame-level / org-level / "
    "self-awareness 动作。\n"
    "   - common_failure_modes: 字符串数组 (4 条)。每条点出一类典型失分模式 (junior 答案 / "
    "redemption tail 太甜 / scapegoating via abstraction / 没有具体 blast radius 等), "
    "并说明 reviewer 为何扣分。\n"
    "3. 不要 angle_label 字段, 不要任何 markdown fence, 不要 prose 包裹。只输出裸 JSON 对象。\n"
    "4. what_good_looks_like 引用的 EX 编号必须是下面 context 里标了 [PRIMARY] 的那个, "
    "动作要落到该 story 的 situation/action/result 具体内容, 不要泛泛而谈。\n"
    "5. render-safe (前端用 react-markdown + remark-math + rehype-katex 渲染, 必须避免被误解析): "
    "绝不出现裸 '$' (会触发 KaTeX 数学渲染); 不用裸 '<' 或 '>' (会被当 HTML); "
    "百分比直接写成 '5%'; 不要在字符串里放 markdown 控制语法 (行首 '#'/'-'/'*'/'>'、表格 '|'、"
    "链接 '[x](y)'、代码反引号); 每条 bullet 是一句普通文本, 不自带项目符号。"
)


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def _question_ctx(c: sqlite3.Connection, qcode: str) -> dict:
    """Pull question + its is_primary example (full STAR) + other linked pitches."""
    q = c.execute(
        "SELECT id, question_id, text, category_name FROM behavioral_questions WHERE question_id=?",
        (qcode,),
    ).fetchone()
    if q is None:
        raise ValueError(f"{qcode}: no such question row")
    rows = c.execute(
        """SELECT e.example_id ec, e.title title, e.situation situation, e.task task,
                  e.action action, e.result result, e.evidence_quotes evidence,
                  e.cn_elevator_pitch pitch, l.is_primary ip
           FROM question_example_links l
           JOIN behavioral_examples e ON l.example_id = e.id
           WHERE l.question_id = ? ORDER BY l.is_primary DESC""",
        (q["id"],),
    ).fetchall()
    primary = next((r for r in rows if r["ip"]), None)
    return {
        "question_id": qcode,
        "text": q["text"],
        "category": q["category_name"],
        "primary": primary,
        "others": [r for r in rows if not r["ip"]],
    }


def _render_ctx(ctx: dict) -> str:
    """Render a question's context block for the DeepSeek user message."""
    p = ctx["primary"]
    lines = [f"QUESTION ({ctx['category']}): {ctx['text']}", ""]
    if p is None:
        lines.append("[WARN] 这道题没有 is_primary link -- 请基于 question intent 撰写, "
                     "what_good_looks_like 用最贴切的 linked story。")
    else:
        def _clip(s: str | None, n: int) -> str:
            return (s or "").strip().replace("\n", " ")[:n]
        lines.append(f"[PRIMARY] {p['ec']} | {p['title']}")
        lines.append(f"  situation: {_clip(p['situation'], 400)}")
        lines.append(f"  task: {_clip(p['task'], 300)}")
        lines.append(f"  action: {_clip(p['action'], 600)}")
        lines.append(f"  result: {_clip(p['result'], 400)}")
        if p["evidence"]:
            lines.append(f"  evidence_quotes: {_clip(p['evidence'], 300)}")
        if p["pitch"]:
            lines.append(f"  cn_elevator_pitch: {_clip(p['pitch'], 300)}")
    if ctx["others"]:
        lines.append("")
        lines.append("OTHER LINKED STORIES (context only, 不必引用):")
        for r in ctx["others"]:
            pitch = (r["pitch"] or r["result"] or "").strip().replace("\n", " ")[:160]
            lines.append(f"- {r['ec']} | {r['title']}: {pitch}")
    return "\n".join(lines)


def _fewshot(c: sqlite3.Connection) -> list[dict]:
    """Build the calibration few-shot: rendered context -> exact probe_notes JSON."""
    shots = []
    for qcode in CALIBRATION:
        ctx = _question_ctx(c, qcode)
        pn = c.execute(
            "SELECT probe_notes FROM behavioral_questions WHERE question_id=?", (qcode,)
        ).fetchone()["probe_notes"]
        shots.append({"user": _render_ctx(ctx), "assistant": pn})
    return shots


# deepseek-v4-pro is a reasoning model: reasoning tokens eat the budget before
# content, AND a full 4-field probe_notes is long -- a fixed cap truncates
# mid-JSON on the longest entries intermittently (different entry each run). Retry
# with escalating budget until the JSON parses (lesson: token_limits).
_MAX_TOKENS_LADDER = (8000, 16000, 24000)


def _gen_one(cli, model: str, shots: list[dict], ctx: dict) -> dict:
    """One DeepSeek generation for a question's probe_notes; retries on truncation."""
    msgs = [{"role": "system", "content": GEN_SYSTEM}]
    # Few-shot: 2 calibration exemplars (ownership-failure + mistake) keep the
    # prompt focused; all 4 fields + voice are demonstrated by these two.
    for shot in shots[:2]:
        msgs.append({"role": "user", "content": shot["user"]})
        msgs.append({"role": "assistant", "content": shot["assistant"]})
    msgs.append({"role": "user", "content": _render_ctx(ctx)})

    last_raw = ""
    for max_tokens in _MAX_TOKENS_LADDER:
        resp = cli.chat.completions.create(
            model=model, temperature=0, max_tokens=max_tokens, messages=msgs
        )
        raw = (resp.choices[0].message.content or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        last_raw = raw
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # likely truncated mid-JSON -- bump the budget and retry.
            continue
    return {"_parse_error": last_raw[:400]}


# Deterministic punctuation normalization -- guarantees the calibration口径
# regardless of model compliance. 全角句号 '。' is the ONE full-width char kept
# (it is canonical in calibration); everything else is mapped to half-width.
_PUNCT_FIX = {
    "—": "--", "、": "/",
    "，": ", ", "：": ": ", "；": "; ", "？": "?", "！": "!",
    "（": "(", "）": ")",
}


def _normalize_punct(pn: dict) -> dict:
    """Map drift punctuation to the calibration口径 (keeps '。'); idempotent.

    Also rewrites numeric comparison operators that start with a render-unsafe
    '<' ('<' opens an HTML tag in react-markdown) into calibration's Chinese
    prose form: '<=N' -> '不超过 N', '<N' -> '低于 N'. This is the recurring
    DeepSeek drift class (latency '<=1%' budget etc.); '<=' must be tried before
    bare '<'. A bidirectional-arrow '<->' or other free-standing '<' is left for
    the render-safety oracle to flag (those need human judgment, not a blind map).
    """
    def fix(s: str) -> str:
        for a, b in _PUNCT_FIX.items():
            s = s.replace(a, b)
        # numeric comparisons: '<=' before '<' so '<=1%' isn't half-eaten.
        s = re.sub(r"<=\s*(?=\d)", "不超过 ", s)
        s = re.sub(r"<\s*(?=\d)", "低于 ", s)
        while "  " in s:
            s = s.replace("  ", " ")
        return s.strip()

    out: dict = {}
    for k, v in pn.items():
        if isinstance(v, str):
            out[k] = fix(v)
        elif isinstance(v, list):
            out[k] = [fix(x) if isinstance(x, str) else x for x in v]
        else:
            out[k] = v
    return out


def _validate(pn: dict) -> list[str]:
    """Return a list of schema/content problems for one generated entry."""
    problems = []
    if "_parse_error" in pn:
        return [f"JSON parse failed: {pn['_parse_error'][:120]}"]
    fields = {
        "core_signal": str,
        "what_good_looks_like": list,
        "what_L5_adds": list,
        "common_failure_modes": list,
    }
    for f, typ in fields.items():
        v = pn.get(f)
        if v is None or (isinstance(v, (str, list)) and len(v) == 0):
            problems.append(f"empty/missing field: {f}")
        elif not isinstance(v, typ):
            problems.append(f"wrong type for {f}: {type(v).__name__}")
    extra = set(pn) - set(fields)
    if extra:
        problems.append(f"unexpected field(s): {sorted(extra)}")

    # Punctuation + render-safety oracle (rules 1a + 5): scan all text.
    blob = " ".join(
        [str(pn.get("core_signal", ""))]
        + [str(x) for f in ("what_good_looks_like", "what_L5_adds", "common_failure_modes")
           for x in (pn.get(f) or []) if isinstance(pn.get(f), list)]
    )
    # '。' is the one canonical full-width char (calibration uses it); allow it.
    fullwidth = [ch for ch in "，：；（）？！、" if ch in blob]
    if fullwidth:
        problems.append(f"full-width punctuation: {''.join(fullwidth)}")
    if "—" in blob:
        problems.append("em-dash '—' (use ASCII '--')")
    # '$' triggers KaTeX, '<' starts an HTML tag in react-markdown. '>' is safe
    # inline (only a LEADING '>' is a blockquote) and is calibration-canonical
    # (used in '->' arrows and 'a > b' comparisons), so it is allowed.
    unsafe = [ch for ch in "$<" if ch in blob]
    if unsafe:
        problems.append(f"render-unsafe char(s): {''.join(unsafe)}")
    bullets = [x for f in ("what_good_looks_like", "what_L5_adds", "common_failure_modes")
               for x in (pn.get(f) or []) if isinstance(x, str)]
    if any(b.lstrip().startswith(">") for b in bullets):
        problems.append("bullet starts with '>' (renders as blockquote)")
    return problems


def _write_review_html(batch: int, results: list[dict]) -> Path:
    """Render a self-contained HTML for human spot-check (source left / notes right)."""
    out = DOCS / f"bq_probe_notes_batch{batch}_20260421.review.html"
    parts = [
        "<!doctype html><meta charset='utf-8'>",
        f"<title>BQ probe_notes review -- batch {batch}</title>",
        "<style>body{font:15px/1.6 -apple-system,Segoe UI,sans-serif;margin:0;"
        "background:#f6f7f9;color:#1a1a1a}header{background:#1f2937;color:#fff;"
        "padding:14px 22px}h1{font-size:18px;margin:0}.q{background:#fff;margin:18px;"
        "border:1px solid #e3e6ea;border-radius:10px;overflow:hidden}"
        ".qh{padding:12px 16px;background:#eef2f7;border-bottom:1px solid #e3e6ea}"
        ".qh b{color:#b91c1c}.grid{display:grid;grid-template-columns:340px 1fr;gap:0}"
        ".src{padding:14px 16px;border-right:1px solid #eee;background:#fafbfc;font-size:13px}"
        ".notes{padding:14px 16px}.f{margin:0 0 14px}.f h4{margin:0 0 6px;font-size:13px;"
        "color:#2563eb;text-transform:uppercase;letter-spacing:.04em}"
        ".f ul{margin:0;padding-left:18px}.f li{margin:0 0 5px}"
        ".bad{color:#b91c1c;font-weight:600}.muted{color:#6b7280}</style>",
        f"<header><h1>BQ-DEPTH-11 (T-P1-582) probe_notes -- batch {batch} -- "
        "AWAITING SPOT-CHECK</h1><div class='muted' style='color:#cbd5e1;font-size:13px'>"
        "原生 source (题面+primary story) 在左, 生成的 probe_notes 在右。"
        f"DeepSeek deepseek-v4-pro, temperature 0. 批准后由 seed_bq_probe_notes (--batch {batch}) 幂等写入。"
        "</div></header>",
    ]
    for r in results:
        pn = r["probe_notes"]
        p = r["primary_rendered"]
        parts.append("<div class='q'>")
        bad = (" <span class='bad'>[" + "; ".join(r["problems"]) + "]</span>") if r["problems"] else ""
        parts.append(f"<div class='qh'><b>{escape(r['question_id'])}</b> "
                     f"<span class='muted'>({escape(r['category'])})</span> "
                     f"{escape(r['text'])}{bad}</div>")
        parts.append("<div class='grid'>")
        parts.append(f"<div class='src'><pre style='white-space:pre-wrap;margin:0;"
                     f"font:12px/1.5 ui-monospace,Consolas,monospace'>{escape(p)}</pre></div>")
        parts.append("<div class='notes'>")
        if "_parse_error" in pn:
            parts.append(f"<div class='bad'>PARSE ERROR: {escape(pn['_parse_error'])}</div>")
        else:
            parts.append(f"<div class='f'><h4>core_signal</h4><div>{escape(str(pn.get('core_signal','')))}</div></div>")
            for key, label in [("what_good_looks_like", "what_good_looks_like"),
                               ("what_L5_adds", "what_L5_adds"),
                               ("common_failure_modes", "common_failure_modes")]:
                items = pn.get(key) or []
                lis = "".join(f"<li>{escape(str(x))}</li>" for x in items)
                parts.append(f"<div class='f'><h4>{label}</h4><ul>{lis}</ul></div>")
        parts.append("</div></div></div>")
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


def main() -> int:
    from openai import OpenAI

    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, required=True, choices=sorted(BATCHES))
    args = ap.parse_args()
    qcodes = BATCHES[args.batch]

    creds = deepseek_creds.load()
    print(f"[582-gen] DeepSeek creds: {creds!r}")
    cli = OpenAI(api_key=creds.key, base_url=creds.base_url)

    c = _conn()
    shots = _fewshot(c)
    print(f"[582-gen] few-shot from calibration: {CALIBRATION[:2]}")

    results = []
    for i, qcode in enumerate(qcodes, 1):
        ctx = _question_ctx(c, qcode)
        pn = _gen_one(cli, creds.model, shots, ctx)
        if "_parse_error" not in pn:
            pn = _normalize_punct(pn)
        problems = _validate(pn)
        results.append({
            "question_id": qcode,
            "text": ctx["text"],
            "category": ctx["category"],
            "primary_id": ctx["primary"]["ec"] if ctx["primary"] else None,
            "primary_rendered": _render_ctx(ctx),
            "probe_notes": pn,
            "problems": problems,
        })
        flag = (" PROBLEMS: " + "; ".join(problems)) if problems else " OK"
        print(f"  [{i}/{len(qcodes)}] {qcode:7} primary={results[-1]['primary_id']}{flag}")

    sidecar = DOCS / f"bq_probe_notes_batch{args.batch}_20260421.deepseek.json"
    sidecar.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[582-gen] wrote sidecar -> {sidecar}")

    html = _write_review_html(args.batch, results)
    print(f"[582-gen] wrote review HTML -> {html}")

    n_bad = sum(1 for r in results if r["problems"])
    print(f"[582-gen] batch {args.batch}: {len(results)} generated, {n_bad} with problems.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
