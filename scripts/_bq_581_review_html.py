"""T-P1-581 review: render the 40 primary-story assignments as a review HTML.

One-off (prefix ``_``). Pulls the canonical decision table from the seed module
(scripts/seed_bq_primary_flags_20260421.ROWS) and enriches each row with the
chosen story's title + Chinese pitch + the question's other candidates, so the
reviewer can actually judge the pick. Output is opened via Start-Process.
"""
from __future__ import annotations

import html
import importlib.util
import sqlite3
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = _ROOT / "data" / "mle_prep.db"
OUT = _ROOT / "logs" / "review" / "bq_581_primary_review.html"

# import the seed module (filename starts with a digit-free name, load by path)
_spec = importlib.util.spec_from_file_location(
    "seed_bq581", _ROOT / "scripts" / "seed_bq_primary_flags_20260421.py")
_seed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_seed)
ROWS = _seed.ROWS

CAT_NAMES = {
    "ownership": "Ownership", "adaptability": "Adaptability", "impact": "Impact",
    "innovation": "Innovation", "problem_solving": "Problem Solving",
    "execution": "Execution", "leadership": "Leadership",
    "collaboration": "Collaboration", "communication": "Communication",
}


def _db():
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def _load():
    c = _db()
    q_text = {r["question_id"]: r["text"]
              for r in c.execute("SELECT question_id, text FROM behavioral_questions")}
    ex = {r["example_id"]: dict(r) for r in c.execute(
        "SELECT example_id, title, cn_elevator_pitch, result FROM behavioral_examples")}
    # candidates per question
    cand: dict[str, list[str]] = {}
    for r in c.execute(
        """SELECT q.question_id qc, e.example_id ec
           FROM question_example_links l
           JOIN behavioral_questions q ON l.question_id=q.id
           JOIN behavioral_examples e ON l.example_id=e.id"""):
        cand.setdefault(r["qc"], []).append(r["ec"])
    c.close()
    return q_text, ex, cand


def _pitch(ex: dict, ecode: str) -> str:
    row = ex.get(ecode, {})
    return (row.get("cn_elevator_pitch") or row.get("result") or "").strip()


