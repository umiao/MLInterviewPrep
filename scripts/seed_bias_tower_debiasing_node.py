"""Seed: T-P0-854 -- Bias Tower deep-dive -> framework_nodes id=266 description.

Updates the `description` column of the existing framework_nodes row at path
`meta-prep/system-design-must-knows/popularity-bias-debiasing` (id=266,
title="Popularity Bias / Position Bias / Selection Bias") from the short
710-byte 3-types-of-bias overview (originally seeded by
`scripts/seed_meta_prep_sd_must_knows.py`) to a ~6.5KB 8-section deep dive on:

  1. Shallow Bias Tower (YouTube 2019) -- additive two-tower structure,
     why shallow (capacity bottleneck + gradient stealing prevention),
     inductive bias (additive decomposition -> identifiability).
  2. Mask-at-Inference -- training feeds real position, inference masks
     the bias term; two equivalent implementations (set to 0 / set to
     fixed reference); paired feature-dropout regularization.
  3. Bias Tower vs. Direct Feature (4-axis comparison table + theoretical
     equivalence prerequisite for implicit bias tower reconstruction).
  4. isAds Decision Boundary -- counterfactual relevance (-> bias) vs.
     factual prediction P(click|identity) (-> context feature).
  5. Train/Serve Skew -- 4 canonical sources (code-path drift, time
     travel, default-value drift, bias-feature train-real-serve-mask
     distribution mismatch) + offline-good-online-bad failure mode.
  6. Shadow Feature Logging -- log the model's actual feature vector
     at serving time, join labels post-hoc; 3 guarantees (100% train-
     serve parity, point-in-time correctness, bias-feature faithful
     recording) + 4 engineering rules (unbiased sampling, async queue,
     stream label joiner, distribution-drift monitoring).
  7. Closed-loop logic chain (model layer + inference layer + data
     layer = 3-layer debiasing).
  8. Design Doc emphasis 4 lines (verbatim production-grade phrasing).

Source content is verbatim from user-authored Discord msg 1503874418529669201
(2026-05-12, channel #ml-interview-prep), captured in
`docs/prep/meta_mlsd_2026-05-12_top3/source_05_bias_tower_train_serve_skew.md`.

This deep version serves as the terminal "drill-down" target for the sd-card
`sd://meta-top3-comments-golden` (T-P0-853) Bias Tower 简版 fusion segment
(embedded in architecture / production_constraints / cheat_sheet columns)
and for the cd-drawer retrofits T-P0-855..858 (cd94/cd95/cd96/cd97). The
anchor sentence in every upstream surface is verbatim:

    深入见 fr-node meta-prep/system-design-must-knows/popularity-bias-debiasing

so the reader can drill down from any of those simplified card/drawer
segments to this 6.5KB canonical version.

Supersession note: the original short description (710 bytes, written by
`seed_meta_prep_sd_must_knows.py`) is the *first known prior*. Running
this seed will detect that prior verbatim and UPDATE -> new long version.
On re-run, the row will match the new long version -> SKIP. If the row
description is anything else, we CONFLICT (refuse to overwrite hand-edits).

If `seed_meta_prep_sd_must_knows.py` is later re-run, it will re-detect a
description drift on this specific child slug ("popularity-bias-debiasing")
and raise its own CONFLICT -- this is the intended pluralism: the canonical
authority for fr-node 266 has shifted to *this* seed; the old batch seed
should be updated to import the long description from here (deferred --
out of EXPECTED_FILES scope for T-P0-854).

Idempotent:
  1. Row absent -> RuntimeError (this seed only UPDATEs, never INSERTs).
  2. Row.description == DESCRIPTION_NEW -> SKIP (true idempotency).
  3. Row.description == KNOWN_PRIOR_DESC -> UPDATE to DESCRIPTION_NEW.
  4. Row.description == anything else -> CONFLICT.

Usage:
    python scripts/seed_bias_tower_debiasing_node.py [--dry-run] [--db PATH]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

TARGET_PATH = "meta-prep/system-design-must-knows/popularity-bias-debiasing"
TARGET_TITLE = "Popularity Bias / Position Bias / Selection Bias"
TARGET_NODE_ID = 266  # informational; lookup is by path

# Exact 710-byte string originally written by seed_meta_prep_sd_must_knows.py
# for slug='popularity-bias-debiasing'. Treated as the first known prior.
KNOWN_PRIOR_DESC = (
    "训练数据本身有 bias: (a) popularity bias -- 高频 item 在 in-batch "
    "negative 里被过度惩罚, 排序里又被过度曝光, 形成 'rich-get-richer' "
    "正反馈; (b) position bias -- 用户更倾向点高位 item, 导致 click "
    "数据天然偏向高位; (c) selection bias -- 只看到 ranker exposed 的 "
    "item, 没 exposed 的永远没 label. 修法: (1) sampled-softmax logQ "
    "修正去 popularity bias; (2) position bias 用 PAL (Position-Aware "
    "Learning) / IPS (Inverse Propensity Scoring) 折去; (3) selection "
    "bias 用 logging policy + IPS 或 doubly-robust estimator. 面试 "
    "follow-up: 怎么验证 debiasing 真有效 (offline counterfactual eval "
    "+ online A/B). Cross-links: kg://99 (multi_stage_ranking), "
    "kg://121 (causal_inference), sd://pinterest-pin-ranking. "
    "Anti-patterns: 把 click 当 ground-truth label 训; debiasing 没做 "
    "counterfactual sanity check."
)

# Long-form deep version, ~6.5KB, 8 sections, verbatim from
# docs/prep/meta_mlsd_2026-05-12_top3/source_05_bias_tower_train_serve_skew.md
# (Discord msg 1503874418529669201, 2026-05-12).
DESCRIPTION_NEW = """\
**概览 (节点定位)**: 此节点收容 ranking 模型上 3 类核心 bias 的工业级解法.
原 710-byte 简版已升级为 8-节 深版, 中心是 position bias 的 *shallow bias
tower* (YouTube 2019) 机制, 并把 train/serve skew + shadow feature logging
作为 "保证 debias 真生效" 的数据层支撑. Popularity bias (sampled-softmax
logQ 修正) 与 selection bias (logging policy + IPS / doubly-robust) 仍在
原 cross-links kg://99 (multi_stage_ranking) / kg://121 (causal_inference) /
sd://pinterest-pin-ranking 各自的 node 中展开. 本节专攻 "架构纠偏 + 推理纠偏 +
数据纠偏 三层闭环" — 这是 Meta / YouTube / Pinterest ranking team 公开
论文与工程 talk 共享的标准模板.

