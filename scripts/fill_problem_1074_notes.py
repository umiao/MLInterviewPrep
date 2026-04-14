"""Fill Chinese solution notes for problem 1074 (round_by_precision) — T-P0-194."""
import sqlite3
from pathlib import Path

NOTES = """[Pinterest round-by-precision p — Canonical Solution]

## 问题 (Pinterest 2025-11 follow-up)

实现 `round_by_precision(s: str, p: str) -> str`：将字符串十进制数 `s`
按精度 `p`（保证为 10 的整数幂字符串，如 `'100'`、`'1'`、`'0.1'`、`'0.01'`）
四舍五入到最近的 `p` 的整数倍，结果仍以字符串返回。

不允许使用 `float()` —— 浮点会带来二进制表示误差和上下溢。
规则：半进位远离零（half away from zero）。进位可能跨越小数点边界。

## 解法 — 精度转 k，再跑半进位加法

### 核心观察

`p` 是 10 的整数幂：`p = 10^k`，其中 `k` 为整数（可正可负）。
- `p='100'` → `k=2`（舍入到百位）
- `p='1'`   → `k=0`（舍入到整数）
- `p='0.1'` → `k=-1`（保留 1 位小数）
- `p='0.01'`→ `k=-2`（保留 2 位小数）

用字符串解析得到 `k`：定位 `p` 中 `'1'` 的位置相对小数点的偏移。

### 算法步骤

1. **解析** `s` 为 `(sign, int_digits, frac_digits)`，同 1073（状态机）。
2. **解析** `p` 得到 `k`。
3. **定位舍入位**：把 `s` 的所有数字拼成定长数组，以 **小数点位置**
   为原点，计算"第一个被丢弃位"的索引 `cut`。
4. **半进位判定**：若 `digits[cut] >= 5` → 对 `digits[cut-1]` 加 1；
   否则直接截断。
5. **进位传播**：从 `cut-1` 向高位循环 `+1`，处理 `10` 进位；
   可能需要在最高位前插入新的 `'1'`（如 `9.99` at `p=0.1` → `10.0`）。
6. **重组输出**：把 `digits` 按 `k` 重新切回整数/小数部分，
   清理前导零（但保留 `'0'` 本身），处理负零 → 正零，拼回 `sign`。

### 关键边界情形

| 输入 | 说明 |
|------|------|
| `s='49', p='100'` | 舍入结果 `'0'`（低于半进位阈值） |
| `s='50', p='100'` | 恰好半进位 → `'100'` |
| `s='-0.05', p='0.1'` | 远离零 → `'-0.1'` |
| `s='9.99', p='0.1'` | 进位跨越小数点 → `'10.0'` |
| `s='0.005', p='0.01'` | 末位半进位 → `'0.01'` |

注意：**结果必须保留 `p` 所暗示的尾零**（`1234.7` 而不是 `1234.700`；
但 `'100'` 而非 `'1e2'`）。

## Complexity

- Time: O(n)，n = len(s)。
- Space: O(n) for the digit buffer.

## 与 1073 (round()) 的关系

1073 是本题的特例 `p='1'`（`k=0`）。先掌握 1073 的状态机解析 +
半进位加法，本题只需要再加一层"按 k 定位 cut 位"的索引计算。
面试时 tie-break 可主动问面试官：需要 banker's rounding 还是 half-away-from-zero。

## 面试实现模板

```python
def round_by_precision(s: str, p: str) -> str:
    sign, int_digs, frac_digs = _parse_decimal(s)     # raise ValueError on bad input
    k = _precision_exponent(p)                         # p = 10**k
    # pad to common frame: index 0 = highest int digit
    digits = list(int_digs or '0') + list(frac_digs)
    dot_pos = len(int_digs or '0')                     # digits[dot_pos] is 1st frac digit
    cut = dot_pos - k                                  # first discarded index
    if cut <= 0:
        return _format_zero(sign, k)
    round_up = cut < len(digits) and digits[cut] >= '5'
    kept = digits[:cut]
    if round_up:
        kept = _increment(kept)                        # may prepend '1'
    return _reassemble(sign, kept, k)
```

辅助函数 `_parse_decimal`、`_precision_exponent`、`_increment`、`_reassemble`
在白板上逐一实现即可；核心思想是"把十进制数当成数字串做定点运算"。
"""

db = Path(__file__).parent.parent / "data" / "mle_prep.db"
c = sqlite3.connect(db)
cur = c.cursor()
cur.execute("UPDATE problems SET notes=? WHERE id=1074", (NOTES,))
c.commit()
print(f"updated rows: {cur.rowcount}, notes len: {len(NOTES)}")
c.close()
