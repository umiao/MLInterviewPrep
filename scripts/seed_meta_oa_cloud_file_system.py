"""Seed Meta OA Cloud File System 4-level solution doc.

Per T-P0-246. Target: company_documents (company_id=31 Meta).

Idempotency: sentinel <!-- META_OA_CLOUDFS_20260422 --> gates the write.
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
SENTINEL = "<!-- META_OA_CLOUDFS_20260422 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-OA] Cloud File System (4-level)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

CONTENT = SENTINEL + r"""
# Meta OA — Cloud File System (4-level)

> **题型**: in-memory storage system design；4 个 level 逐级解锁，下一关依赖上一关通过。
> **时长**: 90 分钟整套 4 题（Cloud FS / In-Memory DB / Bank System 属于同一族）。
> **评分**: 通过 Level 3 ≈ mid；Level 4 通过 = senior+ 门槛。

---

## 1. Problem Overview

实现一个 **in-memory cloud storage**：文件只有 `name` 和 `size` 两个属性，**不存在真实的目录树**——`name` 就是一个整串 path-like 字符串，比较靠 `startswith` / `endswith` 做。题目明确保证 *"queries will never call operations that result in collisions between file and directory names"*，所以不需要维护 directory 实体。

### Level 梯度

| Level | 新增能力 | 核心数据结构 |
|-------|----------|-------------|
| 1 | `add` / `copy` / `get` | `name -> (size, owner)` dict |
| 2 | `find_file(prefix, suffix)` | 同上，**无需** Trie（O(n) 线性扫描足够） |
| 3 | `add_user` / `add_file_by` / `update_capacity` | 再加 `user -> {capacity, used}` dict |
| 4 | `compress_file` / `decompress_file` | 同上 + 后缀约定 `".COMPRESSED"` |

---

## 2. Level 1: add / copy / get

### API

```python
add_file(name: str, size: int) -> bool
copy_file(name_from: str, name_to: str) -> bool
get_file_size(name: str) -> int | None
```

### 关键规则

- `add_file` 若 name 已存在 → 返回 `False`（**不覆盖**）。
- `copy_file` 若 `name_from` 不存在或 `name_to` 已存在 → 返回 `False`。
- 题目提及 *"points to a directory"*，但保证不会有 directory collision，所以实现里不用显式判 directory。

### 实现

```python
def add_file(self, name, size):
    return self._add_owned(owner="admin", name=name, size=size) is not None

def copy_file(self, name_from, name_to):
    if name_from not in self._files or name_to in self._files:
        return False
    size, owner = self._files[name_from]
    if self._users[owner]["used"] + size > self._users[owner]["capacity"]:
        return False
    self._users[owner]["used"] += size
    self._files[name_to] = (size, owner)
    return True

def get_file_size(self, name):
    entry = self._files.get(name)
    return entry[0] if entry else None
```

---

## 3. Level 2: find_file by prefix + suffix

### API

```python
find_file(prefix: str, suffix: str) -> list[str]
```

### 规则

- 返回 `name.startswith(prefix) and name.endswith(suffix)` 的所有文件。
- 排序：**size 降序，同 size 时 name 升序**。
- 格式："`<name>(<size>)`"，无匹配返回 `[]`。

### 实现

```python
def find_file(self, prefix, suffix):
    hits = [
        (size, name)
        for name, (size, _) in self._files.items()
        if name.startswith(prefix) and name.endswith(suffix)
    ]
    hits.sort(key=lambda x: (-x[0], x[1]))
    return [f"{name}({size})" for size, name in hits]
```

### 踩坑点

- **不要**用 Trie 搞双端前后缀索引。题目原话是 *"code that passes the unit tests is sufficient"*，O(n·L) 暴力扫描就够。花时间写 Trie 一是 bug 多，二是 prefix+suffix 双端 trie 结构复杂度不低。
- 返回 list 顺序错了也会挂 test：key 必须是 `(-size, name)`，不是 `(size, -name)`。

---

## 4. Level 3: users + capacity

### API

```python
add_user(user_id: str, capacity: int) -> bool
add_file_by(user_id: str, name: str, size: int) -> int | None   # 剩余容量
update_capacity(user_id: str, capacity: int) -> int | None       # 驱逐数量
```

### 关键规则

1. **Admin 内置**：`"admin"` 默认存在、容量 `inf`。Level 1 的 `add_file` 统一走 admin。
2. **`copy_file` 保留原 owner**（**不是** caller），这一条容易漏——导致 capacity 记账错误。
3. **Shrink 驱逐顺序**：`update_capacity` 把 cap 调低，若 `used > new_cap`，按 **size 降序 → name 升序** 逐个删除，直到 `used <= new_cap`。
4. 未知 user → `None`（不是 `False`）。

