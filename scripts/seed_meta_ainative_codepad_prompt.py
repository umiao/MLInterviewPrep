"""Seed Meta Code-Pad LLM Prompt + 3-Step Playbook prep doc (T-P0-667).

Companion to scripts/seed_meta_ai_native_prep.py (golden landing). This doc
distills the AI-Native onsite (2026-05-01) into a copy-pasteable code-pad LLM
system prompt + 3-step interactive playbook (clarify -> spec AC -> review)
with two worked examples and a 30-sec spoken opener.

Idempotency: sentinel <!-- META_CODEPAD_PROMPT_20260430 --> gates the write.
Second run on byte-identical content = 0 writes.

Style: Chinese narration + English technical terms (per content_style memory).
No emoji (project invariant).
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_CODEPAD_PROMPT_20260430 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta] Code-Pad LLM Prompt + 3-Step Playbook"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

CONTENT = SENTINEL + r'''
# Meta Code-Pad LLM Prompt + 3-Step Playbook

> 配套 [Meta] AI-Native Onsite Prep (2026-05-01) golden 文档。本篇专门解决一件事:
> **当 interviewer 说 "feel free to use AI in your code pad"**, 你打开 LLM 的第一秒
> 该贴什么 system prompt, 接下来三步走怎么把控 driver 角色。

---

## §1 The 30-second Spoken Opener

> 当 interviewer 说 "you can use AI in your code pad" -- 不要立刻打字, 先讲这段:

> "Cool. Before I touch the AI, let me make sure I understand the problem first --
> I'll restate the spec, list the inputs / outputs / constraints, and call out the
> edge cases I want to cover. Then I'll prompt the AI with explicit acceptance
> criteria, not just 'make it work'. After it produces a draft, I'll walk you
> through the code line-by-line as if I'm reviewing a junior engineer's PR --
> pointing out anything the AI got wrong before we run it. Sound good?"

**这段做对的事**:
- 先 frame 你是 *driver* 而非 typist (senior signal #1)
- 主动声明 "review AI output" 是流程的一部分 (senior signal #2)
- 给 interviewer 一个明确的 contract, 他后面给反馈也容易 (senior signal #3)

**禁忌**: 不要说 "I'll just ask AI" / "let me see what AI gives me" --
**Lead with structure 而不是 lead with tool**.

---

## §2 The Code-Pad System Prompt (copy-paste ready)

打开 code pad 的 LLM 输入框, **第一条 system / user message** 贴下面整段:

```
You are a senior engineer pair-programming with me in a coding interview.
I will give you a problem spec; do NOT start coding immediately.

PHASE 1 - CLARIFY (you ask, I answer):
  Ask up to 3 clarifying questions about: input shape, scale (n, value range,
  duplicates allowed?), expected output format, error/edge behavior, latency
  or memory constraints. Wait for my answers before moving on.

PHASE 2 - SPEC (I write, you confirm):
  I will dictate explicit acceptance criteria + edge cases (empty, single
  element, max size, negative / overflow, duplicates, whitespace, unicode,
  None/null inputs). You echo them back as a numbered checklist and flag
  any that look ambiguous or contradictory. Do NOT add your own AC.

PHASE 3 - DRAFT (you write, I review):
  Produce a single function with: (a) signature + type hints, (b) 3-line
  docstring stating the contract, (c) the implementation, (d) inline
  comments only where the WHY is non-obvious. State the time / space
  complexity at the top of the docstring. Use idiomatic Python 3.11+.

PHASE 4 - SELF-REVIEW (you flag, I decide):
  Before declaring done, list every assumption your code makes that is
  NOT covered by my AC, and every edge case from PHASE 2 that your code
  does NOT yet handle. Present them as a bulleted gap list. Do NOT
  silently fix them.

Constraints throughout:
- No external libraries unless I explicitly approve.
- Never invent stdlib functions / APIs you are not 100 percent sure exist.
- If you are unsure about Python semantics, say so out loud, do not guess.
- Never produce more than one function per turn unless I ask.
```

> **为什么这么写**: 把 AI 框成 "pair-programming partner that asks first",
> 而不是 "code generator". 4 phases 让你在每个阶段都有 "I drive, AI assists"
> 的明确分工. PHASE 4 是最关键的反 happy-path 设计: 强制 AI 自己列 gap,
> 给你做 review 提供线索.

---

## §3 The 3-Step Interactive Playbook

每道题落地的三步走 (对应上面 prompt 的 PHASE 1-2 / 3 / 4).

### Step 1 - Clarify before coding

**做什么**: 拿到题先复述 (restate), 然后 **向 interviewer** 问 1-3 个澄清问题.
拿到答案后再 type 给 AI.

**为什么**: clarification 是 senior 的可观测信号. interviewer 看到的是 "你心里
对题目是有形状的", 不是 "你急着看 AI 怎么说".

**典型问题 checklist**:
- input scale (n 范围, 值域, 是否允许重复 / 负数 / 空)
- output format (单值 / list / 是否要 sort 是否要 stable)
- 错误输入怎么办 (return None / raise / silent skip)
- 性能 budget (是否要 in-place / 是否有 memory cap)

**Trap**: 把 clarification 直接 dump 给 AI 让它"猜". AI 会假设, 你不知道它假设了什么,
最后 review 时会 miss.

### Step 2 - Spec acceptance criteria + edge cases TO the LLM

**做什么**: clarification 拿到答案后, 把 AC + edge cases **手动列成 bullet list**
喂给 AI (PHASE 2). 不要让 AI 替你 brainstorm AC -- 那是你的活.

**为什么**: 模糊 prompt = 模糊产出. "make it work" / "write a function for X"
这种 prompt 让 AI 自由发挥, 结果就是它选了 happy path, 漏了 edge.

**写 AC 的模板** (口头同步告诉 interviewer):
1. **Functional**: input X 给出 output Y, 顺序 / shape 要求.
2. **Edge cases**: empty, single-element, max-size, duplicates, negative,
   overflow, None, unicode (按题意挑相关的 5-6 条).
3. **Complexity bound**: "must be O(n log n) or better".
4. **Forbidden**: "no external libs", "no global state".

**Trap**: 列 AC 时 over-engineer (列 20 条让 AI 写不动) 或 under-engineer
(只列 happy path). 5-8 条是甜蜜区.

### Step 3 - Review LLM output as a junior PR

**做什么**: AI 给出 draft 后, **不要 run**. 先 walk through 代码, 像在 review junior
工程师的 PR. 嘴上 narrate, 指出 1-2 个 AI bug / 假设漏洞.

**为什么**: 这一步是这场面试的 senior signal #1. interviewer 要看的是
"你能 catch AI 错的能力", happy-path 跑通不算赢.

**Review checklist**:
- **Spec drift**: AI 实现的是不是 PHASE 2 的 AC, 有没有偷加假设?
- **Edge case coverage**: PHASE 2 列的 edge case 它都 handle 了吗?
- **Complexity claim**: docstring 说 O(n), 实际是不是? 有没有藏着 O(n log n)?
- **API hallucination**: 用了 stdlib 函数 / 第三方库, 名字真的存在吗?
- **Off-by-one**: range / slice / 边界条件人脑跑一遍.
- **Hidden state**: 全局变量, 默认参数 mutable default trap 之类.

**Trap**: 看到代码 syntactically OK 就直接 run. interviewer 会失望 --
他看不到 review 信号.

---

## §4 Worked Example A - Coding (LRU Cache)

题面 (假设): "Implement an LRU cache with `get(key)` and `put(key, value)`
both O(1)."

**Step 1 - Clarify (口头, 30 秒)**:
- 容量 capacity 是构造时给定还是 dynamic?
- get miss 应该 return None 还是 raise?
- put 同 key 是 update value 还是 也算一次 access?
- 是否需要 thread-safe?

> 假设 interviewer 答: capacity 构造时给, miss return -1, put 同 key
> update value 并 mark 为最近使用, 单线程.

**Step 2 - Spec to LLM**:
```
AC:
1. class LRUCache(capacity: int).
2. get(key: int) -> int: O(1). miss returns -1.
3. put(key, value): O(1). 同 key update value 且 mark 最近使用.
   超过 capacity 时 evict 最久未使用.
4. Edge: capacity = 0 (任何 put 都立即被 evict, get 永远 -1).
5. Edge: capacity = 1 (put 第二个 key 必须 evict 第一个).
6. Edge: 重复 put 同 key 不应增加 size.
7. No external libs (只能 builtin: dict + 自己写双链表 OR collections.OrderedDict).
8. 单线程, 不需要 lock.
```

**Step 3 - Review AI draft**: 重点看
- LinkedList 节点的 `prev`/`next` 指针在 evict 时是否正确接回?
- `put` 同 key 更新时, 是否也把节点 move-to-front?
- capacity = 0 时, AI 通常会 silently 接受 put 但不 evict -- 这是 bug.
- AI 用了 `OrderedDict` 偷懒? 如果 interviewer 想看链表实现, 让它重写.

**口头讲法 (review 阶段)**:
> "OK let me walk through this. The dict-of-nodes lookup is O(1), good. The
> doubly linked list -- I want to check the eviction case... yes, it disconnects
> the tail correctly. But wait, capacity = 0 -- the AI's put method doesn't
> guard against that. Let me ask the AI to add that check."

---

## §5 Worked Example B - ML System Design (Search Ranking with LLM in Loop)

题面 (假设): "Design a search ranking system that uses an LLM in the loop
to improve relevance. Latency budget 300ms p99."

**Step 1 - Clarify (3-5 个问题)**:
- 流量规模? (QPS, peak 是多少)
- query 类型: 短关键词 vs 自然语言 vs 多语言?
- 已有 retrieval 是 BM25 / two-tower / 混合?
- "LLM in loop" 是指 ranking 还是 query rewrite 还是 result summarization?
- relevance 评估指标: NDCG@10? CTR? 人工评估?
- LLM 是 self-hosted 还是 third-party API? cost budget?

**Step 2 - Spec to LLM (设计意图书)**:
```
AC for the design:
1. End-to-end latency <= 300ms p99, given 1k QPS peak.
2. Two-stage: candidate gen (recall 1000) + rerank (top 50) + LLM-rerank (top 10).
3. LLM job: pairwise rerank top-50 with prompt that includes query + 50 docs' titles.
   Cache LLM output by hash(query, top_50_doc_ids) for 1 hour.
4. Fallback: if LLM timeout > 150ms, return non-LLM rerank result.
5. Eval: offline NDCG@10 on labeled set; online A/B with CTR + dwell time.
6. Guardrails: PII redaction before sending to LLM; profanity filter on output.
7. Cost cap: $X/1k queries; budget for cache hit rate >= 60 percent.
```

**Step 3 - Review AI draft (架构图 / 组件清单)**:
- AI 给的图里 LLM 是不是阻塞 path? (应该有 timeout + fallback)
- cache 层是单层还是分层? hit rate 假设是否合理?
- AI 写的 prompt 有没有 length cap? 50 docs 全 dump 进 prompt 会不会超 context?
- A/B 的 metric 是不是 leading? CTR 容易被 clickbait 污染, 要带 dwell time.
- 没有提 fairness / freshness / staleness -- 这是常见漏项.

**口头讲法**:
> "I notice the AI's design puts the LLM call in the synchronous path with a
> 200ms timeout, but if cache miss + LLM cold-start, we'd blow the 300ms
> budget. I'd add a circuit breaker that returns the non-LLM rerank when
> LLM p99 latency over the past minute exceeds 150ms. Also, the prompt
> includes 50 doc titles -- at avg 80 tokens each that's 4k tokens just for
> docs, plus query + system prompt. We need a length guard or we'll OOM
> the context window on long-tail queries."

---

## §6 离场前 60 秒 cheat sheet (每场结束前自检)

1. 我有没有讲那段 30-sec spoken opener? (没讲 = 进入 typist 模式)
2. 我贴的 system prompt 有 PHASE 1-4 吗? (省略 PHASE 4 = 失去 self-review 信号)
3. 我有没有 **大声 review** 至少 1-2 处 AI 的 gap / bug? (没 review = 失分)
4. 我对每个 design 选择都讲过 tradeoff 吗? (只讲 happy path = 学生模式)
5. 如果 AI 工具卡住, 我有没有立刻切到 "let me work this out manually first"?
   (被 AI 卡住才是失分, 主动切 manual 不是)

---

> **核心 mental model**: AI 是 junior engineer, 你是 staff. 你的工作不是
> 写代码, 是 *driving the implementation* + *reviewing the output*.
> Interviewer 评价的是后两件, 不是前者.
'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## §1 The 30-second Spoken Opener",
        "## §2 The Code-Pad System Prompt",
        "## §3 The 3-Step Interactive Playbook",
        "## §4 Worked Example A - Coding (LRU Cache)",
        "## §5 Worked Example B - ML System Design",
        "## §6 离场前 60 秒 cheat sheet",
        "PHASE 1 - CLARIFY",
        "PHASE 2 - SPEC",
        "PHASE 3 - DRAFT",
        "PHASE 4 - SELF-REVIEW",
        "Step 1 - Clarify before coding",
        "Step 2 - Spec acceptance criteria",
        "Step 3 - Review LLM output",
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
    if not (5000 <= len(content) <= 12000):
        raise RuntimeError(f"content length {len(content)} outside 5000-12000")


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
