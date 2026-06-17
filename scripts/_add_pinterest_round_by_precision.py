"""Add Pinterest round-by-precision custom problem to mle_prep.db.

Source: Pinterest coding round 2025-11 (non-LC). Given number string `s` and
precision string `p` (a power of 10, e.g. '100', '10', '1', '0.1', '0.01'),
round `s` to the nearest multiple of `p` as a STRING. Generalizes T-P1-402
(round()-from-scratch) to arbitrary precision.

Idempotent: if a row with this title already exists, updates notes only.

Task: T-P1-403
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "round by precision p (string s, precision p)"
SOURCE = "pinterest_interview,custom"
COMPANY_TAGS = json.dumps(["Pinterest"])
TAGS = json.dumps(["String", "Parsing", "Math", "Rounding"])
PATTERN = "Locate round position from p=10^k, carry-propagate across int/frac boundary"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
PRIORITY = 2  # P1

DESCRIPTION = """\
[Pinterest coding 2025-11, follow-up to T-P1-402] Implement
`round_by_precision(s: str, p: str) -> str` that rounds the decimal number
represented by `s` to the nearest multiple of `p`, where `p` is a power of 10
given as a string (e.g. '100', '10', '1', '0.1', '0.01'). Return the result
as a string. No `float()` (overflow + binary-rep artefacts).

Examples:
  s='12567',    p='100'  -> '12600'
  s='1234.678', p='0.1'  -> '1234.7'
  s='1234.678', p='0.01' -> '1234.68'
  s='99.5',     p='1'    -> '100'
  s='-0.05',    p='0.1'  -> '-0.1'   (half away from zero)
  s='49',       p='100'  -> '0'
  s='50',       p='100'  -> '100'

Half-up rule (away from zero). Carry propagation may cross the decimal
boundary (e.g. '9.99' at p='0.1' -> '10.0').
"""

SOLUTION_TAG = "[Pinterest round-by-precision Canonical Solution]"

NOTES = SOLUTION_TAG + r"""

## Problem (Pinterest 2025-11, follow-up)

Generalize `my_round(s)` (T-P1-402) from "round to ones" to "round to any
power-of-10 precision `p`". `p` is itself a string, always of the form
`10**k` for some integer `k` (positive, zero, or negative).

## Key insight -- find `k`, the round position

Let `k` be the exponent so that `p == 10**k`.

- `p = '100'`   -> `k = 2`   (two zeros after the leading '1')
- `p = '10'`    -> `k = 1`
- `p = '1'`     -> `k = 0`   (degenerate: same as T-P1-402)
- `p = '0.1'`   -> `k = -1`  (one digit after '.')
- `p = '0.01'`  -> `k = -2`

Mechanical rule:
- If `p` contains `.`: `k = -len(frac_part_of_p)`.
- Otherwise:          `k =  len(p) - 1`.

(We trust the contract that `p` is a power of 10; in a strict variant you
would also assert `p` matches `^10*$` or `^0\.0*1$`.)

## Algorithm

1. Parse `s` into `(neg, int_part, frac_part)` using the same 4-segment
   state machine as T-P1-402 (whitespace / sign / int digits / '.' / frac
   digits / trailing whitespace).
2. Identify the **round digit** -- the first digit to the RIGHT of position
   `k`. Two cases:
   - `k >= 0`: the round digit is `int_part[len(int_part) - k]` (the digit
     just below the kept prefix). If missing, treat as `'0'` and pad.
   - `k <  0`: the round digit is `frac_part[-k]` (0-indexed; we keep
     `-k` frac digits). Pad with `'0'` if frac is shorter.
3. If `round_digit >= '5'`, add 1 at position `k` and propagate carry
   leftward across frac -> int boundary (identical carry chain to T-P1-402,
   just with a different starting index).
4. Zero-out (k>=0) or truncate (k<0) everything to the right of position k.
5. Reattach the sign, unless the magnitude ended up at zero (avoid `-0`).

