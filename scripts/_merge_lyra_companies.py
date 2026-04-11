"""One-off: merge Lyra sub-company rows into a single 'Lyra' company.

Before: four companies (25 'Lyra', 26 'Lyra - Therapist Ordinary Sessions',
27 'Lyra - FMLA Meeting with MD - Check In Required',
28 'Lyra - Therapist Ordinary Sessions - Mention the updates about my back,
双相的症状，公司的pinging'). The prep reminders were abused into company names.

After: single company id=25 'Lyra', with a Chinese pre-session prep banner in
companies.prep_notes (markdown with checkboxes -> renders as red dot on
timeline when items are unchecked). Events that referenced 26/27/28 are
re-pointed to 25. The old meta-company rows are deleted.

Pre-session reminders for individual events are preserved in their descriptions.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

LYRA_PREP_BANNER = """\
## Lyra Session 准备提醒 (中文 Banner)

> Lyra 是心理健康服务商 (Lyra Health)，不是求职目标。保持 company_name 简洁，
> 每次 session 前用下面的 checklist 做准备；完成后勾掉，未完成的项会在时间线上
> 显示红点提醒。

### 每次 session 前必做
- [ ] 整理本周心理状态：睡眠质量、情绪波动、能量水平
- [ ] 记录新的压力源（工作 pinging、面试压力、身体状况变化）
- [ ] 提前 10 分钟登录 session 链接，确认音视频正常

### 向 Therapist (Jacqueline) 必提事项
- [ ] **身体**：背部最新情况（疼痛位置、持续时间、理疗/拉伸进展）
- [ ] **情绪**：双相症状波动（躁狂 / 抑郁 episode、触发因素、持续时间）
- [ ] **工作**：公司 pinging + 面试季对情绪和睡眠的影响
- [ ] 上次 session 的 homework / 建议是否执行，效果如何
- [ ] 用药情况（剂量、副作用、漏服）

### FMLA / MD Check-in (Mary Miller) 专用
- [ ] 给 MD 更新最近的症状、睡眠、用药反应
- [ ] 确认 FMLA 文件是否需要续签或补充材料
- [ ] 问清下一次 check-in 的时间窗口
- [ ] 记录任何需要开具的工作调整建议

### Session 后
- [ ] 立即记录三件事：今天讨论了什么 / 有哪些 action item / 下次要跟进什么
- [ ] 如有药物调整，更新服药提醒
"""

EVENT_11_DESC = (
    "Follow-up visit with therapist Jacqueline.\n"
    "Pre-session reminders: (1) mention back updates, (2) 双相 (bipolar) 症状波动, "
    "(3) 公司 pinging 带来的压力影响。See Lyra company prep notes for full checklist."
)

EVENT_12_DESC = (
    "MD video session with Mary Miller for FMLA check-in. "
    "Bring the updated symptom log and medication list; confirm FMLA paperwork status. "
    "See Lyra company prep notes (FMLA section) for full checklist."
)


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        conn.execute("BEGIN")

        # 1. Write the Chinese prep banner to the canonical Lyra row (id=25).
        cur.execute(
            "UPDATE companies SET prep_notes = ? WHERE id = 25",
            (LYRA_PREP_BANNER,),
        )
        assert cur.rowcount == 1, f"expected 1 row updated for company 25, got {cur.rowcount}"

        # 2. Re-point events 11/12 to canonical Lyra id=25.
        cur.execute(
            "UPDATE interview_events SET company_id = 25, company_name = 'Lyra', "
            "description = ? WHERE id = 11",
            (EVENT_11_DESC,),
        )
        assert cur.rowcount == 1, f"event 11 update rowcount={cur.rowcount}"

        cur.execute(
            "UPDATE interview_events SET company_id = 25, company_name = 'Lyra', "
            "description = ? WHERE id = 12",
            (EVENT_12_DESC,),
        )
        assert cur.rowcount == 1, f"event 12 update rowcount={cur.rowcount}"

        # 3. Re-point any other events still referencing 26/27/28 (defense).
        cur.execute(
            "UPDATE interview_events SET company_id = 25, company_name = 'Lyra' "
            "WHERE company_id IN (26, 27, 28)"
        )

        # 4. Delete the redundant company rows.
        cur.execute("DELETE FROM companies WHERE id IN (26, 27, 28)")
        assert cur.rowcount == 3, f"expected 3 companies deleted, got {cur.rowcount}"

        conn.commit()
        print("[OK] Lyra companies merged. Canonical id=25.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
