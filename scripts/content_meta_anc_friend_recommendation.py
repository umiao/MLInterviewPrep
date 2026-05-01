"""[META-ANC-3] Friend Recommendation drawer (Meta AI-Native Coding).

Inserts ONE problems row that becomes the db://<id> drawer for the Friend
Recommendation Meta AI-Native Coding question. Distills the 6-layer ladder
(L1 valid_recommend bug-fix without AI -> L6 the meta-ability layer that
demonstrates judgment) into a single description. The L6 metacognition
layer is the senior signal -- not pressed thin.

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='graph_recommendation_topk'). The pattern column is the STABLE
SLUG -- never rewritten. The title may evolve. A sentinel HTML comment
<!-- ANC_SLUG: meta_anc_friend_recommendation --> is embedded at the top
of the description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup, asserted == 31).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md
(Section 3, lines 156-228).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company  # noqa: E402
from src.backend.models.company_tags import ProblemCompanyTag  # noqa: E402
from src.backend.models.problem import Problem  # noqa: E402

SLUG = "meta_anc_friend_recommendation"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "graph_recommendation_topk"
TITLE = "Meta AI-Native Coding - Friend Recommendation (L1 valid-fix -> L6 meta-ability)"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "valid_recommend",
    "mutual",
    "Adamic-Adar",
    "2-Hop",
    "L6",
    "元能力",
]

DESCRIPTION = SENTINEL + r"""

# Friend Recommendation -- Meta AI-Native Coding (L1 valid-fix -> L6 meta-ability)

> **题型**: 同一道题三小问递进 (Q1-Q3)，覆盖六层能力 (L1-L6)；Q1 不让用 AI（考精准定位 bug 的能力），Q2-Q3 鼓励用 AI（考"指挥 AI"和"过滤 AI 输出"的判断力）。
> **场景**: Meta AI-Native Coding 现场题——L6 元能力层是这道题的差异化信号；六层 ladder 不是凑数，是这道题的核心答案结构。
> **评分信号**: 能主动声明"我不采纳 AI 哪个建议、为什么"= L6 senior signal；只会埋头跟着 AI 改 = L2 baseline。

---

## 1. 三小问题面与允许的 AI 用法

| 小问 | 任务 | AI 用法 | 考察重点 |
|------|------|---------|----------|
| Q1 | Fix `valid_recommend(user, candidates)` 让所有 test 通过 | **不允许 AI** | 精准定位、test 名反推 bug、最小修改 |
| Q2 | 用 AI 实现 `random_recommend(user)`，paste 进去通过测试 | **鼓励 AI** | 第一发 prompt 的完整性、paste 前扫描、迭代止损 |
| Q3 | 讨论好友推荐的指标；新文件实现 mutual friends + 配套测试 | **鼓励 AI** | 过滤 AI 给的指标光谱、复杂度两段论、L6 元能力 |

User 类的关键属性：只有 `id` 和 `currentFriends` 两个字段——**没有** interest / age / location / group。**这是 L3 过滤步骤的核心输入约束**：AI 默认推荐基于 interest 的算法都该被排除。

---

## 2. 六层能力 ladder (L1-L6)

### L1 -- 无 AI 的 Bug Fix (对应 Q1)

**考点 1.1 -- 好友推荐函数的"必查清单"**

看到 `valid_recommend(user, candidates)` 这种签名，自动按以下顺序检查：

1. **排除自指**: `user` 不在 `candidates` 结果里
2. **排除已有好友**: candidate ∉ `user.currentFriends`
3. **去重**: candidates 列表本身可能重复
4. **对称性**: A->B 和 B->A 的处理是否一致
5. **空集边界**: candidates 为空、user 没好友
6. **类型边界**: User 对象 vs user_id 比较方式 (有没有 `__eq__` / `__hash__`)

**实战**: 这道题的 bug 通常是清单第 1 或第 2 条——看 test 名 `test_excludes_self` 直接告诉你"自指没排除"。

**考点 1.2 -- 从 test 名反推 bug**

测试名 = 考点提示。先扫测试名，再看 assertion，最后回函数找缺失分支。盲读函数代码是低效路径。