---

## 零、三类 Bias 速查 (源 710-byte 简版保留)

训练数据本身有 bias, 三类必须同时处理:

- **(a) Popularity bias** -- 高频 item 在 in-batch negative 里被过度惩罚,
  排序里又被过度曝光, 形成 "rich-get-richer" 正反馈.
  修法: sampled-softmax logQ 修正 (训练时减去 log q(item) 的频率项, 让
  正样本 logit 与 negative-sampling 分布解耦).
- **(b) Position bias** -- 用户更倾向点高位 item, 导致 click 数据天然
  偏向高位 (即 "位置而非内容驱动 click").
  修法: PAL (Position-Aware Learning, 把 position 拼进模型作为可显式 mask
  的特征) / IPS (Inverse Propensity Scoring, 1/P(exposure|position) 折损).
  → 本节 1-3 章把 PAL 机制深化为 shallow bias tower + mask-at-inference,
  这是 PAL 的工业落地形态.
- **(c) Selection bias** -- 只看到 ranker exposed 的 item, 没 exposed 的
  永远没 label (logging policy 决定可观测分布).
  修法: logging policy + IPS 或 doubly-robust estimator
  (offline policy evaluation 框架, 同时校正 propensity 与 reward 模型).

面试 follow-up: 怎么验证 debiasing 真有效 →
offline counterfactual eval (在 held-out logged data 上比较 propensity-weighted
metric vs naive metric) + online A/B (业务指标移动, 不仅看 AUC).
Anti-patterns: 把 click 当 ground-truth label 训; debiasing 没做
counterfactual sanity check; bias 特征 train 真值 / serve mask 但不监控分布.

---

## 一、Shallow Bias Tower (YouTube 2019)

**架构**

