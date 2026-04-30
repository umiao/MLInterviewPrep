"""Seed Meta AI-Native Domain Breadth -- 5 Talking Points prep doc (T-P0-668).

Companion to scripts/seed_meta_ai_native_prep.py (golden landing) and
scripts/seed_meta_ainative_codepad_prompt.py (code-pad playbook). This doc
curates 5 concrete harness/portfolio sells the user can drop into the Meta
AI-Native onsite (2026-05-01) to demonstrate domain breadth.

Each point: 30-sec Chinese spoken pitch + English kill-line + concrete file
path for live reference + "when to drop this" contextual cue.

Idempotency: sentinel <!-- META_AINATIVE_BREADTH_20260430 --> gates the write.
Second run on byte-identical content = 0 writes.

Style: Chinese narration + English technical terms (full expansion on first
use), per content_style memory. No emoji (project invariant).
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_AINATIVE_BREADTH_20260430 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta] AI-Native Domain Breadth -- 5 Talking Points"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

CONTENT = SENTINEL + r'''
# Meta AI-Native Domain Breadth -- 5 Talking Points

> 配套 [Meta] AI-Native Onsite Prep (2026-05-01) golden 文档 + Code-Pad LLM
> Prompt + 3-Step Playbook. 本篇专门解决一件事:
> **当 interviewer 在 deep-dive / behavioral / architecture chat 中问到
> "what's a concrete example of you using AI in your own workflow?"**, 你
> 不要 wander, 直接从下面 5 个 talking points 里挑 1 个最贴当前 context 的
> 30 秒讲完, 留 file path 给他随时挖.

每个 point 模板:
- **30-sec spoken pitch (中文 narration + 英文术语)** -- 嘴上讲的版本
- **English kill-line** -- 一句话让 interviewer 记住你的 framing
- **Concrete file path / artifact** -- 如果他想看证据, 你立刻能 navigate 到
- **When to drop this** -- 具体什么 context 信号触发用哪一条

---

## §1 Talking Point 1 -- 3-Layer Harness Model (Hooks / Agents / Skills)

### 30-sec spoken pitch

> "我自己 daily-driver 的 Claude Code 工作站不是 stock 的 -- 我在它上面建了
> 一套 3-layer responsibility model. **Policy Layer** 是 12 个 hook scripts
> (block_dangerous, secret_guard, invariant3_guard 等), 在 PreToolUse / Stop
> 上拦危险 shell command, 拦 secret leak, 验 invariant. **Execution Layer**
> 是 4 个 subagent definition (reviewer, refactor-advisor, test-runner,
> input-reviewer), 跑 read-only research 和 cross-project review.
> **Interface Layer** 是 9 个 user-facing skill (e.g. /sanity-check, /review,
> /e2e-test, /dashboard), 把高频 workflow 封成 slash command. 这套结构让我
> 在 autonomous mode 下 run 几百场 session 而不出错."

### English kill-line

> "I treat Claude Code as a kernel I own, not a tool I use -- hooks are my
> policy layer, agents are execution, skills are interface. The harness
> survives 800+ autonomous sessions because every dangerous path has a
> hook gate before it can fire."

### Concrete file path / artifact

- Root **CLAUDE.md** § "Three-Layer Responsibility Model" (workspace root,
  `Gen_AI_Proj/CLAUDE.md`)
- `MLInterviewPrep/.claude/hooks/` -- 21 hook files: block_dangerous.py,
  secret_guard.py, **invariant3_guard.py** (T-P0-660 + T-P0-660b), tasks_md_guard.py,
  commit_msg_guard.py, file_watch_warn.py, yaml_validate.py, plan_mode_hook.py,
  session_context.py, archive_check.py, lint_check.py, test_check.py,
  task_dedup_check.py, etc.
- `MLInterviewPrep/.claude/agents/` -- 4 agent definitions: reviewer.md,
  refactor-advisor.md, test-runner.md, input-reviewer.md
- `MLInterviewPrep/.claude/skills/` -- 9 skill folders incl. `dashboard/`
  (Surface Identification protocol), `sanity-check/`, `review/`, `e2e-test/`

### When to drop this

- Interviewer asks "how do you scale AI usage beyond just 'I use Copilot'?"
- Interviewer asks about safety / reliability / reproducibility of AI agents
- Behavioral question: "tell me about a time you built infra around a tool
  to make it production-grade"
- Onsite system-design pitch wants a concrete example of layered defense
  (hook = pre-condition gate; skill = abstracted interface)

---

## §2 Talking Point 2 -- Invariant 3 (DB rows must have idempotent seed scripts)

### 30-sec spoken pitch

> "我项目最严的 invariant 是 **Invariant 3**: 每一行 production DB content
> (company_documents / framework_nodes / problems / interview_events) 都必须有
> 一个 git-tracked, idempotent Python seed script 作为 source of truth. Ad-hoc
> SQL or manual DB edits 是禁止的 -- DB 是 seed scripts 的 regenerable
> projection, 不是 source of truth. 这个规则是用 hook (`invariant3_guard.py`)
> 强制的: 任何 raw SQL write from `scripts/migrations/*` to `data/*.db` 会
> 直接 block, 而且我把它扩展 (T-P0-660b) 到 catch schedule-shaped prose
> writes -- ISO-8601 timestamp + interviewer-name pattern 出现在
> company_documents.content 也会被 block, 因为那应该写到 interview_events
> 表. 这就是为什么我 600+ seed scripts 都长得一样."

### English kill-line

> "DB rows without a git-tracked seed script are forbidden in this codebase --
> a hook blocks ad-hoc SQL writes, and a second hook blocks
> schedule-shaped prose from leaking into the wrong table. Reproducibility
> is enforced, not requested."

### Concrete file path / artifact

- `MLInterviewPrep/CLAUDE.md` § "Invariants" (3rd bullet) + § "Surface
  Identification" routing rules table
- `MLInterviewPrep/.claude/hooks/invariant3_guard.py` -- the lint hook
  (T-P0-660 + T-P0-660b extension); ~30 KB Python, regex on raw SQL +
  ISO-8601 + interviewer-name pattern
- `MLInterviewPrep/scripts/seed_*.py` -- ~600 idempotent seed scripts
  following sentinel-based UPSERT pattern, e.g.
  `seed_meta_ai_native_prep.py`, `seed_meta_ainative_codepad_prompt.py`
- `MLInterviewPrep/logs/2026-04-30_pinterest_root_cause.md` -- the post-mortem
  documenting the failure mode that motivated T-P0-660b

### When to drop this

- Interviewer asks about how you handle data correctness / state
  management with AI agents that write to a database
- Interviewer asks about "what's a hard rule you enforce in your team?"
- Discussion about reproducibility, replayability, disaster recovery
- Architecture chat about source-of-truth boundaries

---

## §3 Talking Point 3 -- 800+ Autonomous Sessions + Bootstrap Bug Fix (T-P1-257)

### 30-sec spoken pitch

> "我有一个 orchestrator -- `scripts/autonomous_run.sh` -- 在 background
> 跑 Claude Code 的 autonomous mode. 每个 session 抓一个最高优先级 unblocked
> task, 跑完 update PROGRESS.md + tasks.db + session_state.json 然后退出, 下一个
> session fresh context 进来继续. 到现在跑了 800+ session (PROGRESS.md +
> archive/progress_log.md 加起来 841 个 session entry). 但中间踩过一个 silent-fail
> bug -- T-P1-257: orchestrator 启动时要 reset stale `all_done=true` flag
> (上一轮 drained queue 但同时 task_db 又加了新 task), 我用了 `python -c`
> inline 读 session_state.json, 但传给 Python 的 path 是 MSYS-bash 的
> `/c/Users/...` 形式, Windows Python 读不出来, silent skip 这个 reset, 结果
> 整个 orchestrator 立刻退出. Fix 是把 python 调用 `cd` 到 WORK_DIR, 让 Python
> 看到 relative path 而不是 MSYS path. 教训: cross-shell path 永远要 verify."

### English kill-line

> "Autonomous mode runs at 800+ session scale. The bug that almost killed
> it was an MSYS-bash path silently passed to Windows Python -- `/c/...`
> reads as nonexistent, the orchestrator skipped its all_done reset and
> exited every loop. cd-into-WORK_DIR-then-python is the durable fix."

### Concrete file path / artifact

- `Gen_AI_Proj/scripts/autonomous_run.sh` -- orchestrator script; T-P1-257
  fix is at lines 55-78 (the `cd "$WORK_DIR" && python -c ...` block)
- `MLInterviewPrep/PROGRESS.md` -- 44 most-recent session entries
  (running log)
- `MLInterviewPrep/archive/progress_log.md` -- 797 archived session
  entries (chronological)
- Total session count = 797 + 44 = **841 autonomous sessions** as of
  2026-04-30
- `MLInterviewPrep/docs/reports/t_p1_256_session_state_block_diagnosis.md`
  -- the diagnosis report for the related T-P1-256 cluster
- Comment trail in `autonomous_run.sh` lines 55-63 documents the failure
  mode + fix rationale

### When to drop this

- Interviewer asks about long-running AI agents / background jobs /
  agent reliability at scale
- Behavioral question: "tell me about a hard-to-find bug you debugged"
- Discussion about cross-platform / cross-shell pitfalls (Windows + bash
  interaction, MSYS path translation)
- Discussion about state management between independent agent sessions

---

## §4 Talking Point 4 -- 28-Topic ML Fundamentals Knowledge Graph (Tiered Cleanup)

### 30-sec spoken pitch

> "我的 ML interview prep 里有一个 28-topic ML fundamentals knowledge base
> (`data/ml_fundamentals_inventory.yaml`), source 是 Discord forum 的
> high-frequency interview question dump 加我自己加的 large-scale feature
> selection writeup. 28 topics 跨 7 个 category: classical ML 5 个,
> evaluation/data 2 个, feature engineering selection 1 个, unsupervised 2 个,
> deep learning training 5 个, attention/transformer 6 个, LLM/stats 7 个.
> 每个 topic 我打两个 orthogonal 标签: **tier** (T1/T2/T3, cleanup workload --
> T1 minor polish 14 个, T2 moderate reformat 7 个, T3 deep expansion 7 个) 和
> **interview_freq** (high/mid/low, asked frequency). Tier 决定我下次抽时间
> 改的优先级, freq 决定面试前一天复习哪些. 这套 schema 让我能 plan 出 'I'll
> spend Saturday on the 7 T3 LLM/stats topics' 而不是漫无目的复习."

### English kill-line

> "Knowledge bases without a tier system die from over-coverage. Mine has
> 28 topics, two orthogonal axes (cleanup_tier x interview_frequency), and
> a schema header that makes Saturday's prep deterministic instead of
> emotional."

### Concrete file path / artifact

- `MLInterviewPrep/data/ml_fundamentals_inventory.yaml` -- 486 lines, 28
  items, schema header lines 9-29
- Category breakdown: classical_ml (5) / eval_data (2) /
  feature_engineering_selection (1) / unsupervised (2) / dl_training (5) /
  attention_transformer (6) / llm_stats (7)
- Tier distribution: T1 = 14 items, T2 = 7 items, T3 = 7 items
- Linked task IDs: T-MLF-06a/b/c/d, T-P1-588 (the 28th item, large-scale
  feature selection writeup)
- Each item has: `id`, `slug`, `category`, `tier`, `interview_freq`,
  `line_range`, `title_zh`, `title_en`, `acronyms_to_expand`,
  `cleanup_notes`

### When to drop this

- Interviewer asks "how do you stay sharp on ML fundamentals?"
- ML breadth probing -- pick a specific topic from this list and dive in
  (e.g. KL = Kullback-Leibler divergence, Bias-Variance Tradeoff,
  Multi-Head Attention)
- Discussion about curriculum design / spaced-repetition-like systems
- "How do you decide what to study?" -- answer is **tier x frequency**, not
  vibes

---

## §5 Talking Point 5 -- LLM-as-Judge Production Deployment ($500/day vs Human Annotation)

### 30-sec spoken pitch

> "在前公司 (2023 GenAI Exploration Initiative), 我用 1 周 feasibility math
> 把 leadership 想要的 agentic search 路径 disqualify 掉 -- LLM 接不到
> indexing pipeline, 读不到 live inventory, throughput 在 40K-peak surface
> 上只能跑到 tens of QPS, latency prohibitive. 数字直接 kill 那条路, 我用省下来
> 的 budget 转去做 **LLM-as-Judge** for relevance labeling. 产线上每天产
> **18K labels at $500 total**, 对比 human annotation **$0.30-0.80 per label**
> 就是 vendor 报价的 1/10 到 1/30. 关键不是技术, 是 **feasibility-first scoping
> 把 sunk cost 政治成本压到最小**. 后来这套 LLM-as-Judge 从 relevance team
> scale 到 ads team 再到几个其他 group, 成了 org-wide measurement
> infrastructure -- 1.5% GMB lift."

### English kill-line

> "Vague AI mandates die from sunk cost. The cheapest move nobody assigns
> is the one-week feasibility kill -- it killed agentic search, freed
> budget for LLM-as-Judge, which scaled into org-wide measurement infra
> at $500/day for 18K daily labels vs $0.30-0.80/label human pricing."

### Concrete file path / artifact

- `MLInterviewPrep/docs/bq_behavioral_examples.json` -- BLOG-03 ("Cross-Org
  Boundary Defense via LLM Relevance Pipeline", source: blog_proj
  Teamwork Q3) and EX-14 ("LLM Exploration -- Killing the Agentic Mandate
  with One Week of ROI Math", source_project: 2023 GenAI Exploration
  Initiative)
- BLOG-03 cross-references INN-4 with the literal cost line: "Built LLM
  judgment pipeline producing 18K labels/day at $500 vs $0.30-0.80/label
  for human annotation"
- EX-14 result line: pipeline became production measurement infrastructure
  for relevance team, then ads, then several other groups; GMB
  improvement + user engagement lift; **1.5% GMB lift** (cited in BLOG-03
  IMP-4 cross-reference)
- Principle tags on BLOG-03: collaboration, influence_without_authority,
  earn_trust, innovation, execution, ownership, customer_obsession
- Principle tags on EX-14: adaptability, ownership, innovation,
  feasibility_first, no_precedent_scoping, ROI_math_disqualification,
  infrastructure_over_demo

### When to drop this

- Behavioral question: "tell me about a time you used AI to drive
  business impact"
- "How do you decide what to build with LLMs?" -- answer is feasibility
  math first, novelty last
- Cost discipline / budget conversations -- $500/day for 18K labels is
  the kill-line number
- Cross-org boundary / collaboration questions (BLOG-03 angle: held
  relevance-org boundary while still giving ads team interpretable
  signals)
- Innovation questions where they want infrastructure-over-demo, not
  hackathon-style novelty

---

## §6 离场前 60 秒 cheat sheet (5 个 trigger -> talking-point map)

| Interviewer signal                                   | Drop this point     |
|------------------------------------------------------|---------------------|
| "How do you scale AI usage / make it safe?"          | §1 (3-layer harness)|
| "How do you handle data correctness with agents?"    | §2 (Invariant 3)    |
| "Tell me about a hard bug / long-running agents"     | §3 (T-P1-257 + 841) |
| "How do you stay sharp on ML fundamentals / breadth?"| §4 (28-topic KG)    |
| "Tell me about a time you used AI for impact / cost" | §5 (LLM-as-Judge)   |

**Common trap**: 把 5 个 talking points 一口气讲完. **Don't**. interviewer
问的是一个具体 context, 你只挑 1 个最贴的, 30 秒讲完, 然后停下来等他追问.
追问到第 2 个, 再换一条.

**Prep ritual (面试前 5 分钟)**: 把这 5 条用嘴 narrate 一遍 -- 不是看 doc,
是 actually speak. 卡壳的那条说明今天还没消化, 改去 review 那条的 file path.

---

> **核心 mental model**: Domain breadth 不是 "I know many things", 而是
> "I have artifacts I can navigate to in 5 seconds when prompted". 上面 5
> 条每条都给了具体 file path, 这就是 portfolio depth 的 evidence -- 不是
> claim, 是 navigatable artifact.
'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## §1 Talking Point 1 -- 3-Layer Harness Model",
        "## §2 Talking Point 2 -- Invariant 3",
        "## §3 Talking Point 3 -- 800+ Autonomous Sessions",
        "## §4 Talking Point 4 -- 28-Topic ML Fundamentals",
        "## §5 Talking Point 5 -- LLM-as-Judge Production Deployment",
        "## §6 离场前 60 秒 cheat sheet",
        "### 30-sec spoken pitch",
        "### English kill-line",
        "### Concrete file path / artifact",
        "### When to drop this",
        "T-P1-257",
        "invariant3_guard.py",
        "ml_fundamentals_inventory.yaml",
        "BLOG-03",
        "EX-14",
        "$500",
        "18K labels",
        "841",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    emoji_ranges = (
        (0x1F300, 0x1F6FF),
        (0x1F900, 0x1F9FF),
        (0x2600, 0x27BF),
        (0x1F000, 0x1F2FF),
    )
    for ch in content:
        cp = ord(ch)
        for lo, hi in emoji_ranges:
            if lo <= cp <= hi:
                raise RuntimeError(
                    f"emoji char detected at codepoint U+{cp:04X}: {ch!r}"
                )
    if not (5000 <= len(content) <= 14000):
        raise RuntimeError(f"content length {len(content)} outside 5000-14000")


def main() -> int:
    """Upsert the Meta AI-Native Domain Breadth doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        cur = conn.execute(
            "SELECT id, content FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        )
        existing = cur.fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(CONTENT)

        if existing is None:
            conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                "content_hash, is_golden, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    new_hash,
                    0,
                    now,
                    now,
                ),
            )
            conn.commit()
            new_id = conn.execute(
                "SELECT id FROM company_documents "
                "WHERE company_id = ? AND title = ?",
                (COMPANY_ID, DOC_TITLE),
            ).fetchone()[0]
            print(
                f"[INSERT] id={new_id} len={len(CONTENT)} "
                f"hash={new_hash[:12]}..."
            )
        else:
            existing_id, existing_content = existing
            if SENTINEL in existing_content and existing_content == CONTENT:
                print(
                    f"[UNCHANGED] id={existing_id} sentinel + content "
                    f"match; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, updated_at = ? "
                    "WHERE id = ?",
                    (CONTENT, new_hash, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(CONTENT)} delta={len(CONTENT)-old_len:+d}"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
