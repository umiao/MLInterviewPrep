"""One-shot: write LC 43 solution notes in Chinese."""
import sqlite3

NOTES = r'''## LC 43 - Multiply Strings (High-Precision Multiplication)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 核心重述 (THE Key Insight)

给两个字符串表示的非负整数 `num1`, `num2`，返回乘积字符串。不能用 `int()` / `BigInteger` 直接转。核心洞察：

1. **按位乘法对齐规则**：`num1[i] * num2[j]` 的结果贡献到答案的第 `i + j` 和 `i + j + 1` 位（从左往右数，或者等价地从右往左的第 `len1-1-i + len2-1-j` 和 `...+1` 位）。
2. **用长度为 `m + n` 的数组缓存各位**：两个长度分别为 `m`、`n` 的整数相乘，结果长度最多 `m + n`（至少 `m + n - 1`）。先不管进位，全部加完再统一 carry。
3. **统一进位**：从最低位向高位扫一遍，`carry = val // 10; digit = val % 10`。

### Approach: Digit-by-Digit with Position Array (推荐，O(mn))

```python
class Solution:
    def multiply(self, num1: str, num2: str) -> str:
        if num1 == "0" or num2 == "0":
            return "0"
        m, n = len(num1), len(num2)
        res = [0] * (m + n)  # res[0] is most significant
        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                mul = (ord(num1[i]) - 48) * (ord(num2[j]) - 48)
                p1, p2 = i + j, i + j + 1  # p2 is lower digit
                total = mul + res[p2]
                res[p2] = total % 10
                res[p1] += total // 10
        # 跳过前导零
        out = []
        for d in res:
            if out or d != 0:
                out.append(d)
        return "".join(map(str, out)) if out else "0"
```

**复杂度**：时间 O(mn)；空间 O(m + n)。m, n ≤ 200 → 4e4，远低于 1s。

**为何 `p1 = i + j`, `p2 = i + j + 1`**：用"从左往右"的下标系统 (`num1[0]` 是最高位)。`num1[i] * num2[j]` 的数位权重 = `10^((m-1-i) + (n-1-j))`，放在 `res[(m+n-1) - ((m-1-i)+(n-1-j))] = res[i+j+1]` (个位贡献) 和 `res[i+j]` (进位贡献)。

### Approach B: 模拟竖式 (Shift-and-Add)

外层遍历 `num2` 的每一位 `b`，算出 `num1 * b` 的字符串，然后按位左移（末尾补零），最后所有行做大数加法。代码更长、常数更大，但适合讲清楚 grade-school 算法。面试首选 Approach A。

### Code Review 要点 (常见失误)

- **忘记处理 "0" 边界**：任一乘数为 "0" 直接返回 "0"，否则会输出 "000..."。
- **p1/p2 颠倒**：`p2 = i + j + 1` 是低位，存个位 (`% 10`)；`p1 = i + j` 是高位，累加进位 (`// 10`)。写反了答案会低 10 倍或错位。
- **`res[p1] += carry` 而不是 `= carry`**：`p1` 位可能已经被更高位的 `p2` 写过（它对应更高位乘法的低位），所以必须 `+=`。
- **前导零剥离**：`res` 长度是 `m + n`，但实际结果可能是 `m + n - 1` 位，第 0 位会是 0，要跳过。用 `out or d != 0` 过滤，最后若 `out` 为空补 "0"。
- **`ord(ch) - 48`** 比 `int(ch)` 快一点；`- ord('0')` 更清晰，等价。
- **负数 / 前导零**：题目保证非负且无前导零 (除 "0" 本身)，面试若没说清，应该问。

### 识别模板 (When to Use This Pattern)

- "两个很大的整数相乘 / 相加 / 相减，不能用语言自带的大数"。
- 答案位数已知 (`m + n` 或 `max(m, n) + 1`)，先填数组再进位的写法普遍适用。
- 同族: LC 2 Add Two Numbers (链表版)、LC 415 Add Strings、LC 67 Add Binary、LC 66 Plus One、LC 989 Add to Array-Form of Integer。

### 面试叙述模板 (Talking Points)

1. "先分析：m 位乘 n 位，结果最多 m+n 位；我开一个长度 m+n 的数组，每位先存未进位的累加值。"
2. "双层循环 num1[i] * num2[j]：结果贡献到 res[i+j+1] (个位) 和 res[i+j] (进位)。"
3. "边算边 `% 10`、`// 10` 即可，不需要最后统一扫一遍。"
4. "最后剥前导零。"
5. 复杂度 O(mn)；优化：FFT 可做 O((m+n) log(m+n))，面试通常不要求，可提一嘴。

### Complexity Summary

| Approach | Time | Space |
|----------|------|-------|
| Digit-by-digit (array) | O(mn) | O(m+n) |
| Shift-and-add (竖式) | O(mn) | O(m+n) |
| FFT (理论) | O((m+n) log(m+n)) | O(m+n) |
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 43", (NOTES,))
conn.commit()
print(f"[OK] LC 43 notes updated ({len(NOTES)} chars)")
conn.close()
