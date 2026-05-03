"""Replace notes for problems 1073 / 1074 with simplified partition-based solutions.

Rationale: user feedback 2026-04-15 -- the original state-machine parsers were
over-engineered; `str.partition('.')` plus a single carry pass is clearer and
avoids the excessive `raise ValueError` paths. Validated by
`_smoke_simplified_1073_1074.py` (23/23 pass).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NOTES_1073 = r"""[Pinterest round-from-scratch Simplified Solution 2026-04-15]

## 简化思路

原版写了一个逐字符的 `while` 状态机 + 一堆 `raise ValueError`，啰嗦且白板上容易写错。
观察：字符串结构就是 `[符号][整数部分].[小数部分]`，`str.partition('.')` 一次切开，
整数/小数各自可为空，用 `frac[:1] >= '5'` 直接处理"空串 < '5'"这条边界。

半进位判定只看小数第一位；进位链从最低位向前传，传到顶还有进位就在最前面插 `'1'`。
符号最后施加，`neg and mag` 这个短路判断同时处理 `-0` 归正。

```python
def my_round(s: str) -> int:
    s = s.strip()
    neg = s.startswith("-")
    if s[:1] in "+-":
        s = s[1:]
    int_s, _, frac_s = s.partition(".")
    digits = list(int_s or "0")
    if frac_s[:1] >= "5":
        i, carry = len(digits) - 1, 1
        while i >= 0 and carry:
            d = int(digits[i]) + carry
            digits[i], carry = str(d % 10), d // 10
            i -= 1
        if carry:
            digits.insert(0, "1")
    mag = int("".join(digits))
    return -mag if (neg and mag) else mag
```

## 为什么不用 `float()`

1. **溢出**：`float("1" + "0"*400)` → `inf`。字符串解析保持任意精度。
2. **二进制伪像**：`float("2.675")` 实际是 `2.6749999...`，`round` 会给 `2.67` 而非 `2.68`。
3. **面试意图**：考察解析 + 进位链的手感，不是库函数。

## 关键细节

- `frac_s[:1] >= '5'` 是个小技巧：空串切片返回 `''`，`'' < '5'` 为真，所以空小数部分
  自动走截断分支，不需要 `len(frac_s) > 0` 这种显式判断。
- `int_s or "0"` 一行处理 `".5"` / `"-.5"` 这种空整数部分的输入。
- 进位链用 `d % 10` 和 `d // 10` 比 `if d == 10: ... else: ...` 的写法短一半。
- `neg and mag` 同时承担两个职责：负号施加 + 避免返回 `-0`。

## 复杂度

`O(|s|)` 时间空间。

## 边界矩阵

| 输入     | 输出 | 说明                        |
|----------|------|----------------------------|
| `"2.4"`  | 2    | 截断                        |
| `"2.5"`  | 3    | half-up                    |
| `"-2.5"` | -3   | 远离零                      |
| `"9.5"`  | 10   | 进位传播                    |
| `"99.5"` | 100  | 进位扩到新最高位             |
| `"-.5"`  | -1   | 空整数补 `"0"` 后走常规      |
| `"2."`   | 2    | 空小数自动走截断             |
| `" +3 "` | 3    | trim 空白，接受 `+`          |
| `"0.0"`  | 0    | `neg=False`，返回 0          |
| `"-0"`   | 0    | `neg and mag(=0)` 为假，归正 |

## 面试取舍

非法输入分类（`""` / `"."` / `"1.2.3"` / `"abc"`）原版用 `raise ValueError`
严格拦截；简化版默认信任输入，遇到 `"1.2.3"` 的二次 `.` 会被 `partition` 只切第一次
从而误判（`"1"` + `"2.3"`）。白板上面试官通常会问"需要处理非法输入吗"，答"是"再加
一行 `if s.count('.') > 1: raise ValueError` 即可。不要在 baseline 里先写死。

## 45 秒口播

> "`str.partition('.')` 切成整数部分和小数部分；`frac[:1] >= '5'` 决定是否进位，
> 空串自然小于 `'5'` 所以不需要显式长度判断。进位链从最低位用 `d%10` / `d//10` 向前
> 传，传到顶还有进位就在最前面插 `'1'`。符号最后施加，`neg and mag` 同时避免返回 `-0`。
> 空整数部分用 `int_s or '0'` 一行兜住。O(|s|) 时间空间。1074 是这个解的推广：把进位
> 起点从末尾挪到第 `p` 位。"
"""


NOTES_1074 = r"""[Pinterest round-by-precision Simplified Solution 2026-04-15]

## 简化思路

和 1073 共享同一条骨架：`partition('.')` 解析 + 单趟进位。多出的只是"按 `k` 定位
`cut`"的索引计算 + 按 `k` 切回整数/小数的重组。

**关键观察**：把 `int_s` 和 `frac_s` 拼成一条 digits 串，记 `dot = len(int_s)` 为首个
小数位下标。`p = 10**k`，则首个被丢弃的位置 `cut = dot - k`：
- `p='100'` (k=2)：cut 往左退 2 位 → 舍到百位
- `p='0.01'` (k=-2)：cut 往右推 2 位 → 保留 2 位小数

