"""Seed Meta OA 2026-04-22 Prep Hub doc (aggregate landing page).

Per T-P1-250. Target: company_documents (company_id=31 Meta).

Aggregates the four Meta-OA source docs (ids 76/77/78/79) into one
landing page optimized for the 90-min exam: always-visible TOC +
exam-day strategy, then one <details><summary> drawer per problem
carrying the canonical Python skeleton and top corner cases. Readers
drill into the full per-problem doc via the prep sidebar dropdown.

Idempotency: sentinel <!-- META_OA_HUB_20260422 --> gates the write.
Second run = 0 writes when the content hash is unchanged.

Style: Chinese narration + English technical terms (per MLInterviewPrep
content style rule). Acronyms expanded on first occurrence.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_OA_HUB_20260422 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-OA] 2026-04-22 OA Prep Hub"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

# Source per-problem doc ids (hub references these by title — readers navigate
# via the /companies/31/prep docs dropdown). Kept here so a future doc-id
# refactor surfaces the coupling.
SOURCE_DOC_IDS = (76, 77, 78, 79)

CONTENT = SENTINEL + r'''
# Meta OA 2026-04-22 — Prep Hub

> **用法**: 考试当天早上最后一遍扫这一页。四道题（2 × 独立算法 + 2 × 4-level 系统设计 + 1 × 4-level 账户系统）全都折叠在下方 drawer 里，点开即可看到 canonical Python 骨架 + 高频 corner cases。深入题解请从左侧 docs 下拉切到对应子文档。
> **时长**: 90 min 整。建议 warm-up §1/§2 共 10 min → Cloud File System 20 min → In-Memory Database 25 min → Bank System 30 min，剩 5 min buffer 回头补 corner case。

---

## 目录 (Table of Contents)

- [考场策略 (90-min allocation)](#考场策略-90-min-allocation)
- [一眼速查表 (at-a-glance)](#一眼速查表-at-a-glance)
- [§A 独立算法 warm-up (Same Start/End + Smallest Reversal)](#a-独立算法-warm-up-same-startend-smallest-reversal)
- [§B Cloud File System (4-level)](#b-cloud-file-system-4-level)
- [§C In-Memory Database (L1-L4 + V2)](#c-in-memory-database-l1-l4-v2)
- [§D Bank System (L1-L4)](#d-bank-system-l1-l4)
- [跨题共通坑 (cross-cutting traps)](#跨题共通坑-cross-cutting-traps)

---

## 考场策略 (90-min allocation)

| 阶段 | 任务 | 时间盒 | 目标 |
|------|------|--------|------|
| 00-10 min | §A warm-up（§1 + §2 两题 AC） | 10 min | 建立手感；**两题都 AC 是进入 4-level 的入场券** |
| 10-30 min | §B Cloud FS L1→L4 | 20 min | 至少 L1-L3 AC，L4 compress/decompress 能写出骨架 |
| 30-55 min | §C In-Memory DB L1→L4（+ V2 若剩时间） | 25 min | L1-L4 AC；TTL 的 lazy eviction 是拿分重点 |
| 55-85 min | §D Bank System L1→L4 | 30 min | L1-L3 AC；L3 scheduleTransfer expire 语义必背；L4 merge 最难 |
| 85-90 min | Buffer | 5 min | 回头补 §B §C §D 各 level 的 corner case 断言 |

**取舍**: 卡壳超过分配时间的 1.5 倍就跳。warm-up §2 如果 15 min 还没 AC，直接 return 空实现拿 0 分，进 4-level——4-level 每个 level 大约 25-30% 权重，一道独立题 5-10%。

---

## 一眼速查表 (at-a-glance)

| § | 题目 | 类型 | Levels | 最优复杂度 | 核心技巧 |
|---|------|------|--------|------------|----------|
| A.1 | Same Start/End Letter Count | 独立算法 | — | $O(n)$ | `str.split()` 无参 + `casefold()` |
| A.2 | Smallest String via Prefix/Suffix Reversal | 独立算法 | — | $O(n^3)$ | 枚举 $2n$ 种反转 + `cand < best`；**identity 也是合法候选** |
| B | Cloud File System | 4-level 系统设计 | L1 add/copy/get → L4 compress | $O(n)$ 每次扫 file map | `dict[name] = (size, suffix)` + `.COMPRESSED` 约定 |
| C | In-Memory Database | 4-level + V2 | L1 set/get → L4 backup/restore + V2 CAS | $O(\log k)$ TTL 查询 | **TTL lazy eviction**；append-only history list + binary search |
| D | Bank System | 4-level 账户系统 | L1 create/transfer → L4 merge | $O(\log n)$ topSpenders | **scheduledTransfer expire 语义必背**；dirty-flag 缓存；merge 的 pending transfer 改写 |

---

## §A 独立算法 warm-up (Same Start/End + Smallest Reversal)

> 完整题解：左侧 docs 下拉 → `[Meta-OA] Standalone Algos (Same Start/End + Smallest Reversal)`

<details>
<summary><strong>A.1 Same Start/End Letter Count</strong>（点击展开 — canonical $O(n)$ 解法 + 4 个 corner cases）</summary>

**题意**：给定句子 `sentence`，返回首尾字母相同（**case-insensitive**）的单词数；单字母单词计入。

**Canonical Python**:

```python
def count_same_first_last(sentence: str) -> int:
    """Count words where first letter == last letter (case-insensitive)."""
    return sum(
        1
        for w in sentence.split()
        if w and w[0].casefold() == w[-1].casefold()
    )
```

**四个必须记的要点**:
1. `sentence.split()` **无参** — 自动处理 tab / 多空格 / 首尾空白 / 空串。写 `split(' ')` 就挂 tab 测试用例。
2. `casefold()` 优于 `lower()` — Turkish `İ` / German `ß` 行为更正确；纯 ASCII 等价。
3. 单字母词 `"a"`：`w[0] == w[-1]` 天然成立，不要加 `len(w) > 1` 的多余守卫。
4. **空串输入**：`"".split() == []`，`sum(... for ... in [])` 返回 `0`，无需特判。

**Corner cases 小抄**:

| 输入 | 期望 | 捕获原因 |
|------|------|----------|
| `""` | `0` | 空串 → `split()` 返 `[]` |
| `"a"` | `1` | 单字母词 |
| `"Apple banana ABBA a cat tAct"` | `3` | 混合大小写 + 单字母 |
| `"hello\tworld\t\thello"` | `0` | tab 分隔 + 多 tab（`hello` 首尾 h/o 不等） |

</details>

<details>
<summary><strong>A.2 Smallest String via Prefix/Suffix Reversal</strong>（点击展开 — canonical $O(n^3)$ 解法 + identity 陷阱）</summary>

**题意**：给定字符串 `s`，至多做一次 prefix reversal 或一次 suffix reversal（也可以都不做），返回能得到的字典序最小串。

**Canonical Python**:

```python
def smallest_after_reversal(s: str) -> str:
    """Lexicographically smallest string after at most one prefix or suffix reversal."""
    if not s:
        return s
    best = s  # identity: 什么都不做也是合法候选
    n = len(s)
    for i in range(1, n + 1):           # reverse prefix s[:i]
        cand = s[:i][::-1] + s[i:]
        if cand < best:
            best = cand
    for j in range(n):                  # reverse suffix s[j:]
        cand = s[:j] + s[j:][::-1]
        if cand < best:
            best = cand
    return best
```

**五个必须记的要点**:
1. **`best = s` — identity 必须纳入**。`"aaaa"` / `"abcd"` 这类已最优串，只靠 identity 守住。忘掉 `best = s` → 遗漏 "不反转" 选项。
2. **Prefix 循环 `range(1, n + 1)`** — 含 `i = n`（反转整串）。和 suffix `j = 0` 重合是故意的（多算一次不影响正确性），比写 `range(1, n)` + 边界判断更安全。
3. **Suffix 循环 `range(n)`** — 含 `j = 0` 和 `j = n - 1`；后者反转单字符是 no-op，但不跳过更省脑子。
4. **Python 字符串 `<` 是 lexicographic by Unicode code point**，不需要 `functools.cmp_to_key`；ASCII 范围内这就是字典序。
5. **复杂度 $O(n^3)$ = $2n$ 个候选 × $O(n)$ 构造 × $O(n)$ 比较**。$n \le 10^3$ 量级刚好；别上 suffix array 炫技。

**Corner cases 小抄**:

| 输入 | 期望 | 捕获原因 |
|------|------|----------|
| `""` | `""` | 空串短路 |
| `"a"` | `"a"` | 单字符；identity |
| `"abc"` | `"abc"` | 已最优；identity 守住 |
| `"cba"` | `"abc"` | prefix `i = 3` 反转整串 |
| `"abdc"` | `"abcd"` | suffix `j = 2` 反转 `"dc"` → `"cd"` |

</details>

---

## §B Cloud File System (4-level)

> 完整题解：左侧 docs 下拉 → `[Meta-OA] Cloud File System (4-level)`

<details>
<summary><strong>§B Cloud FS — 4-level 骨架</strong>（点击展开 — dict 存储 + `.COMPRESSED` suffix 约定）</summary>

**Level 梯度**:
- **L1** `add(name, size)` / `copy(src, dst)` / `get(name)` — 基础 CRUD
- **L2** `find_file(prefix, suffix)` — 按前缀 + 后缀列出所有匹配文件（**按 size desc 排序**，tie → 字典序）
- **L3** 引入 `users` + `capacity`；`add_user(user_id, cap)` / `add_file_by(user_id, name, size)` — 每用户有容量上限
- **L4** `compress(name)` / `decompress(name)` — 压缩后 `name + ".COMPRESSED"`，size 减半（向下取整）

**Canonical 类骨架**:

```python
class CloudFS:
    def __init__(self) -> None:
        self.files: dict[str, int] = {}         # name -> size（含 ".COMPRESSED" 后缀直接拼在 key 里）
        self.users: dict[str, tuple[int, int]] = {}  # user_id -> (capacity, used)
        self.owner: dict[str, str] = {}          # name -> user_id（L3 起）

    def add(self, name: str, size: int) -> bool:
        if name in self.files:
            return False
        self.files[name] = size
        return True

    def copy(self, src: str, dst: str) -> bool:
        if src not in self.files or dst in self.files:
            return False
        self.files[dst] = self.files[src]
        return True

    def get(self, name: str) -> int | None:
        return self.files.get(name)

    def find_file(self, prefix: str, suffix: str) -> list[str]:
        hits = [n for n in self.files if n.startswith(prefix) and n.endswith(suffix)]
        # sort by size desc, 再按 name asc
        hits.sort(key=lambda n: (-self.files[n], n))
        return hits

    def compress(self, name: str) -> bool:
        if name not in self.files or name.endswith(".COMPRESSED"):
            return False
        new_name = name + ".COMPRESSED"
        if new_name in self.files:
            return False
        self.files[new_name] = self.files[name] // 2  # 向下取整
        del self.files[name]
        return True

    def decompress(self, name: str) -> bool:
        if not name.endswith(".COMPRESSED") or name not in self.files:
            return False
        orig = name[: -len(".COMPRESSED")]
        if orig in self.files:
            return False
        self.files[orig] = self.files[name] * 2  # 注意 compress 是 // 2，信息损失
        del self.files[name]
        return True
```

**高频踩坑**:
1. **L2 排序**：tie-break 用 `name` 升序，不是降序；key=`(-size, name)` 一行搞定。
2. **L4 `.COMPRESSED` 约定**：压缩后文件名字面拼接后缀，不是元数据 flag。再压缩同一文件必须返回 `False`（suffix 已存在）。
3. **L4 decompress 信息损失**：compress 用 `// 2` 向下取整；decompress 用 `* 2` 不能复原奇数 size。题目通常只要求 decompress 返回 `size * 2`，但务必读清 spec。
4. **L3 容量检查**：`used + size > capacity` 时拒绝，不要忘记 add_file_by 成功时 `users[uid] = (cap, used + size)` 原子更新。

</details>

---

## §C In-Memory Database (L1-L4 + V2)

> 完整题解：左侧 docs 下拉 → `[Meta-OA] In-Memory Database (L1-L4 + V2)`

<details>
<summary><strong>§C In-Memory DB — 4-level + V2 骨架</strong>（点击展开 — TTL lazy eviction + append-only history）</summary>

**Level 梯度**:
- **L1** `set(key, field, value)` / `get(key, field)` / `delete(key, field)` — 二级 dict
- **L2** `scan(key)` / `scan_by_prefix(key, prefix)` — 按字段名字典序返回 `"field(value)"` 列表
- **L3** **TTL (Time To Live，生存时间)** 变体：`set_at(key, field, value, timestamp, ttl)` / `get_at` / `delete_at`，过期不可读
- **L4** `backup(timestamp)` / `restore(from_ts, current_ts)` — 快照 + TTL 重新计时
- **V2** `compare_and_set` / `compare_and_delete` / `get_value_at(key, field, ts)` — 乐观并发 + 时间点查询

**L3 TTL 实现要点（考场最常踩的坑）**:

```python
class InMemoryDB:
    def __init__(self) -> None:
        # data[key][field] = (value, expires_at | None)
        self.data: dict[str, dict[str, tuple[str, int | None]]] = {}

    def set_at(self, key: str, field: str, value: str, ts: int, ttl: int | None = None) -> None:
        expires = ts + ttl if ttl is not None else None
        self.data.setdefault(key, {})[field] = (value, expires)

    def _alive(self, entry: tuple[str, int | None], ts: int) -> bool:
        _, exp = entry
        return exp is None or ts < exp  # 严格小于！ts == exp 已过期

    def get_at(self, key: str, field: str, ts: int) -> str | None:
        if key not in self.data or field not in self.data[key]:
            return None
        entry = self.data[key][field]
        if not self._alive(entry, ts):
            del self.data[key][field]  # lazy eviction：读到过期就删
            if not self.data[key]:
                del self.data[key]
            return None
        return entry[0]
```

**V2 append-only history（`get_value_at` 支持时间点回溯）**:

```python
# history[key][field] = [(ts, value), ...]  升序，二分查找最后一个 ts <= query_ts
import bisect

def get_value_at(self, key: str, field: str, query_ts: int) -> str | None:
    lst = self.history.get(key, {}).get(field, [])
    if not lst:
        return None
    # bisect_right 找到第一个 > query_ts 的位置，往左一位
    idx = bisect.bisect_right(lst, (query_ts, chr(0x10FFFF))) - 1
    return lst[idx][1] if idx >= 0 else None
```

**高频踩坑**:
1. **TTL 比较用严格小于 `ts < exp`**：`ts == exp` 那一刻已过期，不可读。
2. **Lazy eviction vs eager**：考场用 lazy（读到才删），eager 需要 `heapq` + tombstone 更复杂，不划算。
3. **`backup` 快照**：要深拷贝 `data`，否则 restore 时原 DB 的后续写入会污染快照。
4. **`restore` TTL 重新计时**：从 backup ts 到 current ts 的 delta 要加到每个条目的 expires 上（或等价地，把 expires 改写为 `current_ts + (exp - backup_ts)`）。读题时确认 spec 要求哪种。
5. **V2 history binary search**：用 `bisect_right` + 哨兵 `chr(0x10FFFF)` 作为 tie-break value；写得下的话就用 `(ts, seq)` 单调递增。

</details>

---

## §D Bank System (L1-L4)

> 完整题解：左侧 docs 下拉 → `[Meta-OA] Bank System (L1-L4)`

<details>
<summary><strong>§D Bank System — 4-level 骨架</strong>（点击展开 — scheduledTransfer expire 语义 + merge 重写 pending）</summary>

**Level 梯度**:
- **L1** `createAccount(ts, id)` / `deposit(ts, id, amount)` / `pay(ts, id, amount)` / `transfer(ts, src, dst, amount)`
- **L2** `topSpenders(ts, n)` — 按累计支出降序、id 升序返回前 n 名（dirty flag 缓存）
- **L3** `scheduleTransfer(ts, src, dst, amount, delay)` / `cancelTransfer(ts, tid)` / `acceptTransfer(ts, tid)` — **有 expire 语义**
- **L4** `mergeAccounts(ts, id1, id2)` — id2 并入 id1，spent 累加，pending transfer 的双向引用必须改写

**L3 scheduledTransfer expire 语义（**必背**）**:
1. 创建时 `expires_at = ts + delay`；**`now >= expires_at` 时直接拒**（返回 False，不产生 pending）。
2. `acceptTransfer` 时校验 `now < expires_at`，否则 expire。
3. **Expire ≠ cancel**：expire 是 `src` 余额退回（lazy，读到才退）；cancel 是主动撤销。
4. 同一 src 多笔 pending 按 **FIFO** 依次 expire；遍历要按 `scheduled_ts` 升序。

**Canonical L3 + L4 关键代码**:

```python
class BankSystem:
    def __init__(self) -> None:
        self.accounts: dict[str, dict] = {}       # id -> {balance, spent, created_at}
        self.pending: dict[str, dict] = {}         # tid -> {src, dst, amount, expires_at, status}
        self.top_cache: list[tuple[str, int]] | None = None
        self.dirty = True

    def _expire_pending_for(self, src: str, now: int) -> None:
        """Lazy eviction：遍历 src 的所有 pending，把 expires_at <= now 的退款。"""
        for tid, p in list(self.pending.items()):
            if p["src"] == src and p["status"] == "pending" and now >= p["expires_at"]:
                self.accounts[src]["balance"] += p["amount"]  # 退款
                p["status"] = "expired"

    def acceptTransfer(self, ts: int, tid: str) -> bool:
        if tid not in self.pending:
            return False
        p = self.pending[tid]
        if p["status"] != "pending":
            return False
        if ts >= p["expires_at"]:
            # expire 优先于 accept
            p["status"] = "expired"
            self.accounts[p["src"]]["balance"] += p["amount"]
            return False
        # 成功接收
        self.accounts[p["dst"]]["balance"] += p["amount"]
        p["status"] = "accepted"
        return True

    def mergeAccounts(self, ts: int, id1: str, id2: str) -> bool:
        if id1 == id2 or id1 not in self.accounts or id2 not in self.accounts:
            return False
        a1, a2 = self.accounts[id1], self.accounts[id2]
        a1["balance"] += a2["balance"]
        a1["spent"] += a2["spent"]
        # 改写 pending：id2 的 src/dst 全改成 id1
        for tid, p in self.pending.items():
            if p["status"] != "pending":
                continue
            if p["src"] == id2: p["src"] = id1
            if p["dst"] == id2: p["dst"] = id1
        del self.accounts[id2]
        self.dirty = True
        return True
```

**L2 dirty-flag 缓存**:
```python
def topSpenders(self, ts: int, n: int) -> list[str]:
    if self.dirty or self.top_cache is None:
        self.top_cache = sorted(
            ((aid, a["spent"]) for aid, a in self.accounts.items()),
            key=lambda x: (-x[1], x[0]),
        )
        self.dirty = False
    return [aid for aid, _ in self.top_cache[:n]]
```

**L3 的 3 个考场必背 bug**:
1. **`now == expires_at` 已过期** — 用 `>=` 不是 `>`。
2. **Expire 退款在 src，不是 dst** — accept 才到 dst，expire 是回退。
3. **Cancel 和 expire 的退款逻辑是共享的**：封装 `_refund(src, amount)` 避免两处写重复。

**L4 merge 高频坑**:
1. **pending transfer 的双向改写**：src 和 dst 都要改，不能只改 src。
2. **spent 合并但 balance 已合并到 a1，不能双重计数**。
3. **merge 后 `dirty = True`**，下次 topSpenders 必须重建缓存。
4. **自合并拒绝**：`id1 == id2` 返 False，否则会清空账户。

</details>

---

## 跨题共通坑 (cross-cutting traps)

1. **timestamp 单调性**：§C §D 所有带 ts 的 API 假设 ts 单调不减；题目通常会明确，若没说默认单调。非单调要额外排序 → 复杂度上升。
2. **empty input 短路**：§A.1 `""` → 0；§A.2 `""` → `""`；§B `find_file("", "")` → 全文件；§C `scan_by_prefix(key, "")` → 该 key 下全 field。测试用例里经常偷塞空串。
3. **Integer overflow 不是问题**（Python 任意精度），但 `balance` / `spent` 的数值逻辑仍要核对——Meta 测试里有负数 deposit 的 adversarial 用例，记得 guard `amount > 0`。
4. **字典序 vs 自然数序**：§C L2 scan 要求按 field 字典序；§B L2 find_file tie-break 按 name 字典序；§D L2 topSpenders tie-break 按 id 字典序。**数字字符串 `"10" < "2"`**（字典序），如果 spec 要自然数序要特判 `int(x)` key。
5. **None vs 空容器的返回类型**：`get` 查不到返 `None` 还是 `""`？`find_file` 无匹配返 `[]` 还是 `None`？读题确认——写错类型 = 整题 0 分。

---

## 相邻题 / 进一步复习

- §A.1 ≈ LC 819 (Most Common Word) 的简化读入版
- §A.2 ≈ LC 2588 (Make String Sorted) 的反转 lite 变体
- §B ≈ LC 588 (Design In-Memory File System) 的工业强化版
- §C ≈ LC 1244 (Design A Leaderboard) + LC 981 (Time Based KV Store) 的组合
- §D 无直接 LC 映射；考察点接近 LC 635 (Design Log Storage System) 的 multi-level API 风格 + transaction expire 语义

> **离场 checklist**: 交卷前 60 秒，扫 4 个问题 — (1) 所有 API 的返回类型对齐 spec 了吗？(2) empty input 有短路了吗？(3) §C TTL 用 `ts < exp` 严格小于了吗？(4) §D L4 merge 后 dirty flag 置了吗？

'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def slugify(text: str) -> str:
    """Mirror src/frontend/src/utils/slugify.ts exactly.

    Used by MarkdownPreview to generate heading IDs; the TOC anchors in the
    hub body must round-trip through this function to be clickable.
    """
    out = text.lower().strip()
    out = re.sub(r"[\s]+", "-", out)
    out = re.sub(r"[^\w一-鿿㐀-䶿-]", "", out)
    out = re.sub(r"--+", "-", out)
    out = re.sub(r"^-|-$", "", out)
    return out


def validate_toc_anchors(content: str) -> None:
    """Every `[text](#slug)` in the TOC must round-trip through slugify."""
    # Extract TOC block between the "## 目录" heading and the following "---"
    toc_match = re.search(
        r"## 目录 \(Table of Contents\)\s*\n(.*?)\n---",
        content,
        re.DOTALL,
    )
    if not toc_match:
        raise RuntimeError("TOC block not found between '## 目录' and '---'")
    toc_block = toc_match.group(1)
    anchors = re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", toc_block)
    if not anchors:
        raise RuntimeError("no [text](#anchor) entries in TOC block")
    # Collect heading texts present in the doc (h2 + h3)
    headings = re.findall(r"^#{2,3}\s+(.+?)\s*$", content, re.MULTILINE)
    heading_slugs = {slugify(h) for h in headings}
    for text, anchor in anchors:
        # The anchor must match slugify(text) AND that slug must exist as a heading
        expected = slugify(text)
        if anchor != expected:
            raise RuntimeError(
                f"TOC anchor mismatch: text={text!r} -> "
                f"slug(text)={expected!r} but anchor={anchor!r}"
            )
        if anchor not in heading_slugs:
            raise RuntimeError(
                f"TOC anchor {anchor!r} does not match any h2/h3 heading slug"
            )


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## 目录 (Table of Contents)",
        "## 考场策略 (90-min allocation)",
        "## 一眼速查表 (at-a-glance)",
        "## §A 独立算法 warm-up",
        "## §B Cloud File System (4-level)",
        "## §C In-Memory Database (L1-L4 + V2)",
        "## §D Bank System (L1-L4)",
        "## 跨题共通坑 (cross-cutting traps)",
        "<details>",
        "</details>",
        "<summary>",
        "</summary>",
        # One drawer per problem section — 5 summaries total (A.1, A.2, B, C, D)
        "A.1 Same Start/End Letter Count",
        "A.2 Smallest String via Prefix/Suffix Reversal",
        "§B Cloud FS",
        "§C In-Memory DB",
        "§D Bank System",
        # Cross-link titles (match source-doc titles)
        "[Meta-OA] Standalone Algos",
        "[Meta-OA] Cloud File System (4-level)",
        "[Meta-OA] In-Memory Database (L1-L4 + V2)",
        "[Meta-OA] Bank System (L1-L4)",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    # Exactly 5 drawers (one per problem: A.1, A.2, B, C, D)
    n_details_open = content.count("<details>")
    n_details_close = content.count("</details>")
    if n_details_open != 5:
        raise RuntimeError(
            f"expected exactly 5 <details> drawers, got {n_details_open}"
        )
    if n_details_open != n_details_close:
        raise RuntimeError(
            f"<details> / </details> mismatch: {n_details_open} vs {n_details_close}"
        )
    if not (6000 <= len(content) <= 20000):
        raise RuntimeError(f"content length {len(content)} outside 6000-20000")
    validate_toc_anchors(content)


def main() -> int:
    """Upsert the Meta-OA Prep Hub doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        # Sanity: the 4 source docs we reference must exist
        placeholders = ",".join("?" * len(SOURCE_DOC_IDS))
        source_rows = conn.execute(
            f"SELECT id, title FROM company_documents WHERE id IN ({placeholders})",
            SOURCE_DOC_IDS,
        ).fetchall()
        found_ids = {r[0] for r in source_rows}
        missing = [sid for sid in SOURCE_DOC_IDS if sid not in found_ids]
        if missing:
            print(
                f"[ERROR] source docs missing: {missing} — "
                "hub depends on T-P0-246/247/248/T-P1-249 seeds"
            )
            return 1
        print(f"[OK] all {len(SOURCE_DOC_IDS)} source docs present")

        cur = conn.execute(
            "SELECT id, content FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        )
        existing = cur.fetchone()

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(CONTENT)

        if existing is None:
            conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                "content_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    new_hash,
                    now,
                    now,
                ),
            )
            conn.commit()
            new_id = conn.execute(
                "SELECT id FROM company_documents "
                "WHERE company_id = ? AND title = ?",
                (COMPANY_ID, DOC_TITLE),
            ).fetchone()[0]
            print(
                f"[INSERT] id={new_id} len={len(CONTENT)} "
                f"hash={new_hash[:12]}..."
            )
        else:
            existing_id, existing_content = existing
            if SENTINEL in existing_content and existing_content == CONTENT:
                print(
                    f"[UNCHANGED] id={existing_id} sentinel present + "
                    f"content byte-identical; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, updated_at = ? "
                    "WHERE id = ?",
                    (CONTENT, new_hash, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(CONTENT)} delta={len(CONTENT)-old_len:+d}"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
