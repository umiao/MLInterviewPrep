"""Seed Meta OA 2026-04-22 Prep Hub doc (aggregate landing page).

Per T-P1-251 (rewrite of T-P1-250). Target: company_documents
(company_id=31 Meta).

Condenses the four Meta-OA source docs (ids 76/77/78/79) into one compact
landing page optimized for the 90-min exam: always-visible TOC + exam-day
strategy + 4 card-style summaries. Instead of duplicating full solutions
via HTML <details>, the hub uses `[title](db://N)` markdown links. The
frontend MarkdownPreview intercepts the db:// scheme (lines 118-159) and
opens the target doc in a SlideOverPanel drawer (bg-black/40 mask +
right-side slide, Escape / click-outside close) — the same pattern
behavioral prep uses via PrepNotesPage's onDbLinkClick.

Caveat: db:// drawer links only fire when this doc is rendered in the docs
tab of PrepNotesPage (not in the notes tab, which does not wire
onDbLinkClick). Authors viewing the hub inside a standalone preview may
see plain anchor behavior.

Idempotency: sentinel <!-- META_OA_HUB_DRAWER_20260422 --> gates the write.
Second run = 0 writes when content is byte-identical.

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
SENTINEL = "<!-- META_OA_HUB_DRAWER_20260422 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-OA] 2026-04-22 OA Prep Hub"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

# Source per-problem PROBLEM ids (hub opens these in drawer via db:// links).
# Post T-P0-252 migration: detail content now lives in `problems` table, not
# `company_documents`. db://N resolves to /problems/N in ProblemDrawer.
# 1092 Cloud FS · 1093 In-Memory DB · 1094 Bank System · 1095 Standalone Algos.
SOURCE_DOC_IDS = (1092, 1093, 1094, 1095)

CONTENT = SENTINEL + r'''
# Meta OA 2026-04-22 — Prep Hub

> **用法**: 考试当天早上扫这一页。四题速查卡片在下方；点击 [打开完整题解] 链接会在右侧以 drawer (slide-over) 弹出完整题解原文，ESC 或点击遮罩关闭。
> **时长**: 90 min。Warm-up 10 min → Cloud FS 20 min → In-Memory DB 25 min → Bank System 30 min，剩 5 min buffer。

**快速跳转**: [§A Warm-up](db://1095) · [§B Cloud FS](db://1092) · [§C In-Memory DB](db://1093) · [§D Bank System](db://1094)

---

## 目录

- [考场策略 (90-min allocation)](#考场策略-90-min-allocation)
- [一眼速查表](#一眼速查表)
- [§A Standalone Algos warm-up](#a-standalone-algos-warm-up)
- [§B Cloud File System](#b-cloud-file-system)
- [§C In-Memory Database](#c-in-memory-database)
- [§D Bank System](#d-bank-system)
- [跨题共通坑](#跨题共通坑)

---

## 考场策略 (90-min allocation)

| 阶段 | 任务 | 时间盒 | 目标 |
|------|------|--------|------|
| 00-10 min | §A warm-up（§1 + §2 两题 AC） | 10 min | 建立手感；**两题都 AC 是进入 4-level 的入场券** |
| 10-30 min | §B Cloud FS L1→L4 | 20 min | 至少 L1-L3 AC，L4 compress/decompress 骨架 |
| 30-55 min | §C In-Memory DB L1→L4（+ V2 若剩时间） | 25 min | L1-L4 AC；**TTL lazy eviction 是拿分重点** |
| 55-85 min | §D Bank System L1→L4 | 30 min | L1-L3 AC；**L3 scheduleTransfer expire 语义必背**；L4 merge 最难 |
| 85-90 min | Buffer | 5 min | 回头补 §B §C §D corner case 断言 |

**取舍**: 卡壳超过分配时间 1.5 倍就跳。warm-up §2 如果 15 min 还没 AC，直接 return 空实现拿 0 分，进 4-level——4-level 每个 level 约 25-30% 权重，一道独立题 5-10%。

---

## 一眼速查表

| § | 题目 | 类型 | 最优复杂度 | 核心技巧 |
|---|------|------|------------|----------|
| A.1 | Same Start/End Letter Count | 独立算法 | $O(n)$ | `str.split()` 无参 + `casefold()` |
| A.2 | Smallest String via Reversal | 独立算法 | $O(n^3)$ | 枚举 $2n$ 反转 + **identity 合法候选** |
| B | Cloud File System | 4-level 系统设计 | $O(n)$ / 次扫 | `dict[name]=size` + `.COMPRESSED` 后缀约定 |
| C | In-Memory Database | 4-level + V2 | $O(\log k)$ | **TTL lazy eviction**；append-only history |
| D | Bank System | 4-level 账户系统 | $O(\log n)$ | **scheduledTransfer expire**；dirty-flag 缓存；merge 改写 pending |

---

## §A Standalone Algos warm-up

**A.1 Same Start/End Letter Count**:
`sum(1 for w in sentence.split() if w[0].casefold()==w[-1].casefold())`
- 坑：`split(' ')` 挂 tab 测试；`casefold()` 比 `lower()` 鲁棒（`İ`/`ß`）；单字母词天然成立，不加多余守卫。
- 空串：`"".split() == []` → `sum` 返 `0`，无需特判。

**A.2 Smallest String via Prefix/Suffix Reversal**:
- `best = s`（**identity 必须纳入**）；枚举 prefix `range(1, n+1)` 和 suffix `range(n)`。
- `"abcd"` / `"aaaa"` 这类已最优串，只靠 identity 守住。
- Python 字符串 `<` 是按 Unicode code point 的字典序，ASCII 等价；别上 suffix array 炫技。
- 复杂度 $O(n^3) = 2n$ 候选 × $O(n)$ 构造 × $O(n)$ 比较，$n \le 10^3$ 刚好。

**[打开完整题解 → Meta-OA Standalone Algos](db://1095)**

---

## §B Cloud File System

- **L1** `add(name, size)` / `copy(src, dst)` / `get(name)` — `dict[name] = (size, owner)`
- **L2** `find_file(prefix, suffix)` — `sort(key=lambda n: (-size, n))`，**tie-break name 升序**
- **L3** per-user capacity — `users[uid] = (cap, used)`；`used + size > cap` 拒；add_file_by 成功要原子更新
- **L4** `compress` / `decompress` — 名字字面拼接 `.COMPRESSED`，**不用** bool flag；size `// 2` 向下取整；decompress `* 2`（信息损失 OK）
- **坑**：L4 不能重复压缩（suffix 已存在返 `False`）；decompress 时目标 base name 若已被占用也返 `False`。

**[打开完整题解 → Meta-OA Cloud File System 4-level](db://1092)**

---

## §C In-Memory Database

- **L1** `set / get / delete(key, field, value)` — 二级 dict `data[key][field]`
- **L2** `scan(key)` / `scan_by_prefix(key, prefix)` — 按 field 字典序返 `"field(value)"` 列表
- **L3** TTL — `set_at(key, field, value, ts, ttl)`；判活用 `ts < exp` **严格小于**；lazy eviction（读到过期才删）
- **L4** `backup(ts)` / `restore(from_ts, current_ts)` — 快照必 `deepcopy`；TTL 重新计时（expires 改为 `current_ts + (exp - backup_ts)`）
- **V2** CAS (`compare_and_set` / `compare_and_delete`) + `get_value_at` — append-only history list + `bisect_right((ts, chr(0x10FFFF))) - 1`
- **坑**：`ts == exp` 已过期不可读；backup 忘 deepcopy → restore 污染；V2 history 保持严格升序（用 `(ts, seq)` tie-break 更稳）。

**[打开完整题解 → Meta-OA In-Memory Database L1-L4 + V2](db://1093)**

---

## §D Bank System

- **L1** `createAccount / deposit / pay / transfer(ts, src, dst, amount)`
- **L2** `topSpenders(ts, n)` — `sorted(key=lambda x: (-spent, id))` + **dirty-flag 缓存**（`O(n\log n)` 摊销到修改侧）
- **L3** `scheduleTransfer / cancelTransfer / acceptTransfer` — `expires_at = ts + delay`；**`now >= expires_at` 已过期**；expire 退款在 **src**（不是 dst）；FIFO 过期。
- **L4** `mergeAccounts(id1, id2)` — id2 并入 id1；`spent / balance` 合并；pending transfer 的 `src` 和 `dst` **双向都要改写**；self-pending 作废；merge 后 `dirty = True`。
- **3 个 L3 必背 bug**：(1) 过期用 `>=` 不是 `>`；(2) expire 退款在 src；(3) cancel 与 expire 共享 `_refund(src, amount)` 避免两处重复逻辑。

**[打开完整题解 → Meta-OA Bank System L1-L4](db://1094)**

---

## 跨题共通坑

1. **timestamp 单调性**：§C §D 所有带 ts 的 API 假设 ts 单调不减；题目通常会明确，非单调要额外排序。
2. **empty input 短路**：§A.1 `""→0`；§A.2 `""→""`；§B `find_file("","")→全文件`；§C `scan_by_prefix(key,"")→该 key 全 field`。测试用例经常偷塞空串。
3. **字典序 vs 自然数序**：§B §C §D 的 tie-break 全是字典序——**`"10" < "2"`**。若 spec 要自然数序要特判 `int(x)`。
4. **返回类型**：`get` 查不到返 `None` 还是 `""`？`find_file` 无匹配返 `[]` 还是 `None`？读题确认——写错类型 = 整题 0 分。
5. **负数 adversarial**：Meta 测试偶有负 `amount` 的 deposit / transfer——guard `amount > 0`；Python 任意精度不会 overflow，但业务约束仍要校验。

---

> **离场 checklist**（交卷前 60 秒扫 4 题）：(1) API 返回类型对齐 spec？(2) empty input 短路？(3) §C TTL 用 `ts < exp` 严格小于？(4) §D L4 merge 后 `dirty = True`？

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
    toc_match = re.search(
        r"## 目录\s*\n(.*?)\n---",
        content,
        re.DOTALL,
    )
    if not toc_match:
        raise RuntimeError("TOC block not found between '## 目录' and '---'")
    toc_block = toc_match.group(1)
    anchors = re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", toc_block)
    if not anchors:
        raise RuntimeError("no [text](#anchor) entries in TOC block")
    headings = re.findall(r"^#{2,3}\s+(.+?)\s*$", content, re.MULTILINE)
    heading_slugs = {slugify(h) for h in headings}
    for text, anchor in anchors:
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
    """Cheap structural checks on the content payload.

    Enforces the SlideOverPanel drawer pattern: zero HTML `<details>`,
    at least 5 `db://` markdown links, and a sensible length budget
    (4000-6000 chars vs. the old 15327-char version that duplicated full
    solutions inline).
    """
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    required_markers = (
        "## 目录",
        "## 考场策略 (90-min allocation)",
        "## 一眼速查表",
        "## §A Standalone Algos warm-up",
        "## §B Cloud File System",
        "## §C In-Memory Database",
        "## §D Bank System",
        "## 跨题共通坑",
        "快速跳转",
    )
    for marker in required_markers:
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    if "<details>" in content or "</details>" in content:
        raise RuntimeError(
            "HTML <details> drawers are forbidden — use [title](db://N) "
            "markdown links so MarkdownPreview opens SlideOverPanel"
        )
    n_db_links = len(re.findall(r"\]\(db://\d+\)", content))
    if n_db_links < 5:
        raise RuntimeError(
            f"expected >=5 'db://' drawer links, got {n_db_links}"
        )
    for sid in SOURCE_DOC_IDS:
        if f"db://{sid}" not in content:
            raise RuntimeError(f"missing db://{sid} cross-link")
    if not (3500 <= len(content) <= 6000):
        raise RuntimeError(f"content length {len(content)} outside 3500-6000")
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

        # Sanity: the 4 source problems we drawer-link to must exist.
        # Post T-P0-252: detail content migrated from company_documents to problems;
        # db://N now resolves to /problems/N via ProblemDrawer.
        placeholders = ",".join("?" * len(SOURCE_DOC_IDS))
        source_rows = conn.execute(
            f"SELECT id, title FROM problems WHERE id IN ({placeholders})",
            SOURCE_DOC_IDS,
        ).fetchall()
        found_ids = {r[0] for r in source_rows}
        missing = [sid for sid in SOURCE_DOC_IDS if sid not in found_ids]
        if missing:
            print(
                f"[ERROR] source problems missing: {missing} — "
                "hub depends on T-P0-252 migration seed (problems 1092-1095)"
            )
            return 1
        print(f"[OK] all {len(SOURCE_DOC_IDS)} source problems present")

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
