"""Seed: T-P1-526 -- Rewrite id=96 ML Infrastructure Design under A.1.v2.

Replaces framework_nodes.id=96 description with a V2 rewrite that satisfies
the A.1.v2 Writing Discipline shipped by T-P0-519 (Rule 3 >=3-alternatives +
why-not each, Rule 6 implicit-choice coverage, Rule 7 follow-up preemption)
and passes all 5 regex gates (7/8/9/11/12).

V2 content preserves every V1 platform payload: Feature Store / MLflow /
Kubeflow / Airflow / W&B / DDP / FSDP / DeepSpeed / Pipeline Parallelism /
Shadow Deployment / Canary Release / Circuit Breaker / PSI / KL Divergence /
KS Test / Training-Serving Skew / Gang Scheduling / MIG / Preemption /
Spot Instances / Continuous Training / Automatic Rollback / Model Registry
plus CJK glosses. What V2 adds is the L5 skeleton (Prerequisites + 6 numbered
sections + Interview Q&A + Self-Check), per-tech >=3-alternative triage with
why-not across 18 tech-choice cells covering Cluster Orchestrator /
Feature Serving Hot Store / Event Bus / Model Artifact Storage / Service
Split / Workflow Engine / Distributed Training Strategy / Feature Store
Platform / Point-in-time Join / Model Serving Engine / Deployment Strategy /
Circuit Breaker Trigger / Monitoring Platform / Drift Metric / Lineage
Stack / Multi-tenancy Quota / GPU Reliability / Cost Attribution, and
common-followup blocks throughout.

Target range: V1 5677 -> V2 15000-22000 chars per task spec. We allow an
upper buffer to 28500 because the ML-Infra domain breadth (Orchestration
+ Training + Feature Store + Serving + Deployment + Monitoring + Lineage +
Multi-tenancy + Cost) requires 18 triage cells; matches id=97 precedent of
+6K buffer for L5-breadth topics.

Safety:
  1. Timestamped .bak snapshot of mle_prep.db.
  2. Archives V1 description to framework_nodes_description_history.
  3. Idempotent: reads V2 from logs/id96_v2_full_draft.md at runtime; if
     target SHA-256 already stored on the row, exits fast with [SKIP].
  4. Post-update validation: length window, required V1 ML markers, V2
     structural markers, all 5 A.1.v2 regex gates PASS.
  5. Rollback: restore from the .bak snapshot if validation fails.
"""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
V2_SOURCE = REPO_ROOT / "logs" / "id96_v2_full_draft.md"
NODE_ID = 96

LEN_MIN = 15000
LEN_MAX = 28500  # spec 15-22K; +6.5K buffer for ML-Infra breadth (matches id=97 precedent)

# V1 platform payload markers to preserve. Missing any = V2 dropped V1 content.
V1_ML_MARKERS = (
    "Feature Store",
    "MLflow",
    "Kubeflow",
    "Airflow",
    "W&B",
    "DDP",
    "FSDP",
    "DeepSpeed",
    "Pipeline Parallelism",
    "Shadow Deployment",
    "Canary Release",
    "Circuit Breaker",
    "PSI",
    "KL Divergence",
    "KS Test",
    "Training-Serving Skew",
    "Gang Scheduling",
    "Preemption",
    "Spot",
    "Continuous Training",
    "Model Registry",
    "\u8bad\u7ec3",  # 训练
    "\u7279\u5f81",  # 特征
    "\u90e8\u7f72",  # 部署
    "\u76d1\u63a7",  # 监控
    "\u56de\u6eda",  # 回滚
    "\u6f02\u79fb",  # 漂移
    "\u8c03\u5ea6",  # 调度
    "\u79df\u6237",  # 租户
)

