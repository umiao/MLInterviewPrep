"""Extend T-P1-358 to seed cn_elevator_pitch for all 7 master stories
(the original 5 failure-cluster + new EX-34 BBE + new EX-09B privacy).

Updates the description in tasks.db so the autonomous session populates pitches
for all 7 examples in one go, instead of leaving EX-34 and EX-09B for later.
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / ".claude" / "tasks.db"

NEW_DESC = """Add behavioral_examples.cn_elevator_pitch column + populate for the 7 polished master stories: EX-15, EX-16, EX-17, EX-30, EX-33B (the failure cluster) + EX-34 (BBE seller-vs-listing risk policy disagreement) + EX-09B (conversational-search privacy proxy item).

EXECUTION STEPS:

1. Schema migration: append a new tuple to MIGRATIONS in src/backend/database.py with version=16:
   (16, 'Add cn_elevator_pitch column to behavioral_examples', [
       'ADD_COLUMN_IF_MISSING:behavioral_examples:cn_elevator_pitch:'
       'ALTER TABLE behavioral_examples ADD COLUMN cn_elevator_pitch TEXT',
   ])
   (Use ADD_COLUMN_IF_MISSING prefix per the existing pattern at lines 134/145; do NOT skip the prefix.)

2. SQLAlchemy model: src/backend/models/behavioral.py BehavioralExample class — add:
   cn_elevator_pitch = Column(Text, nullable=True)

3. Pydantic schema: src/backend/schemas/behavioral.py BehavioralExampleResponse + BehavioralExampleCreate — add cn_elevator_pitch: str | None = None.

4. Frontend type: src/frontend/src/types/behavioral.ts BehavioralExample interface — add cn_elevator_pitch?: string | null.

5. Seed all 7 master stories via a new idempotent script scripts/seed_master_pitches.py. Embed the EXACT strings below — do NOT regenerate, do NOT translate, do NOT abbreviate. Each entry is one Chinese sentence, then ' | KEY FACTS: ' followed by 3-5 pipe-separated cue phrases (these get displayed as bullet pills on the example card).

EX-15: "按流程下线旧模型却触发未文档化的跨团队依赖；以事故为契机推动跨团队对齐机制与分阶段下线 safety knob | KEY FACTS: 1 周修复 | VP/Senior Director 跨组会议 | 跨团队对齐机制成为新规范 | 分阶段 deprecation safety knob"

EX-16: "主动跨边界做延迟优化但未对齐 infra 团队；C++ 静态编译\\"部落知识\\"导致跨数据中心上线 panic，确立强制 cross-team reviewer 策略 | KEY FACTS: 跨 DC error rate spike | 紧急 rollback | 强制 cross-team reviewer 策略 | 后续被邀请加入 declarative artifactory 倡议（注：此 tail 仅用于 calculated-risk 框架，不在 failure 框架中提及）"

EX-17: "收到 senior IC 严厉反馈\\"缺乏基本工程素养\\"；不 push back 而内化根因——压力下未阻挡 manager shortcut——重建信誉与 gate-keeping 责任 | KEY FACTS: senior IC 严厉反馈 | 'lacked basic engineering quality' | over-promise 根因 | 后续 gate-keeping 责任"

EX-30: "高速 PM 合作期上线\\"数学优雅\\"hash 未询问下游 consumer；致 2-3 个下游 DS 团队数周分析时间损失；跨团队 rescue 提案被拒，最终采纳 indexing 团队 prior art | KEY FACTS: 2-3 个下游 DS/产品团队 | 数周分析时间损失 | 跨四团队 rescue 提案被拒 | 回归 indexing 团队 prior art"

EX-33B: "作为 model believer 在 MoE 上层层迭代——修 bias、修 router、加正交 expert；耗尽 ~80 GPU 后认清 BI/GMB 是真 KPI，MRR 是 self-fulfilling proxy | KEY FACTS: ~80 GPU 节点 | BI + GMB 真 KPI | MRR 不是 KPI | 技术 unblocked 但 business unlaunchable"

EX-34: "在 BBE 项目和 principal researcher disagree on seller-level 绝对风险 policy；用新卖家/小卖家 false-positive 数据 + '绝对标准是 lazy non-action 伪装'重新框定问题；落地 listing-level + cumulative seller escalation 两层机制，并把对方真实顾虑（audit 一致性）变成机制保障 | KEY FACTS: BBE 风险 enforcement 粒度 | seller-level absolutism vs listing-level | 新卖家/小卖家 false-positive 数据 | listing-level + 累积升级 | absolutism smell test"

EX-09B: "在 LLM 对话搜索 design 阶段提出 query rewrite 路径会让用户原始 query 流入下游 log/训练数据的 privacy 风险；与 team 共同 develop proxy item 生成路径，让原始 query 永不流入下游，并把 privacy 优势写入 design doc | KEY FACTS: query rewrite 是基于 query clustering/autocomplete 的自然延伸 | proxy item 完全消除 leakage（eliminate not mitigate） | privacy benefit 写入 design doc | 与 EX-09 是同 project 两个独立 cut"

Script structure: connect to data/mle_prep.db, for each (example_id, pitch): UPDATE behavioral_examples SET cn_elevator_pitch=? WHERE example_id=?. Re-runnable. Use encoding='utf-8' for the script file.

6. Verification commands (run all):
   - python -c "import sqlite3; c=sqlite3.connect('data/mle_prep.db').cursor(); c.execute(\\"SELECT example_id, substr(cn_elevator_pitch,1,40) FROM behavioral_examples WHERE example_id IN ('EX-15','EX-16','EX-17','EX-30','EX-33B','EX-34','EX-09B') ORDER BY example_id\\"); [print(r) for r in c.fetchall()]"
   - Verify all 7 rows show non-null pitches matching the EXACT strings above.
   - Restart uvicorn on port 8100 (if running). Use scripts/run_server.py if it exists, else: pkill the current process and re-launch with the same command.
   - curl -s http://localhost:8100/api/behavioral/examples/by-example-id/EX-34 | python -c 'import json,sys; d=json.load(sys.stdin); print("cn_elevator_pitch:", d.get("cn_elevator_pitch"))'
   - The cn_elevator_pitch field MUST be present and non-null for all 7.

ACCEPTANCE:
- Migration version 16 in MIGRATIONS list, schema_versions table contains row (16, ...).
- Column exists in behavioral_examples (PRAGMA table_info).
- All 7 master stories have non-null cn_elevator_pitch with the EXACT seed strings above (no abbreviation, no rewording, no translation).
- API response from /api/behavioral/examples/by-example-id/EX-34 contains cn_elevator_pitch key.
- types/behavioral.ts updated and frontend type-checks (cd src/frontend && npm run build clean).
- Commit message: '[T-P1-358] Behavioral: cn_elevator_pitch column + seed 7 master pitches'.
"""


def main() -> None:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()
    c.execute("UPDATE tasks SET description=?, updated_at=CURRENT_TIMESTAMP WHERE id='T-P1-358'", (NEW_DESC,))
    print(f"rowcount: {c.rowcount}")
    conn.commit()
    c.execute("SELECT length(description) FROM tasks WHERE id='T-P1-358'")
    print(f"new desc len: {c.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    main()
