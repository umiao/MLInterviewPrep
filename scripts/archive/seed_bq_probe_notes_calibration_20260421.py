"""Seed BQ-DEPTH-09 probe_notes calibration samples (T-P1-580).

Writes 4 calibration probe_notes samples + marks 4 is_primary=1 links on fresh
(post-rewrite) stories, validating the schema + style guide BEFORE bulk C2.

Scope (user direction 2026-04-21, Discord gate):
  - EX-15 (Model Deprecation Incident)          --> primary Q: OWN-1
  - EX-16 (Cross-DC Deployment Incident)        --> primary Q: PS-6
  - EX-17 (Difficult Feedback from Senior IC)   --> primary Q: ADP-19
  - EX-30 (Hash Capability Misdesign)           --> primary Q: ADP-5

Rationale for primary assignment:
  - EX-15 -> OWN-1: dashboard blind-spot ownership is the textbook
    "take ownership of a failure" narrative; absorb-rollback-first sequence
    is the clean signal for this question stem.
  - EX-16 -> PS-6: calculated-risk stem fits cleanly ("took the rollout solo
    when formal PD quota was denied"); ADP-5 is more generic-mistake and
    already used by EX-30 for a cleaner 3-stage handling arc.
  - EX-17 -> ADP-19: "most challenging feedback" is the question the story
    was *written for*; the reliance-vs-trust frame pivot is exactly the
    L5 differentiator the stem probes.
  - EX-30 -> ADP-5: the story's existing relevance_note already maps to the
    3-stage handling arc (escalate -> propose wrong rescue -> accept
    reject); lesson is mental-model class (not tactical).

Schema (behavioral_questions.probe_notes JSON, 4 required fields):
  core_signal          : 1-2 sentence, 中文, L5 signal the stem probes
  what_good_looks_like : 3-5 bullets, 中文+英文术语, L4 bar answers
  what_L5_adds         : 2-3 bullets, L5 bar differentiators on top of L4
  common_failure_modes : 3-4 bullets, junior answer / redemption tail /
                         scapegoating / reviewer-deduction traps

Idempotent:
  - probe_notes: JSON-equality compare on parsed dict. If unchanged, SKIP.
    Otherwise, update + stamp probe_notes_updated_at=utcnow().
  - is_primary: per question, clear all existing is_primary=1 on links OTHER
    than the target, then set target link to is_primary=1. Compare before
    write; SKIP if already at desired state.
  - Re-run prints [SKIP] for every untouched row. 2nd invocation is a full
    no-op.

DB-backup-guarded:
  Before any write, copies the target DB file to
  <db>.bak.<timestamp>_pre_bq_depth_09_calib. Skip via --no-backup.

Usage:
    python scripts/seed_bq_probe_notes_calibration_20260421.py [--no-backup]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.backend.database import SessionLocal, get_engine, init_db  # noqa: E402
from src.backend.models.behavioral import (  # noqa: E402
    BehavioralExample,
    BehavioralQuestion,
    QuestionExampleLink,
)

# ---------------------------------------------------------------------------
# Calibration spec: 4 (question, example) primary pairs + probe_notes payload
# ---------------------------------------------------------------------------

CALIBRATION: list[dict] = [
    {
        "question_id": "OWN-1",
        "primary_example_id": "EX-15",
        "probe_notes": {
            "core_signal": (
                "这题本质在问: 能否在 failure 发生时做到 first-person 的 "
                "structural ownership, 而不是把 blame 分散到工具/团队/流程。"
                "L5 bar 是不止 own execution, 还能 own 自己 frame 里 embed "
                "的 blind spot (dashboard 抓不到什么 / instrumentation 缺口)。"
            ),
            "what_good_looks_like": [
                "明确 first-person attribution: 用 'I / my decision / my "
                "dashboard', 不用 'we / the team / the framework'。EX-15 "
                "primary 动作: 'my traffic dashboard missed hardcoded calls "
                "in the search engine'。",
                "Absorb downstream pain FIRST, 再 argue process: rollback "
                "先跑, 被 block 的 3-4 Query Understanding 团队先解套, 然后 "
                "才谈 structural fix。顺序 inverted 会 kill ownership signal。",
                "Concrete blast radius: 具体到 '3-4 pipelines / 1 week "
                "recovery / N teams blocked', 不是 abstract 'it caused "
                "issues'。量级感 = credibility。",
                "Correction loop 可 trace: 我如何发现 breakage (alert? user "
                "report?), 哪些是 recoverable 哪些 sunk, 哪些 counterpart "
                "我需要主动 credit-protect。",
            ],
            "what_L5_adds": [
                "把 failure locus 从 execution layer 抬到 structural framing "
                "layer: 不止承认 'dashboard miss 了 hardcoded calls', 而是 "
                "承认 'my mental model of the traffic surface was "
                "incomplete' -- 这是 design-time 的 gap, 不是 monitoring-"
                "time 的 gap。",
                "Org-level risk-if-not-addressed: 同 class failure 在 "
                "shared-infra governance 上会 reproduce (EX-15 的 "
                "ownership-transfer-as-third-path 就是 risk 的 structural "
                "fix, 不是单次 patch)。",
                "Credit 抑制: cost 和 accountability 全部留给自己, 不抢 "
                "counterpart 收拾残局的功劳, 这是 L5 区别于 L4 的 "
                "self-awareness 表现。",
            ],
            "common_failure_modes": [
                "Junior 答案: 'I should have written more tests / added "
                "more monitoring' -- 停在 tactical 层, 没有 frame-level "
                "reframe, reviewer 直接给 L4 以下。",
                "Redemption tail 太甜: 把 story 讲成 'I failed BUT then "
                "I saved the day and everyone thanked me' -- L5 bar 要的 "
                "是 clean failure 的勇气, 不是 comeback arc。",
                "Scapegoating via abstraction: '团队的 convention 是这样的 "
                "/ dashboard 没 surface 这个 / framework 就是这样设计的' "
                "-- 即使属实也会 kill ownership, 当场扣分。",
                "没有具体 blast radius: 只有 'it broke production' 没有 "
                "'3-4 teams, specific Query Understanding pipelines, "
                "1-week recovery' -- reviewer 会怀疑是编的或者规模太小。",
            ],
        },
    },
    {
        "question_id": "PS-6",
        "primary_example_id": "EX-16",
        "probe_notes": {
            "core_signal": (
                "这题本质在问: risk-taking 的成熟度 -- 能否 articulate "
                "为什么 risk 是 calculated (不是 reckless, 也不是 伪 risk), "
                "以及 outcome 混合时能否 cleanly 区分 delivery outcome 和 "
                "risk-handling outcome。L5 bar 是能承认 delivery 出问题 "
                "但 risk-handling 的 structural lesson 是 portable 的。"
            ),
            "what_good_looks_like": [
                "Ex-ante (不是 hindsight) 列清 'risk 是什么 / reward 是 "
                "什么 / mitigation 是什么': EX-16 primary 动作 = 'cross-DC "
                "rollout solo, formal PD quota denied, I accepted "
                "counterpart bandwidth gap as the main risk'。",
                "Decision-making criteria 具体: 为什么 accept 这个 risk "
                "(cost of delay > expected cost of partial failure, "
                "alternative 是无限期 block, etc.), 不是 'I just decided "
                "to go for it'。",
                "Outcome 不粉饰: 讲 partial failure (DC1 clean, DC2 broken) "
                "而不是把 story 讲成 clean win。Honest mixed-outcome 反而 "
                "加分。",
                "Mitigation 动作 ex-ante 就 design: staged rollout / "
                "monitoring / rollback plan, 不是 post-hoc 安慰自己说 "
                "'其实我也想过'。",
            ],
            "what_L5_adds": [
                "关键的 L5 动作: 把 'delivery outcome (混合)' 和 "
                "'risk-handling outcome (可 abstract 成原则)' 显式 separate。"
                "EX-16 的 'counterpart bandwidth as a planned line item' "
                "就是 risk class 级别的 lesson, 不是 'ask for help earlier' "
                "这种 tactical rule。",
                "Org-level aftershock: 这次 risk 之后我对同类 decision 的 "
                "default 变了 (e.g., 'I now refuse to take cross-team "
                "delivery without formally booked counterpart bandwidth, "
                "even if it means de-scoping')。Default-shift > lesson-"
                "statement。",
                "Risk 归属 internal: 即使 counterpart 没 deliver, 也把 "
                "risk 归因于 'my choice to proceed without booked "
                "bandwidth' 而不是 'their team 没给 quota'。",
            ],
            "common_failure_modes": [
                "Reckless 伪装成 calculated: 'I just trusted my instinct "
                "and went for it' -- 没有 ex-ante mitigation design, "
                "reviewer 听出是 gambling 不是 calculation。",
                "Risk-averse 伪装成 calculated: 讲一个其实没什么 downside "
                "的 '风险' (e.g., 'I took the risk of writing a design "
                "doc before getting approval') -- L5 bar 要的是 real "
                "stakes, 没 stakes 的 'risk' 直接 downgrade。",
                "Pure clean-win outcome: 让 risk 听起来像 safe bet, "
                "削弱 story 的 weight; 反而 mixed 或 partial-failure "
                "outcome 更能 demonstrate risk-handling maturity。",
                "Blame counterpart: 'if team X had given me bandwidth "
                "this wouldn't have happened' -- 把 risk ownership 推 "
                "给别人, 当场扣 deliver-results + ownership 双 signal。",
            ],
        },
    },
    {
        "question_id": "ADP-19",
        "primary_example_id": "EX-17",
        "probe_notes": {
            "core_signal": (
                "这题本质在问: 面对 tough feedback 的 default reflex -- 是 "
                "defensive unpack 还是 frame pivot。L5 bar 是能承认 "
                "feedback-giver 的 mental model 比自己的更准, 把 feedback "
                "抽象成 defaults-class growth area (一整类 behavior), "
                "而不是单次 patch。"
            ),
            "what_good_looks_like": [
                "具体 reproduce 当时 feedback 的 weight: EX-17 primary "
                "情境 = 'a senior IC refused to keep reviewing my code' "
                "-- 这种 action-level feedback (不是 words-only) 让 "
                "reviewer 相信 stakes 是真的。",
                "第一反应 honestly: 'I initially wanted to walk him "
                "through the technical context (researcher's late naming "
                "changes broke a verified PR)' -- 不假装 gracefully "
                "accepted, defensive 第一反应是人性, 承认它反而加分。",
                "Behavior change 有 specific 触发 action: 拒绝 manager "
                "提出的 explain-away offer / 自己主动 rebuild consistency, "
                "不是 generic 'I became more open to feedback'。",
                "时间轴清晰: feedback 时刻 -> 消化 window -> validation "
                "through consistency wins back trust, 没有 overnight "
                "redemption。",
            ],
            "what_L5_adds": [
                "Frame pivot 动作: 不是 'I adjusted my behavior', 而是 "
                "'I realized I had conflated being relied on with being "
                "trusted' -- EX-17 primary 的 'reliance vs trust' 区分 "
                "就是 mental-model-class 的 reframe, 不是 tactical patch。",
                "Defaults-class 抽象: feedback 不是 fix 一个 PR review, "
                "是 re-calibrate 我整个 '接受 manager-given framing 而 "
                "没 own deep context' 的 default。",
                "Cost acceptance 成熟: 承认 trust 需要时间 rebuild, "
                "没有 '第二天 he immediately started trusting me again' "
                "的廉价 redemption。",
            ],
            "common_failure_modes": [
                "Softball feedback: 挑一个其实不 challenging 的 "
                "feedback 讲 (e.g., 'my manager said I should "
                "communicate updates more often') -- reviewer 看穿后 "
                "直接 downgrade, 因为 'most challenging' 的 bar 被 "
                "自己降了。",
                "Defensive unpacking: '原因其实是 researcher 改了 name "
                "/ 原因是 CI 没 catch / 所以 feedback 其实 half-fair' "
                "-- 即使事实如此, reviewer 会 kill earn-trust + "
                "humility signal。",
                "Redemption tail 太快: '听完 feedback 我第二天就改了, "
                "他 immediately 开始 trust me' -- 不真实, L5 reviewer "
                "知道 trust rebuild 是 weeks-to-months 级。",
                "Agree-to-disagree framing: 'I respectfully disagreed "
                "but adjusted my communication style' -- 没有 real "
                "frame pivot, 停在 cosmetic 层, 丢 have-backbone 信号。",
            ],
        },
    },
    {
        "question_id": "ADP-5",
        "primary_example_id": "EX-30",
        "probe_notes": {
            "core_signal": (
                "这题本质在问: mistake / handling / lesson 三段能否 "
                "balanced 呈现, 且 lesson 是 mental-model 级的 default "
                "shift (不是 tactical patch)。L5 bar 是 lesson 能 transfer "
                "到未来 design decisions, 而不是 'I learned to be more "
                "careful'。"
            ),
            "what_good_looks_like": [
                "Clean failure 不加 rescue tail: EX-30 primary 的 'It "
                "was rejected. And this is where I stopped.' 就是 L5 "
                "的 clean-failure 动作 -- 承认 failure 就在这里结束, "
                "不编 comeback。",
                "Handling 部分 concrete 3 步: (1) escalation landed "
                "+ owned; (2) proposed wrong rescue (cross-4-team "
                "multi-quarter infra change); (3) rescue 被 reject 后 "
                "接受 reject, 不 re-litigate。",
                "Lesson 可操作 + portable: 'domain depth is not design "
                "authority. The authority belongs to whoever consumes "
                "the output.' -- 这是 design-time default shift, 不是 "
                "'I should have asked more questions'。",
                "First-person blame 一路到底: 不怪 PM 没告诉我, 不怪 "
                "indexing team 没来 review, 不怪 framework 没 surface -- "
                "blame 全程在 'my framing of hash as math object'。",
            ],
            "what_L5_adds": [
                "Mental-model shift 的高度: 'domain depth != design "
                "authority' 是 class-level 的 reframe, reviewer 可以直接 "
                "imagine 我在下个 design 里是怎么用的 (先问 'whose "
                "decision depends on this output')。",
                "Structural follow-on signal: 承认 orphan design 之后 "
                "leaked 成 experiment-level confounding, 说明 mistake "
                "的 blast radius 比最初理解的更大 -- 这是 L5 的 "
                "self-audit 动作。",
                "Cost-benefit 的 perspective pivot: 从 'individual "
                "视角 (保留我的 design)' 切换到 'org 视角 (cost 分散到 "
                "4 个团队)' 是 L5 specific 的 ownership 表达。",
            ],
            "common_failure_modes": [
                "Safe/trivial mistake: 'I typo-ed a config' / 'I "
                "forgot to merge a PR' -- reviewer 看穿是在避重就轻, "
                "直接 downgrade。Bar 是 real stakes。",
                "Rescue tail 重点失衡: 'mistake 之后我加班三天全部 "
                "recovery 回来, 最后 launch on time' -- lesson 被 "
                "rescue 淹没, L5 reviewer 想看的是 clean failure + "
                "abstract lesson, 不是 redemption arc。",
                "Lesson 太 generic: 'I learned to communicate more' "
                "/ 'I learned to ask for help' -- 没 default-shift, "
                "reviewer 无法 imagine 我下次怎么不同。",
                "Scapegoating via abstraction: 'the framework didn't "
                "surface this' / 'PM didn't tell me' -- 把 blame 甩 "
                "给 tool / counterpart 而不是 own frame, 当场扣 "
                "ownership。",
            ],
        },
    },
]


# ---------------------------------------------------------------------------
# DB-file backup
# ---------------------------------------------------------------------------


def _backup_db(db_path: Path) -> Path | None:
    """Copy the DB file to a timestamped .bak before mutating.

    Args:
        db_path: Absolute path to the SQLite DB file.

    Returns:
        Path to the backup file, or None if the source does not exist.
    """
    if not db_path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(f"{db_path.name}.bak.{ts}_pre_bq_depth_09_calib")
    shutil.copy2(db_path, backup)
    return backup


def _resolve_db_file() -> Path | None:
    """Return the SQLite DB file path bound to the engine, or None."""
    engine = get_engine()
    url = engine.url
    if url.drivername != "sqlite":
        return None
    if url.database in (None, "", ":memory:"):
        return None
    return Path(url.database).resolve()


# ---------------------------------------------------------------------------
# Idempotent writers
# ---------------------------------------------------------------------------


def _upsert_probe_notes(
    db,
    question: BehavioralQuestion,
    target: dict,
    now: datetime,
) -> bool:
    """Upsert probe_notes JSON by dict-equality compare.

    Args:
        db: SQLAlchemy session.
        question: BehavioralQuestion row.
        target: Desired probe_notes dict (4 required fields).
        now: Timestamp to stamp on update.

    Returns:
        True if a write happened, False if SKIP (already at target).
    """
    existing = question.probe_notes_dict
    if existing == target:
        return False
    question.probe_notes_dict = target
    question.probe_notes_updated_at = now
    return True


def _upsert_primary_link(
    db,
    question: BehavioralQuestion,
    target_example: BehavioralExample,
) -> str:
    """Ensure target link has is_primary=1 + all other links for this
    question have is_primary=0.

    Args:
        db: SQLAlchemy session.
        question: BehavioralQuestion row.
        target_example: BehavioralExample row expected to be primary.

    Returns:
        Status string: 'SET', 'SKIP', or raises if target link does not exist.
    """
    target_link = (
        db.query(QuestionExampleLink)
        .filter(
            QuestionExampleLink.question_id == question.id,
            QuestionExampleLink.example_id == target_example.id,
        )
        .first()
    )
    if target_link is None:
        raise RuntimeError(
            f"No question_example_links row for "
            f"(question={question.question_id}, example={target_example.example_id}). "
            f"Cannot set is_primary. Seed the link first."
        )

    current_primaries = (
        db.query(QuestionExampleLink)
        .filter(
            QuestionExampleLink.question_id == question.id,
            QuestionExampleLink.is_primary == True,  # noqa: E712
        )
        .all()
    )
    # Target state: exactly [target_link.id]
    current_ids = sorted(link.id for link in current_primaries)
    if current_ids == [target_link.id]:
        return "SKIP"

    # Clear any other primary on this question, then set target.
    for link in current_primaries:
        if link.id != target_link.id:
            link.is_primary = False
    target_link.is_primary = True
    return "SET"


# ---------------------------------------------------------------------------
# Main seed routine
# ---------------------------------------------------------------------------


def seed() -> dict:
    """Apply the 4 calibration samples. Returns counter dict for verification.

    Returns:
        Dict with counts probe_notes_updated / probe_notes_skipped /
        primaries_set / primaries_skipped, plus final audit counts.
    """
    engine = get_engine()
    init_db(engine)

    db = SessionLocal()
    try:
        counters = {
            "probe_notes_updated": 0,
            "probe_notes_skipped": 0,
            "primaries_set": 0,
            "primaries_skipped": 0,
        }
        now = datetime.utcnow()

        for spec in CALIBRATION:
            q_id = spec["question_id"]
            ex_id = spec["primary_example_id"]
            question = (
                db.query(BehavioralQuestion)
                .filter(BehavioralQuestion.question_id == q_id)
                .first()
            )
            if question is None:
                raise RuntimeError(f"BehavioralQuestion {q_id!r} missing.")
            example = (
                db.query(BehavioralExample)
                .filter(BehavioralExample.example_id == ex_id)
                .first()
            )
            if example is None:
                raise RuntimeError(f"BehavioralExample {ex_id!r} missing.")

            # probe_notes upsert
            wrote = _upsert_probe_notes(db, question, spec["probe_notes"], now)
            if wrote:
                print(f"[DONE] probe_notes written for {q_id}")
                counters["probe_notes_updated"] += 1
            else:
                print(f"[SKIP] probe_notes unchanged for {q_id}")
                counters["probe_notes_skipped"] += 1

            # is_primary upsert
            status = _upsert_primary_link(db, question, example)
            if status == "SET":
                print(f"[DONE] is_primary=1 set on ({q_id}, {ex_id})")
                counters["primaries_set"] += 1
            else:
                print(f"[SKIP] is_primary already correct on ({q_id}, {ex_id})")
                counters["primaries_skipped"] += 1

        db.commit()

        # Audit: all 4 questions have probe_notes set + exactly 1 primary each
        audit_probe = 0
        audit_primary = 0
        for spec in CALIBRATION:
            q = (
                db.query(BehavioralQuestion)
                .filter(BehavioralQuestion.question_id == spec["question_id"])
                .first()
            )
            if q.probe_notes and q.probe_notes_dict == spec["probe_notes"]:
                audit_probe += 1
            primary_count = (
                db.query(QuestionExampleLink)
                .filter(
                    QuestionExampleLink.question_id == q.id,
                    QuestionExampleLink.is_primary == True,  # noqa: E712
                )
                .count()
            )
            if primary_count == 1:
                audit_primary += 1

        counters["audit_probe_ok"] = audit_probe
        counters["audit_primary_ok"] = audit_primary
        return counters
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip pre-seed DB-file backup",
    )
    args = parser.parse_args(argv)

    if not args.no_backup:
        db_file = _resolve_db_file()
        if db_file is not None:
            bkp = _backup_db(db_file)
            if bkp is not None:
                print(f"[BACKUP] {bkp.name}")
        else:
            print("[BACKUP] skipped -- non-file DB URL")

    report = seed()

    print()
    print("=" * 60)
    print("BQ-DEPTH-09 probe_notes calibration seed report")
    print("=" * 60)
    print(f"probe_notes updated this run : {report['probe_notes_updated']}")
    print(f"probe_notes skipped (no diff): {report['probe_notes_skipped']}")
    print(f"is_primary set this run      : {report['primaries_set']}")
    print(f"is_primary skipped (in state): {report['primaries_skipped']}")
    print(f"Audit: probe_notes == target : {report['audit_probe_ok']}/4")
    print(f"Audit: exactly 1 primary per Q: {report['audit_primary_ok']}/4")

    ok = report["audit_probe_ok"] == 4 and report["audit_primary_ok"] == 4
    if ok:
        print("[OK] All 4 probe_notes + primary flags at target state.")
        return 0
    print("[FAIL] Audit failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
