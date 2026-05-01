"""[META-ANC-6] Compiler Optimization drawer (Meta AI-Native Coding).

Inserts ONE problems row that becomes the db://<id> drawer for the
Compiler-Optimization "reverse-engineer cost from test cases" Meta
AI-Native Coding question. Distills the AI-trap failure mode (LLM
fabricating cost constants), the "test-cases-as-spec" reframe, the
three-stage skeleton (model / fit-with-IDENTITY / search-pass-combos),
the 8-block Meta-Prompt template, the human checklist, and the core
reflection about LLM-fabricated constants into one description.

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='regression_inference_from_tests'). The pattern column is the
STABLE SLUG -- never rewritten. The title may evolve. A sentinel HTML
comment <!-- ANC_SLUG: meta_anc_compiler_optimization --> is embedded
at the top of the description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup, asserted == 31).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md
(Section 5, lines 289-443).
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

SLUG = "meta_anc_compiler_optimization"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "regression_inference_from_tests"
TITLE = (
    "Meta AI-Native Coding - Compiler Optimization "
    "(cost-model regression + Meta-Prompt + 3-stage skeleton)"
)
DIFFICULTY = "hard"
CATEGORY = "ml_coding"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "Meta-Prompt",
    "lstsq",
    "IDENTITY",
    "残差",
    "幻觉",
    "回归",
]

DESCRIPTION = SENTINEL + r"""

# Compiler Optimization -- Meta AI-Native Coding (cost-model regression + Meta-Prompt + 3-stage skeleton)

> **题型**: 给一个 compiler 项目骨架 (`test.py` + 几份 `instructionN.txt` + 一个 stub `extract_time_and_mem_cost`)，目标"优化 compiler 的 time / mem"。表面是写代码，**内核**是从 test cases 反推未知 cost 参数。
> **场景**: Meta AI-Native Coding 现场题；前两个 test 看起来像普通 operator-cost map (`+/-/=` cost=1, `*/` cost=5)，从 test4 开始全错。**面试官在最后 5 分钟才提示去看 `extract_time_and_mem_cost` 在干嘛**——意思就是那些 cost number 是**未知**而不是常量。
> **AI-trap signature**: 楼主问 GPT "1 和 5 是哪里来的"，GPT 答"我自己推理的"；接着楼主问面试官"有没有 universal 定义"，答"没有"；楼主反应不过来，让 GPT 反复 re-infer 直到时间用完。**这是 AI 面试最大失分模式**——把 LLM 编出来的常数当地面真相。

---

## 1. 题面 + 楼主翻车回放

`extract_time_and_mem_cost(instruction)` 输入一份 `.txt` 指令清单（每行 `resN = exprN`），返回 `(time, mem)` 两个数值；`test.py` 里有形如 `assert (extract_time_and_mem_cost('test/instruction1.txt'), 14)` 的硬编码期望值。

楼主跑通 test1 / test2 后，让 GPT 总结出 cost map：

```
('+', '-', '='): cost = 1
('*', '/')    : cost = 5
```

test3 凑巧也对。但是 test4 / test5 / test6 / test7 全错。最后 5 分钟，面试官提示"看看 `extract_time_and_mem_cost` 在干嘛"+ 楼主直接问 GPT "1 和 5 是哪里来的" -> GPT 答"我自己推理的" -> 楼主问面试官"有 universal 定义吗"-> 答"**没有**"-> 楼主反应不过来 -> 时间到。

**关键诊断**: cost 不是常量，是这道题的**未知数**。test cases 不是用来"验证你的实现对不对"，而是 spec 的一部分——你要从 (instruction_text, expected_cost) 这堆配对里**反推**出 cost 是怎么算的。

---

## 2. 核心思路 (一句话)

**把 test cases 当作 spec 的一部分而不是验证手段，把未知 cost 参数当成回归问题，把代码优化和参数拟合当成两个可分离的子问题，先固定一个推另一个。**

形式化：

```
cost_total = f( features( optimize( parse(input) ) ) )
              ─────  ────────  ──────────  ──────────
              拟合     可选       已知         已知
```

四个组件里哪些已知、哪些未知，决定了下一步干嘛。这道题里 `parse` 已知，`optimize` 形式可选/未知，`features` 候选有限，`f` 是参数未知的线性函数。

---

## 3. 三阶段骨架 (B 和 C 必须解耦)

### 阶段 A: 建模 (不写代码，只列结构)

把"未知"按类型分类：(a) 数值参数适合回归，(b) 离散结构选择适合枚举/搜索，(c) 函数形式 (线性 / 取 max / 分段)。先列方程数 vs 未知数，判断 over / under / exactly determined。

