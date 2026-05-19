"""Single source of truth for checkbox -> status/progress reconciliation.

CONSISTENCY MODEL (Architecture Decision -- see docs/adr/ADR-checkbox-canonical.md)
================================================================================
For a KG-Framework *leaf* node, the **checkbox state inside
``framework_nodes.description``** is the single source of truth for "how done
is this node". ``status`` and ``progress_pct`` are **derived projections** of
that checkbox state, never independent facts:

* ``progress_pct`` = ``round(checked / total * 100, 1)`` (JS ``Math.round``
  semantics, byte-identical to the frontend ``handleCheckboxClick`` path).
* ``status`` is derived from ``progress_pct`` with **promote-only** rules
  (byte-faithful to ``src/backend/routers/framework.py`` L212-227): a fully
  checked leaf is ``mastered``; a partially checked ``not_started`` leaf is
  promoted to ``in_progress``; an already-advanced leaf is never demoted.

Consequences that callers MUST understand:

* **A manual ``status`` edit is NOT authoritative.** If someone hand-sets a
  leaf to ``mastered`` in the DB while its boxes are unchecked, that edit is
  *drift*, not intent, and a future reconcile MAY overwrite it. The checkbox
  state wins. (The single deliberate exception is the *reverse* class --
  ``progress_pct > 0`` with **zero** boxes checked -- which this helper
  refuses to silently zero; see :func:`reconcile_node_from_checkboxes`.)
* If a human genuinely needs a node marked complete *without* a checked
  checklist, that is a **separate, explicit mechanism** (out of scope here) --
  e.g. a ``# RECONCILE-EXEMPT:`` marker the future T-P1-912 guard honours --
  **never a silent direct DB edit**. Direct status/pct DB writes are the
  Invariant-3 violation that produced the 2026-05-19 node-44 drift class.

Why this module exists
----------------------
``status``/``progress_pct`` are only derived on the API ``PUT
/framework/nodes/{id}`` path. Content seed scripts write
``framework_nodes.description`` *directly* (the sanctioned Invariant-3 write
path), which **bypasses** that derivation -- so a seed that checks every box
in prose leaves the node showing "Not Started" until something runs the
derive logic. This module promotes the proven node-44 reconcile into ONE
tested, importable function so every seed can re-derive after a description
write, instead of each script re-implementing (and drifting from) the rule.

Checkbox signature
------------------
Byte-faithful to the frontend (``src/frontend/src/utils/markdown.ts``), which
is the production source of ``progress_pct``. Per line, after left-strip:

* unchecked: ``^[-*]\\s*\\[ \\]``
* checked:   ``^[-*]\\s*\\[[xX]\\]``

(The task spec's documentation approximation ``^\\s*[-*]\\s+\\[[ xX]\\]`` is a
human shorthand; the frontend regex above is authoritative because the helper
must reproduce exactly the ``progress_pct`` a real checkbox toggle would PUT.)

Composability
-------------
:func:`reconcile_node_from_checkboxes` takes an *existing* SQLAlchemy session
and **does NOT commit** -- the caller owns the transaction (a seed can batch a
description write + reconcile + commit atomically). It flushes and calls the
**real** ``_propagate_upward`` imported from
``src.backend.routers.framework`` (never re-implemented, per CLAUDE.md
"no duplicate utilities") so ancestor rollup matches production exactly.
"""
from __future__ import annotations

import logging
import math
import re

from sqlalchemy.orm import Session

from src.backend.models.framework import FrameworkNode

# The REAL production rollup -- imported, NEVER re-implemented (AC1 / CLAUDE.md).
from src.backend.routers.framework import _propagate_upward

logger = logging.getLogger(__name__)

# Byte-faithful to src/frontend/src/utils/markdown.ts (the production source of
# progress_pct). Applied to each line AFTER left-strip (JS String.trimStart()).
_UNCHECKED_RE = re.compile(r"[-*]\s*\[ \]")
_CHECKED_RE = re.compile(r"[-*]\s*\[[xX]\]")