**考点 1.3 -- 修复时不要顺手重构**

只修必要的两行，别动其他逻辑。考官在测的是"精准定位"，不是"代码品味"。多动一行就多一个 bug 的可能性——这是 L1 最容易失分的地方。

---

### L2 -- AI 辅助实现的迭代心法 (对应 Q2)

**考点 2.1 -- 第一发 Prompt 的完整结构 (success rate 30% -> 80%)**

第一次 paste AI 输出不 work，几乎都是 prompt 给得不够。第一发 prompt 必须包含：

- **完整类定义**: 把 `class User: id, currentFriends` 全文贴进去
- **相关函数签名**: 让 AI 知道接口约定 (输入是单个 User 还是 `list[User]`)
- **一两个测试用例**: 让 AI 知道期望行为
- **明确的约束**: 依赖（不能用 numpy）、返回类型、长度规则、是否允许 import

评分标准: 第一发 prompt 给得够厚，AI 一次过的概率从 30% 涨到 80%。

**考点 2.2 -- Paste 前的快速扫描 (3 件事)**

AI 输出别直接 paste。三件事扫一遍：

1. **属性名是否匹配**: `user.friends` vs `user.currentFriends` (AI 经常瞎猜)
2. **方法签名是否吻合**: AI 可能多塞或少塞参数
3. **边界条件是否齐全**: candidates 为空、k 大于候选数

这一步比 paste 后 debug 快十倍。

**考点 2.3 -- 增量式 Debug (delta 而非重写)**

第二发 prompt 不要重新描述需求，直接贴：

```
这是你给的代码: ...
这是错误 traceback: ...
请修复
```

这样 AI 改的是 delta，不是从头来过。从头来过经常**改回了第一发的 bug**。

**考点 2.4 -- 迭代失败的止损信号**

迭代两轮还不过，停下来。说明：

- 需求描述本身有歧义
- 你漏看了某个类属性 / 隐含约束

继续盲迭代只会越改越乱。这时回退去重读题目而不是再喂一发 prompt。

**考点 2.5 -- 5 个常见 AI 幻觉模式**

提前知道 AI 在这类题里会幻觉什么：

| 幻觉 | 例子 | 防御 |
|------|------|------|
| 编造不存在的属性 | 假设 `User.interests` 存在 | paste 前对照类定义 |
| 用错 hash | 在没实现 `__hash__` 的对象上 `set(users)` | 看类定义有没有 `__hash__` |
| 引入多余依赖 | 硬塞 `numpy` 做 set 交集 | prompt 里写 "no third-party deps" |
| 忽略给定的辅助函数 | 自己重写 `valid_recommend` 而非调用 | prompt 里点名 "must call valid_recommend" |
| 重命名给定接口 | 改了函数签名让"看起来更通用" | paste 前 diff 签名 |

---

### L3 -- AI 输出的判断与过滤 (对应 Q3 前半)

**考点 3.1 -- "AI 给十个，可用两个"的过滤逻辑**

AI 看到"好友推荐"会列十几种方案，但能用的取决于 User 类有什么数据。过滤步骤：

1. 列出 AI 所有建议
2. 对每条标注"需要什么数据"
3. 对照 User 类属性删掉做不到的
4. 剩下的按实现复杂度排序

**关键洞察**: User 类只有 `id` 和 `currentFriends`——**只有图结构信息**。所有需要 demographic / 行为日志的指标全删，只剩"图-only"光谱里的几条。

**考点 3.2 -- 好友推荐指标的"光谱"知识**

按数据要求从低到高排列：

| 数据要求层 | 指标 | 备注 |
|------------|------|------|
| 只需要图结构 | mutual friends count、Jaccard 相似度、Adamic-Adar 指数、Resource Allocation 指数、2-Hop 路径数 | 这一栏对应当前 User 类，**实战可用** |
| 需要 demographic / profile | 年龄/地区匹配、共同 group、相同学校 / 公司 | User 类没这些字段，**排除** |
| 需要行为日志 | 共同访问页面、消息频率、登录时段重合 | User 类没行为日志，**排除** |

