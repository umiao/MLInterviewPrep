"""Seed Pinterest screening problem 'Reverse Count and Say' (2026-05-06).

User-provided via Discord 2026-05-06: a Pinterest screening interview problem
that is NOT a real LeetCode problem (custom). Adds:

  1. A new row in `problems` (leetcode_id=NULL, custom Pinterest source) with
     the Chinese problem statement + Chinese solution notes containing the
     user's working Python backtracking solution.
  2. The LC index doc (id=47, "Pinterest LC Must-Do: Review & Index") --
     appends one row to the "Pinterest Custom 题 (无 LC 对应)" table.
  3. The card_index doc (id=66, "Pinterest Prep Card Index") -- appends one
     entry to the "Pinterest 定制题" / "Pinterest Custom" cluster card.

Idempotent: re-running detects the existing problem by title and updates in
place; index docs are matched by sentinel substrings so reruns don't dup.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

PINTEREST_COMPANY_ID = 29
PROBLEM_TITLE = "Reverse Count and Say (Pinterest Screening)"
LC_INDEX_DOC_ID = 47
CARD_INDEX_DOC_ID = 66

DIFFICULTY = "medium"
PATTERN = "Backtracking + 1-or-2-digit count parsing"
FAMILY = "backtracking-string-decode"
SOURCE = "pinterest_screening,custom"
CARD_ONE_LINER = "回溯：每步消耗 2 或 3 字符 (1/2 位 count + 1 位 digit)"

DESCRIPTION_ZH = """\
[Pinterest screening 2026-05-06] 给一个由**恰好一次** count-and-say 变换得到的字符串 `encoded`。
每个 group 形如 `count + digit`，其中 `count ∈ [1, 99]`（无前导零，1 或 2 位），紧跟一位 `digit`。
要求返回**所有**可能的原始数字串集合。

**Example**

```
Input:  encoded = "12114"
Output: ["244444444444", "1111111111114"]
```

- 解析 `"12"` 为 1 个 `"2"`，`"114"` 为 11 个 `"4"` → `"244444444444"`
- 解析 `"121"` 为 12 个 `"1"`，`"14"` 为 1 个 `"4"` → `"1111111111114"`
- `"1,2114"`（1 211 个 `"4"`）非法，因为 count ≤ 99。

**Constraints**
- `1 <= len(encoded) <= 64`
- 只含 `'0'..'9'`
- count 区间 `[1, 99]`，无前导零

**Suggested Approach** (题面给出)
- backtracking：在每个位置尝试消耗 2 字符（1 位 count + 1 位 digit）或 3 字符（2 位 count + 1 位 digit）
- 校验：count 不能以 `'0'` 开头；剩余长度 ≥ 2 才能取出一个完整 group
- 展开：把 `digit` 重复 `count` 次拼到当前 candidate 末尾，递归处理剩余子串
- 结尾收集所有合法 candidate 即答案

**Time / Space**
- Time: O(2^n)，每步分叉 1/2 位 count
- Space: O(n) 递归栈 + 输出

*题面整理 2026-05-06。*
"""

NOTES_ZH = """\
## Reverse Count and Say (Pinterest Screening 2026-05-06)

### 题目要点
- 输入是一个 count-and-say **一次**变换后的字符串。
- 每段 group = `count(1..99) + digit`，count 不能有前导零。
- 列举所有能产生这个 encoded 的原始串（顺序无所谓，去重）。

### 解法：DFS / Backtracking

每个位置只有两种合法 split：
1. **2-char**：`encoded[i]` 是 1 位 count（`'1'..'9'`），`encoded[i+1]` 是 digit。
2. **3-char**：`encoded[i:i+2]` 是 2 位 count（首字符 `'1'..'9'`），`encoded[i+2]` 是 digit。

把当前 group 展开成 `int(count) * digit_char`（字符串重复），加入候选 list；当 `i == n` 时把候选拼起来收集进答案。

### 用户提供的 Python 实现 (works for the official example)

```python
from typing import List

def reverse_count_and_say(encoded: str) -> List[str]:
    \"\"\"Return all distinct original strings whose count-and-say is `encoded`.\"\"\"
    n = len(encoded)
    ans = []

    def solve(inputStr, curAnsList):
        # we can fetch either 2 or 3 chars as iteration.
        if not inputStr:
            ansStr = ''.join(curAnsList)
            ans.append(ansStr)
            return

        if inputStr[0] == '0' or len(inputStr) < 2:
            # not legal: leading zero in count, or not enough chars for a group
            return

        # try 2 digits (1-digit count + 1 digit)
        _count, _char = inputStr[0], inputStr[1]
        solve(inputStr[2:], curAnsList + [int(_count) * _char])

        # try 3 digits (2-digit count + 1 digit)
        if len(inputStr) >= 3:
            _count, _char = inputStr[:2], inputStr[2]
            solve(inputStr[3:], curAnsList + [int(_count) * _char])

        return

    solve(encoded, [])
    return ans
```