```python
def round_by_precision(s: str, p: str) -> str:
    # ---- determine k from p ----
    if "." in p:
        _, pfrac = p.split(".", 1)
        k = -len(pfrac)
    else:
        k = len(p) - 1

    # ---- parse s (same state machine as T-P1-402) ----
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
        int_part += s[i]; i += 1
    frac_part = ""
    if i < n and s[i] == ".":
        i += 1
        while i < n and s[i].isdigit():
            frac_part += s[i]; i += 1
    if i != n:
        raise ValueError(f"bad char at {i}: {s!r}")
    if not int_part and not frac_part:
        raise ValueError(f"no digits in {s!r}")
    if not int_part:
        int_part = "0"

    # ---- split digits at position k ----
    if k >= 0:
        # Pad int_part with leading zeros so it has > k digits.
        if len(int_part) <= k:
            int_part = "0" * (k + 1 - len(int_part)) + int_part
        keep_len = len(int_part) - k
        kept_int = list(int_part[:keep_len])
        if keep_len < len(int_part):
            round_digit = int_part[keep_len]
        else:
            round_digit = frac_part[0] if frac_part else "0"
        kept_frac: list[str] = []
    else:
        want_frac = -k
        if len(frac_part) < want_frac + 1:
            frac_part = frac_part + "0" * (want_frac + 1 - len(frac_part))
        kept_int = list(int_part)
        kept_frac = list(frac_part[:want_frac])
        round_digit = frac_part[want_frac]

    # ---- carry if half-up ----
    if round_digit >= "5":
        carry = 1
        j = len(kept_frac) - 1
        while j >= 0 and carry:
            d = int(kept_frac[j]) + carry
            if d == 10:
                kept_frac[j] = "0"; carry = 1
            else:
                kept_frac[j] = str(d); carry = 0
            j -= 1
        j = len(kept_int) - 1
        while j >= 0 and carry:
            d = int(kept_int[j]) + carry
            if d == 10:
                kept_int[j] = "0"; carry = 1
            else:
                kept_int[j] = str(d); carry = 0
            j -= 1
        if carry:
            kept_int.insert(0, "1")

    # ---- reassemble ----
    int_str = "".join(kept_int).lstrip("0") or "0"
    if k >= 0:
        magnitude = int_str + "0" * k
    else:
        magnitude = int_str + "." + "".join(kept_frac)

    # -0 guard: check if magnitude is all-zero.
    if all(c in "0." for c in magnitude):
        return magnitude if "." in magnitude else "0"
    return ("-" + magnitude) if neg else magnitude
```

## Why this generalizes cleanly

The T-P1-402 code is exactly `k = 0` of this routine: `keep_len = len(int_part)`,
`round_digit = frac_part[0] if frac_part else '0'`, carry starts at the ones
place. Every other `k` shifts the round position left (k>0) or right (k<0)
without changing the carry machinery.

## Edge-case matrix

| s          | p       | k  | Output   | Notes                                  |
|------------|---------|----|----------|----------------------------------------|
| '12567'    | '100'   |  2 | '12600'  | basic integer rounding                 |
| '12549'    | '100'   |  2 | '12500'  | round_digit '4' -> truncate            |
| '12550'    | '100'   |  2 | '12600'  | exact half -> up                       |
| '49'       | '100'   |  2 | '0'      | below half, pads to '049'              |
| '50'       | '100'   |  2 | '100'    | carries across pad, lstrip keeps '1'   |
| '1234.678' | '0.1'   | -1 | '1234.7' | basic decimal rounding                 |
| '1234.678' | '0.01'  | -2 | '1234.68'| 2 dp                                   |
| '9.99'     | '0.1'   | -1 | '10.0'   | carry crosses int/frac boundary        |
| '99.95'    | '0.1'   | -1 | '100.0'  | carry extends int width                |
| '-0.05'    | '0.1'   | -1 | '-0.1'   | half away from zero for negatives      |
| '0.04'     | '0.1'   | -1 | '0.0'    | preserves requested precision of zero  |
| '2.5'      | '1'     |  0 | '3'      | degenerate: same as T-P1-402           |

Invalid inputs (empty s, double dot, letters) -> `ValueError`, same as T-P1-402.

## Complexity

O(|s|) time, O(|s|) extra space. `p` is tiny (bounded by int-ness test).