- 双塔加性结构: `logit = main_tower(content, user, ctx) + bias_tower(bias_features)`
- 主塔深 (MMoE)，偏差塔浅 (1-2 层 / 线性)
- 偏差塔输入只放 bias 类特征: position、device、slot type、isAds 等

**为什么浅**

- 容量瓶颈 -> 只吸收加性偏置，吃不下 content 信号
- 防止 position 抢梯度，逼主塔学真实相关性

**核心归纳偏置**

- 加性可分: relevance + bias，提供可识别性
- 主塔输出天然独立于 position，干净的反事实表达

---

## 二、Mask-at-Inference

- 训练: bias tower 喂真实 position
- 推理: 屏蔽 bias 项
- 两种等价实现:
  - 把 bias term 整个置 0 (最干净)
  - position 设为固定参考值 (如 1)，bias term 变常数，不影响排序
- 配套训练技巧: 训练时对 position 做 feature dropout，让模型对缺失鲁棒

---

## 三、Bias Tower vs. 直接当 Feature

| 维度       | Bias Tower             | 拼进主塔                    |
|------------|------------------------|-----------------------------|
| 分解结构   | 加性可分               | content x position 纠缠     |
| 推理 mask  | 良定义                 | 分布外、表示被污染          |
| 梯度竞争   | 主塔学相关性           | position 抢信号             |
| 可识别性   | 强先验                 | 解不唯一                    |

理论等价的前提 (即用工程隐式重建 bias tower): position 随机分布 + dropout + 正则 +
大容量。做齐这些 = 手工搭 bias tower。

---

## 四、isAds 的判断标准

- 想要 反事实「若为 organic 的相关性」-> 当 bias 处理
- 想要 事实预测 P(click | 当前真实身份) -> 当 context feature

判断点: ads 与 organic 是否只是 logit 加性偏移 (-> bias) 还是有真 interaction (-> feature)。

---

## 五、Train/Serve Skew

**常见来源**

- 训练/服务代码路径不一致 (Python vs C++)
- Time travel: 训练特征泄漏未来
- 数据源 / 默认值 / null 处理漂移
- bias 特征训练用真实值、serving 用 mask，分布不匹配

后果: 离线指标好、线上掉点

---

## 六、Shadow Feature Logging

做法: serving 时把模型实际看到的 feature_vector 原样落盘，事后 join label 作为训练样本。

**保证**

- 训练/服务特征 100% 一致 (同一份代码算的)
- Point-in-time 正确，无未来泄漏
- bias 特征 (position / device) 忠实记录，bias tower 训练分布对齐

**工程要点**

- 采样要无偏，避免引入新 bias
- 异步队列 (Kafka / Pub-Sub)，不阻塞 serving
- 流式 label joiner (Flink / Beam) 按 request_id 关联行为
- 持续监控 logged 特征分布 vs serving 实时分布 -> 主动告警 skew

---

## 七、整体设计内在逻辑链

- 隐式反馈 -> 选择偏差 -> 需 debias
- 模型层: shallow bias tower 剥离 position bias
- 推理层: mask-at-inference 实现反事实预测
- 数据层: shadow logging 消除 train/serve skew，保证 1-3 真正生效

口诀: **架构纠偏 (bias tower) + 推理纠偏 (mask) + 数据纠偏 (shadow log)，三层缺一不可。**

---

## 八、Design Doc 强调话术

1. 「采用加性 shallow bias tower，结构性强制 relevance / bias 分解」
2. 「Mask-at-inference 提供干净的反事实排序信号」
3. 「Shadow feature logging 保证 bias 特征训练/服务分布一致，避免 debias 机制被 skew 破坏」
4. 「离线 AUC 可能持平甚至微跌，业务指标 (多样性 / 留存 / 新内容曝光) 为真实评估目标」

---

**Cross-links (carryover from 710-byte prior)**: kg://99 (multi_stage_ranking),
kg://121 (causal_inference), sd://pinterest-pin-ranking, sd://meta-top3-comments-golden
(本 fr-node 的 ranking-side anchor: sd-card 简版 -> 本节深版 drill-down).
"""


def assert_section_headers(text: str) -> None:
    """AC #3: description must contain 8 section headers."""
    required_headers = [
        "## 一、Shallow Bias Tower",
        "## 二、Mask-at-Inference",
        "## 三、Bias Tower vs. 直接当 Feature",
        "## 四、isAds 的判断标准",
        "## 五、Train/Serve Skew",
        "## 六、Shadow Feature Logging",
        "## 七、整体设计内在逻辑链",
        "## 八、Design Doc 强调话术",
    ]
    missing = [h for h in required_headers if h not in text]
    if missing:
        raise AssertionError(
            f"[AC-FAIL] description missing section headers: {missing}"
        )


