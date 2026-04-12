"""One-shot: translate LC 282 solution notes to Chinese."""
import sqlite3

NOTES = r'''## LC 282 - Expression Add Operators (Backtracking + `prev` Trick)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/pinterest_recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 题目
给定数字字符串 `num` 和目标值 `T`，在数字之间插入 `+`、`-`、`*`（不允许一元符号、不允许括号），使表达式的求值等于 `T`。返回所有满足条件的表达式。数字不能有前导零（除 `"0"` 本身外）。

### 每个位置上的两个决策轴
1. **消耗多少位数字** 作为下一个 operand（受前导零约束）。
2. **前面用哪个 operator**（`+` / `-` / `*`，或者在开头时不放 operator）。

共有 ~4^n 种原始表达式（n 为数字位数），但经过前导零剪枝后大约只剩 ~100 条可行分支。我们用 DFS / backtracking 枚举。

---

### Approach A: Brute-force DFS + 自定义 Evaluator（你的第一版写法）

思路：先构建完整的 token list，再用一个自定义 `myEval` 通过 stack 处理 `*` 的优先级。**正确但浪费** —— 只在叶子节点上求值，不能在中途剪枝。

**为什么不直接用 `eval()`？**
1. **安全性**：对任意字符串使用 `eval` 很危险（本题输入受控所以问题不大，但在面试中观感差）。
2. **性能**：每次 `eval` 都要重新 parse 字符串；无法缓存部分结果。
3. **面试期望**：这题的设计意图就是考察你手动处理 operator precedence 的能力。
4. **依赖问题**：某些面试环境（CoderPad 等不完整的 Python 环境）可能没有 `eval`；稳健的代码不应依赖它。

**整理后的 Version A**（保留你的意图）：

```python
class Solution:
    def addOperators(self, num: str, target: int) -> list[str]:
        n = len(num)
        ans = []

        def evaluate(tokens: list[str]) -> int:
            # Collapse * first (precedence), then +/-
            stack = []
            for tok in tokens:
                if tok == "*":
                    stack.append("*")
                elif tok in ("+", "-"):
                    stack.append(tok)
                else:  # operand
                    if stack and stack[-1] == "*":
                        stack.pop()
                        stack[-1] = str(int(stack[-1]) * int(tok))
                    else:
                        stack.append(tok)
            # Now only +/- remain, left-to-right
            total, sign = int(stack[0]), 1
            for tok in stack[1:]:
                if tok == "+": sign = 1
                elif tok == "-": sign = -1
                else: total += sign * int(tok)
            return total

        def dfs(i: int, tokens: list[str]) -> None:
            if i == n:
                if evaluate(tokens) == target:
                    ans.append("".join(tokens))
                return
            max_len = 1 if num[i] == "0" else n - i
            for k in range(1, max_len + 1):
                operand = num[i:i + k]
                if i + k == n:
                    dfs(i + k, tokens + [operand])
                else:
                    for op in ("+", "-", "*"):
                        dfs(i + k, tokens + [operand, op])

        dfs(0, [])
        return ans
```

**对你原写法的 code review**：
- `newList = list(curList)` 每次递归都分配一份新 copy —— 应改成 immutable append（`tokens + [...]`）或 push/pop 模式。每一步都 O(n) 拷贝。
- `firstVal = firstVal + (sign * ...)` —— 直接写 `total += sign * ...` 更清爽。
- `if n == 1` 的 base case 没必要 —— 主 DFS 能正确处理。
- `print(curExpr)` 调试语句忘删了 —— 移除。
- `maxNumLen = 1 if num[depth] == '0' else n - depth` —— 一行三元式更简洁。

---

### Approach B: `prev` Trick（你的优化版，也是 canonical 解法）

关键洞察：我们不需要保存 token list。只需维护当前表达式值 `cur` 和**最后一个加法项** `prev`。当遇到乘号时：
- 已经 commit 的 `cur` 里把 `prev` 作为最后一项。
- 新的乘法意味着本应把 `prev * x` 作为最后一项而不是 `prev`。
- 修正：`new_cur = cur - prev + prev * x`，新的 `prev = prev * x`（这样后续继续连乘也能正确链式更新）。

这让我们可以在每一步以 O(1) 的开销求值，而不必 re-parse，也为剪枝提供了条件（虽然本题不需要剪枝）。

**打磨后的 Version B**：

```python
class Solution:
    def addOperators(self, num: str, target: int) -> list[str]:
        n = len(num)
        ans = []

        def dfs(i: int, expr: list[str], cur: int, prev: int) -> None:
            if i == n:
                if cur == target:
                    ans.append("".join(expr))
                return
            for k in range(1, n - i + 1):
                s = num[i:i + k]
                if len(s) > 1 and s[0] == "0":
                    break  # all longer slices also start with 0 -- prune entire branch
                x = int(s)
                if i == 0:
                    expr.append(s)
                    dfs(i + k, expr, x, x)
                    expr.pop()
                else:
                    for op, new_cur, new_prev in (
                        ("+", cur + x,          x),
                        ("-", cur - x,         -x),
                        ("*", cur - prev + prev * x, prev * x),
                    ):
                        expr.append(op); expr.append(s)
                        dfs(i + k, expr, new_cur, new_prev)
                        expr.pop(); expr.pop()

        dfs(0, [], 0, 0)
        return ans
```

**相对你 B 版的改进**：
1. **在共享 `expr` list 上 push/pop** 而不是做字符串拼接。`expr + '+' + s` 每次调用都分配新字符串 —— 整体 O(n²) 的字符串开销。push/pop + 最后一次 `"".join` 则是 O(n)。
2. **前导零时用 `break` 而非 `continue`** —— 一旦 `s = num[i:i+k]` 以 `"0"` 开头且长度 > 1，任何更大的 `k` 也都会以 `"0"` 开头。用 `break` 可以剪掉整段区间。

---

### `prev` Trick 的 worked example

构建表达式：`1 + 2 * 3`。数字流：`i=0 x=1`，`i=1 x=2`，`i=2 x=3`。

| 步骤 | op | cur 之前 | prev 之前 | x | new cur | new prev | 解释 |
|------|----|-----------|-------------|---|---------|----------|----------------|
| i=0  | -  | 0         | 0           | 1 | 1       | 1        | 第一个数。 |
| i=1  | +  | 1         | 1           | 2 | 3       | 2        | `1 + 2`。 |
| i=2  | *  | 3         | 2           | 3 | 3 - 2 + 2*3 = 7 | 2*3 = 6 | 撤销原本 commit 的 `+2`，改成 `+2*3`。链式安全：如果后面再 `*4`，prev=6 给出 `7 - 6 + 6*4 = 25` = `1 + 2*3*4`。 |

**Invariant**：处理完位置 `i` 之后，`cur` = 假设最后一项在此结束时整个表达式的值，`prev` = 该最后一项的值（带符号：`+` 为正、`-` 为负）。乘法通过"延长最后一项"来修改它。

---

### 复杂度

- **Time**：最坏 O(n * 4^n)（n 个位置、每步 4 种选择：+, -, *, 继续拼在当前 operand 上）。更紧的上界是按 partition 枚举：O(4^n) 个表达式，每个 O(n) 做字符串化。
- **Space**：O(n) 递归深度 + output size。

### 易错点与边界情况

1. **前导零**：`"00"` 不是 `0`，而是两个 operand。判断 `len(s) > 1 and s[0] == '0'` 然后 `break`。
2. **整数溢出**：题目约束 `num.length <= 10` 且 `target` 能装进 int32。Python int 无限精度；Java/C++ 需用 `long`。
3. **Target = 0, num = "0"**：应返回 `["0"]`。两版都通过 `i == 0` 分支正确处理。
4. **不允许一元 minus**：开头不能是 `-`（`i == 0` 分支中你的代码已正确处理）。

### 面试模式识别

关键词："insert operators"、"evaluate expression"、"operator precedence" + "枚举所有表达式" -> **backtracking with running value + `prev` trick**。

同样的 `prev` trick 适用于：
- LC 227 Basic Calculator II（单次求值、无括号）
- LC 772 Basic Calculator III（有括号、递归）
- LC 494 Target Sum（更简单：只有 +/-）

### 小结

| 版本 | 求值方式 | 复杂度开销 | Interview-ready？ |
|---------|------------------|---------------------|------------------|
| 你的 A（自定义 eval） | 只在叶子、用 stack | 每个叶子 O(n) | 能过，但 reviewer 会追问"能否避免 re-parse？" |
| `eval()` | Python 内置 | 同 A，另有安全气味 | 不推荐 —— 应明确避免 |
| 你的 B（`prev` trick） | 每一步 O(1) | 最优 | 是 —— canonical answer |
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 282", (NOTES,))
conn.commit()
print(f"[OK] LC 282 notes updated ({len(NOTES)} chars)")
conn.close()
