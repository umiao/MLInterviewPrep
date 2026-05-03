"""Replace 1074 notes with shift-based refactor (user proposal 2026-04-15).

Insight: round to multiple of p = 10**k is mathematically equivalent to
shifting the decimal point by -k, rounding to the nearest integer
(= invoke 1073's core carry loop), then shifting back by k.

This eliminates the cut-index arithmetic and the `kept==[] -> ['1']` edge.
Validated by `_smoke_shift_reuse_1074.py` (29/29 asserts).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NOTES_1074 = r'''[Pinterest round-by-precision Shift-Based Solution 2026-04-15]

## 核心洞察

`round_p(x) = round(x / p) * p`，当 `p = 10**k` 时等价于：
1. 把 `x` 的小数点向左移 `k` 位（`k<0` 时向右移）
2. 对移位后的数做 round-to-nearest-int（**直接复用 1073 的 `my_round`**）
3. 把小数点右移 `k` 位还原

在字符串上，"移小数点"就是在 `int_s` 和 `frac_s` 之间搬字符：
- 向右借 `n` 位 → `int_s + frac_s[:n].ljust(n, '0')`, `frac_s[n:]`
- 向左借 `n` 位 → `int_s[:-n]`, `int_s[-n:] + frac_s`

这样 1073 的进位链**一字不改**地被复用，1074 的新增复杂度被完全隔离在
"shift 和 unshift"两个对称步骤里，`cut` 索引算术和 `kept == [] → ['1']` 这条
特判都自然消失。

```python
def _shift_decimal(int_s: str, frac_s: str, shift: int) -> tuple[str, str]:
    """把小数点向右移 shift 位（shift<0 则向左）。"""
    if shift >= 0:
        borrowed = frac_s[:shift].ljust(shift, "0")
        return int_s + borrowed, frac_s[shift:]
    n = -shift
    if n >= len(int_s):
        return "0", "0" * (n - len(int_s)) + int_s + frac_s
    return int_s[:-n], int_s[-n:] + frac_s


def _precision_exponent(p: str) -> int:
    pi, _, pf = p.partition(".")
    if pf:
        return -len(pf)
    return len(pi) - len(pi.rstrip("0") or "0")


def round_by_precision(s: str, p: str) -> str:
    s = s.strip()
    neg = s.startswith("-")
    if s[:1] in "+-":
        s = s[1:]
    int_s, _, frac_s = s.partition(".")
    int_s = int_s or "0"
    k = _precision_exponent(p)

    # 左移 k 位（实现为 _shift_decimal 的 shift=-k）
    shifted_int, shifted_frac = _shift_decimal(int_s, frac_s, -k)

    # 复用 my_round 核心：对 (shifted_int, shifted_frac) 半进位
    digits = list(shifted_int)
    if shifted_frac[:1] >= "5":
        i, carry = len(digits) - 1, 1
        while i >= 0 and carry:
            d = int(digits[i]) + carry
            digits[i], carry = str(d % 10), d // 10
            i -= 1
        if carry:
            digits.insert(0, "1")
    rounded = "".join(digits)

    # 右移 k 位还原
    if k >= 0:
        out = rounded + "0" * k
    else:
        n = -k
        if n >= len(rounded):
            out = "0." + "0" * (n - len(rounded)) + rounded
        else:
            out = rounded[:-n] + "." + rounded[-n:]

    left, _, right = out.partition(".")
    left = left.lstrip("0") or "0"
    out = f"{left}.{right}" if right else left
    return "-" + out if neg and out != "0" else out
```

## 为什么这个分解更优

**前一版做法**：在拼接后的 `digits` 串上算 `cut = dot - k`，在 `digits[:cut]` 上
做进位，溢出要 `insert('1')` + `cut += 1`，重组时按 `k` 正负分两支还要切小数点——
所有步骤都纠缠在一起。

**shift 版**：
- **职责分离**：`_shift_decimal` 只搬字符，对"舍入"一无所知。`my_round` 的进位
  循环只处理"截到整数"，对"精度 `k`"一无所知。两者正交。
- **复用 1073**：进位链一字不改，面试时白板上先写 1073，再加一个 `_shift_decimal`
  就完事了。
- **`cut == 0` 的召唤新最高位**：不再需要特判——shift 后 `shifted_int` 可能是
  `"0"`，进位时 `digits=['0']` 自然走标准循环，进位后变 `['1']`，unshift 后得
  `"100"`，全流程同构。
- **k 正负**：两条路径（`k>=0` 补零 vs `k<0` 插小数点）仍在，但现在只是
  unshift 的镜像，不耦合进位逻辑。

## 关键边界（29/29 通过）

| 输入                      | 输出     | 关键点                                      |
|---------------------------|----------|--------------------------------------------|
| `s='12567', p='100'`      | `'12600'`| 左借 2 位 → `my_round('125.67')=126` → 补 2 个 0 |
| `s='50', p='100'`         | `'100'`  | 左借 2 位但 int 不够 → `'0','50'` → round 成 `'1'` → 补 `'00'` |
| `s='49', p='100'`         | `'0'`    | 同上但 frac[0]='4'<'5' → rounded='0' → 补零后归一 |
| `s='9.99', p='0.1'`       | `'10.0'` | 右借 1 位 → `my_round('99.9')=100` → 左移 1 位 → `'10.0'` |
| `s='0.005', p='0.01'`     | `'0.01'` | 右借 2 位 → `my_round('00.5')=1` → 左移 2 位 → `'0.01'` |
| `s='-0.05', p='0.1'`      | `'-0.1'` | 符号与幅值正交处理                           |
| `s='0.00049', p='0.0001'` | `'0.0005'`| 深层右移 4 位                               |

## 与 1073 的关系（最干净的表述）

1073 是本题的 `k=0` 特例：
- `k=0` 时 `_shift_decimal(int_s, frac_s, 0)` 直接返回 `(int_s, frac_s)`，
  进位链就是 1073 本体，unshift 也是恒等。
- `k!=0` 只在前后各加一层字符串搬运，进位逻辑纹丝不动。

## 复杂度

`O(n)` 时间空间，`n = len(s) + |k|`（`k>0` 时 unshift 要补 `k` 个 0）。

## 实现要点

- `_shift_decimal` 的 `n >= len(int_s)` 分支：左借但 int 不够借，左边补零；
  这是 `s='50', p='100'` 这种"被整除到 0.5"能工作的关键。
- `shifted_int = '0'` 在进位时的 `digits=['0']` 情况不需要特判——0+1=1 自然走通。
- Unshift 的 `n >= len(rounded)` 分支：rounded 太短，左边补零；对应
  `s='0.005', p='0.01'` 这类 `rounded='1', k=-2` 输出 `'0.01'` 的情形。

## 45 秒口播

> "`round_p(x) = round(x/p) * p`，`p = 10**k` 时就是"把小数点左移 `k` 位 → 截成
> 整数 → 右移 `k` 位还原"。字符串上就是 `int_s` 和 `frac_s` 互相搬字符：左移就是
> `int_s + frac_s 的前 k 位`，右移是 `int_s 的末 k 位` 并回 `frac_s`。进位链完全
> 沿用 1073，一字不改。`k=0` 时两次搬运都是恒等，所以 1073 天然是 `k=0` 的特例。
> `s='50', p='100'` 这种被整除到 0.5 的情形，shift 后是 `('0','50')`，`my_round`
> 给 `1`，再补两个零得到 `'100'`——不需要任何特判。O(n)。"
'''


def upsert() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.execute("UPDATE problems SET notes = ? WHERE id = ?", (NOTES_1074, 1074))
    conn.commit()
    print(f"[UPDATE] id=1074 rows={cur.rowcount} notes_len={len(NOTES_1074)}")
    conn.close()


if __name__ == "__main__":
    upsert()
