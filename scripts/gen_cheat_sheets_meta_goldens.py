"""Generator (T-P1-924): DeepSeek-author cheat sheets for the 9 Meta golden rows.

Authoring AID (supervised-only; needs scripts/lib/.env.deepseek). Reads each
system_designs row's structured columns, distills them via scripts/lib/ds_distill
into a doc-85-1.6 four-part cheat sheet, ASCII-normalizes the result, and writes
it to scripts/cheatsheet_drafts/<slug>.md.

The .md drafts are the git-tracked, human-reviewable source of truth; the
deterministic seed (scripts/seed_cheat_sheets_meta_goldens.py) reads them and
upserts into the DB. This file is NEVER run in autorun (DeepSeek key absent ->
ds_distill raises FileNotFoundError by design).

Usage:
    python scripts/gen_cheat_sheets_meta_goldens.py                 # all 9
    python scripts/gen_cheat_sheets_meta_goldens.py <slug> [<slug>] # subset
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "lib"))

import ds_distill  # noqa: E402

_DB = _ROOT / "data" / "mle_prep.db"
_DRAFTS = _ROOT / "scripts" / "cheatsheet_drafts"

# The 9 Meta MLSD golden rows missing a cheat_sheet (display_order 134-142).
SLUGS: list[str] = [
    "meta-v2v-search-golden",
    "meta-ads-golden",
    "meta-event-rec-golden",
    "meta-location-rec-golden",
    "meta-yelp-restaurant-golden",
    "meta-fb-newsfeed-golden",
    "meta-ig-story-golden",
    "meta-spotify-music-golden",
    "meta-event-attendance-golden",
]

_COLS = [
    ("overview", "概览 Overview"),
    ("architecture", "架构 Architecture"),
    ("dataflow", "数据流 Data Flow"),
    ("formulas", "公式 Formulas"),
    ("production_constraints", "生产约束 Production Constraints"),
    ("tradeoffs", "权衡 Tradeoffs"),
    ("defense", "应答 Defense"),
    ("verbal_outline", "口述 Verbal Outline"),
]

_SYSTEM = """你是资深 ML 系统设计面试教练。给定某道 ML system design 题的结构化笔记, 生成一张"面试前 5 分钟扫一眼"的一页纸速查表 (cheat sheet)。

严格输出四段式 (doc 85 §1.6 风格), 顺序固定:
1. 顶部一行标题: `## 速查表 (Cheat Sheet) — <题目简称>`
2. **竖排伪架构**: 一个 code-fence (```...```), 展示请求/数据流主干 (retrieval -> ranking -> rerank 这种)。
3. **关键词块**: 用 **加粗** 标出行业黑话 (模型名/算法/指标/基础设施), 每个带一句极短注。
4. **Senior 信号表**: Markdown 表, 列为 `维度 | 不及格答法 | Staff Golden 答法`, 3-5 行。
5. **mini 术语表**: Markdown 表, 列为 `术语 | 一句话`, 展开关键缩写。

硬性要求:
- 风格: 中文叙述 + 英文术语 (首次出现给英文全称)。
- 长度 ~1500-2000 字符。
- 只能从提供的源笔记提炼, 禁止编造源中没有的事实/数字/模型。
- **架构图与全文只用纯 ASCII**: 箭头用 `->`, 竖线用 `|`, 向下用 `v`, 乘号用 `*`。禁止使用制表符 (│ ─ ▼ ▲), 禁止 ⨯ · 等非 ASCII 符号, 禁止非断行连字符。禁止 emoji。
- 数学如有用 $...$ 或 $$...$$。
- 直接输出纯 Markdown 正文, 不要任何前言/解释, 不要用 ```markdown 把整体再包一层。"""

# Mechanical ASCII normalization belt-and-suspenders (the prompt asks for ASCII,
# this guarantees it even if the model slips).
_NORMALIZE = {
    "│": "|",   # | box-drawing vertical
    "─": "-",   # - box-drawing horizontal
    "▼": "v",   # v down-triangle
    "▲": "^",   # ^ up-triangle
    "→": "->",  # -> rightwards arrow
    "↓": "v",   # down arrow
    "⨯": "x",   # x vector cross product
    "×": "x",   # x multiplication sign
    "·": "*",   # * middle dot
    "‑": "-",   # - non-breaking hyphen
    "–": "-",   # en dash -> hyphen
    "—": "--",  # em dash
}

# Emoji / pictograph ranges that must NOT appear (project no-emoji rule).
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF"
    "\U0001F1E6-\U0001F1FF\U00002B00-\U00002BFF]"
)


def normalize(text: str) -> str:
    """Strip code-fence wrapper, apply ASCII map, reject emoji."""
    t = text.strip()
    # Drop an accidental ```markdown ... ``` wrapper around the WHOLE output.
    if t.startswith("```"):
        first_nl = t.find("\n")
        if first_nl != -1 and t.endswith("```"):
            t = t[first_nl + 1 : -3].strip()
    for bad, good in _NORMALIZE.items():
        t = t.replace(bad, good)
    emojis = sorted(set(_EMOJI.findall(t)))
    if emojis:
        raise SystemExit(
            f"generated text contains emoji {[hex(ord(e)) for e in emojis]} -- aborting"
        )
    return t + "\n"


def build_user(row: sqlite3.Row) -> str:
    parts = [f"# 题目: {row['title']}"]
    if row["subtitle"]:
        parts.append(f"> {row['subtitle']}")
    for key, label in _COLS:
        val = (row[key] or "").strip()
        if val:
            parts.append(f"\n## [源] {label}\n{val}")
    return "\n".join(parts)


def generate_one(slug: str, conn: sqlite3.Connection) -> Path:
    row = conn.execute(
        "SELECT title, subtitle, "
        + ", ".join(k for k, _ in _COLS)
        + " FROM system_designs WHERE slug=?",
        (slug,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"slug not found: {slug}")
    user = build_user(row)
    res = ds_distill.complete(_SYSTEM, user, max_tokens=8192, verbose=True)
    text = normalize(res.text)
    out = _DRAFTS / f"{slug}.md"
    out.write_text(text, encoding="utf-8")
    print(
        f"[gen] {slug}: source={len(user)} -> draft={len(text)} chars "
        f"(attempts={res.attempts}, completion_tok={res.usage.get('completion_tokens')}) -> {out.name}"
    )
    return out


def main() -> None:
    slugs = sys.argv[1:] or SLUGS
    unknown = [s for s in slugs if s not in SLUGS]
    if unknown:
        raise SystemExit(f"not Meta-golden slugs: {unknown}")
    _DRAFTS.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB)
    conn.row_factory = sqlite3.Row
    try:
        for slug in slugs:
            generate_one(slug, conn)
    finally:
        conn.close()
    print(f"done: {len(slugs)} draft(s) in {_DRAFTS}")


if __name__ == "__main__":
    main()