### Trace: `encoded = "12114"`

```
solve("12114", [])
├── 2-char: count="1", digit="2" -> "2"
│   solve("114", ["2"])
│   ├── 2-char: count="1", digit="1" -> "1"
│   │   solve("4", ["2","1"])
│   │   └── len < 2, return  (dead-end, "4" 不够取一个 group)
│   └── 3-char: count="11", digit="4" -> "44444444444"
│       solve("", ["2","44444444444"])
│       └── append "244444444444"   ✓
└── 3-char: count="12", digit="1" -> "111111111111"
    solve("14", ["111111111111"])
    └── 2-char: count="1", digit="4" -> "4"
        solve("", ["111111111111","4"])
        └── append "1111111111114"  ✓
```

输出：`["244444444444", "1111111111114"]`。

### 复杂度
- **Time**: 每个位置最多 2 个分支，深度最多 n/2，最坏 O(2^(n/2)) candidate；每个 candidate 拼接 O(n)，总 O(n · 2^(n/2))。题面给的 O(2^n) 是松上界。
- **Space**: O(n) 递归栈 + 输出大小（候选数 × 平均长度）。注意一个 group 展开后长度可达 99，所以输出长度可能远大于输入。

### 边界 / 易错点
1. **前导零**：`encoded[i] == '0'` 时整个分支非法（count ∈ [1,99] 无前导零）。
2. **剩余长度**：`len < 2` 时 group 取不出，直接 dead-end。
3. **2-digit count 也要拒前导零**：用户代码中 `inputStr[:2]` 只有当 `inputStr[0] != '0'` 时才会被尝试（前面已过滤 `inputStr[0] == '0'`），所以 OK。**但若 `inputStr[1] == '0'`**（如 `"10"` 作 count）反而合法——10 是合法 count，无前导零问题。

### 未覆盖的 follow-up（面试可能追问）

题面给的 docstring 暗示 *"adjacent groups have different digits"* 这条规则，但**用户代码没有显式校验**。理由：

- count_and_say 永远把连续相同字符合并成一个 group，所以**合法的** encoded 输入天然不会让用户算法产出"相邻同 digit"的 candidate。
- 若面试官给 adversarial 输入（不一定来自真正的 count_and_say），用户算法可能输出不能 round-trip 的候选。

**面试加分项**：在 base case `if not inputStr` 处加一次 `count_and_say(candidate) == encoded` 验证，或在递归时携带 `prev_digit` 参数剪枝相邻同 digit 分支。两种方法等价：

```python
# 方案 A: 携带 prev_digit 剪枝
def solve(i, prev, cur):
    if i == n:
        ans.append(''.join(cur))
        return
    # ... 在每个分支前加 if _char == prev: continue
```

```python
# 方案 B: 末尾验证（更易写，常数大一点）
def count_and_say(s):
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(f"{j-i}{s[i]}")
        i = j
    return ''.join(out)

# 在 base case: if count_and_say(candidate) == encoded: ans.append(...)
```

