"""Idempotent seed: EX-12B (team-cut of the notebook -> ML platform migration).

Discord approval: msg 1496968113470701568 (2026-04-23 "我觉得挺好的 可以执行").
Draft + link plan approved in: logs/ex12b_draft_v1_20260423.md.

Follows story_rewrite_protocol.md — EX-09/EX-09B dual-cut pattern:
EX-12 keeps intern-coaching / LDR framing; EX-12B = team-wide migration +
platform influence + template+profile abstraction framing. The two cuts
must not be combined in a single answer (USAGE RULE enforced in
risk_statement).

This script:
  1. Backs up the DB to data/mle_prep.db.bak.<timestamp>_pre_ex12b_insert
  2. INSERT (or UPDATE if already present) behavioral_examples row for EX-12B
  3. DELETE EX-12 links for INN-5 / INN-13 / INN-14 (migrated to EX-12B)
  4. INSERT 16 new EX-12B question_example_links (INSERT/UPDATE relevance_note)

Idempotent: second run = all `[SYNC]` / `[SKIP]`, zero deletes/inserts.

Run: python scripts/seed_ex12b_team_cut_migration.py
"""
from __future__ import annotations

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

EXAMPLE_ID = "EX-12B"
TITLE = (
    "Notebook -> ML Platform Migration --- Team Utilization 5% to 40% "
    "via Template+Profile Abstraction (Team-Cut of EX-12)"
)
SOURCE_PROJECT = "Research-team ML infra migration (team-cut, same project as EX-12)"

CN_ELEVATOR_PITCH = (
    "研究团队 notebook fleet 几百 GB memory reserved 但 utilization < 5%；几个 legacy "
    "R boosting 模型 (gbm 类) 无 refresh 通路、scale 不到 serving。先把 <5% 的 profile "
    "数据摆在 leadership 和 RS 面前把\"浪费\"变成事实，再从 researcher 痛点起手做 "
    "RS↔Infra 双向翻译，把 HDFS/Spark/LnP/debug tooling 需求推进 platform roadmap；"
    "然后 push platform 越过 k8s + ephemeral pod 到 persistent dev + reusable pipeline "
    "component；最后在 runtime 上搭 template + profile abstraction 让新人 fork-and-go。"
    "团队 utilization 5%→40%，legacy 模型回到 refresh 节奏，平台能力成为 ML platform "
    "default；\"DS 能不能 ship production\" 从 skill gap 被 reframe 成 tooling gap "
    "| KEY FACTS: utilization 5% → 40% (SRE 监控) | 几百 GB memory / <5% CPU+GPU "
    "| RS↔Infra 双向翻译 | template + profile abstraction | legacy R (gbm 类) → "
    "production refreshable | platform capability 后来成为 org default"
)

SITUATION = (
    "Research team 靠常驻 Jupyter notebook 做 model 开发和 inference pipeline。"
    "整个 notebook fleet 几百 GB memory + 大量 CPU footprint 常年 reserved，实际 "
    "utilization < 5%。几个 legacy 模型还在本地用 R native boosting 包 (gbm 类) 训练 "
    "— 没 refresh 通路，也 scale 不到 serving traffic。组里有个公开的开放问题："
    "researcher / DS 到底能不能 ship 可部署的 production-grade 系统。"
)

TASK = (
    "把 team 从 ad-hoc notebook 环境迁到成熟的 ML platform，不能牺牲 research "
    "velocity；同时正面回应那句\"DS can't ship production\"的 skepticism。我不是 "
    "platform owner — 得靠 RS ↔ Infra 两边的双向翻译，加上把 researcher 的真实需求 "
    "推进 platform roadmap，才能让这次迁移真的落地。"
)

