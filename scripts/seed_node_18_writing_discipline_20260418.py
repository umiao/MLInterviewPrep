"""Seed: T-P0-514 -- Append Appendix A.1 Writing Discipline to id=18.

Appends prose-quality rules to the existing id=18 description so every
downstream L5 MLSD rewrite (id=92 / id=198 V2 and future) has a single
source of truth for:
  - Callout convention (frozen literal patterns `> **GOOD**:` / `> **BAD**:` / `> **NOTE**:`)
  - 4 Writing Discipline rules (Section Contract, Acronym Expansion, Tech-choice Triage, Specificity)
  - Gate 7 (prose ratio), Gate 8 (section contract), Gate 9 (triage signal), Gate 11 (patch-ban)
  - Gate 10 (LLM-judge rubric)
  - audit `--report-only` escape hatch spec

Safety:
  1. Timestamped .bak snapshot of data/mle_prep.db before any write.
  2. Archives old description into framework_nodes_description_history.
  3. Idempotent: if the new-content marker `## Appendix A.1 - Writing Discipline`
     is already present in the DB row, exits fast without re-archiving.
  4. Post-update guards: length in [10000, 12000], all required markers present.
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
NODE_ID = 18

# Composite target length: existing ~7411 chars + appendix ~3300 chars.
LEN_MIN = 10000
LEN_MAX = 12100

APPENDIX_MARKER = "## Appendix A.1 - Writing Discipline"

# Legacy-content patch: the "Reusable playbooks" WebSocket line lacked
# a 因为 clause, which tripped Gate 9. We fix it during this seed so id=18
# self-audits PASS. Both OLD and NEW forms are kept for idempotency.
PLAYBOOK_OLD = "分布式会话存储用 Redis；消费端降级为 long-polling"
PLAYBOOK_NEW = "分布式会话存储用 Redis（因为 in-memory + 跨节点共享 + 亚毫秒）；消费端降级为 long-polling"

APPENDIX_A1 = """

## Appendix A.1 - Writing Discipline

本节是 **Appendix A** 的 prose-quality 补丁。V1 gold（id=92 / id=198）已通过 Appendix A 的机械门（长度、表格、deep-dive 数量），但 review 发现通病：bullet 堆叠、tech-choice 裸名不带 triage、acronym 反复展开或从不展开。本节冻结一套 **对下游全部强制** 的写作纪律，以及对应的自动化审计门。下游所有 V2 重写（T-P0-515 / T-P0-516 / T-P0-518）以及 drawer 样式（T-P2-517）都以本节为契约依据。

### Callout 约定 (FROZEN)

整个 Pillar 3 下所有 V2 描述只允许使用以下三种 callout 字面量，T-P2-517 的 drawer 样式 key 于 EXACTLY 这三种字符串：

```
> **GOOD**: ...
> **BAD**: ...
> **NOTE**: ...
```

- 不允许 emoji 变体（如 check-mark / cross-mark / warning-sign 图形符号）；不允许中文变体（如 `> **好**:`）。
- 如果未来需要新增 callout 种类（例如 `> **WARN**:`），先更新本 appendix，再在内容里使用 —— 顺序不能反。

### Rule 1 - Section Contract（章节契约，合并原 Rule 1/2）

**规则**：每个 `## 1.` 到 `## 6.` 的章节必须由三段组成——

- **Opening**：至少 **2 句散文**（no bullets / no headings / no blockquotes），说明这一节在处理什么、为什么重要、读者将看到什么。
- **Body**：结构化内容（表、列表、代码块）。每个非散文块前先用 1-2 句散文作 intro，把读者"带"进来。
- **Closing**：1 句桥接句，概括本节结论并指向下一节。

> **GOOD**:
> ## 2. Capacity Estimation
> 容量估算这一步的目的不是炫耀数学，而是让后面的每个架构决策有 anchor。我按 **Daily Active Users** (DAU, 日活) → **Queries Per Second** (QPS, 每秒查询) → Storage → Bandwidth 的链路走一遍，并强调哪两个数字直接驱动了架构选型。
>
> - 10K DAU × 3 sessions/day = 30K sessions/day ≈ 0.35 QPS avg
> - 读 : 写 ≈ 50 : 1 ⇒ 17 QPS 读峰值
>
> 这两个数字告诉我：写入负担小但读爆炸，读侧是战场；存储单机能装，暂不分片。下一步用这两个结论切服务边界。

> **BAD**:
> ## 2. Capacity Estimation
> - 10K DAU
> - 120 writes/s
> - Decision: Redis single-node