### 45 秒口播
> "DFS 在每个位置 try 2 种 split：1 位 count + 1 位 digit，或者 2 位 count + 1 位 digit；count 不能以 0 开头；展开 `int(count) * digit` 加入候选。base case 收集答案。复杂度 O(2^(n/2))。题面 docstring 暗示 adjacent group 不能同 digit，工业实现里要么 carry prev_digit 参数剪枝，要么 base case 一次 count_and_say 反向验证；两种都把假候选剔掉。"
"""

LC_INDEX_SENTINEL = "Reverse Count and Say"  # used to detect prior insert
LC_INDEX_OLD_TOTAL = "32 题全部 done"  # match old footer count
LC_INDEX_NEW_TOTAL = "33 题全部 done"
LC_INDEX_OLD_REFACTORED = "*Last refactored: 2026-04-15.*"
LC_INDEX_NEW_REFACTORED = "*Last refactored: 2026-05-06 (added Pinterest screening: Reverse Count and Say).*"


def upsert_problem(conn: sqlite3.Connection) -> int:
    """Create or update the problem row. Returns problems.id."""
    row = conn.execute(
        "SELECT id FROM problems WHERE title = ?", (PROBLEM_TITLE,)
    ).fetchone()
    company_tags = json.dumps(["Pinterest"], ensure_ascii=False)
    tags = json.dumps(["Backtracking", "DFS", "String", "Pinterest"], ensure_ascii=False)
    now = datetime.now(UTC).isoformat()
    if row:
        pid = row[0]
        conn.execute(
            """UPDATE problems SET
                description = ?, notes = ?, difficulty = ?, pattern = ?,
                family = ?, source = ?, company_tags = ?, tags = ?,
                is_completed = 1
            WHERE id = ?""",
            (
                DESCRIPTION_ZH, NOTES_ZH, DIFFICULTY, PATTERN,
                FAMILY, SOURCE, company_tags, tags, pid,
            ),
        )
        print(f"[UPDATE] problems.id={pid} ({PROBLEM_TITLE})")
        return pid

    cur = conn.execute(
        """INSERT INTO problems
            (leetcode_id, title, url, difficulty, tags, pattern, family,
             category, source, company_tags, priority, is_completed,
             comfort_level, description, notes, created_at)
        VALUES (NULL, ?, NULL, ?, ?, ?, ?, 'algorithm', ?, ?, 1, 1, 3, ?, ?, ?)""",
        (
            PROBLEM_TITLE, DIFFICULTY, tags, PATTERN, FAMILY,
            SOURCE, company_tags, DESCRIPTION_ZH, NOTES_ZH, now,
        ),
    )
    pid = cur.lastrowid
    print(f"[INSERT] problems.id={pid} ({PROBLEM_TITLE})")
    return pid


def update_lc_index_doc(conn: sqlite3.Connection, problem_id: int) -> None:
    """Append the new problem to the Pinterest Custom table in doc id=47."""
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id = ?", (LC_INDEX_DOC_ID,)
    ).fetchone()
    if row is None:
        raise SystemExit(f"[FAIL] company_documents.id={LC_INDEX_DOC_ID} missing")
    content = row[0]
    if LC_INDEX_SENTINEL in content:
        print(f"[SKIP] LC index doc id={LC_INDEX_DOC_ID} already references {LC_INDEX_SENTINEL}")
        return

    new_row = (
        f"| 9 | [Reverse Count and Say (screening)](db://{problem_id}) | Backtracking / 字符串解码 |"
        f" 每步消耗 2 或 3 字符；count ∈ [1,99] 无前导零；分叉 1/2 位 count；O(2^(n/2))；"
        f"adjacent-different-digit 规则可在 base case 验证 |"
    )

    # Insert after row "| 8 | [LC 332 Loop Follow-up Addendum]..."
    anchor = "| 8 | [LC 332 Loop Follow-up Addendum](lc://332) | 图 + 环检测 | 变体：判断行程是否必须重访某条边 |"
    if anchor not in content:
        raise SystemExit(
            "[FAIL] Could not locate anchor row 8 in LC index doc -- "
            "structure may have changed"
        )
    content = content.replace(anchor, anchor + "\n" + new_row, 1)

    if LC_INDEX_OLD_TOTAL in content:
        content = content.replace(LC_INDEX_OLD_TOTAL, LC_INDEX_NEW_TOTAL, 1)
    if LC_INDEX_OLD_REFACTORED in content:
        content = content.replace(LC_INDEX_OLD_REFACTORED, LC_INDEX_NEW_REFACTORED, 1)

    conn.execute(
        "UPDATE company_documents SET content = ?, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?",
        (content, LC_INDEX_DOC_ID),
    )
    print(f"[UPDATE] LC index doc id={LC_INDEX_DOC_ID} appended row 9 -> db://{problem_id}")


def update_card_index(conn: sqlite3.Connection, problem_id: int) -> None:
    """Append the new problem to the 'Pinterest 定制题' card in doc id=66."""
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id = ?", (CARD_INDEX_DOC_ID,)
    ).fetchone()
    if row is None:
        raise SystemExit(f"[FAIL] company_documents.id={CARD_INDEX_DOC_ID} missing")
    payload = json.loads(row[0])

    target_card = None
    for card in payload["cards"]:
        if card.get("name_en") == "Pinterest Custom":
            target_card = card
            break
    if target_card is None:
        raise SystemExit("[FAIL] 'Pinterest Custom' card not found in card_index")

    if any(p.get("id") == problem_id for p in target_card["problems"]):
        print(
            f"[SKIP] card_index already contains problems.id={problem_id} "
            "in Pinterest Custom card"
        )
        return

    target_card["problems"].append({
        "id": problem_id,
        "leetcode_id": None,
        "title": PROBLEM_TITLE,
        "one_liner": CARD_ONE_LINER,
    })

    new_content = json.dumps(payload, ensure_ascii=False, indent=2)
    conn.execute(
        "UPDATE company_documents SET content = ?, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?",
        (new_content, CARD_INDEX_DOC_ID),
    )
    print(
        f"[UPDATE] card_index doc id={CARD_INDEX_DOC_ID} -> appended "
        f"problems.id={problem_id} to 'Pinterest Custom' card"
    )


def seed() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.execute("BEGIN")
        pid = upsert_problem(conn)
        update_lc_index_doc(conn, pid)
        update_card_index(conn, pid)
        conn.execute("COMMIT")

        # Verify
        row = conn.execute(
            "SELECT id, title, company_tags, is_completed FROM problems WHERE id = ?",
            (pid,),
        ).fetchone()
        print(f"[VERIFY] problems row -> {row}")
    finally:
        conn.close()
    print("[DONE]")


if __name__ == "__main__":
    seed()
