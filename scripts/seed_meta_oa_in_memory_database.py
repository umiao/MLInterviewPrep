"""Seed Meta OA In-Memory Database 4-level + V2 solution doc.

Per T-P0-247. Target: company_documents (company_id=31 Meta).

Idempotency: sentinel <!-- META_OA_INMEMDB_20260422 --> gates the write.
Second run = 0 writes (update only when content hash changes).

Style: Chinese narration + English technical terms (per MLInterviewPrep
content style rule). Acronyms expanded on first occurrence.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_OA_INMEMDB_20260422 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-OA] In-Memory Database (L1-L4 + V2)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

CONTENT = SENTINEL + r"""
# Meta OA — In-Memory Database (L1-L4 + V2)

> **题型**: in-memory key/field/value store with TTL + snapshot/restore；4 个 level 逐级解锁。
> **时长**: 90 分钟整套 4 题（In-Memory DB / Cloud FS / Bank System 属于同一族）。
> **评分**: 通过 Level 3 ≈ mid；Level 4 + V2 extras = senior+ 门槛。

---

## 1. Problem Overview

实现一个 **in-memory key-field-value store**：支持按 `key -> field -> value` 三级索引，带 **TTL** (time-to-live, 过期时间) 和 snapshot/restore。同一 key 下可以有多个 field；不同 key 互相独立。

### Level 梯度

| Level | 新增能力 | 核心数据结构 |
|-------|----------|-------------|
| 1 | `set` / `get` / `delete` | `key -> {field: value}` 双层 dict |
| 2 | `scan` / `scan_by_prefix`（字典序排序） | 同上 |
| 3 | TTL 变体：`set_at` / `set_at_with_ttl` / `get_at` / `delete_at` / `scan_at` / `scan_by_prefix_at` | 再加 `key -> {field: expire_at}` |
| 4 | `backup(timestamp)` / `restore(timestamp, timestamp_to_restore)` | 再加 `list[(ts, snapshot)]` |
| V2 | `compare_and_set` / `compare_and_delete` / `get_value_at` | 再加 append-only 历史：`key -> {field: [(ts, value_or_None)]}` |

### 题眼提醒

- **TTL semantics**: 过期判定是 `timestamp >= expire_at`（**用 `>=` 而不是 `>`**）——等于过期时间时视为**已过期**。
- **读操作不应修改状态**: `get_at` / `scan_at` 只判活 (alive check) 不 purge，避免 out-of-order 时间戳操作污染状态（考场里 Meta test case 是时间递增的，但鲁棒实现应该两者都能通过）。
- **Backup 只记录活跃字段**: `backup(ts)` 时若 `field` 已过期，**不**写入 snapshot；snapshot 里记录的是 `(value, remaining_ttl)` 而不是绝对 `expire_at`。
- **Restore 要 TTL 重算**: `restore(current_ts, ts_to_restore)` 时新的 `expire_at = current_ts + remaining_ttl`——这是最容易写错的地方。

---

## 2. Level 1: set / get / delete

### API

```python
set(key: str, field: str, value: str) -> None
get(key: str, field: str) -> str | None
delete(key: str, field: str) -> bool
```

### 规则

- `set` 覆盖已有值，**不**返回任何标记。
- `get` 未命中返回 `None`。
- `delete` 成功返回 `True`，不存在返回 `False`。

### 实现

```python
def set(self, key, field, value):
    self._store[key][field] = value
    # set 清除之前可能设过的 TTL（L3 语义继承）
    if key in self._expire and field in self._expire[key]:
        del self._expire[key][field]

def get(self, key, field):
    return self._store.get(key, {}).get(field)

def delete(self, key, field):
    if field in self._store.get(key, {}):
        del self._store[key][field]
        if key in self._expire and field in self._expire[key]:
            del self._expire[key][field]
        return True
    return False
```

---

## 3. Level 2: scan / scan_by_prefix

### API

```python
scan(key: str) -> list[str]
scan_by_prefix(key: str, prefix: str) -> list[str]
```

### 规则

