"""Seed Meta OA Bank System 4-level solution doc.

Per T-P0-248. Target: company_documents (company_id=31 Meta).

Idempotency: sentinel <!-- META_OA_BANKSYS_20260422 --> gates the write.
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
SENTINEL = "<!-- META_OA_BANKSYS_20260422 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-OA] Bank System (L1-L4)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

CONTENT = SENTINEL + r'''
# Meta OA — Bank System (L1-L4)

> **题型**: in-memory bank/ledger system；4 个 level 逐级解锁，同一 `BankSystem` 类贯穿整个 90 min 考场。
> **时长**: 90 分钟整套 4 题（Bank System / In-Memory DB / Cloud FS 属于同一族 4-level 题型）。
> **评分**: 通过 Level 3 (scheduled transfer + expire) ≈ mid；Level 4 (mergeAccounts) 通过 = senior+ 门槛。

---

## 1. Problem Overview

实现一个 **in-memory banking ledger**：支持账户开户、存取款、转账，并逐级扩展到排行榜、延时转账（scheduled transfer）、账户合并。所有操作都带 `timestamp`（严格递增，毫秒级 int），不涉及真实货币语义（没有利率/汇率），但要维护 **spending 累计**（不含 deposit，只计 pay / transfer outbound）。

### Level 梯度

| Level | 新增能力 | 核心数据结构 |
|-------|----------|-------------|
| 1 | `createAccount` / `deposit` / `pay` / `transfer` | `accounts: id -> {balance, spending}` |
| 2 | `topSpenders(n)` 按累计消费排行榜 | 同上 + cache + dirty flag |
| 3 | `scheduleTransfer` / `cancelTransfer` / `acceptTransfer`（带 expire 语义） | 再加 `pending: transfer_id -> record`、`heap: [(process_time, transfer_id)]` |
| 4 | `mergeAccounts(id1, id2)` 保留 balance + spending + 改写 pending transfer | 同上 + rewrite pending + 清堆陈旧条目 |

### 题眼提醒

- **spending 的定义**: 仅累加 `pay(amount)` 和 `transfer(outbound amount)` 的 amount；`deposit` 和 `transfer` 的 **receiver** 都不计 spending。**这条判错 = -1 整个 L2**。
- **topSpenders 的排序**: 按 `spending` 降序，同值时按 `account_id` 字典序升序——Meta OA 标准约定。
- **Scheduled transfer 的 expire 语义**: 创建 scheduled transfer 时**立即 hold** 金额（从 from 账户扣除），`process_time` 到达后进入 "pending accept" 状态，若在 `expire_window` 内未被 `acceptTransfer` 调用，则 **hold 金额退回 source**，transfer 作废。
- **mergeAccounts 要改写 pending**: 合并时把 pending transfer 中 `from == id2` 或 `to == id2` 的条目，全部改写成 `id1`；否则 accept 时会找不到账户。

---

## 2. Level 1: createAccount / deposit / pay / transfer

### API

```python
create_account(timestamp: int, account_id: str) -> bool
deposit(timestamp: int, account_id: str, amount: int) -> int | None   # 返回新 balance
pay(timestamp: int, account_id: str, amount: int) -> int | None        # 返回新 balance
transfer(timestamp: int, from_id: str, to_id: str, amount: int) -> int | None  # 返回 from 的新 balance
```

### 规则

- `create_account`：已存在返回 `False`，否则创建并返回 `True`。初始 `balance=0, spending=0`。
- `deposit` / `pay`：账户不存在返回 `None`；`pay` 余额不足返回 `None`。
- `transfer`：任一账户不存在返回 `None`；**`from == to` 返回 `None`**（自己转给自己无意义）；余额不足返回 `None`。成功时 **from 扣款、to 加款、from 的 spending 累加**。

### 实现

```python
def create_account(self, timestamp, account_id):
    if account_id in self._accounts:
        return False
    self._accounts[account_id] = {"balance": 0, "spending": 0}
    return True

def deposit(self, timestamp, account_id, amount):
    acc = self._accounts.get(account_id)
    if acc is None:
        return None
    acc["balance"] += amount
    return acc["balance"]

def pay(self, timestamp, account_id, amount):
    acc = self._accounts.get(account_id)
    if acc is None or acc["balance"] < amount:
        return None
    acc["balance"] -= amount
    acc["spending"] += amount
    self._dirty = True  # 为 L2 topSpenders 作废 cache
    return acc["balance"]

def transfer(self, timestamp, from_id, to_id, amount):
    if from_id == to_id:
        return None
    src = self._accounts.get(from_id)
    dst = self._accounts.get(to_id)
    if src is None or dst is None or src["balance"] < amount:
        return None
    src["balance"] -= amount
    dst["balance"] += amount
    src["spending"] += amount
    self._dirty = True
    return src["balance"]
```

### 踩坑点

- **spending 只记 from**：`transfer` 不要把 amount 加到 `dst["spending"]`。作者原题解在这里写漏过一次。
- **`from == to` 判空**：Meta 原题明确 "self-transfer returns None"，不要静默通过。
- **amount 允许 0？** 按题目 spec：一般 `amount > 0` 作为前置条件，代码里可以不判；但 `amount < 0` 必须拒绝（Meta OA 测试用例里见过负数攻击）。

---

## 3. Level 2: topSpenders(n) — 缓存 + dirty flag

### API

```python
top_spenders(timestamp: int, n: int) -> list[str]
```

### 规则

- 返回格式 `["<id>(<spending>)", ...]`，按 `spending` 降序，同值按 `id` 升序。
- 长度 `min(n, 账户数)`；不存在账户时返回 `[]`。
- **spending == 0 的账户也要出现**（不是只列有消费的）。

### 缓存设计（dirty flag 优化）

每次 `pay` / `transfer` / 合并账户都把 `self._dirty = True`。
`top_spenders` 调用时：若 `_dirty`，重算并缓存；否则直接返回 cache（含 slice）。

```python
def top_spenders(self, timestamp, n):
    if self._dirty or self._top_cache is None:
        items = [
            (acc["spending"], aid)
            for aid, acc in self._accounts.items()
        ]
        # 注意 tuple 排序：先按 -spending，再按 id
        items.sort(key=lambda x: (-x[0], x[1]))
        self._top_cache = items
        self._dirty = False
    return [f"{aid}({sp})" for sp, aid in self._top_cache[:n]]
```

### 踩坑点

- **排序稳定性**: 直接用 tuple `(-spending, id)` 作 key，不要用 `reverse=True` + 二次排序——后者在同 spending 时会把 id 倒序。
- **cache 失效粒度**: 只要有任何写入操作就 flip dirty；不要试图做 "只有被改过的账户才加回堆"——容易跟 merge/cancel 逻辑打架。
- **n 超长**: `n > len(accounts)` 时直接返回所有账户（`[:n]` 自动处理）。
- **TopN 超时点**: Meta OA 测试里 topSpenders 会被密集调用上千次——**没有 dirty flag 的 O(k log k) 每次重排就会 TLE**。dirty flag 把摊销复杂度降到 O(1) 读 + O(k log k) 写触发。

---

## 4. Level 3: scheduleTransfer / cancelTransfer / acceptTransfer（expire 语义）

### API

```python
schedule_transfer(
    timestamp: int, from_id: str, to_id: str,
    amount: int, delay_ms: int
) -> str | None                             # 返回 transfer_id, 失败返回 None

cancel_transfer(
    timestamp: int, account_id: str, transfer_id: str
) -> bool                                   # from 或 to 都可以 cancel

accept_transfer(
    timestamp: int, account_id: str, transfer_id: str
) -> bool                                   # 只有 to 可以 accept
```

### 核心语义（**必背**）

1. **schedule_transfer 立即 hold**: 创建时就从 from 账户扣除 amount（进 hold），**spending 也立即 +amount**。`process_time = timestamp + delay_ms`。
2. **Expire window**: 常量（题目里给，通常 `EXPIRE_MS = 86400_000` = 24h）。`expire_time = process_time + EXPIRE_MS`。
3. **Process phase**: 当某个操作的 `timestamp >= process_time` 时，该 transfer 变 "pending accept"；到达 `expire_time` 仍未 accept 则**作废**，hold 金额退回 source，**spending 也扣回**。
4. **accept_transfer**: 必须在 `process_time <= ts <= expire_time` 窗口内调用，且 `account_id == to_id`；成功后金额进 to 的 balance，transfer 变 "accepted" 终态。
5. **cancel_transfer**: 只要 transfer 还没 accepted/expired，from 或 to 都可以 cancel；成功后 hold 退回 source（spending 也扣回），变 "cancelled" 终态。

### 懒清理（lazy eviction）

每次对外 API 调用前，先用 `_process_expirations(timestamp)` 把所有 `process_time < timestamp` 且未 accept 的 transfer 处理一遍（用 heapq 按 `process_time` 顺序出队）。这里只做**过期检查 + 退款**——不需要自动 "accept"，accept 永远由显式调用触发。

### 实现

```python
import heapq
from collections import defaultdict

EXPIRE_MS = 86_400_000  # 题目常量，24 小时

def _process_expirations(self, now):
    """弹出所有 process_time <= now 的 pending transfer，处理其 expire。

    Note: 只处理已经到达 process_time 且 expire_time 已过的条目。
    到达 process_time 但未过 expire 的条目要保留在堆里（或用 set 标记已弹出）。
    """
    while self._timers and self._timers[0][0] <= now:
        _, tid = heapq.heappop(self._timers)
        t = self._pending.get(tid)
        if t is None or t["status"] != "scheduled":
            continue  # 已 cancel / accept / merge 改写
        # 进入 pending-accept 阶段后，若 now 超过 expire_time 即作废
        if now >= t["expire_time"]:
            self._refund_hold(t)
            t["status"] = "expired"
        else:
            # 还在 accept 窗口内，标记 ready，但别重新入堆（否则循环）
            t["status"] = "ready"
            # 用独立的 expire heap 延后再检查
            heapq.heappush(self._expire_timers, (t["expire_time"], tid))
    while self._expire_timers and self._expire_timers[0][0] <= now:
        _, tid = heapq.heappop(self._expire_timers)
        t = self._pending.get(tid)
        if t is None or t["status"] != "ready":
            continue
        self._refund_hold(t)
        t["status"] = "expired"

def _refund_hold(self, t):
    """Hold 金额退回 source；spending 同步扣回。"""
    src = self._accounts.get(t["from"])
    if src is not None:
        src["balance"] += t["amount"]
        src["spending"] -= t["amount"]
        self._dirty = True

def schedule_transfer(self, timestamp, from_id, to_id, amount, delay_ms):
    self._process_expirations(timestamp)
    if from_id == to_id:
        return None
    src = self._accounts.get(from_id)
    dst = self._accounts.get(to_id)
    if src is None or dst is None or src["balance"] < amount:
        return None
    tid = f"transfer{self._next_transfer_id}"
    self._next_transfer_id += 1
    # 立即 hold + 计 spending
    src["balance"] -= amount
    src["spending"] += amount
    self._dirty = True
    process_time = timestamp + delay_ms
    self._pending[tid] = {
        "from": from_id,
        "to": to_id,
        "amount": amount,
        "process_time": process_time,
        "expire_time": process_time + EXPIRE_MS,
        "status": "scheduled",
    }
    heapq.heappush(self._timers, (process_time, tid))
    return tid

def cancel_transfer(self, timestamp, account_id, transfer_id):
    self._process_expirations(timestamp)
    t = self._pending.get(transfer_id)
    if t is None or t["status"] not in ("scheduled", "ready"):
        return False
    if account_id not in (t["from"], t["to"]):
        return False
    self._refund_hold(t)
    t["status"] = "cancelled"
    return True

def accept_transfer(self, timestamp, account_id, transfer_id):
    self._process_expirations(timestamp)
    t = self._pending.get(transfer_id)
    if t is None or t["status"] not in ("scheduled", "ready"):
        return False
    if account_id != t["to"]:
        return False
    if timestamp < t["process_time"] or timestamp >= t["expire_time"]:
        return False
    # 正式入账：只加 to 的 balance（spending 已在 schedule 时计过）
    dst = self._accounts[t["to"]]
    dst["balance"] += t["amount"]
    t["status"] = "accepted"
    return True
```

### 作者踩过的 3 个 L3 bug（**考场必背**）

1. **Bug 1 — hold 退回忘扣 spending**: `_refund_hold` 只做 `balance += amount`，漏了 `spending -= amount`。表现：schedule 后 cancel，spending 残留，导致 `top_spenders` 里出现一个从未真正消费的账户排第一。**修复**：退款和加 spending 对称——schedule 时加 spending，refund 必须减 spending。
2. **Bug 2 — activity 记账放错位置**: 最初把 spending 累加放在 `accept_transfer` 里（"收到才算"）。这违反了 Meta 原题定义（"hold 即计入 spending"），并且和 cancel/expire 的 refund 对称性不匹配。**修复**：spending 累加永远在 `schedule_transfer` 的 hold 瞬间发生。
3. **Bug 3 — expire 后仍能被 accept**: 忘了在 `accept_transfer` 里做 `timestamp >= expire_time` 的守卫，测试用例在 expire 后一毫秒调用 accept，程序返回 True。**修复**：accept 先调 `_process_expirations` 推进状态，再严格检查 `process_time <= ts < expire_time`。

### 踩坑点

- **两级 heap**：一个按 `process_time` 出队做 ready 标记，一个按 `expire_time` 做作废。用单个 heap + re-insert 也行，但容易循环 push/pop。
- **cancel 后 heap 陈旧条目**：直接不管——`_process_expirations` 弹出时看 `status != "scheduled"` 就 skip，懒清理。
- **timestamp 严格递增**：Meta 保证外部调用 `timestamp` 递增，但同一 timestamp 可能 multiple calls——heap 顺序用 `(process_time, tid_seq)` 破平，避免 unstable。
- **merge 对 pending 的影响见 §5**。

---

## 5. Level 4: mergeAccounts(id1, id2)

### API

```python
merge_accounts(timestamp: int, id1: str, id2: str) -> bool
```

### 规则（**必背**）

1. 两账户都存在且 `id1 != id2` 才成功，否则返回 `False`。
2. 合并方向：`id2` 的内容并入 `id1`，`id2` 被删除。
3. **Balance**: `id1.balance += id2.balance`。
4. **Spending**: `id1.spending += id2.spending`（累计历史消费保留）。
5. **Pending transfer 改写**: 所有 `status in {scheduled, ready}` 的 pending 记录，把 `from==id2` 改成 `from=id1`，`to==id2` 改成 `to=id1`。**否则 accept 时找不到 id2 账户**。
6. **Self-pending 合并**：若改写后 `from == to`（两头都是合并双方之一），按 Meta spec **退款作废**——保持 transfer 不变性（不允许自转）。

### 实现

```python
def merge_accounts(self, timestamp, id1, id2):
    self._process_expirations(timestamp)
    if id1 == id2:
        return False
    if id1 not in self._accounts or id2 not in self._accounts:
        return False

    # 1) 合并 balance + spending
    a1 = self._accounts[id1]
    a2 = self._accounts[id2]
    a1["balance"] += a2["balance"]
    a1["spending"] += a2["spending"]
    del self._accounts[id2]

    # 2) 改写 pending transfers
    for tid, t in list(self._pending.items()):
        if t["status"] not in ("scheduled", "ready"):
            continue
        rewrote = False
        if t["from"] == id2:
            t["from"] = id1
            rewrote = True
        if t["to"] == id2:
            t["to"] = id1
            rewrote = True
        # self-pending 作废
        if rewrote and t["from"] == t["to"]:
            self._refund_hold(t)
            t["status"] = "cancelled"

    self._dirty = True
    return True
```

### 踩坑点

- **改写前不要删 id2 账户**：如果先 `del self._accounts[id2]` 再 `_refund_hold`，退款会找不到账户——要么合并 balance/spending 早做、再 `del`，要么退款目标统一指向 id1。本实现把 balance/spending 并入 id1 后先 `del id2`，然后改写 pending 时 `_refund_hold` 已经用了 id1（改写完成后的 from）——所以安全。
- **topSpenders cache**：merge 后立即 `self._dirty = True`——合并必改排行榜。
- **历史 cancelled/expired/accepted 不要动**：它们是终态记录，改写了反而破坏审计语义。

---

## 6. Corner Cases 小抄

| Category | 现场易错 |
|----------|----------|
| 自转账 | `transfer(ts, A, A, ...)` → `None`；schedule 同理 |
| 负数/0 amount | `amount <= 0` → `None`（Meta 测试里见过 0 的 edge case） |
| spending 定义 | 只记 from/pay；deposit 不记；transfer 的 receiver 不记 |
| topN 排序 | `(-spending, id)` 作 key，不要 `sorted(...) + reverse=True` |
| topN cache 失效 | pay / transfer / schedule / cancel / expire 退款 / merge 都要 flip dirty |
| Schedule 立即 hold | 立即扣 balance + 加 spending；不要延后到 process_time |
| Accept 时间窗口 | `process_time <= ts < expire_time`，**严格小于** expire |
| Cancel 权限 | from 或 to 都可以 cancel；accept 只有 to |
| Expire 退款 | balance += amount **且** spending -= amount（对称） |
| Merge 改写 pending | `scheduled` 和 `ready` 都要改写；终态不动 |
| Merge 后 self-pending | 改写后若 `from == to` → 作废 + 退款 |
| Heap 陈旧条目 | 懒清理：出队时看 status 判活 |

---

## 7. 完整 `BankSystem` 类骨架

```python
import heapq
from collections import defaultdict


EXPIRE_MS = 86_400_000  # 24h


class BankSystem:
    def __init__(self):
        self._accounts = {}                # id -> {balance, spending}
        self._top_cache = None             # cached sorted list[(spending, id)]
        self._dirty = True
        self._pending = {}                 # tid -> record
        self._next_transfer_id = 1
        self._timers = []                  # heap[(process_time, tid)]
        self._expire_timers = []           # heap[(expire_time, tid)]

    # Internal
    def _refund_hold(self, t): ...
    def _process_expirations(self, now): ...

    # L1
    def create_account(self, timestamp, account_id): ...
    def deposit(self, timestamp, account_id, amount): ...
    def pay(self, timestamp, account_id, amount): ...
    def transfer(self, timestamp, from_id, to_id, amount): ...

    # L2
    def top_spenders(self, timestamp, n): ...

    # L3
    def schedule_transfer(self, timestamp, from_id, to_id, amount, delay_ms): ...
    def cancel_transfer(self, timestamp, account_id, transfer_id): ...
    def accept_transfer(self, timestamp, account_id, transfer_id): ...

    # L4
    def merge_accounts(self, timestamp, id1, id2): ...
```

---

## 8. 复杂度

| Op | Time | Space |
|----|------|-------|
| `create_account` / `deposit` / `pay` / `transfer` | O(1) | O(n) n = 账户数 |
| `top_spenders(n)` | cache 命中 O(n) 切片；miss O(k log k) k = 账户数 | O(k) cache |
| `schedule_transfer` | O(log T) heap push，T = pending transfer 数 | O(T) |
| `cancel_transfer` / `accept_transfer` | 摊销 O(log T)（含 `_process_expirations` 的懒清理） | — |
| `merge_accounts` | O(T) 扫所有 pending + O(1) 账户合并 | — |

---

## 9. 考场策略（90 min 版）

1. **L1 目标 15 min**：4 个方法 + spending 语义，最容易抢分。建议先把 `_accounts = {}` 和 helper `_get(id)` 写好，所有方法走同一 lookup 路径。
2. **L2 目标 10 min**：dirty flag + cache 一套 20 行搞定。先写 naive 每次 `sorted`，再加 cache——**两行 flip 就够**。
3. **L3 目标 35 min（分水岭）**：
   - 先把 schedule_transfer 的 "立即 hold + 加 spending" 写对，草稿纸上画清 `{hold, accept, cancel, expire}` 四种终态的金额流向。
   - `_process_expirations` 写一个两阶段 heap（`process_time` 堆 + `expire_time` 堆），每次对外 API 先调一次。
   - accept 的 `ts >= expire_time` 守卫**一定要写**——作者踩的 bug 3 就是这里。
4. **L4 目标 15 min**：merge 本身简单，关键是**pending 改写 + self-pending 作废**两条。
5. **收尾 5 min**：手跑一个 "schedule → cancel → topSpenders" 的 trace 确认 spending 退回；"schedule → expire → accept" 确认 accept 返回 False。

---

## 10. 相邻题

- `[Meta-OA] In-Memory Database (L1-L4 + V2)` — 同族 4-level, TTL + snapshot/restore。
- `[Meta-OA] Cloud File System (4-level)` — 同族 4-level, prefix/suffix 查找 + compress。
- 考场里这三题按难度序通常是：Cloud FS ≤ Bank System ≤ In-Memory DB（TTL 最难）。

---

## 11. 相邻题 (drawer 快跳)

点击下方链接会在右侧 drawer 展开对应题解（ESC 或点击遮罩关闭）。

- **姊妹 4-level**: [Meta-OA Cloud File System 4-level](db://76) · [Meta-OA In-Memory Database L1-L4 + V2](db://77)
- **Warm-up 独立算法**: [Meta-OA Standalone Algos](db://79)
- **OA Prep Hub**: [Meta-OA 2026-04-22 OA Prep Hub](db://80)

'''


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
        "## 6. Corner Cases",
        "## 8. 复杂度",
        "3 个 L3 bug",
    ):
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    if not (6000 <= len(content) <= 25000):
        raise RuntimeError(f"content length {len(content)} outside 6000-25000")


def main() -> int:
    """Upsert the Meta-OA Bank System doc (idempotent)."""
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
