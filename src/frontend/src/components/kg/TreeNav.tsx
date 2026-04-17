// Adobe/Obsidian-style 3-level outline for the knowledge graph.
// Renders pillar -> category -> leaf with its own independent expand state
// (not coupled to the canvas). Row shows pillar color dot, title, child-count
// badge, and a proportional contentLength mini-bar. The panel can collapse to
// a 40px strip of color dots.
//
// Click-to-navigate integration lives in KG-UX-09; this component only renders
// and self-expands.

import { useMemo, useState } from "react";
import type { KgGraphModel, NodeMeta } from "../../pages/kgGraph.helpers";
import { styleForPillar } from "./kgStyles";

export const TREE_NAV_WIDTH = 260;
export const TREE_NAV_COLLAPSED_WIDTH = 40;
export const TREE_NAV_BAR_MAX_PX = 48;

export interface TreeNavRow {
  id: string;
  meta: NodeMeta;
  depth: number;
  hasChildren: boolean;
}

/**
 * Pure depth-first walk that produces the flat visible row list for the
 * current expand set. Exported so tests can verify expand/collapse logic
 * without needing a DOM.
 */
export function flattenTreeNavRows(
  model: KgGraphModel,
  expanded: Set<string>,
): TreeNavRow[] {
  const rows: TreeNavRow[] = [];
  const walk = (id: string, depth: number) => {
    const meta = model.nodesById.get(id);
    if (!meta) return;
    const kids = model.childrenOf.get(id) ?? [];
    rows.push({ id, meta, depth, hasChildren: kids.length > 0 });
    if (kids.length === 0 || !expanded.has(id)) return;
    for (const kid of kids) walk(kid, depth + 1);
  };
  for (const pid of model.pillarIds) walk(pid, 0);
  return rows;
}

export function maxContentLengthOf(model: KgGraphModel): number {
  let max = 1;
  for (const meta of model.nodesById.values()) {
    if (meta.contentLength > max) max = meta.contentLength;
  }
  return max;
}

export interface TreeNavProps {
  model: KgGraphModel;
  /**
   * Optional seed for the expand set. Defaults to an empty set (pillars only).
   * Used by tests and by parents that want to preselect a tree state.
   */
  initialExpanded?: Set<string>;
  initialCollapsed?: boolean;
}

export default function TreeNav({
  model,
  initialExpanded,
  initialCollapsed = false,
}: TreeNavProps) {
  const [expanded, setExpanded] = useState<Set<string>>(
    () => new Set(initialExpanded ?? []),
  );
  const [collapsed, setCollapsed] = useState(initialCollapsed);

  const maxContentLength = useMemo(() => maxContentLengthOf(model), [model]);

  const toggle = (id: string) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  if (collapsed) {
    return (
      <aside
        data-testid="kg-tree-nav"
        data-collapsed="true"
        aria-label="Knowledge graph outline (collapsed)"
        className="shrink-0 border-r border-gray-200 bg-white flex flex-col items-center py-2 gap-2"
        style={{ width: TREE_NAV_COLLAPSED_WIDTH }}
      >
        <button
          type="button"
          data-testid="kg-tree-nav-toggle"
          aria-label="Expand tree nav"
          onClick={() => setCollapsed(false)}
          className="w-6 h-6 text-xs border border-gray-300 rounded bg-white hover:bg-gray-50"
        >
          {">"}
        </button>
        {model.pillarIds.map((pid) => {
          const meta = model.nodesById.get(pid)!;
          const s = styleForPillar(meta.pillar);
          return (
            <span
              key={pid}
              title={meta.title}
              aria-label={meta.title}
              className="w-3 h-3 rounded-sm"
              style={{ backgroundColor: s.border }}
            />
          );
        })}
      </aside>
    );
  }

  const rows = flattenTreeNavRows(model, expanded);

  return (
    <aside
      data-testid="kg-tree-nav"
      data-collapsed="false"
      aria-label="Knowledge graph outline"
      className="shrink-0 border-r border-gray-200 bg-white overflow-y-auto"
      style={{ width: TREE_NAV_WIDTH }}
    >
      <div className="flex items-center justify-between px-2 py-2 border-b border-gray-100 sticky top-0 bg-white z-10">
        <span className="text-[11px] font-semibold text-gray-600 uppercase tracking-wide">
          Outline
        </span>
        <button
          type="button"
          data-testid="kg-tree-nav-toggle"
          aria-label="Collapse tree nav"
          onClick={() => setCollapsed(true)}
          className="w-6 h-6 text-xs border border-gray-300 rounded bg-white hover:bg-gray-50"
        >
          {"<"}
        </button>
      </div>
      <ul role="tree" className="py-1">
        {rows.map((row) => (
          <TreeRow
            key={row.id}
            row={row}
            isExpanded={expanded.has(row.id)}
            maxContentLength={maxContentLength}
            onToggle={toggle}
          />
        ))}
      </ul>
    </aside>
  );
}

interface TreeRowProps {
  row: TreeNavRow;
  isExpanded: boolean;
  maxContentLength: number;
  onToggle: (id: string) => void;
}

function TreeRow({
  row,
  isExpanded,
  maxContentLength,
  onToggle,
}: TreeRowProps) {
  const { id, meta, depth, hasChildren } = row;
  const style = styleForPillar(meta.pillar);
  const fraction = Math.max(
    0,
    Math.min(1, meta.contentLength / maxContentLength),
  );
  const fillPx = Math.round(fraction * TREE_NAV_BAR_MAX_PX);

  const handleClick = () => {
    if (hasChildren) onToggle(id);
  };
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!hasChildren) return;
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onToggle(id);
    }
  };

  return (
    <li
      role="treeitem"
      aria-expanded={hasChildren ? isExpanded : undefined}
      aria-level={depth + 1}
    >
      <div
        data-testid={`kg-tree-row-${id}`}
        data-depth={depth}
        tabIndex={0}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className="flex items-center gap-1 pr-2 py-1 text-xs hover:bg-gray-50 cursor-pointer focus:outline-none focus:ring-1 focus:ring-blue-400"
        style={{ paddingLeft: 8 + depth * 14 }}
      >
        <span
          aria-hidden
          className="w-2.5 h-2.5 rounded-sm shrink-0"
          style={{ backgroundColor: style.border }}
        />
        {hasChildren ? (
          <span
            aria-hidden
            data-testid={`kg-tree-chevron-${id}`}
            className="w-3 text-gray-500 text-center"
          >
            {isExpanded ? "v" : ">"}
          </span>
        ) : (
          <span aria-hidden className="w-3 shrink-0" />
        )}
        <span
          className="flex-1 truncate text-gray-800 min-w-0"
          title={meta.title}
        >
          {meta.title}
        </span>
        {hasChildren && (
          <span
            data-testid={`kg-tree-badge-${id}`}
            className="text-[9px] px-1 rounded-full shrink-0 font-medium"
            style={{ backgroundColor: style.bg, color: style.border }}
          >
            {meta.childCount}
          </span>
        )}
        <span
          data-testid={`kg-tree-bar-${id}`}
          aria-label="Content length"
          className="h-1 bg-gray-200 rounded-full shrink-0 overflow-hidden"
          style={{ width: TREE_NAV_BAR_MAX_PX }}
        >
          <span
            data-testid={`kg-tree-bar-fill-${id}`}
            className="block h-1 rounded-full"
            style={{
              width: `${fillPx}px`,
              backgroundColor: style.border,
            }}
          />
        </span>
      </div>
    </li>
  );
}