ACTION = (
    "Early call: 把\"浪费\"变成不可辩驳的事实。我 profile 了整个 notebook fleet 的真实 "
    "utilization — <5% 的 CPU/GPU 数字 + idle memory reservation 一起摆在 leadership "
    "和 RS 面前。模糊的\"感觉在浪费\"变成硬数据。\n\n"
    "然后我不从 migration mandate 起手，从 researcher 的痛点起手：kernel 动不动挂、"
    "legacy R 模型没 refresh 通路、没有 scale 到 serving 的路径。聊下来发现他们其实很 "
    "愿意合作 — 只要替代方案真的 viable。\n\n"
    "我把自己放在 RS 和 Infra 之间做双向翻译。Researcher 的真实 workflow requirement "
    "我带进 platform roadmap：HDFS、Spark、internal search engine LnP、debug/scrape "
    "tooling 兼容性，一条都不能丢 — 否则 researcher 离开 notebook 就是**直接降能**，"
    "那这事没人会签。\n\n"
    "然后我 push platform 越过早期的 \"Kubernetes + ephemeral Docker pod\" scope。我的 "
    "论点是：要让 RS 既能做 research 又能直接 ship production component，platform 必须 "
    "支持 persistent dev 环境、reusable pipeline component、和 first-class 的数据源 "
    "接入。\n\n"
    "最后一层，**codify**：在 runtime 之上搭了一层 template repo + abstraction 配 "
    "agreed-upon interface。Researcher 只要用 profile-like config 描述自己训练 / 探索 "
    "行为，底下全自动。新人 fork-and-go，团队的 iteration velocity 和 production "
    "solidity 同时抬起来。"
)

RESULT = (
    "团队 CPU/GPU utilization 从 <5% 抬到 ~40%（SRE 资源监控测量），释放出的 capacity "
    "被其他 workload 接走。40% 其实是我们 workload shape 的现实天花板 — 每轮 process "
    "几百 GB 数据，I/O + memory 要按 peak read 阶段配，data loading 期间 CPU 必然 idle；"
    "在 load / train 阶段动态 re-allocation 落地之前 40% 已经到位，team 非常满意。\n\n"
    "迁移顺带解锁了一批 notebook 时代拿不到的底层能力：自动 model versioning、core "
    "metric + 历史 weight 一键对比、实时 CPU/GPU 诊断便于 failure mitigation。更关键的 "
    "是，它把\"DS 能不能 ship production\"从组内辩论 reframe 成了事实问题 — researcher "
    "在直接交付可复用、可调度、可 auto-refresh 的 pipeline component。原来的 skepticism "
    "被证伪成 **tooling gap，不是 skill gap**。我推动的几项 platform capability 后来成 "
    "了 ML platform 的 default，铺好了其他 team 同类迁移的路。\n\n"
    "The deepest lesson for me: **researcher onboarding is a platform-design problem, "
    "not a training problem.** 想让研究团队 ship production，不是教他们怎么用 "
    "production stack — 是把 production stack 长成他们本来就想要的样子。"
)

PRINCIPLE_TAGS = json.dumps([
    "influence_without_authority",
    "build_mechanism",
    "cross_functional_translator",
    "platform_thinking",
    "evidence_based_advocacy",
    "template_as_artifact",
    "deliver_results",
    "research_to_production_bridge",
])

RISK_STATEMENT = (
    "This story is the TEAM-CUT of the same underlying project that EX-12 covers "
    "as an intern-coaching / LDR example. The two cuts must NEVER be combined in "
    "a single answer — combining the team-wide migration framing with the "
    "intern-coaching tail dilutes both (the migration story gets buried under "
    "\"I mentored N interns\", and the intern-coaching story loses its personal "
    "coaching intimacy).\n\n"
    "USAGE RULE: For innovation / process-improvement / cross-functional / "
    "long-term-impact questions (INN / IMP / COL / OWN-10 / COM-2), use EX-12B "
    "and stop the story at \"platform capabilities became defaults\". Do NOT "
    "bring in intern-specific coaching beats — those belong to EX-12. For "
    "leadership / mentoring / struggling-team-member / empowerment / delegation "
    "questions (LDR-1/2/5/6/10/11), use EX-12 and do NOT bring in the team-wide "
    "utilization numbers — the personal coaching arc is the point.\n\n"
    "NARRATION-RISK GUARD: My leverage here was influence, not authority — I was "
    "not the ML platform owner. If researchers had rejected the new stack "
    "(notebook had real capabilities they would lose otherwise), the migration "
    "would have been a ghost town and the \"DS can't ship production\" line would "
    "have hardened. The bet was that translating researcher pain into platform "
    "requirements was more durable than pushing a mandate. Frame as \"I drove the "
    "migration by bridging RS and Infra\", not \"I migrated the team\" — the "
    "team, platform owners, and researchers shipped together; my contribution "
    "was translation + template codification."
)

ANALOGY = (
    "像给一片满是零星 campfire 的荒地装公共供暖 — 你不能直接把所有 campfire 熄了叫 "
    "大家搬进屋，得先保证屋里比 campfire 更暖、厨具更齐、离水源更近。Researcher "
    "离开 notebook 不能是降能，只能是升能。"
)