**面试用法**: 被问"还能怎么改进"时，从同一光谱往右挪一格 (mutual friends -> Adamic-Adar) 显得**有领域常识**；跨光谱挪 (mutual friends -> 兴趣推荐) 通常会被反问"数据从哪来"——这是失分套路。

**考点 3.3 -- Adamic-Adar 的一句话原理 (会用就行)**

如果只能记一个超出 mutual friends 的指标，记 **Adamic-Adar**：共同好友按其度的反对数加权。

数学定义:

$$
AA(u, v) = \sum_{w \in N(u) \cap N(v)} \frac{1}{\log |N(w)|}
$$

**直觉一句话**: "你和我都认识一个只有 5 个朋友的人，比都认识一个有 5000 朋友的网红，更能说明咱俩关系近。"——一句话能讲清就是会用，不需要背公式。

---

### L4 -- 算法实现 + 复杂度分析 (对应 Q3 后半)

**考点 4.1 -- Top-K Mutual Friends 朴素实现**

```python
import heapq

def top_k_mutual_friends(target_user, all_users, k):
    target_friends = set(target_user.currentFriends)
    scores = []
    for cand in all_users:
        if not valid_recommend(target_user, cand):
            continue
        common = len(target_friends & set(cand.currentFriends))
        if common > 0:
            scores.append((common, cand.id))
    return heapq.nlargest(k, scores)
```

**复杂度**: $O(n \cdot f + n \log k)$，$n$ 是总人数，$f$ 是平均好友数。

**考点 4.2 -- 2-Hop 优化**

```python
from collections import Counter

def top_k_2hop(target_user, user_lookup, k):
    cnt = Counter()
    target_friends = set(target_user.currentFriends)
    for fid in target_user.currentFriends:
        for ffid in user_lookup[fid].currentFriends:
            if ffid != target_user.id and ffid not in target_friends:
                cnt[ffid] += 1
    return cnt.most_common(k)
```

**复杂度**: $O(f^2)$，**何时用**: $n$ 大 $f$ 小的真实社交网络 ($n$ 上亿、$f$ 几百)。**前提**: 要有 `user_id -> User` 的查找字典；如果输入只是 `list of User`，朴素版更合适。

**考点 4.3 -- "基于输入接口选算法"的回答模板**

考官追问"为什么不一开始就用 2-hop"时，标准回答：**先讲约束，再讲算法**。

> "2-hop 需要 O(1) 查表，所以前提是有 user_lookup dict。如果输入只是 list 我就用朴素版；如果允许预处理建索引就用 2-hop。如果是流式数据还要考虑增量更新——那就是另一套系统。"

这种回答展示的是**工程取舍**，不是算法熟练度——这是被招 senior 的人和被招 new grad 的人的分水岭。

**考点 4.4 -- 复杂度分析的"两段论"**

讲复杂度分两步：

1. **先讲主导项**: $O(n \cdot f)$ 是主导，$O(n \log k)$ 是次要的
2. **再讲优化方向**: 哪一步浪费了，怎么省（比如"$n$ 大 $f$ 小时 $O(n \cdot f)$ 的 $n$ 这个因子可以通过 2-hop 换成 $f^2$"）

只讲数字不讲洞察的复杂度分析是低分回答。

---

### L5 -- 测试生成的覆盖意识 (Q3 隐藏考点)

**考点 5.1 -- Mutual Friends 测试的最小覆盖集 (7 条)**

```
1. 正常排序: 多个候选，common count 各异，验证 top-K 顺序正确
2. 自己排除: target 自己不出现在结果里
3. 已有好友排除: target.currentFriends 里的人不出现
4. 零共同好友: 候选与 target 没有共同好友 (skip 还是返回 0?)
5. 并列处理: 两个候选 score 相同时的 tie-breaking (稳定 vs 任意)
6. K > 候选数: 返回所有可推荐的，不报错
7. 空 friend list: target.currentFriends == [] 时返回空
```

**考点 5.2 -- 让 AI 生成测试的 Prompt 模式**