## Common pitfalls

- **Forgetting to pad `int_part`** when `len(int_part) <= k`. E.g. `s='49',
  p='100'`: without left-pad, `keep_len = 0` and you would index out of range.
- **Not padding `frac_part`** when shorter than `-k + 1`. E.g. `s='1.2',
  p='0.001'`: need to treat missing digits as `'0'`.
- **Losing leading zeros on magnitude stringify**: use `lstrip('0') or '0'`
  so `'000'` becomes `'0'`, not empty.
- **`-0` for inputs like `'-0.04', p='0.1'`**: after carry the magnitude is
  `'0.0'`; the all-zero guard prevents emitting `'-0.0'`.
- **Trailing zeros in frac**: the contract preserves them (`'0.0'`, not `'0'`)
  because the caller asked for precision `p` -- trimming would lose it.

## Chinese Notes (中文解析)

**题意**: 在 T-P1-402 的基础上再加一个精度字符串 `p`, `p` 一定是 10 的整数次幂
(`'100'`, `'10'`, `'1'`, `'0.1'`, `'0.01'` ...)。返回按 `p` 四舍五入后的**字符串**。

**核心**: 先算出 `p == 10**k` 的 `k`。
- `p` 含 `.`: `k = -len(p 的小数部分)`。
- 否则:       `k = len(p) - 1` (数末尾有几个 0)。

**判定点 `round_digit`**:
- `k >= 0`: 取 `int_part` 中"被保留前缀"的下一位 (不够就补 '0' 向左 pad)。
- `k <  0`: 取 `frac_part[-k]` (即想保留 `-k` 位小数, 看第 `-k+1` 位决定进位)。

**进位链**: 起点从 `kept_frac` 最右端开始, 进位可以跨越小数点进入 `kept_int`,
再继续向左; 最后还有进位就在最前面插 `'1'`。和 T-P1-402 的进位完全同构。

**去零规范**:
- 保留前缀的前导零要去掉: `'0056' -> '56'`, 但全零要留 `'0'`。
- 小数部分的尾随零**必须保留** (`'9.99', p='0.1' -> '10.0'`), 因为调用方要的
  就是 `p` 位精度; 砍掉就失去了精度语义。
- `-0` 防护: 若整条 magnitude 都是 `0`/`.`, 不加负号。

**常见面试追问**:
- **任意十进制精度 (例如 `p='0.25'`)**: 不再是 10 的幂, 需要做乘法/除法式的
  校准 (把 s 看成 N*p + r, 比较 r 和 p/2)。相当于换一个数制。
- **Banker's rounding (round-half-to-even)**: 只需把 "round_digit >= '5'" 改成
  "round_digit > 5 或 (== 5 且 kept 末位是奇数 或 后续还有非零)"。
- **流式 s (超长)**: 状态机可以一边读一边决定: 遇到整数段超过 `len + k` 长度
  时就确定保留位置, 不必等读完。

**不用 `Decimal`**:
- `Decimal` 可以直接 `q = Decimal(p); s.quantize(q, ROUND_HALF_UP)` 解决, 但
  面试官明显是想考**手写进位链** + **字符串下标对齐**, 所以禁用 `Decimal`
  通常是隐含规则 (和 T-P1-402 禁用 `float` 一致)。

## Self-Test (smoke)

```python
assert round_by_precision('12567',    '100')  == '12600'
assert round_by_precision('12549',    '100')  == '12500'
assert round_by_precision('12550',    '100')  == '12600'
assert round_by_precision('49',       '100')  == '0'
assert round_by_precision('50',       '100')  == '100'
assert round_by_precision('1234.678', '0.1')  == '1234.7'
assert round_by_precision('1234.678', '0.01') == '1234.68'
assert round_by_precision('9.99',     '0.1')  == '10.0'
assert round_by_precision('99.95',    '0.1')  == '100.0'
assert round_by_precision('-0.05',    '0.1')  == '-0.1'
assert round_by_precision('0.04',     '0.1')  == '0.0'
assert round_by_precision('2.5',      '1')    == '3'
assert round_by_precision('-2.5',     '1')    == '-3'
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
