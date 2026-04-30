"""Seed Meta AI-Native -- 临场 Prompt 写作 Best Practices doc (T-P0-670 T4-bp / T-P0-679).

Companion to seed_meta_ai_native_prep.py (slim hub), seed_meta_ainative_codepad_prompt.py
(T1: code-pad playbook), seed_meta_ainative_breadth_5pts.py (T2: domain breadth), and
seed_meta_ainative_behavioral_5pack.py (T3: behavioral 5-pack). This doc distills the
'how to write a coding-interview prompt under 临场 pressure' best-practices, harvested
from the user's harness experience driving AI for production work.

Three layers of order:
1. 思考顺序 (Thinking order): clarify problem -> state domain assumptions -> spec AC + edges
   -> ask for skeleton -> review -> ask for edges -> review -> run -> review output.
2. 逻辑顺序 (Logical order in the prompt itself): role/context -> input/output contract ->
   constraints (perf / memory / API) -> edge cases -> 'show your reasoning before code'
   directive -> 'flag any assumption you made' directive.
3. Anti-patterns (Common pitfalls): vague 'make it work' AC; accepting first output blindly;
   not naming the domain; not stating library/version constraints; iterating on output not
   prompt.

Plus verification rituals (LLM output as junior PR, not source of truth) and a worked
side-by-side weak-vs-strong prompt example on the same coding question.

T-P0-679 augmentation (per review attachment §四 / §五 / §六):
- New §7 30-second Spoken Opener with the §五 verbatim text + 4 design bullets
  (drive-myself-first / three explicit actions / AI as edge-pressure-tester /
  end-with-option-not-approval).
- New §8 Canonical 1-sentence English prompt: Version A (recommended), Version B
  (shorter alt), Version C (NOT recommended -- explicit 'junior engineer' framing
  reads as performative role-play; the directives in A/B already imply the same
  senior-junior dynamic without the awkward labelling).
- New §9 §六 临场 Review 6-Pack mirroring cd://86 §6: continuous narration,
  AI-vs-your-direction handling, 45-min time allocation 3/3/10/5/5/5, manual
  trace as review step, fallback when AI is stuck, prompt transparency.

Idempotency: sentinel <!-- META_AINATIVE_PROMPT_BESTPRACTICES_20260501 --> (rev'd
from _20260430 because T-P0-679 is a structural augmentation -- the old sentinel
would short-circuit the upsert via content-hash equality on the smaller body).
Style: Chinese narration + English term expansion on first use. No emoji.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_AINATIVE_PROMPT_BESTPRACTICES_20260501 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta] AI-Native -- 临场 Prompt 写作 Best Practices"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

# Verbatim text fragments (T-P0-679): mirror cd://86's locked anchors so the
# two docs' opener and prompt versions stay byte-identical.
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
VERSION_C_PROMPT = (
    "Treat me as the senior engineer and yourself as the junior. Don't "
    "write code until I give you AC + edges; after your draft, list every "
    "assumption and unhandled edge case as a gap list for me to decide on; "
    "wait for my approval before merge."
)
OPENER_30SEC = (
    "Before I bring in the AI, I'd like to drive this myself first -- "
    "restate, lay out AC + edges, sketch approach. Then I'll use AI to "
    "draft and pressure-test edges, but review line-by-line before we "
    "run. Does that work, or would you prefer I lean on AI sooner?"
)

CONTENT = SENTINEL + r'''
# Meta AI-Native -- 临场 Prompt 写作 Best Practices

> 配套 [Meta] AI-Native Onsite Prep hub. 本篇专门解决 **AI-native coding 面试现场,
> 嘴里讲 high-level idea 之后, 手里要往 LLM 抛 prompt 那一瞬间** 的写法问题.
> 核心命题: **prompt = 一份 PR-quality 的 issue 描述, 不是一句话许愿.**
> 模糊 prompt = 模糊产出 = 失分信号 (interviewer 看到的是你 driving 不动 AI).
>
> 本文 3 层 order: (1) 你脑子里的 thinking order, (2) prompt 字面上的 logical
> order, (3) 必须避开的 anti-patterns. 末尾给一个 worked weak-vs-strong example.

---

## §1 思考顺序 (Thinking order, 你脑子里的 8 步)

下面 8 步是 **你拿到题到 final 答案之间** 的 mental sequence. 不是每步都需要单独
prompt LLM, 但**每步都要意识到自己处在哪一步**. 跳步 = AI 给出"看起来对"的答案
而你接受了没自己验.

1. **Clarify problem (对自己, 不对 LLM)**: 题目读 2 遍, 列出输入输出 + 我**还
   不知道**的: scale? latency budget? 是否单线程? 输入 stream 还是 batch? 重
   复元素允许? 这些**先口头问 interviewer**, 不是丢给 LLM 让它替你假设.
2. **State domain assumptions to LLM (对 LLM, 第一句)**: prompt 第一句要给
   LLM 一个 context, 比如 "this is a streaming-rank model with budget P95<200ms,
   候选集 ~10K, Python 3.11, 不能引第三方库" -- 让 LLM 知道这是个**有 domain
   constraint** 的题, 不是 leetcode warmup.
3. **Spec acceptance criteria + edge cases (对 LLM, 第二句)**: 写明"必须满足
   X / 不能用 Y / edge cases 包括 Z 1-2 条 / 复杂度上限 O(?)". AC 要可观测
   (能跑 test 验证), 不能是"高效"或"clean"这种含糊词.
4. **Ask for skeleton, NOT full implementation**: 第一轮 prompt 让 LLM 给
   **函数签名 + step-by-step plan + 复杂度分析**, 不要立刻给完整代码. 这一步
   你能 catch 它对题意的误解 (在它没写代码之前 cheap fix).
5. **Review skeleton (对自己 + 对 interviewer)**: 把 skeleton 读出声 ("它选
   了 hash map 因为 lookup O(1), 我同意"), interviewer 听到的是你 driving;
   不同意就回去改 prompt 第 2-3 步.
6. **Ask for edges + corner cases (对 LLM, 第二轮)**: skeleton OK 后, 让它列
   **它打算如何处理** 每个 edge case. 这也是在给它写代码前再 cheap-verify 一次.
7. **Run + review output**: 让它写完代码, **运行**, 看 stdout / stderr.
   不要只看代码就接受. Type error / off-by-one / NameError / NoneType 才是真
   测试. 跑完之后再走读一遍代码, 主动指出: "这里 off-by-one 了 / 这里它
   silently swallow exception".
8. **Stop-condition criterion**: 进入 prompt 之前先想好"什么样的输出我就接受
   / 什么样的就 reject 重写". 没 stop criterion = 在 LLM 回答里 wander, 时
   间烧光.

---

## §2 逻辑顺序 (Logical order in the prompt itself, 7 块结构)

每条 prompt 字面上按下面 7 块顺序写, **顺序 matters** (LLM 倾向先看到的 token
对后面 generation 影响大):

1. **Role / context** (1-2 句): "You are a senior Python engineer pairing
   on an interview screen. We have 30 minutes." 不要省 -- LLM 不会自己 infer
   '你想要 production-quality 还是 hacky'.
2. **Input / output contract** (函数签名 + 一两个例子): 用代码块直接给
   `def f(arr: list[int]) -> int:` 和 `>>> f([1,2,3]) == 6`. **不要用自然
   语言描述输入输出** -- 自然语言永远比代码 ambiguous.
3. **Constraints** (perf / memory / API / library): "n <= 1e6, must be O(n
   log n), no numpy, no external APIs, Python 3.11 stdlib only." 缺 constraint
   = LLM 默认上 numpy / pandas / 外部 lib, 你 review 都来不及.
4. **Edge cases** (3-5 条具体的, 不要一句"handle edge cases"): "empty input
   returns 0; all-equal input returns input as-is; negative numbers allowed;
   floats not allowed (assert int)." 列具体 case 让 LLM 在 skeleton 阶段
   预先标注每条怎么处理.
5. **'Show your reasoning before code' directive**: 一句 "first explain in
   3-5 bullets which data structure you'll use and why; only then write
   code". 这是从 thinking-step 4 (skeleton-first) 落到 prompt 字面.
6. **'Flag any assumption you made' directive**: 一句 "if any constraint is
   ambiguous, list your assumption explicitly with the prefix `ASSUMPTION:`
   instead of guessing silently". 这条 catch 80% 的 'silent assumption' bug.
7. **Stop condition / output format**: "produce the function only, no driver
   code, no test harness; if you need to choose between two approaches, give
   only one and state the tradeoff in 1 sentence." 让 LLM 不要 over-generate
   wall-of-text 浪费你 review 时间.

**模板速查 (临场抄)**:

```
You are a senior Python engineer pairing on an interview screen.

Problem: <one-line restatement>.
Signature: def solve(...) -> ...
Examples:
  >>> solve(...) == ...
Constraints: <scale, latency, lib whitelist>.
Edge cases: 1) ... 2) ... 3) ...
Show reasoning before code (3-5 bullets, then implementation).
Flag any assumption with prefix ASSUMPTION:.
Output: function body only, plus a 1-sentence complexity note.
```

---

## §3 Anti-patterns (Common pitfalls, 5 个临场最常踩的)

| Anti-pattern | 翻车样子 | 修复 |
|---|---|---|
| **'Make it work'** | "write a function that handles this" | 改成: "function with signature X, AC list Y, edges Z" |
| **接受第一版输出** | LLM 给完代码立刻 paste, 跑过就交 | 永远走读 + 至少 1 次 prompt 改进 + 跑 stress edge case |
| **不 name domain** | 把 leetcode 当 generic 算法题, 不告诉 LLM 这是"streaming-rank" | prompt 第一句必须 declare domain + budget |
| **不 state lib/version** | LLM 用 pandas / numpy / 不存在的 stdlib 函数 | 显式 whitelist: "Python 3.11 stdlib only, no third-party" |
| **iterate on output 不 iterate on prompt** | 看到 bug 在 LLM 答案上手改, 不回头改 prompt | 发现 bug = 回 prompt 加 constraint 或 edge, 让 LLM 重出 |

**5 个临场判断 'AI 输出该不该接受' 的 yes-no 问题**:

1. 我能不能解释**每一行**为什么这样写? (不能 = reject, 让 LLM 解释或重写)
2. 我有没有**自己心算**复杂度匹配它声称的复杂度? (不匹配 = reject)
3. 它**有没有 silently 假设了什么**我没说的? (有 silent 假设 = reject 改 prompt)
4. 给它一个 edge case 我**预先想好答案**, 跑出来对吗? (不对 = reject)
5. 跑完代码 stdout/stderr **完全干净**? (有 warning / deprecation = 至少
   surface 给 interviewer 听到, 不假装没看见)

---

## §4 Verification rituals (把 LLM 当 junior PR, 不是 source of truth)

用户自己 harness 经验提炼的 4 条 ritual, **每场 AI-native coding 都用**:

1. **Junior-PR mindset**: "AI generates a draft; I am the reviewer who owns
   the merge button." 这句话默念一次, 心态就对了 -- 不是 'AI 帮我做', 是
   'AI 提交 PR, 我 review + merge'. Interviewer 在评你的 reviewer 能力,
   不是评 LLM 的 generation 能力.
2. **Always run + read errors**: 永远 actually 跑代码. 静态读代码漏掉的 bug,
   `python file.py` 一秒抓出来. Stderr 里的 DeprecationWarning / SyntaxWarning
   也要读 -- 它们经常预示真 bug.
3. **Assert on shape before content**: 拿到 LLM 输出先看 **structure**: 函数
   签名对吗? 返回类型对吗? 异常处理在吗? 之后再看**算法 content**. 80% 的
   'AI 看起来对其实错' bug 在 shape 层就能 catch.
4. **Stop-condition before chain**: 不要让自己进入"再 prompt 一次说不定就好
   了"的 dopamine loop. 第一轮失败前就想好: 第二轮 prompt 哪条 constraint
   要加? 加上还失败就**自己手写**, 别 chain prompt 6 轮把时间烧光.

---

## §5 Worked example: 同一题 weak prompt vs strong prompt

**题**: 给一个 stream of (timestamp, key, value) tuples, 实现 'most-recent
value per key in last 5 minutes' query.

### Weak prompt (临场最常见的写法 -- 拿不到分)

```
write a function that returns the most recent value for each key
in the last 5 minutes
```

**LLM 典型回应**: 给一个 `dict[key] = (ts, value)` + 每次 query 全表扫描的
$O(n)$ 实现, 不处理 ts 单调性, 不说 stream 是 bounded 还是 unbounded, 用
了 `from collections import OrderedDict` 但没说为什么, edge case "key 在 5
分钟前出现过现在没了" 没处理. 你 paste 上去跑通 example 就交 -- interviewer
看到的是: 候选人**没 driving 这个 prompt**.

### Strong prompt (按 §2 7-block structure 写)

```
You are a senior Python engineer pairing on a 30-min interview screen.

Problem: maintain a sliding window of (ts, key, value) updates and
answer "most recent value per key seen in the last 300 seconds"
queries efficiently.

Signature:
    class RecentValueStore:
        def update(self, ts: int, key: str, value: int) -> None: ...
        def query(self, ts: int) -> dict[str, int]: ...

Examples:
    >>> s = RecentValueStore()
    >>> s.update(0, "a", 1); s.update(100, "b", 2); s.update(400, "a", 3)
    >>> s.query(450)
    {'a': 3, 'b': 2}      # b at ts=100 still in window (450-100=350 > 300? -> evict)
    # Note: actually b should be evicted since 450-100=350 > 300

Constraints: ts is monotonic non-decreasing, n <= 1e6 updates, query
budget P95 < 1ms, Python 3.11 stdlib only (no third-party).

Edge cases:
  1) empty store -> query returns {}
  2) same key updated twice in window -> latest wins
  3) key updated then expires from window -> dropped from query result
  4) ts boundary: update at ts=t, query at ts=t+300 -> evicted (strict <)

Show reasoning before code (3-5 bullets explaining the data structure
choice and complexity), only then write the implementation.

Flag any assumption with prefix ASSUMPTION: (e.g. about tie-breaking
or empty-key behavior).

Output: class definition only, no driver, no tests; end with one
sentence on amortized complexity.
```

**LLM 典型回应**: 给 `dict[key] -> deque[(ts, value)]` + lazy eviction on
query / 更优是 per-key 单 latest + 每 update O(1) / query 用全 deque 扫
+ ASSUMPTION 标注 'strict less-than 即 ts==t+300 evict'. 你看到 reasoning
bullets 就**预先 catch** 它对 boundary 的处理选择, 跑 example 验证. 这是
interviewer 看到的 driving signal: 候选人 **constraint 给得清, AC 给得
明, edge 列得全, LLM 顺着 prompt 出可 review 的解**.

### 一句话 takeaway

**Weak prompt 看上去 50% 时间省, 实际 review 时间多 3x + miss bug 概率高
5x. Strong prompt 多花 1 分钟写, 省 5 分钟 debug + 拿到 senior signal.**

---

## §6 Onsite 临场 60 秒 cheat sheet (开 prompt 之前默念)

1. **第一句给 domain + budget** (不是 "write a function").
2. **函数签名用代码块给** (不是自然语言描述).
3. **AC + edges 至少 3 条具体的** (不是 "handle edge cases").
4. **要 skeleton 不要 implementation** (第一轮).
5. **要它 flag assumption** (一句 directive 写在 prompt 里).
6. **跑 + review 是必修课** (静态读不算 review).
7. **bug = 回去改 prompt** (不是手改 LLM 输出).

---

## §7 The 30-second Spoken Opener (临场开场词 verbatim)

Interviewer 一说 "feel free to use AI in your code pad" -- **不要立刻打字**,
先讲下面这段 (30 秒一口气, 与 cd://86 §1 落地版本同源):

> "''' + OPENER_30SEC + r'''"

**4 个 design bullets (为什么这段是对的)**:

1. **"drive this myself first" 锚定 you as driver, AI as tool** -- 第一帧
   mental model: 这候选人 own it, 不是 typist. Senior signal #1.
2. **三个明确动作 (restate / AC + edges / sketch approach)** -- structured
   ownership, 不是 vague "I'll think about it"; 三步是后面 §1-§3 的微缩.
3. **AI 框成 edge-pressure-tester, 不是 code-writer** -- "pressure-test
   edges" + "review line-by-line before we run". AI 提交 PR, 你 merge.
4. **End with option, not approval** -- "would you prefer I lean on AI
   sooner?" 给 interviewer 选择权, 但**不是** ask permission. Senior posture
   = open the option, not seek approval.

禁忌: 不要说 "I'll just ask AI" -- **lead with structure 不是 lead with tool**.

---

## §8 Canonical 1-sentence English Prompt (Version A / B / 不推荐 C)

§2 给的是完整 7-block 结构 (role / IO / constraints / edges / reasoning /
assumption / stop). 但**临场没时间打 30 行**. 1 句 prompt 覆盖 (a)
acceptance-criteria-first, (b) gap list, (c) no-API-hallucination 三件事.
配套 cd://86 §2 给同源临场粘贴版本.

### Version A (recommended)

```
''' + VERSION_A_PROMPT + r'''
```

锁了三件:
- (a) "Don't write code until I give you the acceptance criteria and edge
  cases" = *I drive, AI follows*. AI 不替你假设, 等你给 spec.
- (b) "surface ... as a gap list for me to decide on rather than silently
  fixing them" = AI 是 **gap reporter**, 不让 silent fix. 这条是 catch
  spec drift 最便宜的一招.
- (c) "flag any stdlib API you're not 100% sure exists" = 直接 catch
  hallucination. LLM 经常凭空造 stdlib 函数名, 这条让它先承认不确定.

### Version B (shorter alt -- 时间紧贴这版)

```
''' + VERSION_B_PROMPT + r'''
```

B 比 A 短约 30%, 保留 3 个核心 directive (AC-first / gap-list /
uncertain-API), 语义等价. 第二轮 prompt / 时间紧时默认贴 B.

### Version C (NOT recommended -- 看起来 senior 实则 performative)

```
''' + VERSION_C_PROMPT + r'''
```

为什么 C 不推荐: explicit "junior engineer" framing **makes you look
performative**. Senior signal 来自你的 *driving behavior* -- 你怎么 review,
怎么提 gap, 怎么切 manual fallback -- **不是来自 prompt 里把 AI 标成
junior**. Version A / B 的 directives ("don't write code until ...",
"gap list for me to decide on") 已经隐含 senior-junior dynamic, 不需要
在 prompt 里 role-play. Interviewer 看到 C 会读出 "这候选人在演 senior,
不是在干 senior 的活". **砍掉 role label, 留 directive** = 更稳的姿态.

---

## §9 §六 临场 Review 6-Pack (整场 driving 看得见的 6 件事)

§4 verification rituals 是 review LLM output 时的 4 条; 这 6 条是**整场
45 min 全程做** 的, 跨 phase. 与 cd://86 §6 mirror, 此处给 deeper 解释 +
反例 (反例 = 失分长什么样).

1. **Continuous narration**: AI 生成时**不能沉默 wait**. 边等边 narrate
   "OK 它在写 X, 我等下 verify Y". 反例: AI 在跑, 你 30 秒 dead air =
   interviewer 看到 disengaged, 信号丢. 锚点: 全程 engaged, 你脑子在
   ahead-of-AI.
2. **AI-vs-your-direction handling**: AI 输出和你心里方向不一致 = **暂停,
   大声讲出你的方向**让 interviewer 听到 disagreement, 然后改 prompt 或手
   写. 反例: "AI 说这样, 那就这样吧" = 失分 (你 follow AI, 不是 AI follow
   你). 锚点: 你 catch AI 偏离 + 主动 correct, 不是被 AI 拽着走.
3. **45-min time allocation 3/3/10/5/5/5**: 3 min clarify (问 interviewer)
   / 3 min prompt + AC (写给 AI) / 10 min AI draft + you narrate / 5 min
   review (junior PR) / 5 min fix + rerun / 5 min buffer + manual trace.
   共 31 min 主循环, 14 min followup. 反例: prompt 上花 8 min, review 只
   1 min = 失分 (review 是真信号, prompt 只是工具). 锚点: review 时间
   至少和 draft 时间 1:2.
4. **Manual trace as review step**: 跑代码**前**, 拿 1-2 个 example 手动
   trace ("input [3,1,2], i=0, state=...; i=1, state=..."). Catch
   off-by-one + 隐含状态比静态读代码强 5x. 反例: AI 给完代码立刻 run,
   看 example 输出对就接受 = 失分 (你信任 example 不信任 trace). 锚点:
   trace 时讲出每步 state, 主动指出 boundary 隐患.
5. **Fallback when AI is stuck**: 第二轮 prompt 还不对就 abandon AI 手写,
   narrate "let me work this out manually first, then we'll use AI to
   pressure-test". 不 chain prompt 6 轮. 反例: 被 AI 卡 5 轮还在改 prompt
   = 失分 (driving 失败 = 不是 senior). 锚点: 主动切 manual = 加分; 配套
   §1 step 8 stop-condition + §4 ritual #4.
6. **Prompt transparency**: 写 prompt 时**让 interviewer 看到** (大声读 /
   屏幕共享留 prompt 框可见 / 写完口头复述 directive). 反例: 你低头打
   prompt + interviewer 看不见 = signal 丢 (driving 物证消失). 锚点:
   prompt 是 driving 信号最直接的物证, interviewer 看不见 = 没发生.

> **整合**: §1-§4 让你 *写对 prompt + review 对 output*; §六 6-pack 让你
> *整场 driving 看得见*. 两者缺一不可. 临场缺时间砍 §1-§4 任意一条,
> 但 §六 6-pack 6 条 each 30 秒一条, 全场必做.

---

> **Senior framing**: 这套 best practice 不是为了"显得正式". 是因为 Meta
> AI-native coding round 真正要看的是 **你能不能像 staff/PM 那样 driving
> AI**. Driving 的可观测证据 = (a) prompt 里有 contract / constraint /
> edge, (b) 你主动 review 输出指出 gap, (c) 你 iterate on prompt 不是 on
> output. 三条都做到 = 这场过. 缺一条 = 候选人 framing 没立住.
'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload (T-P0-679 contract).

    Locks the augmentation contract in addition to the original §1-§6 baseline:
    - §7 30-sec Spoken Opener present with verbatim OPENER_30SEC.
    - §8 Canonical 1-sentence prompt with Version A / B / C verbatim, AND
      explicit explanation of why C is NOT recommended (performative framing).
    - §9 §六 临场 Review 6-Pack covers all 6 pillars (mirrors cd://86 §6).
    - cd://86 cross-reference present (this doc is the deep companion).
    """
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## §1 思考顺序",
        "## §2 逻辑顺序",
        "## §3 Anti-patterns",
        "## §4 Verification rituals",
        "## §5 Worked example",
        "## §6 Onsite 临场 60 秒 cheat sheet",
        "## §7 The 30-second Spoken Opener",
        "## §8 Canonical 1-sentence English Prompt",
        "## §9 §六 临场 Review 6-Pack",
        "Junior-PR mindset",
        "Stop-condition",
        "ASSUMPTION:",
        "RecentValueStore",
        "Weak prompt",
        "Strong prompt",
        "8 步",
        "7 块",
        "P95",
        # T-P0-679 acceptance: §8 Version A / B / C explicit headings.
        "### Version A (recommended)",
        "### Version B (shorter alt",
        "### Version C (NOT recommended",
        "performative",
        # T-P0-679 acceptance: §9 6-pack pillars (mirror cd://86 §6).
        "Continuous narration",
        "AI-vs-your-direction handling",
        "45-min time allocation 3/3/10/5/5/5",
        "Manual trace as review step",
        "Fallback when AI is stuck",
        "Prompt transparency",
        # Cross-link to cd://86 (companion doc).
        "cd://86",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")

    # T-P0-679 verbatim locks: opener + Version A / B / C must match
    # cd://86's anchor strings byte-identically.
    if VERSION_A_PROMPT not in content:
        raise RuntimeError(
            "Version A canonical prompt missing verbatim "
            "(must match cd://86 §2 anchor)"
        )
    if VERSION_B_PROMPT not in content:
        raise RuntimeError(
            "Version B alt prompt missing verbatim "
            "(must match cd://86 §2 anchor)"
        )
    if VERSION_C_PROMPT not in content:
        raise RuntimeError(
            "Version C 'junior engineer' prompt missing verbatim "
            "(needed to explain why C is NOT recommended)"
        )
    if OPENER_30SEC not in content:
        raise RuntimeError(
            "§7 30-sec opener missing verbatim "
            "(must match cd://86 §1 anchor)"
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
    if not (5000 <= len(content) <= 18000):
        raise RuntimeError(f"content length {len(content)} outside 5000-18000")


def main() -> int:
    """Upsert the Meta AI-Native Prompt Best Practices doc (idempotent)."""
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