不要说"写测试"，要说：

> 写测试覆盖以下场景：[列出 5-7 条具体场景]

前者得到笼统的 happy path 三件套，后者得到能用的测试套件。**模板是关键**——没有显式列场景，AI 默认只覆盖 happy path。

**考点 5.3 -- 测试也要 paste 前扫一眼**

AI 生成的 test 也会幻觉：

- 调用一个不存在的 helper
- assert 一个错误的预期 (常见: 预期顺序但 mutual friends 排序未定义)
- import 多余的库

Test 文件也要按 L2 的扫描原则过一遍。这一步常被忽略——很多人觉得测试无所谓所以直接 paste，结果 test 本身有 bug，更难 debug。

---

### L6 -- 元能力 (这一层最值钱，是 senior signal)

这一层不是技术点，是**怎么让考官看见你的判断力**。同样的代码，不同表述差一个等级。

**考点 6.1 -- 主动声明"我不采纳什么"**

讲"为什么不用 AI 的某个建议"比"我用了什么"更值钱。例：

> "AI 建议基于 interest 做推荐，但 User 类没有 interest 字段，所以排除。"

——这一句话直接展示了 L3 的判断力，而不是埋头跟着 AI 改。L6 元能力的核心是：**让考官听见你的过滤过程**，不是只看到你的最终代码。

**考点 6.2 -- "够用即可"的工程取舍**

面试时间有限。明确说出：

> "我先实现 mutual friends，因为最简单且时间够；Adamic-Adar 是可选的优化方向。"

考官想看的是有取舍意识的工程师，不是炫技的人。试图在 30 分钟内塞 Adamic-Adar + 2-Hop + 测试套件 = 大概率三个都没做完。

**考点 6.3 -- 把 AI 当"协作者"而非"代写"的措辞**

外化思考过程：边操作边讲：

> "我现在让 AI 生成 X，因为 Y；它给了 Z，但我要改 W，因为类里没有 V。"

这种自言自语式的解说，让考官**看见你的判断节奏**。沉默地 paste-试-paste-试是最低分的姿态——考官看不到你的思考，只看到你像个搬运工。

---

## 3. AI 协同分工对照表

| 让 AI 做 | 自己做更快/更靠谱 |
|----------|-------------------|
| 列推荐指标的"光谱" (L3.2) | 对照 User 属性挑出可用项 (L3.1) |
| 实现 Top-K Mutual Friends 朴素版 (L4.1) | 复杂度两段论的口头表述 (L4.4) |
| 实现 2-Hop 版本 (L4.2) | "基于输入接口选算法"的回答模板 (L4.3) |
| 生成测试覆盖 7 条场景 (L5.2) | 测试 paste 前的扫描 (L5.3) |
| 解释 Adamic-Adar 的公式 | Adamic-Adar 的"5 朋友 vs 5000 朋友"直觉 (L3.3) |
| - | L6 主动声明"我不采纳什么"——这一句必须自己讲，AI 不会替你说 |

底线: **L6 这一层 AI 帮不上**。所有"判断"和"取舍"必须用嘴讲出来——这是这道题的差异化得分点。

---

## 4. 三句金句 (面试用来秀洞察)

1. **L3 过滤金句**: "AI 建议基于 interest 推荐，但 User 类没有 interest 字段——所以排除。" (展示数据约束意识)
2. **L4 复杂度金句**: "$O(n \cdot f)$ 是主导项；$O(n \log k)$ 是 heap 取 top-K 的次要项——所以优化空间在 $n \cdot f$ 这一块。" (展示分析层次)
3. **L6 元能力金句**: "我先实现 mutual friends，因为最简单且时间够；Adamic-Adar 是可选的优化方向。" (展示工程取舍)

讲这三句的时候放慢节奏——它们值的分比埋头写代码多。

---

## 5. 一图流总结