def _js_round(x: float) -> int:
    """Replicate JavaScript ``Math.round`` (round half toward +inf).

    Python's built-in ``round`` uses banker's rounding (round-half-to-even),
    so ``round(62.5) == 62`` whereas ``Math.round(62.5) === 63``. The frontend
    computes ``progress_pct`` with ``Math.round``; the helper MUST match it
    byte-for-byte or a reconciled partial node would disagree with the value a
    live checkbox toggle would PUT. ``checked/total`` is always >= 0, so the
    positive-only ``floor(x + 0.5)`` form is exact here.
    """
    return math.floor(x + 0.5)


def count_checkboxes(description: str | None) -> tuple[int, int]:
    """Return ``(checked, total)`` GFM task-list boxes in ``description``.

    ``total = checked + unchecked``. A ``None``/empty description, or one with
    no checkbox lines, yields ``(0, 0)`` -- never raises (NULL-description
    edge case). Matching is byte-faithful to the frontend counters.

    Args:
        description: Raw markdown body of a framework node, or ``None``.

    Returns:
        Tuple ``(checked_count, total_count)``.
    """
    if not description:
        return (0, 0)
    checked = 0
    unchecked = 0
    for line in description.split("\n"):
        stripped = line.lstrip()
        if _CHECKED_RE.match(stripped):
            checked += 1
        elif _UNCHECKED_RE.match(stripped):
            unchecked += 1
    return (checked, checked + unchecked)


def checkbox_progress_pct(checked: int, total: int) -> float | None:
    """Derive ``progress_pct`` from a checkbox ratio.

    Byte-faithful to ``handleCheckboxClick`` in
    ``src/frontend/src/hooks/useFrameworkNotes.ts``::

        total > 0 ? Math.round((checked / total) * 100 * 10) / 10 : undefined

    Args:
        checked: Number of checked boxes.
        total: Total number of boxes (checked + unchecked).

    Returns:
        Rounded percentage in ``[0, 100]``, or ``None`` when ``total == 0``
        (no checklist -> nothing derivable).
    """
    if total <= 0:
        return None
    return _js_round((checked / total) * 100 * 10) / 10