def build() -> Path:
    q_text, ex, cand = _load()
    n = {"keep": 0, "accept-swap": 0, "override": 0}
    for r in ROWS:
        n[r["decision"]] = n.get(r["decision"], 0) + 1

    css = """
    body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,'Microsoft YaHei',sans-serif;
         max-width:1080px;margin:0 auto;padding:28px 22px;color:#1c2430;background:#f7f8fa;line-height:1.55}
    h1{font-size:25px;margin:0 0 4px} .sub{color:#5a6573;margin:0 0 18px;font-size:14px}
    .tally{background:#fff;border:1px solid #e3e7ee;border-radius:10px;padding:14px 18px;margin-bottom:22px}
    .tally b{font-size:15px}
    .gate{background:#fff7e6;border:1px solid #ffd591;border-radius:10px;padding:12px 16px;margin-bottom:22px;font-size:14px}
    h2{font-size:17px;margin:26px 0 10px;border-bottom:2px solid #e3e7ee;padding-bottom:5px}
    .card{background:#fff;border:1px solid #e3e7ee;border-radius:10px;padding:14px 16px;margin:10px 0;
          box-shadow:0 1px 2px rgba(20,30,50,.03)}
    .qline{font-size:15px;font-weight:600;margin-bottom:8px}
    .qid{display:inline-block;background:#eef2f8;color:#2c5b9e;border-radius:5px;padding:1px 7px;
         font-size:12px;font-weight:700;margin-right:8px;font-family:ui-monospace,Consolas,monospace}
    .pick{margin:6px 0;font-size:14px}
    .exid{font-family:ui-monospace,Consolas,monospace;font-weight:700;color:#13795b}
    .was{color:#b54708;font-size:12.5px}
    .title{color:#2a3340;font-weight:600}
    .pitch{color:#55606e;font-size:13px;margin-top:3px}
    .meta{margin-top:9px;font-size:13px;color:#3a4452;border-top:1px dashed #e8ebf1;padding-top:8px}
    .badge{display:inline-block;border-radius:5px;padding:1px 7px;font-size:11.5px;font-weight:700;margin-right:6px}
    .b-keep{background:#e7f6ec;color:#1a7f4b} .b-swap{background:#e7f0fd;color:#2c5b9e}
    .b-flag{background:#fdf0e7;color:#b54708}
    .dec-keep{color:#1a7f4b;font-weight:700} .dec-accept{color:#2c5b9e;font-weight:700}
    .dec-override{color:#b54708;font-weight:700}
    .ds{color:#5a6573} .note{color:#27313d}
    .cands{font-size:12px;color:#8a93a0;margin-top:6px}
    """

    parts = [f"<!doctype html><html lang='zh'><head><meta charset='utf-8'>"
             f"<title>T-P1-581 Primary-Story Review</title><style>{css}</style></head><body>"]
    parts.append("<h1>BQ-DEPTH-10 (T-P1-581) — Top-40 主打故事指派 · 审阅</h1>")
    parts.append("<p class='sub'>每行把一个 (题, 故事) link 置 <code>is_primary=1</code>。"
                 "流程:Claude 起草 → DeepSeek 判官(<code>deepseek-v4-pro</code>, temp0)→ "
                 "Claude accept-default 复审 → <b>你批准</b> → 幂等 .bak 守护 seed 落库。</p>")
    parts.append(f"<div class='tally'><b>复审统计:</b> {n.get('keep',0)} 条按草稿保留(DeepSeek 同意)· "
                 f"{n.get('accept-swap',0)} 条采纳 DeepSeek 换故事 · "
                 f"{n.get('override',0)} 条否决 DeepSeek(保留草稿,理由见各行)。"
                 f" 全部 40 个 primary 均为已存在的 link。</div>")
    parts.append("<div class='gate'><b>[审阅] 此为审阅稿,尚未写 DB。</b> 你批准后我才跑 "
                 "<code>seed_bq_primary_flags_20260421.py --apply</code>(先备份 + audit + 自校验每题恰一个 primary)。"
                 "可整批批准,或指出要改的行。</div>")

    by_cat: dict[str, list[dict]] = {}
    for r in ROWS:
        by_cat.setdefault(r["cat"], []).append(r)

    for cat in ["ownership", "adaptability", "impact", "innovation",
                "problem_solving", "execution", "leadership", "collaboration",
                "communication"]:
        rows = by_cat.get(cat, [])
        if not rows:
            continue
        parts.append(f"<h2>{CAT_NAMES[cat]} <span style='color:#9aa3b0;font-weight:400'>"
                     f"({len(rows)})</span></h2>")
        for r in rows:
            q, fin = r["q"], r["final"]
            qt = html.escape(q_text.get(q, "?"))
            title = html.escape(ex.get(fin, {}).get("title", "?"))
            pitch = html.escape(_pitch(ex, fin)[:240])
            was = (f" <span class='was'>(原草稿 {html.escape(r['draft'])})</span>"
                   if fin != r["draft"] else "")
            ds_badge = {"keep": "b-keep", "swap": "b-swap", "flag": "b-flag"}[r["ds"]]
            ds_label = r["ds"].upper() + (f"→{r['ds_sug']}" if r["ds_sug"] else "")
            dec_cls = {"keep": "dec-keep", "accept-swap": "dec-accept",
                       "override": "dec-override"}[r["decision"]]
            dec_label = {"keep": "保留", "accept-swap": "采纳换story",
                         "override": "否决DeepSeek"}[r["decision"]]
            others = [c for c in cand.get(q, []) if c != fin]
            cand_html = (f"<div class='cands'>该题其它候选: {html.escape(', '.join(others))}</div>"
                         if others else "")
            parts.append(
                f"<div class='card'>"
                f"<div class='qline'><span class='qid'>{html.escape(q)}</span>{qt}</div>"
                f"<div class='pick'>主打 → <span class='exid'>{html.escape(fin)}</span>{was} "
                f"<span class='title'>{title}</span>"
                f"<div class='pitch'>{pitch}</div></div>"
                f"<div class='meta'>"
                f"<span class='badge {ds_badge}'>DeepSeek {ds_label}</span> "
                f"<span class='ds'>{html.escape(r['ds_reason'])}</span><br>"
                f"<span class='{dec_cls}'>Claude 决定 · {dec_label}:</span> "
                f"<span class='note'>{html.escape(r['note'])}</span></div>"
                f"{cand_html}"
                f"</div>")
    parts.append("</body></html>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(parts), encoding="utf-8")
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"[581-review] wrote {p}")
