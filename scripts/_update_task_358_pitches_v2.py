"""Update T-P1-358 task description with the v2 (规范化) Chinese elevator pitches.

User feedback: v1 pitches were 'slightly flippant' (略显轻挑); v2 drops colloquial
words (头铁/烧掉/炸出/傲慢/没找/当面说) while preserving all facts and the cuing
function. The full task description is rewritten to embed v2 verbatim so the
autonomous session has the exact strings to insert (no inventing).
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / ".claude" / "tasks.db"

NEW_DESC = """Add behavioral_examples.cn_elevator_pitch column + populate for the 5 failure-cluster master stories (EX-15, EX-16, EX-17, EX-30, EX-33B).

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

5. Seed the 5 master stories via a new idempotent script scripts/seed_failure_cluster_pitches.py. Embed the EXACT strings below — do NOT regenerate, do NOT translate, do NOT abbreviate. Each entry is one Chinese sentence ending with a 'KEY FACTS:' suffix that lists 3-5 pipe-separated cue phrases (these get displayed as bullet pills on the example card).

EX-15: "按流程下线旧模型却触发未文档化的跨团队依赖；以事故为契机推动跨团队对齐机制与分阶段下线 safety knob | KEY FACTS: 1 周修复 | VP/Senior Director 跨组会议 | 跨团队对齐机制成为新规范 | 分阶段 deprecation safety knob"

EX-16: "主动跨边界做延迟优化但未对齐 infra 团队；C++ 静态编译\\"部落知识\\"导致跨数据中心上线 panic，确立强制 cross-team reviewer 策略 | KEY FACTS: 跨 DC error rate spike | 紧急 rollback | 强制 cross-team reviewer 策略 | 后续被邀请加入 declarative artifactory 倡议（注：此 tail 仅用于 calculated-risk 框架，不在 failure 框架中提及）"

EX-17: "收到 senior IC 严厉反馈\\"缺乏基本工程素养\\"；不 push back 而内化根因——压力下未阻挡 manager shortcut——重建信誉与 gate-keeping 责任 | KEY FACTS: senior IC 严厉反馈 | 'lacked basic engineering quality' | over-promise 根因 | 后续 gate-keeping 责任"

EX-30: "高速 PM 合作期上线\\"数学优雅\\"hash 未询问下游 consumer；致 2-3 个下游 DS 团队数周分析时间损失；跨团队 rescue 提案被拒，最终采纳 indexing 团队 prior art | KEY FACTS: 2-3 个下游 DS/产品团队 | 数周分析时间损失 | 跨四团队 rescue 提案被拒 | 回归 indexing 团队 prior art"

EX-33B: "作为 model believer 在 MoE 上层层迭代——修 bias、修 router、加正交 expert；耗尽 ~80 GPU 后认清 BI/GMB 是真 KPI，MRR 是 self-fulfilling proxy | KEY FACTS: ~80 GPU 节点 | BI + GMB 真 KPI | MRR 不是 KPI | 技术 unblocked 但 business unlaunchable"

Script structure: connect to data/mle_prep.db, for each (example_id, pitch): UPDATE behavioral_examples SET cn_elevator_pitch=? WHERE example_id=?. Re-runnable. Use encoding='utf-8' for the script file.

6. Verification commands (run all):
   - python -c "import sqlite3; c=sqlite3.connect('data/mle_prep.db').cursor(); c.execute(\\"SELECT example_id, cn_elevator_pitch FROM behavioral_examples WHERE example_id IN ('EX-15','EX-16','EX-17','EX-30','EX-33B') ORDER BY example_id\\"); [print(r) for r in c.fetchall()]"
   - Verify all 5 rows show non-null pitches matching the EXACT strings above.
   - Restart uvicorn on port 8100 (if running). Use scripts/run_server.py if it exists, else: pkill the current process and re-launch with the same command.
   - curl -s http://localhost:8100/api/behavioral/examples/by-example-id/EX-33B | python -c 'import json,sys; d=json.load(sys.stdin); print("cn_elevator_pitch:", d.get("cn_elevator_pitch"))'
   - The cn_elevator_pitch field MUST be present and non-null for all 5.

ACCEPTANCE:
- Migration version 16 in MIGRATIONS list, schema_versions table contains row (16, ...).
- Column exists in behavioral_examples (PRAGMA table_info).
- All 5 master stories have non-null cn_elevator_pitch with the EXACT seed strings above (no abbreviation, no rewording).
- API response from /api/behavioral/examples/by-example-id/EX-33B contains cn_elevator_pitch key.
- types/behavioral.ts updated and frontend type-checks (cd src/frontend && npm run build clean).
- Commit message: '[T-P1-358] Behavioral: cn_elevator_pitch column + seed 5 failure-cluster pitches'.
"""


def main() -> None:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET description=?, updated_at=CURRENT_TIMESTAMP WHERE id='T-P1-358'",
        (NEW_DESC,),
    )
    print(f"rowcount: {c.rowcount}")
    conn.commit()
    c.execute("SELECT length(description) FROM tasks WHERE id='T-P1-358'")
    print(f"new desc len: {c.fetchone()[0]}")
    # spot-check that all 5 v2 pitches are present
    c.execute("SELECT description FROM tasks WHERE id='T-P1-358'")
    desc = c.fetchone()[0]
    for marker in ["按流程下线旧模型", "主动跨边界做延迟优化", "收到 senior IC 严厉反馈",
                   "高速 PM 合作期上线", "model believer 在 MoE 上层层迭代"]:
        present = marker in desc
        print(f"  {marker[:30]:30s} -> {'OK' if present else 'MISSING'}")
    conn.close()


if __name__ == "__main__":
    main()
