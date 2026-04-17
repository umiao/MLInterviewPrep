"""One-shot: write LC 282 solution notes into problems.notes."""
import sqlite3

NOTES = r'''## LC 282 - Expression Add Operators (Backtracking + `prev` Trick)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### Problem
Given digit string `num` and target `T`, insert `+`, `-`, `*` (no unary, no parens) between digits so the expression equals `T`. Return all such expressions. Numbers cannot have leading zeros (except `"0"` itself).

### Two Decision Axes at Each Position
1. **How many digits** to consume as the next operand (leading-zero constraint).
2. **Which operator** comes before it (`+`/`-`/`*`, or none at the start).

This gives ~4^n raw expressions for n digits, but ~100 of them survive leading-zero pruning. We enumerate via DFS/backtracking.

---

### Approach A: Brute-force DFS + Custom Evaluator (your first version)

Your idea: build the full token list, then evaluate with a custom `myEval` that respects `*` precedence via a stack. **Correct but wasteful** -- we evaluate only at the leaves, so we can't prune mid-branch.

**Why not `eval()`?**
1. **Security**: `eval` on arbitrary strings is dangerous (not relevant here since input is controlled, but interview optics are bad).
2. **Performance**: each `eval` re-parses the string; cannot cache partial results.
3. **Interview expectation**: this problem is specifically designed to test your ability to handle operator precedence manually.
4. **`eval` dependency**: some interview environments (CoderPad without full Python) may not have it; robust code shouldn't rely on it.

**Cleaned-up Version A** (preserving your intent):

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

**Code review of your original**:
- `newList = list(curList)` allocates a fresh copy every recursion -- use immutable append (`tokens + [...]`) or push/pop pattern instead. O(n) copy per step.
- `firstVal = firstVal + (sign * ...)` -- just use `total += sign * ...`.
- The `if n == 1` base case is unnecessary -- the main DFS handles it correctly.
- `print(curExpr)` debug leaked -- remove.
- `maxNumLen = 1 if num[depth] == '0' else n - depth` -- cleaner one-liner.

---

### Approach B: The `prev` Trick (your optimized version, the canonical solution)

The key insight: we don't need to store the token list. We can maintain a running expression value `cur` and the **last additive term** `prev`. When we multiply:
- The already-committed `cur` includes `prev` as its last term.
- The new multiplication means we should have used `prev * x` instead of `prev` as the last term.
- Correction: `new_cur = cur - prev + prev * x`, and the new `prev` is `prev * x` (so further multiplications chain correctly).

This lets us **prune** (though this problem doesn't need it) and evaluate in O(1) per step instead of O(n) via re-parsing.

**Polished Version B**:

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

**Improvements over your B version**:
1. **Push/pop on a shared `expr` list** instead of string concatenation. String concat `expr + '+' + s` allocates a new string every call -- O(n²) total string work. Push/pop + final `"".join` is O(n) total.
2. **`break` on leading zero** (not `continue`) -- once `s = num[i:i+k]` starts with `"0"` and has length > 1, every larger `k` will also start with `"0"`. Break prunes the entire range.

---

### The `prev` Trick, Worked Example

Expression being built: `1 + 2 * 3`. Digit stream: `i=0 x=1`, `i=1 x=2`, `i=2 x=3`.

| Step | op | cur before | prev before | x | new cur | new prev | Interpretation |
|------|----|-----------|-------------|---|---------|----------|----------------|
| i=0  | -  | 0         | 0           | 1 | 1       | 1        | First number. |
| i=1  | +  | 1         | 1           | 2 | 3       | 2        | `1 + 2`. |
| i=2  | *  | 3         | 2           | 3 | 3 - 2 + 2*3 = 7 | 2*3 = 6 | Undo committing `+2`, redo as `+2*3`. Chain-safe: if a `*4` follows, prev=6 gives `7 - 6 + 6*4 = 25` = `1 + 2*3*4`. |

**Invariant**: after processing digits up to `i`, `cur` = full expression value AS IF the last term ended here, and `prev` = value of that last term (signed: positive for +, negative for -). Multiplication modifies the last term by extending it.

---

### Complexity

- **Time**: O(n * 4^n) worst case (at each of n positions, 4 choices: +, -, *, no-op on operand length). Actually bounded tighter by partition choices: O(4^n) expressions, each O(n) to stringify.
- **Space**: O(n) recursion depth + output size.

### Traps & Edge Cases

1. **Leading zeros**: `"00"` is NOT 0, it's two operands. Check `len(s) > 1 and s[0] == '0'` then `break`.
2. **Integer overflow**: constraints say `num.length <= 10` and `target` fits in int32. Python ints are unbounded; in Java/C++ use `long`.
3. **Target = 0, num = "0"**: should return `["0"]`. Both versions handle it via the `i == 0` branch.
4. **No unary minus**: don't start with `-` (your code correctly handles this via the `i == 0` branch).

### Interview Pattern Recognition

Keywords: "insert operators", "evaluate expression", "operator precedence" + "enumerate all expressions" -> **backtracking with running value + `prev` trick**.

Same `prev` trick applies to:
- LC 227 Basic Calculator II (single evaluation without parens)
- LC 772 Basic Calculator III (with parens, recursion)
- LC 494 Target Sum (simpler: only +/-)

### Summary

| Version | How it evaluates | Complexity overhead | Interview-ready? |
|---------|------------------|---------------------|------------------|
| Your A (custom eval) | Only at leaves, via stack | O(n) per leaf | Works, but reviewer will ask "can you avoid re-parsing?" |
| `eval()` | Python built-in | Same as A, plus security smell | No -- explicitly avoid |
| Your B (`prev` trick) | O(1) per recursion step | Optimal | Yes -- canonical answer |
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 282", (NOTES,))
conn.commit()
print(f"[OK] LC 282 notes updated ({len(NOTES)} chars)")
conn.close()