- 返回格式 `"<field>(<value>)"`，按 **field 字典序升序**。
- 未命中 key 返回 `[]`（不是 `None`）。
- `scan_by_prefix` 只保留 `field.startswith(prefix)` 的。

### 实现

```python
def scan(self, key):
    fields = self._store.get(key, {})
    return [f"{f}({v})" for f, v in sorted(fields.items())]

def scan_by_prefix(self, key, prefix):
    fields = self._store.get(key, {})
    return [
        f"{f}({v})"
        for f, v in sorted(fields.items())
        if f.startswith(prefix)
    ]
```

### 踩坑点

- 别用 `OrderedDict` 或维护额外排序结构。`sorted(dict.items())` O(n log n) 对 Meta OA 规模足够。
- prefix 为空字符串时 `startswith("")` 永真——即退化为 `scan`，不需要特判。

---

## 4. Level 3: TTL 变体

### API

```python
set_at(key, field, value, timestamp) -> None
set_at_with_ttl(key, field, value, timestamp, ttl) -> None
get_at(key, field, timestamp) -> str | None
delete_at(key, field, timestamp) -> bool
scan_at(key, timestamp) -> list[str]
scan_by_prefix_at(key, prefix, timestamp) -> list[str]
```

### 关键规则

1. **Expire 判定**: `timestamp >= expire_at` 视为过期（用 `>=`）。
2. **set_at（无 TTL）** 要**清除**之前设过的 TTL——这是 set 覆写的标准语义。
3. **set_at_with_ttl** 的 `expire_at = timestamp + ttl`，绝对时间戳。
4. **读操作只判活**：不要在 get/scan 里 purge 过期字段——保持 read-only，避免状态污染。
5. **scan 的 timestamp 守卫**：作者原题解里 `scan` 忘了加 `expire > timestamp` guard，导致已过期 field 仍出现在结果里。**这是高频 bug**。

### 实现

```python
def _is_alive(self, key, field, now):
    if field not in self._store.get(key, {}):
        return False
    exp = self._expire.get(key, {}).get(field)
    if exp is None:
        return True
    return now < exp  # expire_at 到达瞬间就算过期

def set_at(self, key, field, value, timestamp):
    self._store[key][field] = value
    if key in self._expire and field in self._expire[key]:
        del self._expire[key][field]
    self._history[key][field].append((timestamp, value))

def set_at_with_ttl(self, key, field, value, timestamp, ttl):
    self._store[key][field] = value
    self._expire[key][field] = timestamp + ttl
    self._history[key][field].append((timestamp, value))

def get_at(self, key, field, timestamp):
    if not self._is_alive(key, field, timestamp):
        return None
    return self._store[key][field]

def delete_at(self, key, field, timestamp):
    if not self._is_alive(key, field, timestamp):
        return False
    del self._store[key][field]
    if key in self._expire and field in self._expire[key]:
        del self._expire[key][field]
    self._history[key][field].append((timestamp, None))
    return True

def scan_at(self, key, timestamp):
    items = []
    for f, v in self._store.get(key, {}).items():
        if self._is_alive(key, f, timestamp):  # ← 作者题解漏掉这一行
            items.append((f, v))
    return [f"{f}({v})" for f, v in sorted(items)]

def scan_by_prefix_at(self, key, prefix, timestamp):
    items = []
    for f, v in self._store.get(key, {}).items():
        if f.startswith(prefix) and self._is_alive(key, f, timestamp):
            items.append((f, v))
    return [f"{f}({v})" for f, v in sorted(items)]
```

### 踩坑点

- **`>=` vs `>`**: Meta 原题描述是 "expire at this timestamp"，所以 `now == expire` 时**已过期**。用 `<` 做 alive 判定（等价于 `>=` 做 expire 判定）。
- **set_at 后残留的 expire**: 同一 (key, field) 先 set_at_with_ttl 再 set_at，必须把 expire 清掉，否则新值会沿用旧 TTL 提前消失。
- **不要 purge 在 read path**: 虽然看起来 "读时顺手清理" 是小优化，但会破坏幂等——同一时间戳连续 scan 两次结果应相等。
- **scan_at 的 ordering**: 排序 key 是 field 名，不是 value。