### Rule 2 - Acronym Expansion（首次出现逐节展开）

**规则**：每个 acronym 在 **一个 section 内** 的第一次出现必须完整展开成 `**English full name** (ACR, 中文译名)`。同一 section 后续复用直接写 ACR。跨 section 再次首现重新展开。这是 sweet spot：文档级太松（读者忘了缩写原义）、段落级过于膨胀（相同术语连续展开三次）、section 级恰好匹配读者的短期记忆节拍。

> **GOOD**: 派单这一步我用 **Compare-And-Swap** (CAS, 比较并交换) 作为并发控制。CAS 单条 SQL 搞定。后文 §4 再次出现 `CAS` 可以裸写，但在 §5 首次出现 `SLA` / `DAU` / `MoE` 时仍需首次展开。

> **BAD**: 派单用 CAS。CAS 单条 SQL 搞定。（读者完全不知道 CAS 是什么）

### Rule 3 - Tech-choice Triage（技术选型必带 4 要素）

**规则**：任何 tech-choice（产品、算法、协议）在其首次声明性出现处必须同时给出 4 要素：**pick + reason + ≥1 alternative with when-better + switch-trigger**。Gate 9 通过 regex 侦测：任何 `/\\b(选|使用|用|pick)\\b/` 动词后 1000 字符内必须出现 `/\\b(因为|because)\\b/`。

> **GOOD**:
> 地理查询我选 **Redis GEO**，因为单城 600 司机峰值 500 并发查询，Redis 单机 10-100K QPS 完全够用且内存访问亚毫秒。候选有 **PostGIS** 和 **S2**：PostGIS 在需要持久化 + 复杂多边形查询时更合适，但这里只做 radius 查询且允许近似一致；S2 是极大规模（多城全球）的升级路径。当单机 Redis 内存紧张或跨城查询出现时，我改为按 city-key sharding，进一步换 S2/H3。

> **BAD**: 选 Redis GEO。（看表）

### Rule 4 - Specificity Discipline（具体性纪律）

**规则**：两条边界条件——

- **(a)** 如果 §1 Clarification 里没有某项能力需求（例如没有 geo 需求），**不要** 在后文点名具体产品（不写 Redis GEO）。"为炫技而具体"会被扣分。
- **(b)** 如果点名了具体产品，必须走完 4 步因果链：**requirement → why this class → why this product → when insufficient**。部分具体（只说 pick，不说 alternative）被判 FAIL。

GOOD / BAD 两种形态见上面 Rule 3 的同一对范例——具体性与 triage 是同一条纪律的两面。

### Rule 5 - Patch-style Rewrite 禁令（Gate 11）

**规则**：V2 写作者 **不允许** 通过在 V1 的 bullet 之间插入散文 filler 句来凑 prose 比例。任何 section 若 `bullet_line_count > prose_line_count` 即 Gate 11 FAIL。合规方式是 **结构性合并**：把若干 bullets 融入散文段落。Patch 式改写是最常见的 gaming 模式，机械门单独挂一条用于阻断。

### Mechanical Quality Gates（追加到 Appendix A 的 Gates 1-6）

下述 gates 由 `scripts/audit_mlsd_prose_quality.py` 执行：

- **Gate 7 - Prose ratio ≥ 30%**：`non-bullet-non-table lines / total non-empty lines ≥ 0.3`，按整份文档计。
- **Gate 8 - Section Contract**：每个 §1-§6 的 opening 散文 ≥ 60 字符（首行非 `-` / `#` / `|` / `>`）；在下一个 `##` 前需有 closing 桥接句。
- **Gate 9 - Triage signal presence**：任何含 `/\\b(选|使用|用|pick)\\b/` 的行后 1000 字符内必须出现 `/\\b(因为|because)\\b/`。0 违规。
- **Gate 11 - Patch-ban**：逐 section，`prose_lines ≥ bullet_lines`。0 违规。

Gate 7/8/9/11 是 **必要非充分** 条件。regex 能抓 filler 密度、抓不出 filler 质量。真正的质量裁判是 Gate 10（LLM-judge，下节）。

### Gate 10 - LLM-as-Judge Rubric（FROZEN）

给定同一 section 的 V1 与 V2 两份文本，judge 在三个维度各打 0-10 整数分：