### 阶段 B: 参数拟合 (先假定 `optimize = IDENTITY`)

不优化、直接数 op 的频次，用 `numpy.linalg.lstsq` 反推 cost。

- **拟合上了 (残差 == 0)** -> cost model 不要求优化，直接收工。
- **拟合不上 (残差非 0)** -> 进入阶段 C。

### 阶段 C: 优化形式搜索

枚举几种主流优化组合：CSE (Common Subexpression Elimination) / constant folding / DCE (Dead Code Elimination) / inline，每种组合下重做阶段 B，看哪一种让所有 test 残差为 0。

**关键洞察**: **阶段 B 和 C 可以独立验证，不要一开始就把它俩耦合起来想，会爆炸**。先固定一个 (optimize=IDENTITY) 推另一个 (cost 参数)；推不出再回来动 optimize。

---

## 4. Meta-Prompt 模板 (8 块完整保留——这道题的金句模板)

下面这个模板可以直接喂给 GPT / Claude，针对这类"给 example 反推规则"的题型。占位符用 `{{...}}` 标出：

```
我有一道"从 test cases 反推未知规则"的题。请按以下结构帮我分析,
不要凭直觉给常数, 所有数值必须从 test 中推导。

═══ 1. INPUT ═══
- Function signature: {{def f(...) -> ...}}
- All test cases (input + expected output):
  {{完整列出, 包括输入文件内容}}
- Constraints from problem statement: {{有哪些已知规则}}

═══ 2. UNKNOWNS ═══
列出所有未知量, 分类为:
  (a) 数值参数 (适合用回归求解)
  (b) 离散结构选择 (适合枚举或搜索)
  (c) 函数形式 (线性? 取 max? 分段?)

═══ 3. FEATURE EXTRACTION ═══
为每个 input 提取候选特征向量。先列尽量全的特征,
标注哪些是"必然相关"哪些是"可能相关":
  - {{特征 1}}: 必然 / 可能 / 备选
  - ...

═══ 4. EQUATIONS ═══
把每个 test 写成一个方程:
  test_k: Σ c_i · f_i^(k) = output_k
列出方程数 vs 未知数, 判断 over/under/exactly determined。

═══ 5. SOLVE ═══
- 用 numpy.linalg.lstsq 解
- 报告残差: 全 0 / 系统性偏差 / 随机
- 如果残差非 0, 提出最可能漏掉的特征是什么并说明理由

═══ 6. VALIDATE ═══
用解出的参数回代验证每个 test, 给出每个 test 的
  predicted vs expected 对比表

═══ 7. ITERATE ═══
如果验证失败, 按以下顺序假设并重试:
  Step 1: 加入优化 pass (CSE / folding / DCE / inline)
  Step 2: 改变函数形式 (线性 -> 分段线性 / max / peak)
  Step 3: 加入结构性特征 (peak liveness / critical path)
每次改动只改一个变量, 记录哪些假设有效。

═══ OUTPUT ═══
最终给我:
  - 拟合出的参数表
  - 必要的优化 pass 列表
  - 残差为 0 的证明 (所有 test predict == expected)
  - 实现 f(...) 的最简代码
```

---

## 5. 配套代码骨架 (5 段独立可测)

每一层都可以独立调试；残差非 0 时能精确定位是**特征不够**还是**优化 pass 不对**。

```python
import numpy as np
from itertools import combinations

# ---- 1. Parse: 字符串 -> IR ----
def parse(text):
    # 'res1 = var1 + var2' -> ('res1', '+', 'var1', 'var2')
    ...

# ---- 2. Optimize: IR -> IR (可选 pass 组合, IDENTITY 即不动) ----
def optimize(ir, passes=()):
    for p in passes:
        ir = p(ir)
    return ir

# 各 pass 单独写、单独可测
def constant_fold(ir): ...
def dead_code_elim(ir): ...
def common_subexpr(ir): ...
def inline_all(ir): ...

# ---- 3. Featurize: IR -> 特征向量 ----
FEATURE_NAMES = ['n_add', 'n_sub', 'n_mul', 'n_div',
                 'n_assign', 'n_unique_vars', 'peak_live']
def featurize(ir):
    return np.array([...])  # 长度 = len(FEATURE_NAMES)

# ---- 4. Fit: 用所有 test 反推 cost (lstsq 回归) ----
def fit(test_cases, passes=()):
    # test_cases: [(ir, expected_time), ...]
    X = np.stack([featurize(optimize(ir, passes)) for ir, _ in test_cases])
    y = np.array([t for _, t in test_cases])
    coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    return coef, pred, y, np.abs(pred - y).max()

# ---- 5. Search: 枚举 pass 组合找 max_error == 0 ----
ALL_PASSES = [constant_fold, dead_code_elim, common_subexpr, inline_all]
for k in range(len(ALL_PASSES) + 1):
    for combo in combinations(ALL_PASSES, k):
        coef, pred, y, err = fit(test_cases, passes=combo)
        if err < 1e-9:
            print(f"FOUND passes={[p.__name__ for p in combo]}")
            print(f"      coef={dict(zip(FEATURE_NAMES, coef))}")
            break
```