TECH_TERMS = json.dumps({
    "Jupyter notebook fleet": "long-running interactive dev instances; memory-heavy, low-utilization when idle",
    "ML platform": "mature internal platform with scheduled pipelines, model versioning, resource-aware runtime",
    "HDFS / Spark": "distributed storage and compute backbones the research team depended on",
    "LnP (Learn & Predict)": "internal search engine that several legacy pipelines called directly",
    "Kubernetes + ephemeral Docker pod": "early platform scope; insufficient for research-style persistent dev",
    "persistent dev environment": "long-lived containerized workspace with researcher-side caches and mounted state",
    "reusable pipeline component": "first-class shareable unit of production workflow (feature gen, training, eval)",
    "template repo + profile abstraction": "fork-and-go scaffold where a researcher's training/exploration is declared via a profile-like config over a standardized interface",
    "gbm / R native boosting": "legacy R boosting packages used for some models; no production refresh path, no serving scale",
    "utilization (CPU/GPU)": "fraction of provisioned compute actually doing work, measured by SRE resource monitor",
})

# Canonical EX-12 link migrations (remove from EX-12, add to EX-12B)
EX12_LINKS_TO_REMOVE = ["INN-5", "INN-13", "INN-14"]

# Canonical EX-12B links (question_id -> relevance_note)
EX12B_LINKS = [
    ("INN-5",  "Team-wide migration off notebook onto ML platform; utilization 5%→40%, legacy R models back on refresh cadence."),
    ("INN-6",  "Proposed template + profile abstraction on top of ML platform runtime — the process change that made researcher adoption default and delivered utilization 5%→40% + platform-wide capability defaults."),
    ("INN-7",  "Didn't just fix notebook waste — pushed platform roadmap beyond ephemeral pods toward persistent dev + reusable pipelines; strategic bet that later became ML platform defaults."),
    ("INN-11", "Migrated entire research team off ad-hoc notebook environments onto a mature ML platform with template+profile abstraction; utilization 5%→40%."),
    ("INN-13", "Well-established notebook workflow was inefficient at <5% utilization; team-wide migration with template+profile abstraction improved it without killing research velocity."),
    ("INN-14", "Template+profile abstraction codified as team best practice; new researchers fork-and-go, team iteration velocity + production solidity both rose."),
    ("INN-15", "Codified team-accepted best practice: template repos + profile-like config so researchers describe training / exploration declaratively; fork-and-go for new joiners."),
    ("COL-3",  "Two-way translator between Research Science and ML platform / Infra — carried RS workflow requirements (HDFS, Spark, LnP, debug tooling) into platform roadmap so migration preserved capability."),
    ("COL-5",  "Aligned researchers (worried about losing notebook capability) with platform team (scoped initially to k8s + ephemeral pods) around a shared roadmap that satisfied both."),
    ("COL-7",  "RS (non-infra) + ML platform engineers (non-research) had no shared language; translated in both directions — surfaced <5% utilization to leadership, carried HDFS/Spark/LnP requirements into platform scope."),
    ("IMP-4",  "Notebook→ML platform migration: utilization 5%→40%, freed capacity benefits other workloads, legacy R models refreshable, platform capabilities became defaults for other teams."),
    ("IMP-6",  "Template+profile abstraction sustains onboarding for new researchers without coaching overhead; auto model versioning + historical weights + real-time CPU/GPU diagnostics replaced notebook-era ad-hoc maintenance."),
    ("IMP-8",  "Built template+profile abstraction that scales horizontally (fork-and-go) rather than by coaching hours; platform capabilities pushed during migration became ML platform defaults."),
    ("IMP-10", "Short-term: team utilization 5%→40% + unblocked refreshable legacy models. Long-term: platform capabilities adopted org-wide as defaults; reframed \"DS can't ship production\" from skill gap to tooling gap."),
    ("OWN-10", "Prioritized platform-level change (persistent dev + reusable pipelines into ML platform roadmap) over short-term migration; capabilities later became defaults for other teams."),
    ("COM-2",  "Persuaded leadership with utilization data and persuaded researchers with pain-first empathy — didn't mandate notebook deprecation, made the alternative viable enough that cooperation was rational."),
]


def _backup_db() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB_PATH.with_name(f"mle_prep.db.bak.{ts}_pre_ex12b_insert")
    shutil.copy2(DB_PATH, backup)
    return backup


