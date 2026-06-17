"""Read-only decision report for the LOW-RISK partial pct-stale leaf class.

Source: T-P3-916. Review (missed-4) explicitly split the two ambiguous
drift classes that the fully-checked sweep (T-P0-911/915) left untouched:

* **reverse** -- ``progress_pct > 0`` with **0** boxes checked (the 115/171
  shape). Silent-corruption risk; owned by T-P0-911/T-P0-913. **NOT this task.**
* **partial pct-stale** -- a *partially* checked leaf
  (``0 < checked < total``) whose stored ``progress_pct`` disagrees with the
  deterministic checked-ratio (e.g. node 92: 7/15 boxes checked but
  ``progress_pct = 0``). This is **low-risk and deterministic**: the only
  correct value is the checked-ratio, and the only status move is the
  promote-only ``not_started -> in_progress``. **This task owns ONLY this
  class.**

Why a separate report (and why read-only)
-----------------------------------------
Keeping the two classes in separate queues stops the deterministic, safe fix
from being gated behind the genuinely ambiguous reverse class. This tool does
**zero DB writes** (AC2): it opens a session, classifies by signature, renders
an HTML decision doc to ``logs/review/``, and never commits. The actual
reconcile -- *if the human approves* -- is a trivial follow-up that calls the
already-tested ``scripts.lib.framework_progress.reconcile_node_from_checkboxes``
partial branch (promote-only ``in_progress`` + pct = checked-ratio); it is NOT
performed here.

Determinism
-----------
The "stale" predicate and the recommended target are computed entirely from
the checkbox signature via the single tested T-P0-910 helper
(``count_checkboxes`` / ``checkbox_progress_pct``) -- byte-faithful to the
frontend ``progress_pct`` a live checkbox toggle would PUT. No node id is
hardcoded; the report re-audits the live table every run (AC / edge case: a
node may have moved class since planning).

Run::

    python scripts/audit_partial_pct_stale_20260617.py            # write HTML report
    python scripts/audit_partial_pct_stale_20260617.py --print    # also echo summary
"""

from __future__ import annotations

import argparse
import html
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib.framework_progress import (  # noqa: E402
    checkbox_progress_pct,
    count_checkboxes,
)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402

REPORT_DIR = PROJECT_ROOT / "logs" / "review"
# Fixed (dated) name so an idempotent re-run overwrites the same committed
# deliverable instead of spamming copies (matches the T-P0-914 / T-P0-911
# logs/review/*_20260519 naming convention).
REPORT_PATH = REPORT_DIR / "partial_pct_stale_decision_20260617.html"

# Floating-point tolerance for "stored pct == checked-ratio". progress_pct is
# stored to one decimal (Math.round(.. * 10)/10), so anything beyond 1e-6 is a
# genuine disagreement, not rounding noise.
_PCT_EPS = 1e-6


@dataclass(frozen=True)
class PartialStaleRow:
    """One partially-checked leaf whose stored pct disagrees with the ratio.

    Attributes:
        node_id: ``framework_nodes.id``.
        path: ``framework_nodes.path`` (human-readable).
        status: Current ``framework_nodes.status``.
        stored_pct: Current ``framework_nodes.progress_pct`` (NULL -> 0.0).
        checked: Number of checked checkboxes.
        total: Total checkboxes (checked + unchecked).
        ratio_pct: Deterministic checked-ratio = the recommended target pct.
        target_status: Recommended status -- promote-only
            (``in_progress`` iff currently ``not_started``, else unchanged).
    """

    node_id: int
    path: str
    status: str
    stored_pct: float
    checked: int
    total: int
    ratio_pct: float
    target_status: str


def classify_partial_stale(db) -> list[PartialStaleRow]:
    """Return every partially-checked leaf whose pct != checked-ratio.

    A *leaf* (no node names it as parent) with ``0 < checked < total`` whose
    stored ``progress_pct`` differs from ``checkbox_progress_pct(checked,
    total)`` by more than :data:`_PCT_EPS`. Parent nodes are excluded: their
    pct is a rolled-up projection, not a checkbox-derived fact. A partial leaf
    already in sync (pct == ratio) is **not** stale and is omitted.

    Args:
        db: An active SQLAlchemy session (read-only; never committed).

    Returns:
        Rows sorted by ``node_id``.
    """
    nodes = db.query(FrameworkNode).order_by(FrameworkNode.id).all()
    parent_ids = {n.parent_id for n in nodes if n.parent_id is not None}
    rows: list[PartialStaleRow] = []
    for n in nodes:
        if n.id in parent_ids:
            continue  # not a leaf
        checked, total = count_checkboxes(n.description)
        if not (total > 0 and 0 < checked < total):
            continue  # not partially-checked
        ratio = checkbox_progress_pct(checked, total)
        if ratio is None:
            continue
        stored = float(n.progress_pct or 0.0)
        if abs(stored - ratio) <= _PCT_EPS:
            continue  # already in sync -- not stale
        target_status = "in_progress" if n.status == "not_started" else n.status
        rows.append(
            PartialStaleRow(
                node_id=n.id,
                path=n.path,
                status=n.status,
                stored_pct=stored,
                checked=checked,
                total=total,
                ratio_pct=ratio,
                target_status=target_status,
            )
        )
    return rows