```
Q1 (no AI) -> L1 必查清单 + test 名反推 + 最小修改
              |
Q2 (with AI) -> L2 第一发 prompt 完整 + paste 前 3 件事 + 迭代止损 + 5 种幻觉
              |
Q3 (with AI) -> L3 光谱过滤 + Adamic-Adar 一句话原理
                L4 朴素 + 2-Hop + "基于输入接口选算法"
                L5 7 条覆盖集 + AI 生成测试的 prompt 模式
              |
              -> L6 元能力 (主动声明不采纳 + 够用即可 + 协作者措辞)
                       ^ 这一层是 senior signal，所有判断都要外化
```

**记住**: L1-L5 是技术执行层，AI 都能帮；**L6 元能力层**是这道题的差异化签名——必须自己讲出来。
"""


def _normalize(text: str) -> str:
    """Semantic normalization for NOOP comparison.

    Strip per-line trailing whitespace, force LF line endings, collapse
    3+ blank lines down to 2. Forbids accidental [UPDATED] reports caused
    by trailing-whitespace drift or platform line-ending differences.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _assert_required_keywords(description: str) -> None:
    """Abort if any REQUIRED-KEYWORD is missing from the description."""
    for kw in REQUIRED_KEYWORDS:
        if kw not in description:
            raise RuntimeError(
                f"[META-ANC-3] missing keyword {kw!r} -- regenerate"
            )


def _assert_no_emoji(description: str) -> None:
    """Project rule: no emoji characters in content."""
    for ch in description:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1FAFF
            or 0x1F000 <= cp <= 0x1F2FF
            or 0x2600 <= cp <= 0x27BF
        ):
            raise RuntimeError(
                f"[META-ANC-3] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_friend_recommendation() -> int:
    """Insert or update the Friend Recommendation drawer; return problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-3] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-3] expected Meta company_id=31, got {company_id}"
            )
        print(f"[OK] target company: id={company_id} name='Meta'")

        existing = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .first()
        )

        normalized_new = _normalize(DESCRIPTION)

        if existing is None:
            problem = Problem(
                title=TITLE,
                description=DESCRIPTION,
                difficulty=DIFFICULTY,
                pattern=PATTERN,
                category=CATEGORY,
                source=SOURCE,
                description_source=DESCRIPTION_SOURCE,
                is_completed=False,
                comfort_level=0,
            )
            db.add(problem)
            db.flush()
            pid = int(problem.id)
            print(
                f"[INSERT] problems id={pid} title={TITLE!r} "
                f"len={len(DESCRIPTION)}"
            )
        else:
            pid = int(existing.id)
            normalized_old = _normalize(existing.description or "")
            if normalized_old == normalized_new:
                print(
                    f"[NOOP] problems id={pid} description "
                    f"semantically identical (len={len(DESCRIPTION)})"
                )
            else:
                old_len = len(existing.description or "")
                existing.description = DESCRIPTION
                existing.title = TITLE
                existing.difficulty = DIFFICULTY
                existing.category = CATEGORY
                existing.description_source = DESCRIPTION_SOURCE
                print(
                    f"[UPDATED] problems id={pid} old_len={old_len} "
                    f"new_len={len(DESCRIPTION)} "
                    f"delta={len(DESCRIPTION) - old_len:+d}"
                )

        existing_tag = (
            db.query(ProblemCompanyTag)
            .filter(
                ProblemCompanyTag.problem_id == pid,
                ProblemCompanyTag.company_id == company_id,
            )
            .first()
        )
        if existing_tag is None:
            tag = ProblemCompanyTag(
                problem_id=pid,
                company_id=company_id,
                relevance="core",
                source="manual",
                notes="Meta AI-Native Coding 2026-05-01 inventory",
            )
            db.add(tag)
            print(
                f"[INSERT] problem_company_tags problem_id={pid} "
                f"company_id={company_id} relevance=core"
            )
        else:
            print(
                f"[NOOP] problem_company_tags problem_id={pid} "
                f"company_id={company_id} already present"
            )

        db.commit()

        final = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .one()
        )
        print(
            f"[VERIFY] problems id={final.id} pattern={final.pattern!r} "
            f"source={final.source!r} desc_len="
            f"{len(final.description or '')}"
        )
        return int(final.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upsert_meta_anc_friend_recommendation()
