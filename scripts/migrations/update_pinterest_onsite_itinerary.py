"""
Pinterest VO itinerary now confirmed (received 2026-04-30 from candidate's calendar).
Update:
  - companies.id=29 interview_stages JSON (dates + interviewers per round)
  - companies.id=29 notes (correct round count/duration; add itinerary summary)
  - company_documents.id=83 ([Pinterest] ML Virtual Onsite Prep) — rewrite the top
    blockquote with concrete itinerary, attach interviewer + date + duration to each
    section header, replace the prep-call action item at the bottom with a
    day-by-day stamina strategy.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[2] / "data" / "mle_prep.db"
COMPANY_PINTEREST = 29
DOC_ID = 83


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


# ---- New interview_stages JSON ----
NEW_STAGES = [
    {"name": "Recruiter Call", "status": "completed"},
    {"name": "Phone Screen (60min)", "status": "completed"},
    {
        "name": "VO Day 1 R1: ML Systems Design (60min) — Yiyang Zhang",
        "status": "scheduled",
        "scheduled_at": "2026-05-05T15:00:00-07:00",
    },
    {
        "name": "VO Day 1 R2: HM/Competency (45min) — Daniel Liu (Manager II)",
        "status": "scheduled",
        "scheduled_at": "2026-05-05T16:00:00-07:00",
    },
    {
        "name": "VO Day 2 R1: Data/Algos (45min) — Jiankai Sun",
        "status": "scheduled",
        "scheduled_at": "2026-05-06T13:00:00-07:00",
    },
    {
        "name": "VO Day 2 R2: Data/Algos (45min) — Yijian Xiang",
        "status": "scheduled",
        "scheduled_at": "2026-05-06T14:00:00-07:00",
    },
    {
        "name": "VO Day 2 R3: ML Practitioner (60min) — Zihao Zhang",
        "status": "scheduled",
        "scheduled_at": "2026-05-06T15:00:00-07:00",
    },
]

NEW_NOTES = """Senior ML Engineer position
TC ~$500K/yr
Hiring model: general pool, ~5 HC available, competitive Team Match required

2026-04-08 Recruiter Call Summary:
- Phone Screen (60min): ML Project Discussion + 3 ML Fundamentals questions + Coding
- Virtual Onsite (5 rounds, ~4h 15min total): 2× DSA (45min) + ML Practitioner (60min) + ML Systems Design (60min) + HM/Competency (45min)
- Environment: Google Meet + CoderPad (no compiler)