def reconcile_node_from_checkboxes(db: Session, node_id: int) -> bool:
    """Re-derive a leaf's status/progress from its checkbox state.

    Byte-faithful to the checkbox-driven ``PUT /framework/nodes/{id}`` path
    (``src/backend/routers/framework.py`` L212-227 + the L219-227 timestamp
    side-effects + the L235-240 setattr/flush/propagate), i.e. exactly what a
    real checkbox toggle would persist -- with ONE deliberate, documented
    divergence for the *reverse* class (see below).

    Branch contract (AC5):

    * **fully checked** (``checked == total > 0``) -> ``mastered`` / ``100``;
      stamps ``started_at``/``completed_at`` only-if-NULL.
    * **partially checked** (``0 < checked < total``) -> ``progress_pct`` =
      ratio; ``status`` promoted to ``in_progress`` **only if currently
      ``not_started``** (promote-only: an already ``in_progress``/``review``/
      ``mastered`` leaf keeps its status).
    * **zero checked, no prior progress** -> untouched (no-op).
    * **REVERSE -- ``progress_pct > 0`` with zero boxes checked** (the
      115/171 shape): the live PUT path *would* zero it (the frontend sends
      ``0``); this helper **refuses to** -- it logs a WARN and leaves the row
      untouched. That class is owned by T-P0-911/T-P0-913, never silently
      corrected here.
    * **no checklist / NULL description** (``total == 0``) -> no-op, never
      raises.

    Idempotent (AC4): a second call on an already-reconciled node computes the
    same target state, detects no delta, and returns ``False`` **without
    flushing, propagating, or writing anything**.

    Composability: does **not** commit. On a real change it ``db.flush()``-es
    the leaf then calls the real ``_propagate_upward`` so ancestors are
    recomputed by the production weighted-average + status derivation. The
    caller owns the surrounding transaction/commit.

    Args:
        db: An active SQLAlchemy session (caller-owned; not committed).
        node_id: ``framework_nodes.id`` of the leaf to reconcile.

    Returns:
        ``True`` if the node (and thus its ancestors) was changed, else
        ``False``.
    """
    node = db.query(FrameworkNode).filter(FrameworkNode.id == node_id).first()
    if node is None:
        logger.warning("reconcile: framework_node id=%s not found", node_id)
        return False

    checked, total = count_checkboxes(node.description)

    # No checklist -> nothing is derivable. Never crash on NULL description.
    if total == 0:
        return False

    # Zero checked. Either a genuinely fresh node (no-op) or the REVERSE
    # drift class (pct>0 with 0 boxes -- 115/171 shape). The live PUT path
    # would zero pct here; we deliberately DO NOT (AC5): silently zeroing an
    # unknown-origin pct is itself data loss. Flag it for T-P0-911/913.
    if checked == 0:
        if (node.progress_pct or 0.0) > 0:
            logger.warning(
                "reconcile: REVERSE drift on node %s (%s): progress_pct=%s "
                "but 0/%d boxes checked -- leaving untouched; owned by "
                "T-P0-911/T-P0-913, not silently zeroed here.",
                node_id, node.path, node.progress_pct, total,
            )
        return False

    # checked >= 1 -- compute the target state the checkbox-driven PUT would
    # persist. Mirrors routers/framework.py exactly:
    new_pct = checkbox_progress_pct(checked, total)  # never None here

    # L212-217: promote-only status derive (status absent from a checkbox PUT).
    p = new_pct or 0.0
    status_set = False
    derived_status = node.status
    if p >= 100:
        derived_status = "mastered"
        status_set = True
    elif p > 0 and node.status == "not_started":
        derived_status = "in_progress"
        status_set = True

    target_status = derived_status if status_set else node.status

    # L219-227: timestamp side-effects fire only when status was (re)derived;
    # only-set-never-clear. mastered also pins pct=100 (and the L235 setattr
    # re-applies update_data["progress_pct"], which is exactly 100.0 when
    # fully checked -- so target_pct == new_pct in every branch).
    target_started_at = node.started_at
    target_completed_at = node.completed_at
    if status_set:
        if target_status != "not_started" and node.started_at is None:
            target_started_at = "NOW"  # resolved to datetime.utcnow() on apply
        if target_status == "mastered" and node.completed_at is None:
            target_completed_at = "NOW"
    target_pct = new_pct

    # Idempotency / "writes nothing": decide BEFORE mutating so a no-op never
    # flushes, never propagates, never issues an UPDATE (AC4).
    changed = (
        (node.progress_pct or 0.0) != target_pct
        or node.status != target_status
        or (target_started_at == "NOW" and node.started_at is None)
        or (target_completed_at == "NOW" and node.completed_at is None)
    )
    if not changed:
        return False

    from datetime import datetime  # local: keep module import surface minimal
    now = datetime.utcnow()
    node.progress_pct = target_pct
    node.status = target_status
    if target_started_at == "NOW":
        node.started_at = now
    if target_completed_at == "NOW":
        node.completed_at = now

    db.flush()  # leaf visible to the rollup, mirrors PUT L238
    _propagate_upward(node_id, db)  # the REAL production rollup (AC1)
    return True


def reconcile_all_fully_checked(db: Session) -> list[int]:
    """Reconcile every **fully-checked** leaf; return the changed node ids.

    The safe, unambiguous batch class (Class A in the T-P0-914 root-cause
    note: e.g. nodes 111/114 -- fully checked but never derived to
    ``mastered``). Partial nodes are intentionally **out of scope** of this
    batch (their reconcile is per-node via
    :func:`reconcile_node_from_checkboxes`); the reverse / zero-checked class
    (115/171) is excluded by construction (it is never *fully* checked) and is
    owned by T-P0-911/T-P0-913.

    This is the building block the T-P0-911 sweep composes; it operates by
    signature over the whole table (never an id allowlist) so a node like 69
    with no checklist simply never matches.

    Composability: does **not** commit -- the caller commits once after the
    batch. Each per-node reconcile flushes + propagates internally.

    Args:
        db: An active SQLAlchemy session (caller-owned; not committed).

    Returns:
        Sorted list of ``framework_nodes.id`` that were changed.
    """
    changed_ids: list[int] = []
    nodes = db.query(FrameworkNode).order_by(FrameworkNode.id).all()
    for node in nodes:
        checked, total = count_checkboxes(node.description)
        if (
            total > 0
            and checked == total
            and reconcile_node_from_checkboxes(db, node.id)
        ):
            changed_ids.append(node.id)
    return changed_ids
