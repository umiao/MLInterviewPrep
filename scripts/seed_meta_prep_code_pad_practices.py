"""Seed: T-P1-805 [KG-INT B3-3] -- meta-prep/code-pad-best-practices children.

Distills shared coding-round / code-pad practices from the 10 P0+P1 companies'
prep surfaces (S1 prep_notes, S3 company_documents) into shared
`meta-prep/code-pad-best-practices/<slug>` framework_nodes per the promotion
threshold locked in `docs/workflow/promotion_criteria.md` (>=3 of 11 P0+P1
companies AND de-companiable wording).

A grep-driven coverage scan was run across the coding-round-related docs of
the 10 P0+P1 companies (LinkedIn ids=2/22/23/26, DoorDash, Meta ids=82/86/87/
88/89/90, Pinterest ids=39/47/66, Uber id=37, Google, Adobe, TikTok, Slack,
PARSPEC). Six universal code-pad practices cleared the >=3 threshold and are
seeded as de-companiable "must-do" plays. Each child node embeds:

  - 1-2 sentence definition + actionable rule
  - Why-it-matters / where-it-shows-up paragraph
  - Cross-links via kg://N (framework_nodes.id) for adjacent KG nodes
  - Top failure modes / interview anti-patterns
  - relevant_companies CSV listing the >=3 P0+P1 sources

The parent stub `meta-prep/code-pad-best-practices` (T-P1-800) had a
`TODO[KG-INT-B3-3]` marker. This seed updates the parent description to a
real summary on first run.

Scope decision (AI-native handling):
  The task spec mentions "Meta-style 3-step prompt drill, AI tool usage best
  practices". Direct AI-native code-pad signal is currently concentrated in
  Meta (docs 82, 86, 87, 88, 89, 90) -- LinkedIn and Pinterest reference
  CoderPad as the environment but do not yet have AI-pair-programming
  playbooks of their own. Per the locked promotion criteria
  (`docs/workflow/promotion_criteria.md` -- "Threshold-relaxation creep"
  anti-pattern), AI-native-specific patterns that only meet >=1 P0+P1 source
  are NOT promoted to meta-prep. They remain as Meta-specific
  framework_nodes (and are flagged in T-P1-821 B4-promotion consolidation
  for future re-evaluation if a 2nd / 3rd P0+P1 company adds AI-native
  rounds). The 6 children seeded here are the underlying CODE-PAD
  fundamentals (clarify-first, think-out-loud, edge-case enumeration, BUD
  optimization, walk-through, language choice) that the AI-native playbook
  builds ON TOP OF -- so these meta-prep nodes are the foundation that
  any future AI-native expansion would extend.

Safety:
  1. SHA-256 of the `meta-prep/code-pad-best-practices` subtree captured
     pre/post.
  2. Refuses to overwrite a child whose title/description/companies have
     drifted from this seed (someone hand-edited it).
  3. Idempotent: re-run yields inserted=0, updated=0, skipped=7
     (1 parent + 6 children).
  4. Parent description UPDATED only on first run (TODO marker present).
  5. Post-run invariant: exactly 7 rows match
     path = 'meta-prep/code-pad-best-practices' OR
     path LIKE 'meta-prep/code-pad-best-practices/%'.
  6. AC checks:
       - children count >= 4 (task spec)
       - each child has >=3 valid P0+P1 sources in relevant_companies
       - description contains at least one kg:// cross-link

Usage:
    python scripts/seed_meta_prep_code_pad_practices.py
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

PARENT_PATH = "meta-prep/code-pad-best-practices"
PARENT_TITLE = "Code-Pad Best Practices"
PARENT_DESCRIPTION_NEW = (
    "跨公司 coding round / code-pad 通用 practices "
    "(shared coding-interview substrate, distilled from 10 P0+P1 companies' "
    "coding-round prep surfaces). 子节点按 stage 拆分: pre-typing "
    "(clarify + restate + edge-case enumeration), during-typing "
    "(think-out-loud narration + walk-through-before-implement), "
    "optimization (BUD framework), 和 environment (language choice / "
    "code-pad quirks like no-compiler / no-autocomplete). 每个子节点带 "
    "kg://N cross-links 指向具体 framework_node (pillar1 algorithms / "
    "data_structures / mle_coding). 这套基础 practice 是 AI-native "
    "code-pad 的底座 -- AI-pair-programming playbook (Meta 的 3-Step + "
    "prompt 7-block 结构) build on top of these. AI-native 单公司证据 "
    "(目前仅 Meta) 留在 Meta-specific framework_nodes 中, 等 2-3 家 "
    "P0+P1 公司 也加 AI-native round 之后再 promote (T-P1-821 B4-promotion "
    "consolidation flag)."
)
PARENT_TODO_MARKER = "TODO[KG-INT-B3-3]"

P0P1_COMPANY_NAMES = {
    "LinkedIn", "DoorDash", "Google", "Uber", "Adobe",
    "TikTok", "Slack", "PARSPEC", "Pinterest", "Meta",
}

# Each tuple: (slug, title, description, [companies])
# Description should embed at least one kg://N cross-link.
CLUSTERS: list[tuple[str, str, str, list[str]]] = [
    (
        "clarify-restate-before-typing",
        "Clarify + Restate Before Typing",
        "拿到题第一动作不是写代码, 而是 restate (复述题面) + 向 interviewer "
        "问 1-3 条 clarification (澄清问题), 答案到手再 type. 经典 4 类 "
        "clarification: (a) input scale -- n 范围 / 值域 / 是否有重复 / 是否 "
        "允许负数 / 是否允许空; (b) output format -- 单值 / list / 是否需要 "
        "排序 / 是否 stable; (c) error handling -- None / raise / silent skip; "
        "(d) performance budget -- in-place / memory cap / latency 上限. "
        "为什么这一步 senior signal 最强: 面试官从 clarification 看你**心里 "
        "对题目有没有形状**. 跳过 clarify 直接写 = 你在 leetcode warmup; "
        "做对 clarify = 你在 production scoping. 配合 'state your assumption' "
        "动作 (没问到的部分明确说 'I'll assume X, confirm?') 让 interviewer "
        "在你写代码前 catch misinterpretation 比写完再返工 cheap 10 倍. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://197 (pillar1.scaling_resource_model L4 framework -- 也强调 "
        "scoping-first), kg://244 (parent code-pad-best-practices). "
        "Anti-patterns: 'I think I understand' 然后默认假设开始写 (silent "
        "assumption 是 senior signal 杀手); 把 clarify 全交给 AI 让它替你 "
        "假设 (interviewer 看到的是 stalling); 一次性问 10 个 clarification "
        "(说明你没 prioritize, 抓 3 个最影响算法选择的就够).",
        ["DoorDash", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "think-out-loud-narration",
        "Think Out Loud / Continuous Narration",
        "Coding round 全程**边想边讲**, 不要脑里走完才开口. 三层 narration: "
        "(1) high-level 选型 -- '我打算用 hash map 因为 O(1) lookup'; "
        "(2) per-line 决策 -- '这里用 enumerate 而不是 range(len) 因为...'; "
        "(3) self-verification -- '让我快速 trace 一下 [1,2,3] 这个 example: "
        "i=0 时...'. 沉默 30 秒以上 = interviewer 不知你卡哪里 = 失分. "
        "卡住时也要 narrate 卡哪 -- '我现在在想是 DP 还是 greedy, DP 的话 "
        "状态是..., greedy 的话 invariant 是...; 我倾向 DP 因为...'. "
        "这等于 think-aloud protocol (心理学的 protocol analysis 方法), "
        "interviewer 评的不是你最后答案是否最优, 而是 reasoning trace 是否 "
        "structured. 配合 'pause-and-summarize' 动作 (每 3-5 分钟主动 "
        "summarize where I am) 让 interviewer 知道你 driving 进度. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://244 (parent code-pad-best-practices), "
        "kg://251 (meta-prep behavioral storytelling-framework-starr -- "
        "narration discipline 同源). Anti-patterns: 沉默 coding 模式 "
        "(interviewer 看不到你 process); narrate 过细到逐 token 解释 "
        "(over-narration 噪声大); 不同意 interviewer hint 就闭嘴 (应该 "
        "verbal disagree + reasoning, 不是 silent push back).",
        ["Google", "Meta", "Pinterest", "Uber"],
    ),
    (
        "enumerate-edge-cases-bullet-list",
        "Enumerate Edge Cases as Explicit Bullet List",
        "在写代码前**显式列 edge case bullet list** (不能光说 'I'll handle "
        "edge cases'). 8 类标准 edge case 库: (1) empty input (空数组 / "
        "空字符串 / null); (2) single element (n=1); (3) max-size (overflow "
        "/ 性能 boundary); (4) duplicates (重复值是否允许 / 是否 distinct); "
        "(5) negative numbers (sign handling); (6) overflow (int range / "
        "long); (7) None / null / undefined; (8) unicode / 多字节 (字符串 "
        "题专属). 临场挑 3-5 条 most relevant 写出来 -- 5-8 条是甜蜜区, "
        "20 条是 over-thinking. 这一步 dual-purpose: 一是逼自己想全面, "
        "二是给 interviewer 一个 catch -- 他可能加一条你漏的 (这是 senior "
        "follow-up 模式). AI-pair-programming 时把这个 bullet list 直接喂给 "
        "AI 当 acceptance criteria, 防止 AI silent assume. 写完代码后逐条 "
        "trace 对应 edge 的 execution path = 最强 self-test 信号. "
        "Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://9 (pillar1.data_structures), kg://244 (parent). "
        "Anti-patterns: 写完 happy path 才开始想 edge case (大概率 refactor); "
        "edge case 列了不写 test 就交 (interviewer 会问 'did you test'); "
        "'handle edge cases' 当作一句口号没具体化 (无法 verify).",
        ["DoorDash", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "bud-bottleneck-unnecessary-duplicated",
        "BUD Optimization Framework (Bottleneck / Unnecessary / Duplicated)",
        "Cracking the Coding Interview (Gayle Laakmann McDowell) 的 BUD "
        "优化框架, 是从 brute force -> optimal 的最常用 systematic path. "
        "三个 lever: (B) **Bottleneck** -- 找时间复杂度的瓶颈 step "
        "(e.g. O(n^2) 嵌套循环里那一层), 单点优化它; (U) **Unnecessary "
        "work** -- 去掉多余计算 (e.g. 已经 sort 过的数组不要重 sort, "
        "已知不可能的分支 early exit); (D) **Duplicated work** -- 消除重复 "
        "计算 (memoization / DP / 中间结果 cache). 配合 5 种 standard "
        "optimization tactic: (1) hash map 把 O(n) lookup 降 O(1); "
        "(2) 排序 + 双指针把 O(n^2) 降 O(n log n); (3) 前缀和 / 差分数组 "
        "把 range query 降 O(1); (4) 二分答案把搜索空间降 log; "
        "(5) DP / memoization 消重叠子问题. 临场 sequence: 先 brute force + "
        "复杂度分析 -> apply BUD 找单一 lever -> 直接说出对应 tactic -> "
        "再写代码. Interviewer 看的是**你能不能 verbalize 优化的 reasoning**, "
        "不是直接报最优解. Cross-links: kg://1 (pillar1 Coding & Algorithms), "
        "kg://10 (pillar1.algorithm_paradigms), kg://244 (parent). "
        "Anti-patterns: 跳过 brute force 直接报最优 (interviewer 不知你 "
        "有没有理解 baseline); apply BUD 但不说出来 (silent optimization = "
        "missed signal); 同时优化 3 个地方 (一次 1 lever 让 narration 清晰).",
        ["DoorDash", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
    (
        "walk-through-before-implement",
        "Walk Through Algorithm on Example Before Implementing",
        "选定 approach 之后 (BUD 优化完成), **不要直接写代码**. 先在 "
        "interviewer 视野里**手动 trace 一个小 example** 走完整 algorithm, "
        "verbalize 每一步 state 变化. e.g. binary search 题 trace [1,3,5,7,9] "
        "找 5: 'lo=0 hi=4, mid=2, nums[2]=5, hit return 2'. 这一步 dual: "
        "(a) 帮你自己 catch off-by-one / boundary bug (写代码前发现比写完 "
        "debug cheap); (b) 让 interviewer confirm 'yes that's the algorithm "
        "I want, go ahead' = 写代码前就拿到 alignment 信号, 写完不会被否. "
        "高级版本 (senior signal): trace 完 happy path 后再 trace 1-2 个 "
        "edge case (empty / boundary / duplicate), 说 'this also handles X "
        "because Y'. AI-pair-programming 时这一步等于 'review skeleton "
        "before AI writes full code' -- 让 AI 先给函数签名 + step plan, "
        "你 walk through agree 后再让它实现. Cross-links: kg://1 (pillar1 "
        "Coding & Algorithms), kg://10 (pillar1.algorithm_paradigms), "
        "kg://244 (parent). Anti-patterns: 选定 approach 立刻 type "
        "(没让 interviewer 验证选型); walk-through 用太大 example "
        "(n=20 trace 不完, 用 n=3-5); walk-through 但不 verbalize "
        "(interviewer 看不到 reasoning).",
        ["LinkedIn", "Meta", "Pinterest"],
    ),
    (
        "language-choice-python-default",
        "Language Choice: Python Default + Code-Pad Quirks",
        "Coding round 默认语言**首选 Python** -- ML / data 岗 industry "
        "standard, syntax 简洁, dict / list comprehension / sorted / "
        "collections 等 stdlib 直接用. 备选: Java (强类型 signal, 适合 "
        "OOD round) / C++ (perf signal, 适合 systems / infra 岗). "
        "面试官最熟悉这三种, 不要选小众语言 (Rust / Go) 否则 interviewer "
        "卡你 syntax 反失分. CoderPad 等 code-pad 环境特有 quirk 必须意识到: "
        "(a) **无 compiler** -- 一些 pad 不能 run code, syntax 不需要 100% "
        "精确, 但 logic 要清楚; (b) **无 autocomplete / no IDE assist** -- "
        "stdlib import 要背 (e.g. heapq / collections.Counter / "
        "functools.lru_cache), `from X import Y` 路径写错就卡; "
        "(c) **plain-text formula** -- 没 LaTeX, 数学公式用 ASCII 写 "
        "(e.g. `w = (X^T X)^-1 X^T y` 不是 latex). 出场前 30 秒检查: "
        "Python version (3.10+ 才有 match-case), 是否允许第三方 (numpy / "
        "pandas), 是否允许 stdlib only. Cross-links: kg://1 (pillar1 "
        "Coding & Algorithms), kg://9 (pillar1.data_structures), "
        "kg://11 (pillar1.mle_coding), kg://244 (parent). "
        "Anti-patterns: 默认用最熟悉的小众语言 (interviewer 看不懂 "
        "syntax 反质疑 logic); 写代码用 IDE 才记得的 API "
        "(stdlib hallucination); 假设 pad 能 run code 就不 mental-trace "
        "(很多 pad 实际不能 compile).",
        ["Adobe", "Google", "LinkedIn", "Pinterest", "Uber"],
    ),
]


def sha256_subtree(conn: sqlite3.Connection) -> str:
    """SHA-256 of all 'meta-prep/code-pad-best-practices%' rows, ordered by path."""
    rows = conn.execute(
        "SELECT path, depth, title, description, relevant_companies "
        "FROM framework_nodes "
        "WHERE path = ? OR path LIKE 'meta-prep/code-pad-best-practices/%' "
        "ORDER BY path",
        (PARENT_PATH,),
    ).fetchall()
    h = hashlib.sha256()
    for r in rows:
        h.update(repr(r).encode("utf-8"))
    return h.hexdigest()


def update_parent_description(
    conn: sqlite3.Connection, parent_id: int, current_desc: str | None
) -> str:
    """Update parent description if still TODO; otherwise SKIP."""
    if current_desc and PARENT_TODO_MARKER in current_desc:
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (PARENT_DESCRIPTION_NEW, parent_id),
        )
        return "UPDATED"
    if current_desc == PARENT_DESCRIPTION_NEW:
        return "SKIPPED"
    raise RuntimeError(
        f"[CONFLICT] parent description has been edited to something "
        f"other than the TODO marker or the seed's target text. "
        f"Refusing to overwrite. Current: {current_desc!r}"
    )


def upsert_child(
    conn: sqlite3.Connection,
    *,
    parent_id: int,
    slug: str,
    title: str,
    description: str,
    relevant_companies_csv: str,
) -> tuple[str, int]:
    """Insert child if absent; SKIP if present with matching content."""
    path = f"{PARENT_PATH}/{slug}"
    existing = conn.execute(
        "SELECT id, title, description, relevant_companies "
        "FROM framework_nodes WHERE path = ?",
        (path,),
    ).fetchone()
    if existing is not None:
        node_id, ex_title, ex_desc, ex_companies = existing
        if (ex_title == title and ex_desc == description
                and (ex_companies or "") == relevant_companies_csv):
            return "SKIPPED", node_id
        raise RuntimeError(
            f"[CONFLICT] path={path!r} exists but content has drifted from "
            f"seed. title_match={ex_title == title} "
            f"desc_match={ex_desc == description} "
            f"companies_match={(ex_companies or '') == relevant_companies_csv}. "
            f"Refusing to overwrite hand-edited content; resolve by either "
            f"reverting the edit or updating the seed."
        )
    cur = conn.execute(
        """
        INSERT INTO framework_nodes
            (parent_id, path, depth, title, description,
             importance, priority, status, progress_pct, relevant_companies)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (parent_id, path, 2, title, description,
         0.7, "P1", "not_started", 0.0, relevant_companies_csv),
    )
    return "INSERTED", cur.lastrowid


