"""Backfill cheat_sheet column for 5 old Pinterest ML SDs (batch 4 / final of T-P2-683).

Targets (display_order 200-205, all currently empty on cheat_sheet):
  id=29 pinterest-ad-ctr             (CTR prediction)
  id=30 pinterest-embeddings         (User & Pin embeddings)
  id=31 pinterest-chatbot-pins       (Personalized chat bot)
  id=33 pinterest-pins-search        (Pins search engine)
  id=34 pinterest-notification-reco  (Notification recommendation)

Idempotent: rewrites only the cheat_sheet column for the 5 target slugs;
all other columns are left untouched.

Style (per project memory feedback_content_style_cn_en + 2026-05-02 batches 1/2/3
reference seed_sd_cheat_sheets_interview_batch{2,3}_20260502.py):
  - Markdown table with 11-12 rows.
  - Columns: 'Item' / 'Number / Decision'.
  - Chinese narration + English technical-term expansion on first use.
  - 250-700 chars (compact flash card).
  - Numbers / decisions sourced from each row's existing overview /
    production_constraints / tradeoffs / formulas columns -- no new content
    invented.

Pinterest 5 are ML SDs (vs interview 9 which were infra SDs); cheat-sheets
emphasize model architecture / training pipeline / online metric over QPS.

Final batch of T-P2-683. After this runs:
  SELECT COUNT(*) FROM system_designs WHERE LENGTH(IFNULL(cheat_sheet,'')) = 0
should return 0.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

CHEAT_SHEETS: dict[str, str] = {
    "pinterest-ad-ctr": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 500M MAU, 10B impr/天, peak 150K QPS |
| Latency | Ad ranker P99 <60ms |
| 计费 | **oCPM** ⇒ pCTR **必须 calibrated** |
| L1 ranker | GBDT ~100 特征, <5ms, 2k→200 |
| L2 ranker | **DeepFM / DCN-v2** 自动 cross |
| Multi-task | **MMoE / PLE** + pCTR/pCVR/pCloseup heads |
| 校准 | Isotonic; ECE 分桶, hourly ratio ∈ [0.9,1.1] |
| Cold start | <1000 impr → **Thompson on Beta** + creative emb |
| Position bias | training 加 pos feat, serving 固定 pos=1 |
| 训练 | Daily 增量 + weekly full, 8-GPU sync |
| 部署 | shadow 1 天 + canary 1→5→50→100% |
| Metric | LogLoss / **NE** / Calib ratio + PSI drift |
""",

    "pinterest-embeddings": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 5B pins × 500M MAU, peak 200K QPS |
| 维度 | Pin **256d** |
| 架构 | **Two-tower**（cross-attention 不能 ANN） |
| Pin tower | Content (image+text) + **PinSage**（cold day-1） |
| User tower | 短 50 序列 + 长 30 天 topic（Transformer） |
| Freshness | User 15-min streaming, Pin T+1 + 新 pin 实时 |
| Loss | **Contrastive** in-batch B=8192 + LogQ correction |
| Hard negs | ANN top-100 未 repin |
| 训练 | 256 A100 + **embedding parallel**（1.2 TB 必分片） |
| Multi-task | 主 long-repin + 辅 click/closeup MMoE |
| Downstream | CG Recall +30%, ranker NDCG +2%, similar-pins |
| 评估 | Recall@100/500, cold-pin recall, drift KL >0.1 |
""",

    "pinterest-chatbot-pins": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 10M DAU × 5 turn ⇒ peak 600 QPS |
| Latency | first-token <2s, full reply <3s |
| 检索 | **三路 RRF (k=60)**: Dense + BM25 + Personalized |
| Re-rank | Stage-1 LightGBM top-50; Stage-2 LLM 仅 compare |
| 生成 | **7B Llama-3** INT8 vLLM, 80 tok/s/GPU |
| Grounding | **Structured decoding** JSON; pin_id 必在 top-50 |
| 多样性 | MMR λ=0.3 + same-board ≤3 + L2-cat ≤6 |
| Safety | 双向 input(PII/jailbreak) + retrieval + output |
| Self-harm | hard override → hotline |
| 训练 | **SFT 100K** → **DPO 50K**（vs PPO 更稳） |
| Cold start | 降级 BM25+dense + persona clarify |
| Kill switch | 每模块 flag → retrieval-only / pure-LLM |
""",

    "pinterest-pins-search": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 500M MAU, 5B pins, peak 100K QPS |
| Latency | P99 <500ms（CG <150ms + rank <200ms） |
| Funnel | Query → CG 5k → L1 500 → L2 50 |
| CG | **Two-tower + ANN (ScaNN/HNSW)** + BM25 |
| L1 ranker | **GBDT** + **LambdaRank**, 5-10ms |
| L2 ranker | **MMoE**: y_ctr / y_repin / y_closeup / y_hide |
| 融合分 | $w_1 y_{ctr} + w_2 y_{repin} - w_4 y_{hide}$ |
| Personalization | user emb + GRU last-50 |
| Exposure bias | **IPS** + 1-2% randomized exploration |
| 训练 | DDP 8x A100, 1 epoch/day; 1→10→50% A/B |
| Offline | Recall@K / NDCG/MAP / golden 10K |
| North star | **Repin-rate per session**（vs CTR 易 spam） |
""",

    "pinterest-notification-reco": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 500M MAU, peak 3B push/天 |
| Latency | 触发-投递 P99 <30s |
| Channel | mobile push + email + in-app inbox |
| 通知类型 | Engagement / Re-engagement / Transactional / Marketing |
| 候选 | followed-board 新 pin / dormant / order |
| Ranking | **Multi-task DNN**: pOpen + pClick + pDisable + **LTV** |
| 损失 | BCE + 负向 head（pDisable 抑骚扰） |
| 决策 | per-user budget + (pOpen×LTV > τ) + freq cap |
| 硬约束 | quiet hours + channel cap + unsubscribe |
| North star | **WAU 7-28 天**（vs open-rate 易 spam） |
| Guardrail | unsubscribe / uninstall / complaint / bounce |
| Holdout | **1% 完全不发** 长期保留 + 2-week A/B sticky |
""",
}

TARGET_SLUGS = list(CHEAT_SHEETS.keys())


def main() -> None:
    """UPSERT cheat_sheet for the 5 Pinterest ML system designs (batch 4 / final)."""
    init_db()
    db = SessionLocal()
    chinese_pattern = re.compile(r"[一-鿿]")
    failed: list[str] = []
    try:
        for slug in TARGET_SLUGS:
            row = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
            if row is None:
                print(f"[ERROR] slug not found: {slug}")
                failed.append(slug)
                continue

            new = CHEAT_SHEETS[slug]
            old = row.cheat_sheet or ""
            action = "NOOP" if old == new else ("INSERT" if not old else "UPDATE")
            row.cheat_sheet = new

            char_len = len(new)
            has_cn = bool(chinese_pattern.search(new))
            warn = ""
            if not has_cn:
                warn += " [WARN: no CN chars]"
            if char_len < 250 or char_len > 700:
                warn += f" [WARN: len {char_len} outside 250-700]"

            print(f"[{action}] {slug}: cheat_sheet={char_len} chars{warn}")

        db.commit()
        if failed:
            print(f"[FAIL] {len(failed)} slug(s) not found: {failed}")
            sys.exit(1)
        print(f"[DONE] cheat_sheet patched for {len(TARGET_SLUGS)} Pinterest ML SDs (batch 4 / final).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