def _upsert_example(cur: sqlite3.Cursor) -> tuple[str, int]:
    """Insert or update EX-12B row. Returns (action, example_pk)."""
    row = cur.execute(
        "SELECT id, title FROM behavioral_examples WHERE example_id = ?",
        (EXAMPLE_ID,),
    ).fetchone()

    fields = {
        "example_id": EXAMPLE_ID,
        "title": TITLE,
        "source_project": SOURCE_PROJECT,
        "situation": SITUATION,
        "task": TASK,
        "action": ACTION,
        "result": RESULT,
        "principle_tags": PRINCIPLE_TAGS,
        "risk_statement": RISK_STATEMENT,
        "analogy": ANALOGY,
        "tech_terms": TECH_TERMS,
        "cn_elevator_pitch": CN_ELEVATOR_PITCH,
    }

    if row is None:
        cols = ", ".join(fields.keys())
        placeholders = ", ".join(["?"] * len(fields))
        cur.execute(
            f"INSERT INTO behavioral_examples ({cols}) VALUES ({placeholders})",
            tuple(fields.values()),
        )
        return "INSERT", cur.lastrowid

    pk = row[0]
    set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
    cur.execute(
        f"UPDATE behavioral_examples SET {set_clause} WHERE id = ?",
        (*fields.values(), pk),
    )
    return "UPDATE", pk


def _resolve_question_pk(cur: sqlite3.Cursor, qid: str) -> int | None:
    row = cur.execute(
        "SELECT id FROM behavioral_questions WHERE question_id = ?", (qid,)
    ).fetchone()
    return row[0] if row else None


def _resolve_example_pk(cur: sqlite3.Cursor, eid: str) -> int | None:
    row = cur.execute(
        "SELECT id FROM behavioral_examples WHERE example_id = ?", (eid,)
    ).fetchone()
    return row[0] if row else None


def main() -> None:
    backup = _backup_db()
    print(f"[BACKUP] {backup.name}")

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("BEGIN")

    try:
        action, ex12b_pk = _upsert_example(cur)
        print(f"[{action}] behavioral_examples EX-12B pk={ex12b_pk}")

        ex12_pk = _resolve_example_pk(cur, "EX-12")
        if ex12_pk is None:
            raise RuntimeError("EX-12 not found — cannot migrate links.")

        # Phase 2: remove migrated INN links from EX-12
        removed = 0
        for qid in EX12_LINKS_TO_REMOVE:
            q_pk = _resolve_question_pk(cur, qid)
            if q_pk is None:
                print(f"[WARN]   question {qid} not found; skipping EX-12 link removal")
                continue
            res = cur.execute(
                "DELETE FROM question_example_links "
                "WHERE question_id = ? AND example_id = ?",
                (q_pk, ex12_pk),
            )
            if res.rowcount:
                print(f"[DELETE] EX-12 <-> {qid} link (rowcount={res.rowcount})")
                removed += res.rowcount
            else:
                print(f"[SKIP]   EX-12 <-> {qid} link (already removed)")

        # Phase 3: upsert EX-12B links
        inserted = 0
        synced = 0
        for qid, note in EX12B_LINKS:
            q_pk = _resolve_question_pk(cur, qid)
            if q_pk is None:
                print(f"[WARN]   question {qid} not found; skipping EX-12B link")
                continue
            existing = cur.execute(
                "SELECT id, relevance_note FROM question_example_links "
                "WHERE question_id = ? AND example_id = ?",
                (q_pk, ex12b_pk),
            ).fetchone()
            if existing is None:
                cur.execute(
                    "INSERT INTO question_example_links "
                    "(question_id, example_id, relevance_note) VALUES (?, ?, ?)",
                    (q_pk, ex12b_pk, note),
                )
                print(f"[INSERT] EX-12B <-> {qid}")
                inserted += 1
            else:
                link_pk, old_note = existing
                if old_note == note:
                    print(f"[SKIP]   EX-12B <-> {qid} (note unchanged)")
                else:
                    cur.execute(
                        "UPDATE question_example_links SET relevance_note = ? "
                        "WHERE id = ?",
                        (note, link_pk),
                    )
                    print(f"[SYNC]   EX-12B <-> {qid} (note updated)")
                    synced += 1

        conn.commit()
        print(
            f"\nDone. example={action}, "
            f"EX-12 links removed={removed}, "
            f"EX-12B links inserted={inserted}, synced={synced}"
        )
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