CROSS_LINK_RE = re.compile(r"(kg://\d+|sd://[a-z0-9-]+)")


def assert_promotion_threshold() -> None:
    """Static AC: each cluster has >=3 P0+P1 sources, all valid names; >=4 children;
    each description embeds at least one kg:// or sd:// cross-link."""
    if len(CLUSTERS) < 4:
        raise AssertionError(
            f"[AC-FAIL] only {len(CLUSTERS)} clusters defined; AC requires >=4"
        )
    seen_slugs: set[str] = set()
    for slug, _title, description, companies in CLUSTERS:
        if slug in seen_slugs:
            raise AssertionError(f"[AC-FAIL] duplicate slug {slug!r}")
        seen_slugs.add(slug)
        if len(companies) < 3:
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} has only {len(companies)} sources; "
                f"promotion threshold is >=3"
            )
        if len(companies) != len(set(companies)):
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} has duplicate sources: {companies}"
            )
        invalid = set(companies) - P0P1_COMPANY_NAMES
        if invalid:
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} references non-P0+P1 companies: "
                f"{sorted(invalid)}"
            )
        if not CROSS_LINK_RE.search(description):
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} description has no kg:// or sd:// "
                f"cross-link"
            )


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    """Update parent description (if TODO) and seed N child clusters."""
    counts = {"INSERTED": 0, "UPDATED": 0, "SKIPPED": 0}

    parent = conn.execute(
        "SELECT id, description FROM framework_nodes WHERE path = ?",
        (PARENT_PATH,),
    ).fetchone()
    if parent is None:
        raise RuntimeError(
            f"[FAIL] parent {PARENT_PATH!r} does not exist; "
            f"run scripts/seed_meta_prep_pillar.py first (T-P1-800)."
        )
    parent_id, parent_desc = parent
    parent_action = update_parent_description(conn, parent_id, parent_desc)
    counts[parent_action] += 1
    print(f"[{parent_action}] parent id={parent_id} path={PARENT_PATH}")

    for slug, title, description, companies in CLUSTERS:
        relevant_companies_csv = ",".join(companies)
        action, child_id = upsert_child(
            conn,
            parent_id=parent_id,
            slug=slug,
            title=title,
            description=description,
            relevant_companies_csv=relevant_companies_csv,
        )
        counts[action] += 1
        n_links = len(CROSS_LINK_RE.findall(description))
        print(
            f"[{action}] child  id={child_id} "
            f"slug={slug} sources={len(companies)} cross_links={n_links}"
        )

    return counts


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    assert_promotion_threshold()
    print(
        f"[AC-OK] all {len(CLUSTERS)} clusters have >=3 valid P0+P1 sources "
        f"and embed at least one kg:// or sd:// cross-link"
    )

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_subtree(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = seed(conn)
        conn.commit()

        post_hash = sha256_subtree(conn)
        print(f"[POST] sha256={post_hash}")

        total = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes "
            "WHERE path = ? OR path LIKE 'meta-prep/code-pad-best-practices/%'",
            (PARENT_PATH,),
        ).fetchone()[0]
    finally:
        conn.close()

    print(
        f"[SUMMARY] inserted={counts['INSERTED']} "
        f"updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total_in_subtree={total}"
    )

    expected_total = 1 + len(CLUSTERS)
    if total != expected_total:
        print(f"[FAIL] Expected {expected_total} rows, got {total}")
        sys.exit(1)
    touched = counts["INSERTED"] + counts["UPDATED"] + counts["SKIPPED"]
    if touched != expected_total:
        print(f"[FAIL] Expected to touch {expected_total} nodes, touched {touched}")
        sys.exit(1)
    print("[DONE]")


if __name__ == "__main__":
    main()