### 实现

```python
def add_user(self, user_id, capacity):
    if user_id in self._users:
        return False
    self._users[user_id] = {"capacity": capacity, "used": 0}
    return True

def add_file_by(self, user_id, name, size):
    return self._add_owned(owner=user_id, name=name, size=size)

def update_capacity(self, user_id, capacity):
    if user_id not in self._users:
        return None
    self._users[user_id]["capacity"] = capacity
    if self._users[user_id]["used"] <= capacity:
        return 0
    owned = [
        (-size, name)
        for name, (size, owner) in self._files.items()
        if owner == user_id
    ]
    heapq.heapify(owned)
    removed = 0
    while self._users[user_id]["used"] > capacity and owned:
        neg_size, name = heapq.heappop(owned)
        size = -neg_size
        if name not in self._files:
            continue
        cur_size, cur_owner = self._files[name]
        if cur_owner != user_id or cur_size != size:
            continue
        del self._files[name]
        self._users[user_id]["used"] -= size
        removed += 1
    return removed
```

### 踩坑点

- **Heap 里放的是旧快照**：Level 4 `compress_file` 会改 size 和 name。所以从 heap 弹出后一定要**回查**当前 `self._files[name]` 是否仍对应同一个 `(size, owner)`。否则会 double-evict 或 evict 错文件。
- **admin 的 `used`** 不要维护（或维护但不检查）——admin 容量 inf，没意义，但如果维护了，`copy_file` 的 used += size 仍需要执行，否则 admin→user merge 类扩展题会出错。本实现统一维护 used，只是不对 admin 做 cap 检查（inf 比较永远通过）。

---

## 5. Level 4: compress / decompress

> **注意**：截图里没有 Level 4 的原始 spec，下列接口是按 docx 提取代码 + Meta OA 常见变体推断。

### API

```python
compress_file(name: str) -> bool
decompress_file(name: str) -> bool
```

### 规则（约定 suffix = `".COMPRESSED"`）

- `compress_file`:
  - name 不存在 → `False`。
  - name 已以 `.COMPRESSED` 结尾（double-compress）→ `False`。
  - 目标 `name + ".COMPRESSED"` 已存在 → `False`。
  - 否则：old 文件删除，新建 `name+".COMPRESSED"` 大小 `size // 2`（**整除**），owner 不变；used 减少 `size - size//2`。
  - **不做** 容量检查（压缩只会释放字节）。

- `decompress_file`:
  - name 不以 `.COMPRESSED` 结尾 → `False`。
  - 去掉后缀的 `new_name` 已存在 → `False`（碰撞）。
  - 新 size = `size * 2`；若 `used + size > capacity` → `False`。
  - 否则：old 文件删除，新建 `new_name` 大小 `size*2`，owner 不变。

### 实现

```python
COMPRESSED_SUFFIX = ".COMPRESSED"

def compress_file(self, name):
    if name not in self._files or name.endswith(COMPRESSED_SUFFIX):
        return False
    new_name = name + COMPRESSED_SUFFIX
    if new_name in self._files:
        return False
    size, owner = self._files[name]
    new_size = size // 2
    del self._files[name]
    self._files[new_name] = (new_size, owner)
    if owner in self._users:
        self._users[owner]["used"] -= (size - new_size)
    return True

def decompress_file(self, name):
    if name not in self._files or not name.endswith(COMPRESSED_SUFFIX):
        return False
    new_name = name[: -len(COMPRESSED_SUFFIX)]
    if new_name in self._files:
        return False
    size, owner = self._files[name]
    new_size = size * 2
    delta = new_size - size
    if owner in self._users:
        cap = self._users[owner]["capacity"]
        if self._users[owner]["used"] + delta > cap:
            return False
        self._users[owner]["used"] += delta
    del self._files[name]
    self._files[new_name] = (new_size, owner)
    return True
```

### 踩坑点

- **Double compress / re-decompress**：必须用 `endswith` 短路。**不要** 用一个 `is_compressed` bool 属性——后缀约定是唯一 source of truth。
- **Collision check**：decompress 时如果 base name 已经被另一个文件占用，**不能** 覆盖，必须返回 `False`。
- **Heap stale entry**（和 Level 3 的 `update_capacity` 交叉）：compress 改了 size，heap 里旧 entry 已过期，回查保护是关键。

---

## 6. 完整 `CloudFS` 类骨架