- **Readability（可读性）**：文本是否作为一条 coherent narrative 流动？senior interviewer 若听到有人口头讲出这段，能否无需回头就跟上？
- **Triage completeness（triage 完整度）**：对每个 tech choice，读者能否仅从 prose（而非 tradeoff 表格）推出 4 triage 要素（pick / reason / alternative / switch-trigger）？
- **Information density（信息密度）**：每句话是否都在承载（教某件事、证明某件事、连接某件事）？还是存在 "值得注意"、"具体来说" 这类没下文的 filler？

**Pass condition**：V2 必须 **严格大于** V1 在三个维度的得分。**平分视作 FAIL**。裁判返回 JSON：
`{"readability": {"v1": N, "v2": N}, "triage": {"v1": N, "v2": N}, "density": {"v1": N, "v2": N}, "verdict": "PASS|FAIL", "notes": "..."}`。

实现：`scripts/llm_judge_mlsd.py` 通过 `claude -p --model claude-sonnet-4-6 --system-prompt <rubric> --setting-sources user --tools ""` subprocess（同 `rewrite_nodes_to_cn.py` 调用模式）调用。V2 seed 脚本（T-P0-515 / T-P0-516）在 regex 审计通过后必须再跑 LLM-judge，FAIL 则 abort。

### `--report-only` 逃生舱

`scripts/audit_mlsd_prose_quality.py` 支持 `--report-only` 标志：打印违规清单但无论如何退出 0。生产 seed 路径使用默认 strict 模式；迭代 / 人肉调试路径使用 `--report-only`。默认 strict。
"""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def backup_db() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(DB_PATH, dst)
    print(f"[INFO] DB backup -> {dst.name}")
    return dst


REQUIRED_MARKERS = (
    "## Appendix A.1 - Writing Discipline",
    "### Callout 约定 (FROZEN)",
    "> **GOOD**:",
    "> **BAD**:",
    "### Rule 1 - Section Contract",
    "### Rule 2 - Acronym Expansion",
    "### Rule 3 - Tech-choice Triage",
    "### Rule 4 - Specificity Discipline",
    "### Rule 5 - Patch-style Rewrite",
    "Gate 7 - Prose ratio",
    "Gate 8 - Section Contract",
    "Gate 9 - Triage signal presence",
    "Gate 11 - Patch-ban",
    "### Gate 10 - LLM-as-Judge Rubric",
    "`--report-only`",
)


def validate(desc: str) -> list[str]:
    problems: list[str] = []
    n = len(desc)
    if n < LEN_MIN or n > LEN_MAX:
        problems.append(f"length {n} outside window [{LEN_MIN}, {LEN_MAX}]")
    if not desc.startswith("# ML System Design Framework"):
        problems.append("description does not start with expected title")
    for marker in REQUIRED_MARKERS:
        if marker not in desc:
            problems.append(f"missing marker: {marker!r}")
    return problems


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

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
            print(f"[FAIL] framework_node id={NODE_ID} has NULL description; "
                  f"run seed_node_18_mlsd_framework_20260418.py first")
            return 1

        has_appendix = APPENDIX_MARKER in old_desc
        has_playbook_patch = PLAYBOOK_NEW in old_desc
        needs_playbook_patch = PLAYBOOK_OLD in old_desc and not has_playbook_patch

        if has_appendix and not needs_playbook_patch:
            print(f"[SKIP] Node {NODE_ID} already contains '{APPENDIX_MARKER}' "
                  f"and playbook patch applied")
            print(f"[PASS] Current length = {len(old_desc)} chars")
            return 0

        patched_body = old_desc
        if needs_playbook_patch:
            patched_body = patched_body.replace(PLAYBOOK_OLD, PLAYBOOK_NEW, 1)
            print(f"[INFO] Applied playbook Gate-9 patch ({len(PLAYBOOK_OLD)} -> "
                  f"{len(PLAYBOOK_NEW)} chars on that line)")

        if has_appendix:
            new_desc = patched_body
        else:
            new_desc = patched_body.rstrip() + APPENDIX_A1

        problems = validate(new_desc)
        if problems:
            print("[FAIL] Composite content failed self-validation:")
            for p in problems:
                print(f"  - {p}")
            return 1

        print(f"[INFO] Char length: {len(old_desc)} -> {len(new_desc)}")
        print(f"[INFO] Old hash: {sha256(old_desc)[:12]}")
        print(f"[INFO] New hash: {sha256(new_desc)[:12]}")

        backup_db()

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
            print("[FAIL] Post-update validation failed:")
            for p in post:
                print(f"  - {p}")
            return 1

        hist_rows = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes_description_history WHERE node_id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        print(f"[PASS] Node {NODE_ID} updated; length now {len(check)} chars; "
              f"history rows for this node = {hist_rows}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