def _row_html(r: PartialStaleRow) -> str:
    """Render one :class:`PartialStaleRow` as a table row."""
    status_cell = (
        f"{html.escape(r.status)} &rarr; <b>{html.escape(r.target_status)}</b>"
        if r.target_status != r.status
        else f"{html.escape(r.status)} <span class='small'>(unchanged)</span>"
    )
    return (
        "<tr>"
        f"<td>{r.node_id}</td>"
        f"<td><code>{html.escape(r.path)}</code></td>"
        f"<td>{r.checked}/{r.total}</td>"
        f"<td class='risk-pct'>{r.stored_pct}</td>"
        f"<td class='ok-pct'><b>{r.ratio_pct}</b></td>"
        f"<td>{status_cell}</td>"
        "</tr>"
    )


def render_html(rows: list[PartialStaleRow], total_nodes: int,
                generated_at: datetime) -> str:
    """Render the read-only decision document (HTML).

    Args:
        rows: Stale partial leaves from :func:`classify_partial_stale`.
        total_nodes: Total framework node count scanned (transparency).
        generated_at: Report generation timestamp.

    Returns:
        The full HTML document as a string.
    """
    ts = generated_at.strftime("%Y-%m-%d %H:%M:%S")
    n = len(rows)
    if rows:
        table = (
            "<table>"
            "<tr><th>node</th><th>path</th><th>boxes</th>"
            "<th>stored pct (stale)</th><th>recommended pct</th>"
            "<th>status</th></tr>"
            + "".join(_row_html(r) for r in rows)
            + "</table>"
        )
        empty_note = ""
    else:
        table = ""
        empty_note = (
            "<div class='box ok'><p class='verdict'>没有任何 partial pct-stale "
            "叶子节点。所有部分勾选的叶子，其 <code>progress_pct</code> 都已等于"
            "勾选比例 —— 无需任何动作（幂等重跑结果）。</p></div>"
        )

    return f"""<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Partial pct-stale 决策稿 (T-P3-916) — {ts}</title>
<style>
  :root{{--ink:#1a1a1a;--mut:#666;--line:#e2e2e2;--ok:#137333;--warn:#9a6700;--risk:#b3261e;--bg:#fafafa;--code:#f4f4f5}}
  *{{box-sizing:border-box}}
  body{{font:15px/1.65 -apple-system,Segoe UI,Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);max-width:980px;margin:0 auto;padding:32px 24px;background:#fff}}
  h1{{font-size:24px;margin:0 0 4px}}
  h2{{font-size:19px;margin:34px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--line)}}
  .sub{{color:var(--mut);margin:0 0 20px}}
  code{{font-family:"SF Mono",Consolas,Menlo,monospace;background:var(--code);padding:1px 5px;border-radius:4px;font-size:13px}}
  .box{{border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0;background:var(--bg)}}
  .ok{{border-left:4px solid var(--ok)}}
  .warn{{border-left:4px solid var(--warn)}}
  .low{{border-left:4px solid var(--warn);background:#fffdf6}}
  table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.5px}}
  th,td{{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}}
  th{{background:#f0f0f1}}
  .risk-pct{{color:var(--risk);font-weight:600}}
  .ok-pct{{color:var(--ok)}}
  .kv{{margin:3px 0}}.kv b{{display:inline-block;min-width:150px;color:var(--mut)}}
  ul{{margin:6px 0 6px 0;padding-left:22px}}li{{margin:3px 0}}
  .small{{font-size:12.5px;color:var(--mut)}}
  .verdict{{font-size:15px;font-weight:600}}
  .tag{{display:inline-block;font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px}}
  .t-low{{background:#fff4e5;color:var(--warn)}}
</style>
</head>
<body>

<h1>Partial pct-stale 决策稿 <span class="tag t-low">LOW RISK · 确定性</span></h1>
<p class="sub">T-P3-916 · 只读审计（零 DB 写入）· 生成于 {ts} · 扫描 {total_nodes} 个 framework 节点</p>

<div class="box low">
<p class="verdict">结论：发现 <b>{n}</b> 个「部分勾选但 <code>progress_pct</code> 落后于勾选比例」的叶子节点。
这是<strong>低风险、确定性</strong>的一类 —— 唯一正确的 pct 就是勾选比例，唯一的状态变化是
promote-only 的 <code>not_started &rarr; in_progress</code>。本稿<strong>不写库</strong>；是否执行回填由你拍板。</p>
<div class="kv"><b>这一类是什么</b> 叶子节点 <code>0 &lt; checked &lt; total</code> 且 <code>progress_pct &ne; 勾选比例</code></div>
<div class="kv"><b>确定性修复</b> <code>progress_pct</code> 回填为勾选比例 + 状态 promote-only 提升至 <code>in_progress</code></div>
<div class="kv"><b>与 115/171 区别</b> 那是 reverse 类（pct&gt;0 但 0 勾选，有静默损坏风险），由 T-P0-911/913 拥有，<strong>不在本稿</strong></div>
</div>

{empty_note}

<h2>受影响的叶子节点</h2>
{table or "<p class='small'>（无）</p>"}

<h2>为什么这是确定性 + 低风险</h2>
<ul>
<li><b>pct 来源唯一</b>：叶子节点的 <code>progress_pct</code> 是勾选状态的<em>投影</em>，不是独立事实
（见 <code>docs/adr/ADR-checkbox-canonical.md</code>）。部分勾选时，正确值只能是
<code>round(checked/total*100,1)</code> —— 没有歧义。</li>
<li><b>状态只升不降</b>：promote-only 规则只把 <code>not_started</code> 提升为 <code>in_progress</code>；
已经是 <code>in_progress</code>/<code>review</code>/<code>mastered</code> 的叶子保持不动 —— 不会丢失任何更高级的进度。</li>
<li><b>无静默损坏风险</b>：与 reverse 类不同，这里勾选框是<strong>有内容的</strong>（用户确实勾了 N 个框），
回填只是让 pct 追上既成事实，不是凭空猜测一个来历不明的数字。</li>
</ul>

<h2>下一步（两个分支）</h2>
<div class="box ok">
<p><b>分支 A — 你批准回填</b>：创建一个 trivial 跟进任务，对上表每个 node 调用
<code>scripts.lib.framework_progress.reconcile_node_from_checkboxes</code> 的 partial 分支
（promote-only <code>in_progress</code> + pct=勾选比例），带 <code>.bak</code> + commit + JSONL 审计，
复用 T-P0-915 的 apply 生命周期。</p>
<p><b>分支 B — 你暂缓</b>：记为<strong>已知低风险欠债</strong>，不做任何动作。叶子节点在 UI 上会继续显示
偏低的进度，但勾选框本身是真实的；随时可重跑本审计确认这一类是否变化。</p>
</div>

<p class="small">复跑：<code>python scripts/audit_partial_pct_stale_20260617.py --print</code> ·
本稿只读，重跑只覆盖同一份 HTML，永不写库。</p>

</body>
</html>
"""


