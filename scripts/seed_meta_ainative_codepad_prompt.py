"""Seed Meta Code-Pad LLM Prompt + 3-Step Playbook prep doc (T-P0-667 / T-P0-678).

Companion to scripts/seed_meta_ai_native_prep.py (slim hub). This sub-doc is
the deep-dive for the AI-Native Coding rounds (11:00 / 13:00 on 2026-05-01)
opened via the hub's cd://86 drawer link.

T-P0-678 rewrite (per review attachment):
- §1 30-sec opener replaced with §五 verbatim text ('drive-myself-first'
  framing instead of 'before I touch the AI').
- §2 KILLED the 30+ line PHASE 1-4 system prompt; replaced with the
  canonical 1-sentence English prompt (Version A) plus a shorter Version B
  alt for compressed-time scenarios.
- §3 Step 1 fixed: clarifying questions go FROM YOU TO THE INTERVIEWER,
  not AI-asks-you (the old PHASE-1 wording had the direction backwards).
- §4 LRU OrderedDict critique replaced with 'first ask interviewer which
  implementation they want -- that's the senior move.'
- New §6 §六 6-pack: continuous narration, AI-vs-your-direction handling,
  45-min time allocation 3/3/10/5/5/5, manual trace as review step,
  fallback when AI is stuck, prompt transparency.
- Length budget tightened to <8000 chars (target 7000-7900).

Idempotency: sentinel <!-- META_CODEPAD_PROMPT_20260501 --> gates the write
(rev'd from _20260430 because the rewrite is a structural change, not a
typo fix; a fresh sentinel forces the upsert path to update existing rows
instead of being short-circuited by content-hash equality on the old
sentinel).

Style: Chinese narration + English term first-occurrence expansion. No
emoji. Section headings keep English where they read as headings, mixed
zh/en where they don't.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_CODEPAD_PROMPT_20260501 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta] Code-Pad LLM Prompt + 3-Step Playbook"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

# Verbatim text fragments locked by validation (must appear byte-identical).
VERSION_A_PROMPT = (
    "Don't write code until I give you the acceptance criteria and edge "
    "cases; after you draft, surface every assumption you made and every "
    "edge case you didn't handle as a gap list for me to decide on rather "
    "than silently fixing them, and flag any stdlib API you're not 100% "
    "sure exists."
)
VERSION_B_PROMPT = (
    "Hold off on code until I lay out AC + edges; after the draft, list "
    "every assumption, unhandled edge case, and uncertain stdlib API as "
    "a gap list for me to call rather than silently fixing them."
)
OPENER_30SEC = (
    "Before I bring in the AI, I'd like to drive this myself first -- "
    "restate, lay out AC + edges, sketch approach. Then I'll use AI to "
    "draft and pressure-test edges, but review line-by-line before we "
    "run. Does that work, or would you prefer I lean on AI sooner?"
)

CONTENT = SENTINEL + r'''
# Meta Code-Pad LLM Prompt + 3-Step Playbook

> 配套 [Meta] AI-Native Onsite Prep (2026-05-01) hub. 解决一件事: interviewer
> 说 "feel free to use AI in your code pad", 你打开 LLM 第一秒**该贴什么
> prompt**, 怎么把控 *driver* 角色. 配套 §T4-bp (cd://89) 给 7-block 结构.

---

## §1 The 30-second Spoken Opener

Interviewer 说 "you can use AI" -- **不要立刻打字**, 先讲这段 (30 秒一口气):

> "''' + OPENER_30SEC + r'''"

**做对 4 件事**:
- "drive this myself first" 锚定**你**是 driver, AI 是工具 (signal #1).
- restate / AC + edges / sketch approach 三个明确动作 = 结构化 ownership (#2).
- "pressure-test edges" 把 AI 框成 edge-tester, 不是 code generator (#3).
- 结尾给 interviewer 一个 option, 不是 ask permission (#4).

禁忌: 不要说 "I'll just ask AI" -- **lead with structure 不是 lead with tool**.

> 深度 design rationale (4 bullets 拆解 + 反例) 见 cd://89 §7.

---

## §2 The Code-Pad LLM Prompt (canonical 1-sentence)

第一条 user message 就贴 1 句. 不需要 30 行 system prompt -- 1 句覆盖
acceptance criteria-first / gap-list / no-API-hallucination 三件事.

### Version A (recommended)

```
''' + VERSION_A_PROMPT + r'''
```

锁了三件: (a) "Don't write code until AC + edges" = *I drive, AI follows*;
(b) "gap list for me to decide" = AI 是 gap reporter, 不让 silent fix; (c)
"flag any stdlib API you're not 100% sure exists" = 直接 catch hallucination.

### Version B (shorter alt -- 时间紧贴这版)

```
''' + VERSION_B_PROMPT + r'''
```

B 比 A 短 30%, 保留 3 个核心 directive, 语义等价. 第二轮 prompt / 迭代时
默认用 B.

> 不要再贴旧 doc 里 "PHASE 1-4 system prompt" (30+ 行的). 临场没时间打,
> 而且 PHASE 1 让 AI 问你 = direction backwards: clarification 必须**你
> 问 interviewer**, AI 不参与那步.

> Version C ("junior engineer" framing) 不推荐 + 详细解释见 cd://89 §8.

---

## §3 The 3-Step Interactive Playbook

Prompt 是 *what AI does*, playbook 是 *what you do around AI*.

### Step 1 -- Clarify (你问 interviewer, **不是 AI 问你**)

拿到题先 restate, 然后**向 interviewer** 问 1-3 个澄清, 答案到手才 type 给 AI.

口头问 interviewer:
- input scale: n 范围 / 值域 / 重复 / 负数 / 空?
- output format: 单值 / list / sort / stable?
- 错误输入: None / raise / silent skip?
- 性能 budget: in-place / memory cap / latency 上限?

为什么不是问 AI: senior signal 看的是 *你心里对题目有形状*. 让 AI 替你问 =
失分 (interviewer 看到的是 stalling). AI 替你假设也失分 (review 时 miss).

### Step 2 -- Spec AC + Edges TO the LLM

clarification 答案到手, 把 AC + edge cases **手动列成 bullet list** 喂 AI,
配合 §2 Version A 一起贴.

口头同步告诉 interviewer 你在写什么:
1. Functional: input X 给 output Y, 顺序 / shape 要求.
2. Edge cases: empty / single / max-size / duplicates / negative / overflow /
   None / unicode -- 挑相关 5-6 条 (5-8 条是甜蜜区, 不要 20 条).
3. Complexity bound: "O(n log n) or better".
4. Forbidden: "no external libs", "no global state".

### Step 3 -- Review LLM Output as a Junior PR

AI 给 draft 后**不要立刻 run**. 先 walk through, 像 review junior PR. 嘴上
narrate, 主动指出 1-2 个 gap / bug.

Review checklist:
- Spec drift: AI 实现的是 Step 2 的 AC, 还是偷加假设?
- Edge coverage: Step 2 列的 edge case 都 handle 了吗?
- Complexity claim: docstring 说 O(n), 实际是不是?
- API hallucination: stdlib 函数名真的存在吗?
- Off-by-one + hidden state (mutable default arg / 全局变量).

Trap: 看到代码 syntactically OK 就直接 run = 没 review 信号.

---

## §4 Worked Example A -- Coding (LRU Cache)

题面: "Implement an LRU cache with `get(key)` and `put(key, value)` both O(1)."

**Step 1 -- Clarify (问 interviewer 30 秒)**:
- capacity 构造时给定还是 dynamic?
- get miss return -1 还是 None 还是 raise?
- put 同 key 算 access 吗?
- thread-safe?
- **关键 senior 动作**: ask interviewer first which implementation they
  want -- "do you want me to roll my own doubly-linked list, or is
  `collections.OrderedDict` acceptable? I'm fine either way -- depends
  what signal you're looking for." 把"实现选型"权交回面试官, 不默认偷
  懒也不默认炫技, **让 interviewer 表态后再写** -- that's the senior move.

> 假设 interviewer 答: capacity 构造时给, miss return -1, 单线程, "show
> me the doubly-linked list -- that's the signal I want".

**Step 2 -- Spec to LLM** (配合 §2 Version A):
```
AC:
1. class LRUCache(capacity: int).
2. get(key) -> int: O(1). miss returns -1.
3. put(key, value): O(1). 同 key update + mark 最近. 超 capacity evict LRU.
4. Edge: capacity = 0 (任何 put 立即 evict, get 永远 -1).
5. Edge: capacity = 1 (put 第二 key 必须 evict 第一).
6. Edge: 重复 put 同 key 不应增加 size.
7. HashMap + doubly-linked list (interviewer asked). 不用 OrderedDict.
8. 单线程.
```

**Step 3 -- Review AI draft**:
- 双链表 prev/next 在 evict 时是否接回 head/tail 哨兵?
- put 同 key 更新时也 move-to-front 了吗?
- capacity = 0 时 AI 通常 silent 接受 = bug.
- grep `OrderedDict` 在输出里, 有就 reject (AC #7 禁了).

---

## §5 Worked Example B -- ML System Design (Search Ranking with LLM)

题面: "Design a search ranking system using LLM in the loop. 300ms p99."

**Step 1 -- Clarify (问 interviewer 3-5 个)**:
- QPS / peak? query 类型? 已有 retrieval (BM25 / two-tower / 混合)?
- LLM 用在 ranking / query rewrite / summarization?
- 评估: NDCG@10 / CTR / 人工? LLM self-hosted vs API? cost budget?

**Step 2 -- Spec to LLM**:
```
1. End-to-end <= 300ms p99 at 1k QPS peak.
2. Three-stage: retrieve 1000 -> rerank 50 -> LLM-rerank 10.
3. LLM: pairwise rerank top-50, cache by hash(query, top50_ids) 1h TTL.
4. Fallback: LLM timeout > 150ms -> non-LLM result.
5. Eval: offline NDCG@10; online A/B CTR + dwell time.
6. Guardrails: PII redact pre-LLM; profanity filter post.
7. Cost cap $X/1k queries; cache hit rate >= 60%.
```

**Step 3 -- Review**: LLM 是阻塞 path 吗 (timeout + fallback)?
50 docs 进 prompt 超 context window? CTR 单 metric 容易 clickbait
污染. 漏项: fairness / freshness / staleness.

---

## §6 §六 临场 Review 6-Pack (做对这 6 件整场就稳)

AI-Native coding 全程做, 不只 Step 3:

1. **Continuous narration**: AI 生成时**不能沉默**. 边等边 narrate "OK 它
   写 X, 我等下 verify Y". 信号 = 全程 engaged, 不是被动等.

2. **AI-vs-your-direction handling**: AI 输出和你心里方向不一致 = **暂停,
   大声讲出你的方向**让 interviewer 听到 disagreement, 然后改 prompt 或手
   写. 反例 = "AI 说这样, 那就这样吧" (失分).

3. **45-min time allocation 3/3/10/5/5/5**: 3 min clarify / 3 min prompt+AC /
   10 min AI draft + narrate / 5 min review / 5 min fix / 5 min buffer + trace.
   共 31 min 主循环, 14 min followups.

4. **Manual trace as review step**: 跑代码**前**, 拿 1-2 个 example 手动 trace
   ("input [3,1,2], i=0..."). Catch off-by-one + 隐含状态比静态读代码强 5x.

5. **Fallback when AI is stuck**: 第二轮 prompt 还不对就 abandon AI 手写,
   narrate "let me work this out manually first". 不 chain prompt 6 轮.
   被 AI 卡 = 失分; 主动切 manual = 加分.

6. **Prompt transparency**: 写 prompt 时**让 interviewer 看到** (大声读 /
   屏幕共享留 prompt 框可见). Prompt 是 driving 信号最直接的物证 --
   interviewer 看不见 = 信号丢了.

---

## §7 离场前 60 秒 cheat sheet

1. 讲了 30-sec opener (§1 verbatim) 吗? 没讲 = typist 模式.
2. 贴了 §2 Version A 或 B 吗? 没贴 = AI 没 contract = 失分.
3. 大声 review 过 1-2 处 AI gap / bug 吗? 没 = 失分.
4. 每个选择讲过 tradeoff 吗? 只讲 happy path = 学生模式.
5. AI 卡住时切了 "let me work this out manually" 吗? 被卡 = 失分.
6. interviewer 看得见你写的 prompt 吗? 看不见 = driving 信号丢了.

---

> **Mental model**: AI 是 junior engineer, 你是 staff. 工作不是写代码, 是
> *driving + reviewing*. Interviewer 评后两件. 配套 §T4-bp (cd://89) 给
> 7-block prompt 结构.
'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload (T-P0-678 contract).

    Locks the rewrite contract:
    - 4-PHASE block must be GONE (PHASE 1 / PHASE 2 / PHASE 3 / PHASE 4
      anywhere = old structure leaked back in).
    - OrderedDict critique must be replaced (no 'force it to rewrite'
      framing); §4 must instead carry the 'ask interviewer which impl'
      senior move.
    - Version A + Version B prompts present verbatim.
    - 30-sec opener present verbatim (§五 alignment with doc 89).
    - §6 6-pack covers all 6 review pillars.
    - Length under 8000 chars (target 7000-7900).
    """
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## §1 The 30-second Spoken Opener",
        "## §2 The Code-Pad LLM Prompt",
        "### Version A",
        "### Version B",
        "## §3 The 3-Step Interactive Playbook",
        "### Step 1 -- Clarify",
        "### Step 2 -- Spec AC + Edges",
        "### Step 3 -- Review LLM Output",
        "## §4 Worked Example A -- Coding (LRU Cache)",
        "## §5 Worked Example B -- ML System Design",
        "## §6 §六 临场 Review 6-Pack",
        "## §7 离场前 60 秒 cheat sheet",
        # 6-pack pillars (T-P0-678 acceptance criteria #5):
        "Continuous narration",
        "AI-vs-your-direction handling",
        "45-min time allocation 3/3/10/5/5/5",
        "Manual trace as review step",
        "Fallback when AI is stuck",
        "Prompt transparency",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")

    # Lock removal of 4-PHASE block (T-P0-678 acceptance #2).
    forbidden_old_phases = (
        "PHASE 1 - CLARIFY",
        "PHASE 2 - SPEC",
        "PHASE 3 - DRAFT",
        "PHASE 4 - SELF-REVIEW",
    )
    for marker in forbidden_old_phases:
        if marker in content:
            raise RuntimeError(
                f"old PHASE 1-4 block leaked back in: {marker!r}; "
                f"must use 1-sentence Version A/B per T-P0-678"
            )

    # Lock removal of 'force AI to rewrite OrderedDict' framing
    # (T-P0-678 acceptance #4). The §4 example must instead carry the
    # 'ask interviewer first' senior move.
    if "force it to rewrite" in content:
        raise RuntimeError(
            "old OrderedDict 'force it to rewrite' framing leaked back in; "
            "must use 'ask interviewer which implementation' per T-P0-678"
        )
    if "ask interviewer" not in content.lower():
        raise RuntimeError(
            "§4 LRU example must carry 'ask interviewer which impl' senior "
            "move per T-P0-678 acceptance criterion #4"
        )

    # Verbatim locks (T-P0-678 acceptance criteria #1, #2):
    if VERSION_A_PROMPT not in content:
        raise RuntimeError("Version A canonical prompt missing verbatim")
    if VERSION_B_PROMPT not in content:
        raise RuntimeError("Version B alt prompt missing verbatim")
    if OPENER_30SEC not in content:
        raise RuntimeError(
            "§1 30-sec opener missing verbatim (must match §五 anchor "
            "shared with doc 89)"
        )

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

    # T-P0-678 acceptance: target <8000 chars (down from 8969 baseline).
    if len(content) >= 8000:
        raise RuntimeError(
            f"content length {len(content)} exceeds 8000 cap "
            f"(T-P0-678 reduction target)"
        )
    if len(content) < 6000:
        raise RuntimeError(
            f"content length {len(content)} suspiciously short "
            f"(<6000); did the body get truncated?"
        )


def main() -> int:
    """Upsert the Meta Code-Pad LLM Prompt + 3-Step Playbook doc (idempotent)."""
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