---

## 5. Level 4: backup / restore

### API

```python
backup(timestamp) -> int   # 返回 snapshot 中 (key, field) 的总数
restore(timestamp, timestamp_to_restore) -> None
```

### 关键规则

1. **Backup 只记录活跃字段**: `backup(ts)` 时对每个 field 判 `ts < expire_at`，过期字段**不**进 snapshot。
2. **Snapshot 内存的是 remaining_ttl**: `remaining = expire_at - ts`（若无 TTL 则存 `None`）。存绝对 `expire_at` 是错的——restore 到未来时间点时旧的绝对值就失效。
3. **Restore 时 TTL 重算**: 新 `expire_at = timestamp + remaining_ttl`。`timestamp` 是**当前**调用 restore 的时间，`timestamp_to_restore` 是目标 backup 的时间。
4. **Restore 使用最近的 backup**: 找 `ts <= timestamp_to_restore` 中最大的那个（`bisect_right(list, ts_to_restore) - 1`）。
5. **Restore 时若无任何 backup <= ts_to_restore**: spec 未明确，一般行为是**no-op**（也有变体返回 error，以题目描述为准）。

### 实现

```python
import bisect

def backup(self, timestamp):
    snapshot = {}
    count = 0
    for key, fields in self._store.items():
        live = {}
        for f, v in fields.items():
            exp = self._expire.get(key, {}).get(f)
            if exp is not None and timestamp >= exp:
                continue  # 已过期 → 不入 backup
            remaining = (exp - timestamp) if exp is not None else None
            live[f] = (v, remaining)
            count += 1
        if live:
            snapshot[key] = live
    # 维护 self._backups 按 timestamp 升序
    ts_list = [t for t, _ in self._backups]
    idx = bisect.bisect_left(ts_list, timestamp)
    if idx < len(self._backups) and self._backups[idx][0] == timestamp:
        self._backups[idx] = (timestamp, snapshot)  # 覆盖同 ts backup
    else:
        self._backups.insert(idx, (timestamp, snapshot))
    return count

def restore(self, timestamp, timestamp_to_restore):
    ts_list = [t for t, _ in self._backups]
    idx = bisect.bisect_right(ts_list, timestamp_to_restore) - 1
    if idx < 0:
        return  # no-op
    _, snapshot = self._backups[idx]
    self._store = defaultdict(dict)
    self._expire = defaultdict(dict)
    for key, fields in snapshot.items():
        for f, (v, remaining) in fields.items():
            self._store[key][f] = v
            if remaining is not None:
                self._expire[key][f] = timestamp + remaining
            self._history[key][f].append((timestamp, v))  # 历史留痕
```

### 踩坑点

- **Snapshot 存 expire_at 绝对值**是**错的**。假设 `backup(5)` 时某 field 还剩 7s TTL（expire=12），若 restore 发生在 `timestamp=20`，直接用 expire=12 意味着刚恢复就过期。正确做法：存 remaining=7，restore 时重算 `expire=20+7=27`。
- **Restore 时 history 是否应该回滚**？取决于 V2 spec。保守做法：history append-only 不回滚，restore 在 history 里追加一条 `(timestamp, value)` 条目即可——否则 `get_value_at` 会在 restore 后看到错误的值。
- **Backup 时过期字段**要主动跳过，不能 "backup 所有 + restore 时再过滤"——后者会污染 `count` 返回值。

---

## 6. V2 Extras: compareAndSet / compareAndDelete / getValueAt

### API

```python
compare_and_set(key, field, expected, new_value, timestamp) -> bool
compare_and_delete(key, field, expected, timestamp) -> bool
get_value_at(key, field, timestamp) -> str | None
```

### 规则

- **CAS (compare-and-swap)** 语义：当前 `value == expected` 时原子替换为 `new_value` 并返回 `True`；否则返回 `False`。
- **compare_and_delete** 同理：匹配就删、不匹配就不动。
- **get_value_at(ts)** 查历史：返回 `ts` 时刻**之前（含）最近一次**写入的值；若 `ts < 首次写入`，返回 `None`；若最近一次是 delete，返回 `None`。

