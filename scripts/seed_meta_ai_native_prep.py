"""Seed Meta AI-Native onsite prep doc as the slim hub for company_id=31.

Source: T-P0-670. After T-P0-667/668/669 created 3 deep sub-docs and T-P0-670
added a 4th (Prompt Best Practices), the original 临场速查 4-section doc became
redundant -- this script restructures doc id=82 in-place as a SLIM hub (<200
lines) that drawer-links to T1/T2/T3/T4-bp via `[title](cd://N)` markdown
(per T-P1-251 SlideOverPanel pattern; NEVER HTML <details>).

T-P0-675: cross-table-corruption fix. Sub-doc IDs (86/87/88/89) collide with
`problems.id` 86/87/88/89 -- the original db:// links accidentally resolved to
unrelated LeetCode problems through ProblemDrawer instead of opening the sub-
docs through CompanyDocDrawer. Switched to the cd:// scheme (T-P0-672/673/674)
so MarkdownPreview wires the correct drawer.

Sub-docs resolved at runtime by canonical title (so doc IDs survive a fresh
DB build):
  T1  '[Meta] Code-Pad LLM Prompt + 3-Step Playbook'
  T2  '[Meta] AI-Native Domain Breadth -- 5 Talking Points'
  T3  '[Meta] AI-Native Behavioral 5-Pack'
  T4-bp '[Meta] AI-Native -- 临场 Prompt 写作 Best Practices'

The hub keeps day-of practical: schedule + interviewer names + opening line +
60-sec離场 self-check (content unique to the hub, not duplicated in sub-docs).
Hub also serves as the GOLDEN landing for company_id=31 (is_golden=1) so
clicking Meta on the Companies page surfaces this hub by default.

Idempotency: sentinel <!-- META_AI_NATIVE_HUB_20260430 --> gates the write.
Second run = 0 writes when content is byte-identical (sub-doc IDs are part
of content; if they change, the hub is rewritten with new IDs).

Style: Chinese narration + English term expansion on first use. No emoji.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_AI_NATIVE_HUB_20260430 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta] AI-Native Onsite Prep (2026-05-01)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

# Sub-doc canonical titles. Resolved to ids at runtime.
SUB_T1_TITLE = "[Meta] Code-Pad LLM Prompt + 3-Step Playbook"
SUB_T2_TITLE = "[Meta] AI-Native Domain Breadth -- 5 Talking Points"
SUB_T3_TITLE = "[Meta] AI-Native Behavioral 5-Pack"
SUB_T4BP_TITLE = "[Meta] AI-Native -- 临场 Prompt 写作 Best Practices"
SUB_TITLES = (SUB_T1_TITLE, SUB_T2_TITLE, SUB_T3_TITLE, SUB_T4BP_TITLE)


def render_content(t1_id: int, t2_id: int, t3_id: int, t4bp_id: int) -> str:
    """Render hub markdown with sub-doc IDs substituted into db:// links."""
    return SENTINEL + f'''
# Meta AI-Native Onsite — 2026-05-01 Prep Hub

> 5/1 (五) 4 场虚拟 onsite. 本页是 hub: 当天早上扫一遍, 4 个 deep-dive 子文档
> 通过下方链接以 drawer (slide-over) 弹出 (ESC 关闭). **核心 framing**: 你
> 不是手撸 AI 代码的人, 是用 staff/PM 视角去 *driving* AI / *review* AI 输出
> 的 senior IC.

---

## 当天 schedule (UTC-7 / Pacific)

| 时段 | Round | Interviewer | Drawer 链接 (戳开看 deep-dive) |
|------|-------|-------------|-------------------------------|
| 09:00 | AI-Enabled ML System Design | Nailong Z. | [§T2 Domain Breadth -- 5 Talking Points](cd://{t2_id}) |
| 11:00 | AI-Native Coding | Sai Srujan E. | [§T1 Code-Pad LLM Prompt + 3-Step Playbook](cd://{t1_id}) · [§T4-bp 临场 Prompt 写作 Best Practices](cd://{t4bp_id}) |
| 13:00 | AI-Native Coding | Nikhil U. | [§T1 Code-Pad LLM Prompt + 3-Step Playbook](cd://{t1_id}) · [§T4-bp 临场 Prompt 写作 Best Practices](cd://{t4bp_id}) |
| 15:00 | AI-Native Behavioral | (pending) | [§T3 Behavioral 5-Pack](cd://{t3_id}) |

**休息 / 饮水 / 上厕所窗口**: 09:45-11:00 (75 min) · 12:00-13:00 (60 min) ·
14:00-15:00 (60 min). 中午吃饭安排进 12:00-13:00.

---

## §T1 Code-Pad LLM Prompt + 3-Step Playbook

两场 AI-Native Coding (11:00 / 13:00) 的 code-pad 临场 playbook: high-level
idea 先开口, 给 LLM 设 acceptance criteria, 下半场重 review 不重 typing.

[**[打开 §T1 完整 playbook → drawer]**](cd://{t1_id})

## §T2 AI-Native Domain Breadth -- 5 Talking Points

09:00 ML System Design round 的 5 条 domain 谈资 (LLM serving / eval /
RAG / agent / cost). 用来在 SD round 主动 give tradeoff + 在 buzzword 周围
留 specific 可观测的 statement.

[**[打开 §T2 5 Talking Points → drawer]**](cd://{t2_id})

## §T3 AI-Native Behavioral 5-Pack

15:00 BQ round 的 5 条 story (EX-14 / BLOG-03 / EX-01 / EX-05 / EX-17).
每条都有 30-45 秒中文口述 + English kill-line + AI-native angle + match-
question hints, 末尾 5-trigger -> story routing table.

[**[打开 §T3 Behavioral 5-Pack → drawer]**](cd://{t3_id})

## §T4-bp 临场 Prompt 写作 Best Practices

两场 coding round 之前 5 分钟扫一遍. 思考顺序 (8 步 mental sequence) +
逻辑顺序 (prompt 字面 7 块结构) + 5 个 anti-patterns + worked weak-vs-
strong example.

[**[打开 §T4-bp Prompt Best Practices → drawer]**](cd://{t4bp_id})

---

## 共通 pattern (4 场都适用)

| 维度 | 做对的样子 | 翻车的样子 |
|------|-----------|-----------|
| Think fast | 30 秒内 high-level 草图 + 1-2 候选方案 | 沉默 2 分钟想 "完美答案" |
| Think out loud | 边想边讲, 不确定也讲 | 脑里走完才开口, interviewer 不知你卡哪 |
| Be proactive | 主动 propose 下一步 / 主动给 tradeoff / 主动 surface risk | 等 interviewer 问什么答什么 |
| Prove != trust AI | 每个 AI 输出都 mentally run / 主动 point out gap | "AI 写的应该没问题吧" |
| Senior framing | "我会这么 drive 这个项目..." | 学生口吻 "请问这样对吗?" |

---

## 开场 90 秒 opening line (4 场通用)

> "Thanks. Before we dive in -- I want to set the framing: my background is
> {{senior MLE on relevance / search ranking}}, and the way I work with AI in
> production is to treat LLM output as a junior-PR draft that I review and
> own the merge button on. So in this round you'll see me clarifying the
> contract, asking the AI to show its reasoning before code, and pushing
> back on its first answer. Let me know if you want me to skip that and
> just type."

(Interviewer 通常会说 "no please go ahead", 这就是绿灯; 偶尔会说 "skip,
just type", 那就 type 但 review 节奏不变.)

---

## 离场前 60 秒 cheat sheet (每场结束前自检)

1. 我开口的第一句是 **clarification 还是 high-level idea**? (都不是 = 重置)
2. 我有没有让 interviewer 看到我**心里的图**而不是只看到屏幕上的 AI 文本?
3. 我**主动**指出过 AI 输出的 1+ 个问题吗? (coding 必备; design 用 "这个
   组件的失败模式是" 替代)
4. 我对每个选择都讲过 **tradeoff** 吗?
5. (BQ round 专属) 我有没有按 §T3 的 trigger->story map 选对 story, 留了
   kill-line + artifact reference?

---

> **如果 AI 工具卡住**: 立刻口头说 "let me work this out manually first",
> 把它当 PM 在等技术 demo 时切到白板. 卡 AI 不是失分, 被 AI 卡住才是.
'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the rendered hub content."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## 当天 schedule",
        "## §T1 Code-Pad LLM Prompt",
        "## §T2 AI-Native Domain Breadth",
        "## §T3 AI-Native Behavioral 5-Pack",
        "## §T4-bp 临场 Prompt 写作 Best Practices",
        "## 共通 pattern",
        "## 开场 90 秒 opening line",
        "## 离场前 60 秒 cheat sheet",
        "Nailong Z.",
        "Sai Srujan E.",
        "Nikhil U.",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    if "<details>" in content or "</details>" in content:
        raise RuntimeError(
            "HTML <details> drawers are forbidden -- use [title](db://N) "
            "markdown links so MarkdownPreview opens SlideOverPanel"
        )
    n_cd_links = len(re.findall(r"\]\(cd://\d+\)", content))
    if n_cd_links < 6:
        raise RuntimeError(
            f"expected >=6 'cd://' drawer links (4 sub-docs, T1+T4bp linked "
            f"twice from schedule), got {n_cd_links}"
        )
    n_stale_db_links = len(re.findall(r"\]\(db://\d+\)", content))
    if n_stale_db_links:
        raise RuntimeError(
            f"hub must use cd:// for sub-docs, found {n_stale_db_links} stale "
            f"db:// link(s) (T-P0-675 cross-table-corruption regression)"
        )
    # Slim invariant: under 200 lines (excluding sentinel comment).
    n_lines = content.count("\n") + 1
    if n_lines > 200:
        raise RuntimeError(
            f"hub exceeded 200-line slim budget: got {n_lines} lines"
        )
    emoji_ranges = (
        (0x1F300, 0x1F6FF),
        (0x1F900, 0x1F9FF),
        (0x2600, 0x27BF),
        (0x1F000, 0x1F2FF),
    )
    for ch in content:
        cp = ord(ch)
        for lo, hi in emoji_ranges:
            if lo <= cp <= hi:
                raise RuntimeError(
                    f"emoji char detected at codepoint U+{cp:04X}: {ch!r}"
                )
    if not (2500 <= len(content) <= 6000):
        raise RuntimeError(f"content length {len(content)} outside 2500-6000")


def resolve_sub_doc_ids(conn: sqlite3.Connection) -> dict[str, int]:
    """Look up each sub-doc by canonical title, return title -> id map."""
    out: dict[str, int] = {}
    for title in SUB_TITLES:
        row = conn.execute(
            "SELECT id FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, title),
        ).fetchone()
        if row is None:
            raise RuntimeError(
                f"sub-doc not found: title={title!r} -- run T1/T2/T3/T4-bp "
                f"seed scripts first (T-P0-667/668/669/670)"
            )
        out[title] = row[0]
    return out


def main() -> int:
    """Restructure the Meta AI-Native hub doc as a slim drawer-link landing."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        sub_ids = resolve_sub_doc_ids(conn)
        t1 = sub_ids[SUB_T1_TITLE]
        t2 = sub_ids[SUB_T2_TITLE]
        t3 = sub_ids[SUB_T3_TITLE]
        t4bp = sub_ids[SUB_T4BP_TITLE]
        print(
            f"[OK] sub-docs resolved: T1={t1} T2={t2} T3={t3} T4-bp={t4bp}"
        )

        content = render_content(t1, t2, t3, t4bp)
        validate_content(content)

        cur = conn.execute(
            "SELECT id, content, is_golden FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        )
        existing = cur.fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(content)

        if existing is None:
            conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                "content_hash, is_golden, golden_at, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    content,
                    SOURCE_TYPE,
                    DOC_KIND,
                    new_hash,
                    1,
                    now,
                    now,
                    now,
                ),
            )
            conn.commit()
            new_id = conn.execute(
                "SELECT id FROM company_documents "
                "WHERE company_id = ? AND title = ?",
                (COMPANY_ID, DOC_TITLE),
            ).fetchone()[0]
            print(
                f"[INSERT] id={new_id} len={len(content)} "
                f"hash={new_hash[:12]}... is_golden=1"
            )
        else:
            existing_id, existing_content, existing_golden = existing
            if (
                SENTINEL in existing_content
                and existing_content == content
                and existing_golden == 1
            ):
                print(
                    f"[UNCHANGED] id={existing_id} sentinel + content + "
                    f"is_golden=1 all match; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, is_golden = ?, "
                    "golden_at = COALESCE(golden_at, ?), updated_at = ? "
                    "WHERE id = ?",
                    (content, new_hash, 1, now, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(content)} delta={len(content)-old_len:+d} "
                    f"is_golden -> 1"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