def assert_size_floor(text: str, floor_bytes: int = 5 * 1024) -> None:
    """AC #3: description length > 5KB."""
    n = len(text.encode("utf-8"))
    if n <= floor_bytes:
        raise AssertionError(
            f"[AC-FAIL] description is {n} bytes; AC requires > {floor_bytes} bytes"
        )


def upsert_description(
    conn: sqlite3.Connection, *, dry_run: bool
) -> tuple[str, int, int]:
    """Look up the target row by path and update description if needed.

    Returns (action, before_len, after_len) where action is one of:
      "SKIPPED" -- row already at DESCRIPTION_NEW (true idempotent re-run)
      "UPDATED" -- row was at KNOWN_PRIOR_DESC, now at DESCRIPTION_NEW
      "DRY-RUN-WOULD-UPDATE" -- dry-run path on a real update
    Raises RuntimeError on missing row or unexpected content drift.
    """
    row = conn.execute(
        "SELECT id, title, description FROM framework_nodes WHERE path = ?",
        (TARGET_PATH,),
    ).fetchone()
    if row is None:
        raise RuntimeError(
            f"[FAIL] target node not found: path={TARGET_PATH!r}. "
            f"Run seed_meta_prep_sd_must_knows.py first to seed the parent + "
            f"child stub, then re-run this script."
        )
    node_id, title, current_desc = row
    if node_id != TARGET_NODE_ID:
        # Informational mismatch only; path lookup is authoritative.
        print(
            f"[INFO] target node id={node_id} (expected {TARGET_NODE_ID}); "
            f"using path-based lookup; proceeding.",
            file=sys.stderr,
        )
    if title != TARGET_TITLE:
        raise RuntimeError(
            f"[FAIL] target node title drifted: got {title!r}, "
            f"expected {TARGET_TITLE!r}. Resolve by reverting title."
        )
    before_len = len(current_desc.encode("utf-8")) if current_desc else 0
    after_len = len(DESCRIPTION_NEW.encode("utf-8"))
    if current_desc == DESCRIPTION_NEW:
        return "SKIPPED", before_len, after_len
    if current_desc != KNOWN_PRIOR_DESC:
        raise RuntimeError(
            f"[CONFLICT] target node description has drifted from the known "
            f"prior (seed_meta_prep_sd_must_knows.py) and is not yet the new "
            f"long version. Refusing to overwrite a hand-edit. "
            f"Current length: {before_len} bytes. "
            f"Expected prior length: {len(KNOWN_PRIOR_DESC.encode('utf-8'))} bytes. "
            f"Resolve by reverting the hand-edit, or by updating "
            f"KNOWN_PRIOR_DESC in this seed to acknowledge the new prior."
        )
    if dry_run:
        return "DRY-RUN-WOULD-UPDATE", before_len, after_len
    conn.execute(
        "UPDATE framework_nodes SET description = ? WHERE path = ?",
        (DESCRIPTION_NEW, TARGET_PATH),
    )
    return "UPDATED", before_len, after_len


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Update framework_nodes id=266 description with 8-section "
            "Bias Tower / Train-Serve Skew / Shadow Logging deep dive."
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"Path to SQLite DB (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Probe state, log intended action, but do not write.",
    )
    args = parser.parse_args(argv)

    # Static AC checks (no DB needed).
    assert_section_headers(DESCRIPTION_NEW)
    assert_size_floor(DESCRIPTION_NEW)

    if not args.db.exists():
        print(f"[FAIL] DB not found: {args.db}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(args.db)
    try:
        action, before_len, after_len = upsert_description(
            conn, dry_run=args.dry_run
        )
        if not args.dry_run and action == "UPDATED":
            conn.commit()
        print(
            f"[{action}] path={TARGET_PATH} "
            f"description: {before_len}B -> {after_len}B "
            f"(dry-run={args.dry_run})"
        )
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