### 实现（历史用 append-only list + binary search）

```python
def compare_and_set(self, key, field, expected, new_value, timestamp):
    if not self._is_alive(key, field, timestamp):
        return False
    if self._store[key][field] != expected:
        return False
    self._store[key][field] = new_value
    # 保留原 TTL（不重置）——CAS 不改生命周期
    self._history[key][field].append((timestamp, new_value))
    return True

def compare_and_delete(self, key, field, expected, timestamp):
    if not self._is_alive(key, field, timestamp):
        return False
    if self._store[key][field] != expected:
        return False
    del self._store[key][field]
    if key in self._expire and field in self._expire[key]:
        del self._expire[key][field]
    self._history[key][field].append((timestamp, None))
    return True

def get_value_at(self, key, field, timestamp):
    hist = self._history.get(key, {}).get(field, [])
    if not hist:
        return None
    ts_list = [t for t, _ in hist]
    idx = bisect.bisect_right(ts_list, timestamp) - 1
    if idx < 0:
        return None
    return hist[idx][1]  # None 代表历史点就是删除
```

### 踩坑点

- **CAS 是否要保留 TTL**：题目未明说时默认 "保留"（只改值、不改生命周期）。面试里可以主动问面试官。
- **getValueAt 返回 delete 的 None** 是正确行为——"ts 时刻该 field 就是不存在"。**不要**跳过 delete 记录去找更早的 value。
- **二分搜索键要一致**：`bisect_right(ts_list, timestamp)` 找的是严格大于 timestamp 的第一个位置，减 1 就是 "<=" 的最右位置。用 `bisect_left` 会漏当前 timestamp 的写入。

---

## 7. 完整 `InMemoryDB` 类骨架

```python
import bisect
from collections import defaultdict


class InMemoryDB:
    def __init__(self):
        self._store = defaultdict(dict)         # key -> {field: value}
        self._expire = defaultdict(dict)        # key -> {field: expire_at}
        self._backups = []                      # sorted list[(ts, snapshot)]
        self._history = defaultdict(             # key -> {field: [(ts, v_or_None)]}
            lambda: defaultdict(list)
        )

    def _is_alive(self, key, field, now):
        if field not in self._store.get(key, {}):
            return False
        exp = self._expire.get(key, {}).get(field)
        return exp is None or now < exp

    # L1
    def set(self, key, field, value): ...
    def get(self, key, field): ...
    def delete(self, key, field): ...

    # L2
    def scan(self, key): ...
    def scan_by_prefix(self, key, prefix): ...

    # L3
    def set_at(self, key, field, value, timestamp): ...
    def set_at_with_ttl(self, key, field, value, timestamp, ttl): ...
    def get_at(self, key, field, timestamp): ...
    def delete_at(self, key, field, timestamp): ...
    def scan_at(self, key, timestamp): ...
    def scan_by_prefix_at(self, key, prefix, timestamp): ...

    # L4
    def backup(self, timestamp): ...
    def restore(self, timestamp, timestamp_to_restore): ...

    # V2
    def compare_and_set(self, key, field, expected, new_value, timestamp): ...
    def compare_and_delete(self, key, field, expected, timestamp): ...
    def get_value_at(self, key, field, timestamp): ...
```

---

## 8. Corner Cases 小抄