```python
import heapq

COMPRESSED_SUFFIX = ".COMPRESSED"


class CloudFS:
    def __init__(self):
        self._files = {}                                  # name -> (size, owner)
        self._users = {"admin": {"capacity": float("inf"), "used": 0}}

    # Level 1
    def add_file(self, name, size): ...
    def copy_file(self, name_from, name_to): ...
    def get_file_size(self, name): ...

    # Level 2
    def find_file(self, prefix, suffix): ...

    # Level 3
    def add_user(self, user_id, capacity): ...
    def add_file_by(self, user_id, name, size): ...
    def update_capacity(self, user_id, capacity): ...

    # Level 4
    def compress_file(self, name): ...
    def decompress_file(self, name): ...

    # shared helper
    def _add_owned(self, owner, name, size):
        if owner not in self._users: return None
        if name in self._files: return None
        u = self._users[owner]
        if u["used"] + size > u["capacity"]: return None
        self._files[name] = (size, owner)
        u["used"] += size
        remaining = u["capacity"] - u["used"]
        return remaining if remaining == float("inf") else int(remaining)
```

---

## 7. Corner Cases 小抄

| Category | 现场易错 |
|----------|----------|
| Return type | L1/L2 返回 bool；L3 `add_file_by` / `update_capacity` 返回 **int 或 None**（不是 False） |
| Admin 语义 | admin 容量 inf，`copy_file` 保留原 owner（**非** caller） |
| Capacity check | `used + size > cap` 用 `>` 不是 `>=`；等于 cap 合法 |
| Eviction order | **size desc, name asc**；shrink 后剩余恰好 `<= new_cap` 即停 |
| Heap stale | `update_capacity` 从 heap 弹出后必须回查 `(size, owner)` 一致性 |
| Compress suffix | `.COMPRESSED` 是唯一 is_compressed 判据；不要另建 bool 属性 |
| Double compress | `compress_file` 里先查 `endswith(suffix)` 再做其他判断 |
| Decompress collision | base name 已占用 → `False`（不覆盖） |
| Decompress cap | `used + delta > capacity` → `False`；容量恰好够仍合法 |
| copy 跨所有者 | 题目不允许（copy 保留原 owner），但如果 spec 改成 "new owner"，记账要同步迁移 used |

---

## 8. 复杂度

| Op | Time | Space |
|----|------|-------|
| `add_file` / `copy_file` / `get_file_size` | O(1) | O(n) 存文件 |
| `find_file` | O(n · L) 扫描 + O(k log k) 排序，L = 平均 name 长度 | O(k) 输出 |
| `add_user` / `add_file_by` | O(1) | O(u) 存用户 |
| `update_capacity` | O(f log f) 建堆 + O(e log f) 驱逐；f = 该 user 的文件数，e = 驱逐数 | O(f) |
| `compress_file` / `decompress_file` | O(1) 摊销 | O(1) |

n = 总文件数，k = `find_file` 命中数。题目明确不要求最优；O(n) 扫 + `sort` 即可。

---

## 9. 考场策略（90 min 版）

1. **L1 + L2 目标 25 min 做完**（15 min 理想）。Dict + startswith/endswith，稳扎稳打。
2. **L3 容量账本**：30–40 min 区段。三个坑——admin inf、copy 保留 owner、eviction 的 size-desc/name-asc 排序。建议 15 min 写完后跑一轮手动 trace 检查 `used` 字段。
3. **L4 compress / decompress**：如果 L3 卡壳就直接跳 L4 的数据结构延展（suffix 约定 + capacity delta 回滚），模式比 L3 简单。
4. **Debug 原则**：Meta OA 的 test case 经常是 **10 个 account × 多种操作**的长链，看不懂就在本地 `print(fs._files, fs._users)` 一行 dump 整个状态，比 step-through 快得多。

---

## 10. 参考链接

- 原 docx 提取代码：`staging/04_22_Meta_OA/docx_extract.txt`
- Level 4 原截图缺失；`.COMPRESSED` 后缀约定为 Meta OA 常见变体推断。

---

## 11. 相邻题 (drawer 快跳)

点击下方链接会在右侧 drawer 展开对应题解（ESC 或点击遮罩关闭）。

- **姊妹 4-level**: [Meta-OA In-Memory Database L1-L4 + V2](db://77) · [Meta-OA Bank System L1-L4](db://78)
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
        "## 7. Corner Cases",
        "## 8. 复杂度",
    ):
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    if not (5000 <= len(content) <= 20000):
        raise RuntimeError(f"content length {len(content)} outside 5000-20000")


def main() -> int:
    """Upsert the Meta-OA Cloud File System doc (idempotent)."""
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