def write_report(content: str) -> Path:
    """Write the HTML decision doc to the fixed ``logs/review/`` deliverable.

    Args:
        content: Rendered HTML from :func:`render_html`.

    Returns:
        Path to the written report.
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")
    return REPORT_PATH


def main(argv: list[str] | None = None) -> int:
    """CLI entry point -- read-only; never writes the DB.

    Args:
        argv: Optional argv override (for tests). Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code (0 success).
    """
    parser = argparse.ArgumentParser(
        description=(
            "Read-only decision report for the partial pct-stale leaf class "
            "(0 < checked < total, pct != ratio). ZERO DB writes."
        )
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="echo",
        help="also echo a console summary",
    )
    args = parser.parse_args(argv)

    init_db()
    db = SessionLocal()
    try:
        total_nodes = db.query(FrameworkNode).count()
        rows = classify_partial_stale(db)
    finally:
        db.rollback()  # belt-and-suspenders: guarantee ZERO DB writes
        db.close()

    report = render_html(rows, total_nodes, datetime.now())
    path = write_report(report)

    if args.echo:
        print(f"[INFO] nodes_scanned={total_nodes} "
              f"partial_pct_stale={len(rows)}")
        for r in rows:
            print(
                f"[STALE] node={r.node_id} {r.path} boxes={r.checked}/"
                f"{r.total} pct {r.stored_pct}->{r.ratio_pct} "
                f"status {r.status}->{r.target_status}"
            )
    print(f"[PASS] decision report written -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
