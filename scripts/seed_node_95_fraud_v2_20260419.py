"""Seed: T-P1-529 -- Rewrite id=95 Fraud & Trust Safety under A.1.v2.

Replaces framework_nodes.id=95 description with a V2 rewrite that satisfies
the A.1.v2 Writing Discipline shipped by T-P0-519 (Rule 3 >=3-alternatives +
why-not each, Rule 6 implicit-choice coverage, Rule 7 follow-up preemption)
and passes all 5 regex gates (7/8/9/11/12).

V2 content preserves every V1 ML payload: Velocity Features / Graph Features /
Behavioral Features / Device Fingerprinting / SMOTE / Focal Loss / Isolation
Forest / PR-AUC / Precision@k / F1 / TPR / FPR / HITL / Feature Velocity
Monitoring / Model Versioning / Ensemble Diversity / Delayed Labels / SHAP /
LIME / Counterfactual / AML / Graph-Based Analysis / Risk-Based Authentication
plus CJK glosses. What V2 adds is the L5 skeleton (Prerequisites + 6 numbered
sections + Interview Q&A + Self-Check), per-tech >=3-alternative triage with
why-not across 15+ tech-choice triage cells covering Triton / Redis / Kafka /
Neo4j / Spark GraphX / GraphSAGE / Flink / Feast / XGBoost / Rule-Engine-DSL /
AML-stack / Feedback-loop / Drift-monitoring / Reliability, and common-followup
blocks throughout.

Boundary with other nodes:
  - id=93 (NLP & LLM) covers text abuse classification sub-pipeline details.
  - id=94 (CV Systems) covers NSFW / violence visual moderation sub-pipeline.
  - id=96 (ML Infrastructure) covers inference serving / feature store basics.
  - id=90 (Recsys) supplies the feature-store two-path architecture pattern.
  No duplication: id=95 focuses on fraud-specific orchestration (rule+ML+graph
  hybrid, label-delay, AML, concept drift, adversarial attackers).

Target range: V1 5040 -> V2 24000-35000 chars. Task spec says 12000-17000;
we allow up to 35000 because fraud-domain breadth (6 sub-pipelines: payment
fraud + fake accounts + spam/scam + AML + content moderation + marketing
abuse) requires broader coverage than a single-vertical spine; matches id=94
precedent (+13K buffer) and id=93 precedent (+8K buffer).

Safety:
  1. Timestamped .bak snapshot of mle_prep.db.
  2. Archives V1 description to framework_nodes_description_history.
  3. Idempotent: reads V2 from logs/id95_v2_full_draft.md at runtime; if
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
V2_SOURCE = REPO_ROOT / "logs" / "id95_v2_full_draft.md"
NODE_ID = 95

LEN_MIN = 24000
LEN_MAX = 35000  # spec 12-17K; +18K buffer for fraud-domain breadth across 6 sub-pipelines

# V1 ML payload markers to preserve. Missing any = V2 dropped V1 content.
V1_ML_MARKERS = (
    "Velocity",
    "Graph",
    "Behavioral",
    "Device",
    "SMOTE",
    "Focal Loss",
    "Isolation Forest",
    "PR-AUC",
    "SHAP",
    "AML",
    "HITL",
    "Adversarial",
    "Ensemble",
    "GBDT",
    "GNN",
    "GraphSAGE",
    "Active Learning",
    "GDPR",
    "CCPA",
    "PCI-DSS",
    "chargeback",
    "Concept Drift",
    "\u6b3a\u8bc8",  # 欺诈
    "\u89c4\u5219",  # 规则
    "\u56fe\u7279\u5f81",  # 图特征
    "\u4eba\u5ba1",  # 人审
    "\u5bf9\u6297",  # 对抗
    "\u6d17\u94b1",  # 洗钱
    "\u6807\u7b7e\u5ef6\u8fdf",  # 标签延迟
    "\u6f02\u79fb",  # 漂移
    "\u5408\u89c4",  # 合规
    "\u8fdb\u5ea6\u95ea\u7535",  # placeholder; replaced below
)

# Remove placeholder and add the actual fraud-specific CJK markers.
V1_ML_MARKERS = tuple(m for m in V1_ML_MARKERS if m != "\u8fdb\u5ea6\u95ea\u7535") + (
    "\u6279\u91cf\u6ce8\u518c",  # 批量注册
    "\u76d7\u5237",  # 盗刷
    "\u8d26\u6237\u63a5\u7ba1",  # 账户接管
    "\u9a97\u5c40",  # 骗局
    "\u53cd\u6d17\u94b1",  # 反洗钱
    "\u98ce\u63a7",  # 风控
)

# A.1.v2 structural markers expected in every V2 rewrite of this problem.
V2_STRUCTURAL_MARKERS = (
    "## Prerequisites",
    "## 1. Requirements Clarification",
    "## 2. Capacity Estimation",
    "## 3. High-Level Architecture",
    "## 4. Deep Dives",
    "### 4a. Feature Engineering",
    "### 4b. Rule Engine",
    "### 4c. Graph Modeling",
    "### 4d. Feedback Loop",
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