| Category | 现场易错 |
|----------|----------|
| TTL 判定 | `timestamp >= expire_at` 视为过期；用 `<` 做 alive 判定 |
| set_at TTL 清除 | set_at（无 ttl）必须**清**掉之前 set_at_with_ttl 留下的 expire |
| scan timestamp 守卫 | 作者题解漏掉 `is_alive` 检查——scan 会返回已过期 field |
| Read 不 purge | get_at/scan_at 不修改 `_store`——保持同一时刻多次读一致 |
| Backup 过滤 | backup 时已过期 field 不入 snapshot；count 只记活跃 |
| Backup 存储形式 | 存 **remaining_ttl** 不存绝对 expire_at——restore 时重算 |
| Restore TTL 重算 | 新 expire = `timestamp (restore 调用时) + remaining` |
| Restore 无匹配 | 没有 ts <= ts_to_restore 的 backup → no-op |
| CAS TTL 保留 | compare_and_set 不改 TTL（只改值） |
| getValueAt delete | 历史里最近一次是 delete → 返回 None（不往前找） |
| 空字符串 prefix | `"".startswith("")` 永真——退化为 scan，不需特判 |
| 同 timestamp 覆盖 backup | backup(ts) 若已有同 ts 的 backup，覆盖（spec 变体，按题目 spec） |

---

## 9. 复杂度

| Op | Time | Space |
|----|------|-------|
| `set` / `get` / `delete` / `set_at*` / `get_at` / `delete_at` | O(1) 摊销 | O(n·f) 存所有 field |
| `scan` / `scan_at` | O(f log f)，f = 该 key 下 field 数 | O(f) 输出 |
| `scan_by_prefix_at` | O(f log f + p)，p = prefix 长度 | O(k) k 为命中数 |
| `backup` | O(F) 扫所有 field | O(F) snapshot |
| `restore` | O(log B) 二分 + O(F) 装载，B = backup 数 | O(F) |
| `compare_and_*` | O(1) | O(h) 每 field 历史长度 |
| `get_value_at` | O(log h) 二分 | — |

F = 所有 (key, field) 总数；B = backup 条目数；h = 单 field 历史长度。

---

## 10. 考场策略（90 min 版）

1. **L1 + L2 目标 15 min**。双层 dict，扫完排序就交。
2. **L3 TTL 是分水岭**（30–40 min 区段）：
   - 先写 `_is_alive` helper，所有读操作都走它——**集中式 guard**，避免散落五处漏一处。
   - 用 `<` 而不是 `>=`，这条写在草稿纸上以防走神。
   - `set_at` 清 TTL 这条，先用小 case 手动 trace 一遍。
3. **L4 backup/restore**（20 min）：
   - Snapshot 结构死活记住存 `remaining_ttl`——考场上最容易写成绝对 `expire_at`。
   - Restore 时用 `defaultdict(dict)` 一键重置 `_store` / `_expire`，比逐 key 清快。
4. **V2 extras**（15 min）：
   - 历史 list + bisect 一套，写完后用 "先 set A 再 set B 再 delete 再 set C" 手动跑一遍 `get_value_at` 的四个时间点。
5. **Debug 原则**：长链 test case 直接 `print(db._store, db._expire, db._history)` 一行 dump，比 step-through 快。

---

## 11. 参考链接

- 原 docx 提取代码：`staging/04_22_Meta_OA/in memory sys/docx_extract.txt`
- 作者题解 bug：`scan_at` / `scan_by_prefix_at` 缺 `timestamp < expire` guard（本文 §4 踩坑点第 3 条）。
- 相邻题：`[Meta-OA] Cloud File System (4-level)`（同族 4-level 结构）。

---

## 12. 相邻题 (drawer 快跳)

点击下方链接会在右侧 drawer 展开对应题解（ESC 或点击遮罩关闭）。

- **姊妹 4-level**: [Meta-OA Cloud File System 4-level](db://76) · [Meta-OA Bank System L1-L4](db://78)
- **Warm-up 独立算法**: [Meta-OA Standalone Algos](db://79)
- **OA Prep Hub**: [Meta-OA 2026-04-22 OA Prep Hub](db://80)
"""


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    for marker in (
        "## 2. Level 1",
        "## 3. Level 2",
        "## 4. Level 3",
        "## 5. Level 4",
        "## 6. V2 Extras",
        "## 8. Corner Cases",
        "## 9. 复杂度",
    ):
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    if not (6000 <= len(content) <= 25000):
        raise RuntimeError(f"content length {len(content)} outside 6000-25000")


def main() -> int:
    """Upsert the Meta-OA In-Memory Database doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # Verify Meta company exists.
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        # Look up by (company_id, title).
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
