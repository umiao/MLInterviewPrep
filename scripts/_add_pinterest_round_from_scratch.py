"""Add Pinterest round()-from-scratch custom problem to mle_prep.db.

Source: Pinterest coding round 2025-11 (non-LC). Implement a function that
rounds a decimal number provided as a STRING to the nearest integer WITHOUT
using float() (avoids float overflow and binary-representation surprises).

Idempotent: if a row with this title already exists, updates notes only.

Task: T-P1-402
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "round() from scratch (string input, no float)"
SOURCE = "pinterest_interview,custom"
COMPANY_TAGS = json.dumps(["Pinterest"])
TAGS = json.dumps(["String", "Parsing", "Math", "State Machine"])
PATTERN = "Manual parse (sign / int / dot / frac) + half-up with carry propagation"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
PRIORITY = 2  # P1

DESCRIPTION = """\
[Pinterest coding 2025-11] Implement `my_round(s: str) -> int` that rounds the
decimal number represented by `s` to the nearest integer, WITHOUT calling
`float(s)`. Using float() would silently overflow for very long inputs
(e.g. 400-digit numbers) and introduce binary rounding artefacts
(`float('2.675')` round-half-even differs from decimal half-up).

Half-up rule (away from zero for negatives):
  '2.4'   -> 2
  '2.5'   -> 3
  '-2.5'  -> -3
  '9.5'   -> 10          # carry propagates
  '-.2'   -> 0           # leading dot, no integer part
  '2.'    -> 2           # trailing dot, no fractional part
  '  +3 ' -> 3           # whitespace + explicit sign

Invalid inputs (`""`, `"."`, `"1.2.3"`, `"abc"`) -> ValueError.

Follow-up (T-P1-403): generalize to round at precision p (keep p decimal
digits), which reuses the same parse + carry machinery but stops the carry
at position p instead of the ones place.
"""

SOLUTION_TAG = "[Pinterest round-from-scratch Canonical Solution]"

NOTES = SOLUTION_TAG + r"""

## Problem (Pinterest 2025-11)

Implement `my_round(s: str) -> int`. Rules: half-up (away from zero),
no `float()`, handle leading/trailing-dot forms and signs.

## Solution -- state machine over 4 segments

Parse `s` as [whitespace][sign][int_digits].[frac_digits][whitespace].
Any other character -> `ValueError`. `int_digits` AND `frac_digits` may each
be empty, but NOT both (`"."` is invalid; `"2."` and `".2"` are valid).

After parsing, look only at the FIRST fractional digit `frac[0]`:
- `frac[0] >= '5'` -> add 1 to the integer part (with carry propagation)
- otherwise        -> truncate

The remaining frac digits do not matter for half-up at the ones place
(they cannot flip the decision). They WILL matter in T-P1-403 where we
round at arbitrary precision `p`.

```python
def my_round(s: str) -> int:
    s = s.strip()
    if not s:
        raise ValueError("empty string")

    i, n = 0, len(s)
    neg = False
    if s[i] in "+-":
        neg = s[i] == "-"
        i += 1

    int_part = ""
    while i < n and s[i].isdigit():
        int_part += s[i]
        i += 1

    frac_part = ""
    if i < n and s[i] == ".":
        i += 1
        while i < n and s[i].isdigit():
            frac_part += s[i]
            i += 1

    if i != n:
        raise ValueError(f"unexpected char at {i}: {s!r}")
    if not int_part and not frac_part:
        raise ValueError(f"no digits in {s!r}")
    if not int_part:
        int_part = "0"

    round_up = len(frac_part) > 0 and frac_part[0] >= "5"
    digits = list(int_part)
    if round_up:
        j = len(digits) - 1
        carry = 1
        while j >= 0 and carry:
            d = int(digits[j]) + carry
            if d == 10:
                digits[j] = "0"
                carry = 1
            else:
                digits[j] = str(d)
                carry = 0
            j -= 1
        if carry:
            digits.insert(0, "1")

    mag = int("".join(digits))
    return -mag if (neg and mag != 0) else mag
```

## Why avoid `float()`?

1. **Overflow**: `float("1" + "0"*400)` -> `inf`. Our parser handles arbitrary
   length because we stay in strings / Python int (unbounded).
2. **Binary artefacts**: `float("2.675")` is actually `2.6749999...`, so
   `round(float("2.675"), 2)` gives `2.67`, not `2.68`. Decimal string
   parsing bypasses this entirely.
3. **Locale / encoding**: `float` accepts Unicode digits, NaN, inf, exponent
   forms; the interviewer usually wants STRICT decimal-only.

## Complexity

O(|s|) time, O(|s|) extra space for the parsed digit strings.

## Edge-case matrix