2026-04-30 VO Itinerary CONFIRMED:
- Day 1 (Tue 2026-05-05 PDT): 15:00-16:00 ML Systems Design (Yiyang Zhang); 16:00-16:45 HM/Competency (Daniel Liu, Manager II)
- Day 2 (Wed 2026-05-06 PDT): 13:00-13:45 Data/Algos (Jiankai Sun); 14:00-14:45 Data/Algos (Yijian Xiang); 15:00-16:00 ML Practitioner (Zihao Zhang)
- 15min breaks between Day-2 rounds
- Day 1 ordering insight: ML SD first (heaviest, fresh) → HM second (45min, lower-stakes warmup-to-cooldown)
- Day 2 ordering insight: 2× DSA back-to-back early (stamina for algorithmic precision while sharp), then ML Practitioner deep-dive at the end (after warmup, can talk fluently for 60min)
"""


def main() -> None:
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # ---- 1) Update companies row ----
    c.execute(
        "UPDATE companies SET interview_stages = ?, notes = ? WHERE id = ?",
        (json.dumps(NEW_STAGES, ensure_ascii=False), NEW_NOTES, COMPANY_PINTEREST),
    )
    print("companies row updated")

    # ---- 2) Read + edit doc 83 ----
    content = c.execute(
        "SELECT content FROM company_documents WHERE id = ?", (DOC_ID,)
    ).fetchone()[0]

    # 2a) Replace the top blockquote (3 lines) with concrete itinerary
    old_blockquote = (
        "> 5 场 virtual onsite，**no particular order**: 2× DSA (45 min) + 1× ML Practitioner (60 min) + 1× ML System Design (60 min) + 1× Competency/HM (45 min)。总 ~4h 10min。\n"
        "> 核心 framing: 你不是 model 调参员，是从 problem framing 一路 own 到 deployment 的工程师，每个决策都能讲清 *为什么* 和 *放弃了什么*。\n"
        "> 当前状态: HR prep call 2026-04-29 14:00 PT；onsite 日期 TBD this week。"
    )
    if old_blockquote not in content:
        raise SystemExit("ERROR: top blockquote pattern not found — abort")

    new_blockquote = (
        "> **Itinerary (CONFIRMED 2026-04-30)**: 5 rounds × 2 days, total ~4h 15min.\n"
        "> **Day 1 — Tue May 5, 2026 PDT**\n"
        "> - 15:00-16:00 (60min) **ML Systems Design** — Yiyang Zhang (Sr. MLE)\n"
        "> - 16:00-16:45 (45min) **HM/Competency** — Daniel Liu (Manager II, MLE)\n"
        ">\n"
        "> **Day 2 — Wed May 6, 2026 PDT**\n"
        "> - 13:00-13:45 (45min) **Data/Algos** — Jiankai Sun (Sr. MLE)\n"
        "> - *15-min break*\n"
        "> - 14:00-14:45 (45min) **Data/Algos** — Yijian Xiang (Sr. MLE)\n"
        "> - *15-min break*\n"
        "> - 15:00-16:00 (60min) **ML Practitioner** — Zihao Zhang (Sr. MLE)\n"
        ">\n"
        "> 核心 framing: 你不是 model 调参员，是从 problem framing 一路 own 到 deployment 的工程师，每个决策都能讲清 *为什么* 和 *放弃了什么*。\n"
        ">\n"
        "> **顺序解读**: Day 1 把最重的 ML SD 排第一 (体力满) → HM 第二 (45min 收尾，问完即下班)；Day 2 两场 DSA 早上压轴 (算法精度需要清醒) → ML Practitioner 最后 60min (热身够了能聊得开)。两天之间留一晚做 Day-2 题型 cool-down 复习, 别再开新 topic."
    )
    content = content.replace(old_blockquote, new_blockquote)

    # 2b) Append interviewer + duration + date to each §1-§4 header
    section_renames = [
        (
            "## §1 DSA × 2 (45 min × 2，1-2 题/场)",
            "## §1 DSA × 2 — Day 2 (May 6) 13:00 Jiankai Sun + 14:00 Yijian Xiang (45min × 2)",
        ),
        (
            "## §2 ML Practitioner (60 min)",
            "## §2 ML Practitioner — Day 2 (May 6) 15:00 Zihao Zhang (60min)",
        ),
        (
            "## §3 ML System Design (60 min)",
            "## §3 ML System Design — Day 1 (May 5) 15:00 Yiyang Zhang (60min)",
        ),
        (
            "## §4 Competency / HM (45 min)",
            "## §4 Competency / HM — Day 1 (May 5) 16:00 Daniel Liu, Manager II (45min)",
        ),
    ]
    for old_h, new_h in section_renames:
        if old_h not in content:
            raise SystemExit(f"ERROR: section header {old_h!r} not found")
        content = content.replace(old_h, new_h)

    # 2c) Replace the trailing prep-call action item with day-by-day stamina notes
    old_trailing = (
        "> **prep call (4/29 14:00 PT) 要确认的事**: (1) onsite 具体日期 (this week 哪两天) (2) 5 场顺序 (3) 是否有 take-home (4) 面试官是 ML team 哪个组 (5) HM 是谁。"
    )
    if old_trailing not in content:
        raise SystemExit("ERROR: trailing prep-call line not found")

    new_trailing = (
        "## §7 两天之间的 stamina playbook\n\n"
        "**5/4 (Mon) 前夜**:\n"
        "- ML SD: 把 Pixie / Two-Tower / HNSW / User Sequence Modeling 的 Pinterest 官方 4 篇资源各扫一遍 5 分钟; 准备 4 个高频 SD 题各一段 90 秒 high-level architecture 口述.\n"
        "- HM/Competency: 1 个 deep-dive 项目 (5-min + 15-min 双版本); 2 个 challenge 故事 (1 技术 + 1 协作), 每个都明确 \"学到什么\" 一句.\n\n"
        "**5/5 (Tue) Day 1 — ML SD 15:00 + HM 16:00**:\n"
        "- 14:30 进 Google Meet warm-up: 喝水, 调好 mic / 摄像头 / 屏幕共享.\n"
        "- ML SD 60 min: 永远先 gather requirement (5 题 clarify); Patrick Halina 的 framework 当骨架; 每个组件讲 pros/cons/trade-off; 最后留 5 分钟讲 monitoring + failure mode.\n"
        "- HM 45 min: deep-dive 项目时强调 *决策权* (\"我决定了 X 因为 Y, 团队最初想 Z\"); challenge 故事必须落到 \"现在我会怎么做\"; 提到 team 时区分 \"我\" 和 \"我们\".\n"
        "- 16:45 之后: 不复盘, 不刷题. 吃饭 + 散步 + 早睡.\n\n"
        "**5/6 (Wed) Day 2 — DSA 13:00 + DSA 14:00 + ML Practitioner 15:00**:\n"
        "- 12:00 起做 1 道中等 LeetCode (warm-up, 不查答案), 把手指打开.\n"
        "- DSA 第 1 场 (Jiankai Sun): 算法 flavor — graph / DP / two-pointer / interval. 先 clarify, 边讲边写, 写完自查 corner.\n"
        "- 13:45-14:00 break: 站起来走动, 喝水, 不复盘上一场.\n"
        "- DSA 第 2 场 (Yijian Xiang): systems-flavored — LRU / rate limiter / scheduler. 同样先 clarify, 不要 import sortedcontainers 跳过实现.\n"
        "- 14:45-15:00 break: 这 15 min 关键 — 切换 mode 从 \"写代码\" 到 \"讲 ML\". 大致回顾 deep-dive 项目的 4 评估维度 (framing / featurization / deployment / evaluation).\n"
        "- ML Practitioner 60 min (Zihao Zhang): 准备 1 个真实 deep-dive 项目, 4 维度逐一让面试官钻; offline metric ↔ business objective 对齐要讲清; cold-start / fallback / online A/B 都要主动提.\n\n"
        "## §8 离场前 60 秒 cheat sheet (5 场都适用)\n\n"
        "1. 我开口的第一句是 **clarification 还是 high-level**? (都不是 = 重置)\n"
        "2. 我有没有讲过至少 **2 个 tradeoff**?\n"
        "3. 我有没有用 Pinterest 的产品语境 (Pin / Homefeed / Search / Ads)?\n"
        "4. 我有没有在某处主动 **surface 失败模式或 limitation**?\n"
        "5. (Day 2 DSA 专属) 我有没有自查 corner 和 off-by-one?"
    )

    # The original §6 was the cheat-sheet; we'll fold it into §8 (renumbered).
    # First strip the old §6 header + content + trailing line, then append §7+§8.
    old_section_6_full = (
        "## §6 离场前 60 秒 cheat sheet\n\n"
        "1. 我开口的第一句是 **clarification 还是 high-level**? (都不是 = 重置)\n"
        "2. 我有没有讲过至少 **2 个 tradeoff**?\n"
        "3. 我有没有用 Pinterest 的产品语境 (Pin / Homefeed / Search / Ads)?\n"
        "4. 我有没有在某处主动 **surface 失败模式或 limitation**?\n\n"
        "---\n\n"
        + old_trailing
    )
    if old_section_6_full not in content:
        raise SystemExit("ERROR: §6 + trailing block not found")
    content = content.replace(old_section_6_full, new_trailing)

    # 2d) Recompute hash + timestamps + flip is_golden if needed
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    now = now_iso()
    c.execute(
        """
        UPDATE company_documents
        SET content = ?, content_hash = ?, updated_at = ?, golden_at = ?
        WHERE id = ?
        """,
        (content, content_hash, now, now, DOC_ID),
    )

    conn.commit()
    print(f"doc {DOC_ID} updated, new len={len(content)}, hash={content_hash}")

    # ---- 3) Verify ----
    row = c.execute(
        "SELECT id, name, status, applied_at, interview_stages, notes FROM companies WHERE id=?",
        (COMPANY_PINTEREST,),
    ).fetchone()
    print(f"\nPinterest row: id={row[0]} name={row[1]} status={row[2]}")
    stages = json.loads(row[4])
    print(f"  stages count = {len(stages)}")
    for s in stages:
        when = s.get("scheduled_at", "")
        print(f"    [{s['status']:9}] {s['name']}  {when}")
    conn.close()


if __name__ == "__main__":
    main()