**先用 `passes=()` (即 IDENTITY) 跑一次**——这就是阶段 B 的全部。残差非 0 再进 search 循环，这就是阶段 C。

---

## 6. 心法版 5 步 (面试时脑子里跑的 checklist)

不喂 LLM、自己脑内跑的更短版：

1. **"这题里有没有看起来是常数、其实是未知数的东西？"** — 就是这道题面试官"没有 universal 定义"想点醒你的。
2. **"test 给的数字是验证我，还是定义问题？"** — 如果是后者，**回归**方程组思路立刻启动。
3. **"我能不能把'推规则'和'应用规则'分两步做？"** — 别耦合。先 IDENTITY 推 cost，再回头看 optimize。
4. **"先用最朴素的模型拟合一次，看残差告诉我什么"** — 不要 upfront 上复杂模型。
5. **"残差是系统性还是随机？"** — 系统性 = **漏特征**；随机 = **模型形式错** (线性应该改分段 / max)。

---

## 7. 核心反射 (这题的灵魂金句)

> **"LLM 给的常数永远要问'你怎么得到这个数的'。"**

如果它答"标准做法"或"惯例"，且这个领域**实际上没有标准**，那这个数 100% 是**幻觉**。这道题里 1 和 5 就是典型——LLM 知道乘法比加法贵 (这部分对)，但**具体倍数是它编的** (这部分错)。

**反射动作**: 任何 LLM 给出的没有引用源的具体数值，**先假设是错的**，除非能从问题约束里独立验证。

### AI 协同分工对照表

| 让 AI 做 | 自己做更快 / 更靠谱 |
|----------|---------------------|
| 写 parse / optimize pass 模板 | 把 cost 当未知数的**重新建模** (核心 senior signal) |
| 写 lstsq 拟合 + 残差分析骨架 | 看到残差非 0 后判断"漏特征 vs 模型形式错" |
| 列优化 pass 候选名 (CSE / folding / DCE / inline) | 阶段 B 和 C 解耦的**结构选择** |
| 生成可枚举的 pass 组合代码 | 把 test 当 spec、不当验证手段的**框架翻转** |
| 给 IDENTITY transform 模板 | **"这个数你怎么得到的"反射动作** |

**底线**: AI 帮你写代码 + 列候选；**框架翻转 (test = spec, cost = unknown) 和反射 (LLM 常数永远怀疑) 必须自己讲**。这是 senior signal vs junior signal 的分水岭。

---

## 8. 一图流总结

```
症状: test1/2 跑通, test4+ 全错; LLM 自信给 (1, 5) cost map
        |
        v
重新建模 (test = spec, cost = unknown)
        |
        v
cost_total = f(features(optimize(parse(input))))
        |  4 个组件: 哪些已知 / 哪些未知
        |
        v
阶段 A 建模:
  (a) 数值参数 -> 回归 (lstsq)
  (b) 离散结构 -> 枚举 / 搜索
  (c) 函数形式 -> 线性 / max / 分段
        |
        v
阶段 B (optimize=IDENTITY) lstsq 反推 cost
        |
   残差 == 0 ? -> 直接收工 (cost map 推出)
   残差 != 0 ? -> 阶段 C
        |
        v
阶段 C 枚举 pass 组合 (CSE/folding/DCE/inline)
        |  每种组合重跑阶段 B; 找 err == 0 的组合
        v
反射: LLM 给的没引用源的具体数值 = 默认幻觉
```

**记住**: 这道题的差异化签名 = (1) 把 test 从"验证手段"翻转成"spec 一部分"，(2) 把 cost 从"常量"翻转成"未知参数"，(3) 阶段 B 和 C 解耦先 IDENTITY 推 cost。三件事讲到 + 把"LLM 常数永远怀疑"的反射讲出来 = senior signal。
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
                f"[META-ANC-6] missing keyword {kw!r} -- regenerate"
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
                f"[META-ANC-6] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_compiler_optimization() -> int:
    """Insert or update the Compiler Optimization drawer; return problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-6] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-6] expected Meta company_id=31, got {company_id}"
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
    upsert_meta_anc_compiler_optimization()