| Input    | Output | Notes                                   |
|----------|--------|-----------------------------------------|
| `"2.4"`  | 2      | truncate                                |
| `"2.5"`  | 3      | half-up                                 |
| `"-2.5"` | -3     | half away from zero (sign applied last) |
| `"9.5"`  | 10     | carry propagates                        |
| `"99.9"` | 100    | carry to new digit                      |
| `"-.2"`  | 0      | empty int_part -> "0"                   |
| `"-.5"`  | -1     | empty int_part rounds up then negated   |
| `"-0.5"` | -1     | explicit "-0" + half-up                 |
| `"2."`   | 2      | empty frac_part -> truncate             |
| `" +3 "` | 3      | trim whitespace, accept '+'             |
| `""`     | raise  | empty                                   |
| `"."`    | raise  | no digits                               |
| `"1.2.3"`| raise  | two dots                                |
| `"1e2"`  | raise  | exponent not supported                  |

**-0 normalization**: when `mag == 0`, we must NOT return `-0`. Python `int`
does not distinguish, but the check `neg and mag != 0` keeps the contract
clear (and matters when converting back to string for the `my_round_str`
variant).

## Chinese Notes (中文解析)

**题意**: 手写 `round(s)` 接收字符串, 禁用 `float()`, 半进位 (half-up, 远离零)。

**为什么不能用 `float`**:
- 长字符串溢出成 `inf` (超过 ~1.8e308)。
- 二进制浮点的老梗: `float('2.675')` 其实是 `2.6749999...`, 用原生 `round`
  会四舍五不入, 背离面试官要的十进制半进位。
- 面试官考的是 *解析 + 进位链* 的手感, 不是库函数调用。

**状态机四段**: [空白][符号][整数位].[小数位][空白]。任何非法字符 -> 抛错。
整数和小数**允许各自为空, 但不能同时为空** (纯 `"."` 非法, `"2."` 和 `".2"`
合法)。

**半进位判定只看 `frac[0]`**: 个位的半进位只看第一个小数位, 后续位不影响决策。
(到了 T-P1-403 按精度 p 四舍五入时, 才需要看第 p 位那一位。)

**进位链**: 从最低位 (ones) 开始, `d+1 == 10` 就置 0 并继续进位, 最后若仍有
进位, 在最前面 insert 一个 `"1"` (对应 `99 -> 100`)。

**符号最后施加**: 永远先算幅值再加符号, 避免 `-0` / 负数进位两套写法。
`neg and mag != 0` 这个判断是为了避免返回 `-0` (Python int 不区分, 但转回
字符串时会出 `"-0"` 的丑格式)。

**常见坑**:
- `"-.5"` 很容易返回 `0`: 因为整数部分为空时不小心早退。修法: 空 int_part
  先补 `"0"` 再走常规流程。
- `"9.5"` 返回 `10` 是对进位链的基本检查, 面试常问。
- `"99.5"` -> `100` 检查进位扩位 (新增最高位)。

**追问**:
- **任意精度 p** (T-P1-403): 同样的解析, 进位起点从 ones 改为 `frac[p-1]`
  所在的位置, 其余逻辑不变。
- **科学计数法** (`"1.5e2"`): 再多一个解析段, 把指数乘到整数/小数边界上
  (或者把小数点手动移动 e 位)。
- **流式输入** (很长的字符串, 不能一次装入): 逐字符状态机, 维护
  (sign, int_buf, frac_seen_first, carry_decision) 即可, 空间 O(1) 附加。

## Self-Test (smoke)

```python
assert my_round("2.4") == 2
assert my_round("2.5") == 3
assert my_round("-2.5") == -3
assert my_round("9.5") == 10
assert my_round("99.5") == 100
assert my_round("-.2") == 0
assert my_round("-.5") == -1
assert my_round("-0.5") == -1
assert my_round("2.") == 2
assert my_round(" +3 ") == 3
assert my_round("0.0") == 0
for bad in ["", ".", "1.2.3", "1e2", "abc", "- 2", "+-1"]:
    try:
        my_round(bad); raised = False
    except ValueError:
        raised = True
    assert raised, bad
```
"""


def upsert() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "SELECT id, notes FROM problems WHERE title = ? AND leetcode_id IS NULL",
        (TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now(UTC).isoformat()

    if row is None:
        cur.execute("SELECT MAX(id) FROM problems")
        next_id = (cur.fetchone()[0] or 0) + 1
        cur.execute(
            """
            INSERT INTO problems (
                id, leetcode_id, title, url, difficulty, tags, pattern,
                category, source, company_tags, priority, is_completed,
                comfort_level, created_at, description, notes
            ) VALUES (?, NULL, ?, NULL, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)
            """,
            (
                next_id,
                TITLE,
                DIFFICULTY,
                TAGS,
                PATTERN,
                CATEGORY,
                SOURCE,
                COMPANY_TAGS,
                PRIORITY,
                now,
                DESCRIPTION,
                NOTES,
            ),
        )
        print(f"[INSERT] id={next_id} title={TITLE!r}")
    else:
        pid, existing_notes = row
        if existing_notes and SOLUTION_TAG in existing_notes:
            print(f"[SKIP] id={pid} already has canonical solution")
        else:
            merged = (existing_notes + "\n\n---\n\n" + NOTES) if existing_notes else NOTES
            cur.execute(
                "UPDATE problems SET notes = ?, description = ? WHERE id = ?",
                (merged, DESCRIPTION, pid),
            )
            print(f"[UPDATE] id={pid} notes appended")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    upsert()