```python
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
    k = _precision_exponent(p)

    digits = list((int_s or "0") + frac_s)
    dot = len(int_s or "0")
    cut = dot - k

    if cut < 0:
        return "0"

    kept = digits[:cut]
    if cut < len(digits) and digits[cut] >= "5":
        if not kept:
            kept = ["1"]
        else:
            i, carry = len(kept) - 1, 1
            while i >= 0 and carry:
                d = int(kept[i]) + carry
                kept[i], carry = str(d % 10), d // 10
                i -= 1
            if carry:
                kept.insert(0, "1")
                cut += 1

    if k >= 0:
        out = "".join(kept) + "0" * k
    else:
        head = "".join(kept[: cut + k]) or "0"
        tail = "".join(kept[cut + k :]).ljust(-k, "0")
        out = head + "." + tail

    if "." in out:
        left, right = out.split(".")
        left = left.lstrip("0") or "0"
        out = f"{left}.{right}"
    else:
        out = out.lstrip("0") or "0"

    return "-" + out if (neg and out != "0") else out
```

## 算法步骤

1. 解析 `s` 为 `(neg, int_s, frac_s)` —— `partition('.')` 一次到位。
2. 解析 `p` 得到 `k`（`p = 10**k`）。
3. 拼 digits 串，记 `dot = len(int_s or '0')`，`cut = dot - k`。
4. `cut < 0` 直接返回 `'0'`（舍入位在最高位之左）。
5. `kept = digits[:cut]`；若 `digits[cut] >= '5'`：
   - `kept` 为空（cut == 0）→ `kept = ['1']`（对应 `50` round 到百位 → `100`）。
   - 否则在 `kept` 末尾做标准进位链，溢出就 `insert('1')` 且 `cut += 1`。
6. 按 `k` 重组：`k >= 0` 直接补 `k` 个零；`k < 0` 在 `kept[:cut+k]` 和 `kept[cut+k:]` 之间插小数点，小数部分用 `ljust(-k, '0')` 保尾零。
7. 清前导零、加回符号。

## 关键边界

| 输入                      | 输出     | 说明                                  |
|---------------------------|----------|---------------------------------------|
| `s='12567', p='100'`      | `'12600'`| 常规进位                              |
| `s='1234.678', p='0.1'`   | `'1234.7'` | 保 1 位小数                          |
| `s='1234.678', p='0.01'`  | `'1234.68'`| 保 2 位小数                          |
| `s='99.5', p='1'`         | `'100'`  | 进位扩位（等价于 1073）                |
| `s='-0.05', p='0.1'`      | `'-0.1'` | 远离零                                |
| `s='49', p='100'`         | `'0'`    | `digits[cut]='4'<'5'`，kept 为空       |
| `s='50', p='100'`         | `'100'`  | cut==0 且需进位 → `kept=['1']`         |
| `s='9.99', p='0.1'`       | `'10.0'` | 进位跨越小数点                        |
| `s='0.005', p='0.01'`     | `'0.01'` | 末位半进位                            |

## 与 1073 的关系

1073 是本题 `p='1'`（`k=0`）的特例。骨架完全一样：
- 1073 的 "`frac_s[:1] >= '5'`" 等价于本题的 "`digits[cut] >= '5'`"（因为 `cut=dot` 时就是首个小数位）。
- 1073 的进位链只作用在 `int_s`；本题的进位链作用在 `digits[:cut]`，溢出时同样 `insert('1')`。
- 多出的复杂度都在"重组"那一步，因为 1074 需要按 `k` 还原成字符串（带保留的尾零）。

## cut == 0 的坑

这是本题唯一比 1073 新增的边界：当 `cut == 0` 且需要进位时，`kept` 是空列表，不能直接
跑进位循环。单独处理成 `kept = ['1']` 即可——对应"`50` round 到百位 → `100`"这类把
一个完全的新最高位召唤出来的情形。

## 复杂度

`O(n)` 时间空间，`n = len(s)`。

## 面试取舍

- `_precision_exponent` 内部只处理 `p = 10**k` 的合法形式（题目保证），没加校验。
- 负零归正：`out != '0'` 一条兜住；若 `out` 形如 `'0.0'`（拖尾零），`out != '0'` 为真，
  会输出 `'-0.0'`——可以多加 `set(out) <= {'0','.'}` 做 strict 归正，但面试里先问清楚
  tie-break 语义再决定。
- 结果的尾零语义："保留 `p` 暗示的位数"，用 `ljust(-k, '0')` 一行保住（`1234.7` 而不是 `1234.700`）。

## 45 秒口播

> "`p = 10**k`，`k` 从 `p.partition('.')` 里拿：有小数部分就是 `-len(frac)`，否则是
> 尾零个数。把 `int_s + frac_s` 拼成 digits 串，记 `cut = dot - k`，首个被丢弃位就
> 在那。`digits[cut] >= '5'` 就进位：若 `kept` 为空（cut==0）直接 `['1']`，否则标准
> 进位链，溢出 `insert('1')` 且 `cut += 1`。重组按 `k >= 0` 补零、`k < 0` 插小数点，
> 小数位用 `ljust(-k, '0')` 保尾零。O(n) 时间空间。1073 就是 `k=0` 的特例。"
"""


def upsert() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    for pid, notes in ((1073, NOTES_1073), (1074, NOTES_1074)):
        cur.execute("UPDATE problems SET notes = ? WHERE id = ?", (notes, pid))
        print(f"[UPDATE] id={pid} rows={cur.rowcount} notes_len={len(notes)}")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    upsert()