# A.1.v2 structural markers expected in every V2 rewrite of this problem.
V2_STRUCTURAL_MARKERS = (
    "## Prerequisites",
    "## 1. Requirements Clarification",
    "## 2. Capacity Estimation",
    "## 3. High-Level Architecture",
    "## 4. Deep Dives",
    "### 4a. Training Orchestration",
    "### 4b. Feature Store",
    "### 4c. Model Serving",
    "### 4d. Monitoring",
    "## 5. Reliability",
    "## 6. Summary & Tradeoffs",
    "## Interview Q&A",
    "## Self-Check",
    "\u5e38\u89c1\u8ffd\u95ee",  # 常见追问
)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def backup_db() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(DB_PATH, dst)
    print(f"[INFO] DB backup -> {dst.name}")
    return dst


def run_audit(desc: str) -> list[str]:
    """Run A.1.v2 regex gates 7/8/9/11/12 on a description string."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from audit_mlsd_prose_quality import (  # type: ignore
        gate7_prose_ratio,
        gate8_section_contract,
        gate9_triage_signal,
        gate11_patch_ban,
        gate12_triage_depth,
        split_sections,
    )

    sections = split_sections(desc)
    problems: list[str] = []
    g7_ok, g7_msg, _ = gate7_prose_ratio(desc)
    if not g7_ok:
        problems.append(f"Gate 7 FAIL: {g7_msg}")
    g8 = gate8_section_contract(sections)
    for p in g8:
        problems.append(f"Gate 8 FAIL: {p}")
    g9 = gate9_triage_signal(desc)
    for p in g9:
        problems.append(f"Gate 9 FAIL: {p}")
    g11 = gate11_patch_ban(sections)
    for p in g11:
        problems.append(f"Gate 11 FAIL: {p}")
    g12 = gate12_triage_depth(desc)
    for p in g12:
        problems.append(f"Gate 12 FAIL: {p}")
    return problems


def validate(desc: str) -> list[str]:
    problems: list[str] = []
    n = len(desc)
    if n < LEN_MIN or n > LEN_MAX:
        problems.append(f"length {n} outside window [{LEN_MIN}, {LEN_MAX}]")
    for marker in V1_ML_MARKERS:
        if marker not in desc:
            problems.append(f"missing V1 ML marker: {marker!r}")
    for marker in V2_STRUCTURAL_MARKERS:
        if marker not in desc:
            problems.append(f"missing V2 structural marker: {marker!r}")
    problems.extend(run_audit(desc))
    return problems


def load_v2_content() -> str:
    if not V2_SOURCE.exists():
        raise SystemExit(f"[FAIL] V2 source not found: {V2_SOURCE}")
    return V2_SOURCE.read_text(encoding="utf-8")


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    new_desc = load_v2_content()
    new_hash = sha256(new_desc)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] framework_node id={NODE_ID} not found")
            return 1
        old_desc = row[0]
        if old_desc is None:
            print(f"[FAIL] framework_node id={NODE_ID} has NULL description")
            return 1

        old_hash = sha256(old_desc)
        if old_hash == new_hash:
            print(f"[SKIP] Node {NODE_ID} already at target V2 hash {new_hash[:12]}")
            print(f"[PASS] Current length = {len(old_desc)} chars")
            return 0

        pre_problems = validate(new_desc)
        if pre_problems:
            print("[FAIL] V2 content failed pre-update validation:")
            for p in pre_problems:
                print(f"  - {p}")
            return 1

        print(f"[INFO] Char length: {len(old_desc)} -> {len(new_desc)}")
        print(f"[INFO] Old hash: {old_hash[:12]}")
        print(f"[INFO] New hash: {new_hash[:12]}")

        bak = backup_db()

        conn.execute(
            "INSERT INTO framework_nodes_description_history(node_id, description) "
            "VALUES (?, ?)",
            (NODE_ID, old_desc),
        )
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (new_desc, NODE_ID),
        )
        conn.commit()

        check = conn.execute(
            "SELECT description FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()[0]
        post = validate(check)
        if post:
            print("[FAIL] Post-update validation failed -- rolling back from backup:")
            for p in post:
                print(f"  - {p}")
            conn.close()
            shutil.copy2(bak, DB_PATH)
            print(f"[INFO] Restored from {bak.name}")
            return 1

        hist_rows = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes_description_history WHERE node_id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        print(
            f"[PASS] Node {NODE_ID} updated; length now {len(check)} chars; "
            f"history rows for this node = {hist_rows}"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
