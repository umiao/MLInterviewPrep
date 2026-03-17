import { useState, useCallback, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import type { FrameworkNode, NodeStatus } from "../types/framework";

const STATUS_COLORS: Record<NodeStatus, { bg: string; text: string; bar: string }> = {
  not_started: { bg: "bg-red-100", text: "text-red-700", bar: "bg-red-400" },
  in_progress: { bg: "bg-yellow-100", text: "text-yellow-700", bar: "bg-yellow-400" },
  review: { bg: "bg-blue-100", text: "text-blue-700", bar: "bg-blue-400" },
  mastered: { bg: "bg-green-100", text: "text-green-700", bar: "bg-green-400" },
};

const STATUS_LABELS: Record<NodeStatus, string> = {
  not_started: "Not Started",
  in_progress: "In Progress",
  review: "Review",
  mastered: "Mastered",
};

function StatusBadge({ status }: { status: NodeStatus }) {
  const c = STATUS_COLORS[status] ?? STATUS_COLORS.not_started;
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${c.bg} ${c.text}`}>
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}

function ProgressBar({ pct, status }: { pct: number; status: NodeStatus }) {
  const c = STATUS_COLORS[status] ?? STATUS_COLORS.not_started;
  return (
    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
      <div
        className={`h-full rounded-full transition-all duration-300 ${c.bar}`}
        style={{ width: `${Math.min(pct, 100)}%` }}
      />
    </div>
  );
}

function ConfidenceDots({ level }: { level: number }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          className={`w-2 h-2 rounded-full ${
            i <= level ? "bg-blue-500" : "bg-gray-200"
          }`}
        />
      ))}
    </div>
  );
}

/** Chevron icon that rotates when expanded. */
function Chevron({ expanded }: { expanded: boolean }) {
  return (
    <svg
      className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${
        expanded ? "rotate-90" : ""
      }`}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  );
}

/** Highlight matching substring in title. */
function HighlightedTitle({
  title,
  query,
  className,
}: {
  title: string;
  query: string;
  className: string;
}) {
  if (!query) {
    return <span className={className} title={title}>{title}</span>;
  }
  const lowerTitle = title.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const idx = lowerTitle.indexOf(lowerQuery);
  if (idx === -1) {
    return <span className={className} title={title}>{title}</span>;
  }
  const before = title.slice(0, idx);
  const match = title.slice(idx, idx + query.length);
  const after = title.slice(idx + query.length);
  return (
    <span className={className} title={title}>
      {before}
      <mark className="bg-yellow-200 text-inherit rounded-sm px-0.5">{match}</mark>
      {after}
    </span>
  );
}

/**
 * Compute which node IDs match, and which IDs are visible (match or ancestor of match).
 * Returns { matchIds, visibleIds }.
 */
function computeSearchSets(
  nodes: FrameworkNode[],
  query: string,
): { matchIds: Set<number>; visibleIds: Set<number> } {
  const matchIds = new Set<number>();
  const visibleIds = new Set<number>();

  if (!query) return { matchIds, visibleIds };

  const lowerQuery = query.toLowerCase();

  // Collect all matching node IDs and build parent map
  const parentMap = new Map<number, number | null>();
  const walk = (list: FrameworkNode[]) => {
    for (const n of list) {
      parentMap.set(n.id, n.parent_id);
      if (n.title.toLowerCase().includes(lowerQuery)) {
        matchIds.add(n.id);
      }
      walk(n.children);
    }
  };
  walk(nodes);

  // For each match, mark all ancestors as visible
  for (const id of matchIds) {
    visibleIds.add(id);
    let pid = parentMap.get(id) ?? null;
    while (pid !== null) {
      visibleIds.add(pid);
      pid = parentMap.get(pid) ?? null;
    }
  }

  // Also mark children of matches as visible (so matching parent shows its subtree)
  const markChildren = (list: FrameworkNode[]) => {
    for (const n of list) {
      if (matchIds.has(n.id)) {
        const addAll = (children: FrameworkNode[]) => {
          for (const c of children) {
            visibleIds.add(c.id);
            addAll(c.children);
          }
        };
        addAll(n.children);
      }
      markChildren(n.children);
    }
  };
  markChildren(nodes);

  return { matchIds, visibleIds };
}

function TreeNode({
  node,
  expandedIds,
  toggleExpand,
  onSelect,
  selectedId,
  searchQuery,
  matchIds,
  visibleIds,
}: {
  node: FrameworkNode;
  expandedIds: Set<number>;
  toggleExpand: (id: number) => void;
  onSelect: (node: FrameworkNode) => void;
  selectedId: number | null;
  searchQuery: string;
  matchIds: Set<number>;
  visibleIds: Set<number>;
}) {
  const hasChildren = node.children.length > 0;
  const isExpanded = expandedIds.has(node.id);
  const isSelected = selectedId === node.id;
  const isMatch = matchIds.has(node.id);
  const status = node.status as NodeStatus;

  // When searching, filter children to only visible ones
  const isSearching = searchQuery.length > 0;
  const visibleChildren = isSearching
    ? node.children.filter((c) => visibleIds.has(c.id))
    : node.children;
  const showChildren = isSearching ? visibleChildren.length > 0 : hasChildren && isExpanded;

  return (
    <div>
      <div
        className={`flex items-center gap-2 py-1.5 px-2 rounded-md cursor-pointer hover:bg-gray-50 transition-colors ${
          isSelected
            ? "bg-blue-50 ring-1 ring-blue-200"
            : isMatch && isSearching
              ? "bg-yellow-50"
              : ""
        }`}
        style={{ paddingLeft: `${node.depth * 20 + 8}px` }}
        onClick={() => {
          if (hasChildren) toggleExpand(node.id);
          onSelect(node);
        }}
      >
        {/* Expand/collapse toggle */}
        <button
          className="w-5 h-5 flex items-center justify-center shrink-0"
          onClick={(e) => {
            e.stopPropagation();
            if (hasChildren) toggleExpand(node.id);
          }}
        >
          {hasChildren ? (
            <Chevron expanded={isSearching ? showChildren : isExpanded} />
          ) : (
            <span className="w-4" />
          )}
        </button>

        {/* Title */}
        <HighlightedTitle
          title={node.title}
          query={searchQuery}
          className={`text-sm font-medium truncate ${
            node.depth === 0
              ? "text-gray-900 text-base font-semibold"
              : node.depth === 1
                ? "text-gray-800"
                : "text-gray-700"
          }`}
        />

        {/* Spacer */}
        <span className="flex-1" />

        {/* Notes link */}
        <Link
          to={`/framework/${node.id}/notes`}
          onClick={(e) => e.stopPropagation()}
          className="shrink-0 text-gray-400 hover:text-blue-600 transition-colors"
          title="Open notes"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </Link>

        {/* Confidence */}
        {node.depth >= 2 && <ConfidenceDots level={node.confidence_level} />}

        {/* Progress bar */}
        <ProgressBar pct={node.progress_pct} status={status} />

        {/* Percentage */}
        <span className="w-10 text-right text-xs text-gray-500">
          {Math.round(node.progress_pct)}%
        </span>

        {/* Status badge */}
        <StatusBadge status={status} />
      </div>

      {/* Children */}
      {showChildren && (
        <div>
          {visibleChildren.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              expandedIds={expandedIds}
              toggleExpand={toggleExpand}
              onSelect={onSelect}
              selectedId={selectedId}
              searchQuery={searchQuery}
              matchIds={matchIds}
              visibleIds={visibleIds}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function FrameworkTreeView({
  nodes,
  onSelect,
  selectedId,
  searchQuery = "",
}: {
  nodes: FrameworkNode[];
  onSelect: (node: FrameworkNode) => void;
  selectedId: number | null;
  searchQuery?: string;
}) {
  // Start with pillars (depth 0) expanded
  const [expandedIds, setExpandedIds] = useState<Set<number>>(() => {
    const ids = new Set<number>();
    for (const n of nodes) {
      if (n.depth === 0) ids.add(n.id);
    }
    return ids;
  });

  // Build parent map for ancestor lookup
  const parentMap = useMemo(() => {
    const map = new Map<number, number | null>();
    const walk = (list: FrameworkNode[]) => {
      for (const n of list) {
        map.set(n.id, n.parent_id);
        walk(n.children);
      }
    };
    walk(nodes);
    return map;
  }, [nodes]);

  // Auto-expand ancestors when selectedId changes (e.g. URL navigation)
  useEffect(() => {
    if (selectedId === null) return;
    const ancestors: number[] = [];
    let pid = parentMap.get(selectedId) ?? null;
    while (pid !== null) {
      ancestors.push(pid);
      pid = parentMap.get(pid) ?? null;
    }
    if (ancestors.length === 0) return;
    setExpandedIds((prev) => {
      const next = new Set(prev);
      let changed = false;
      for (const id of ancestors) {
        if (!next.has(id)) {
          next.add(id);
          changed = true;
        }
      }
      return changed ? next : prev;
    });
  }, [selectedId, parentMap]);

  const { matchIds, visibleIds } = useMemo(
    () => computeSearchSets(nodes, searchQuery),
    [nodes, searchQuery],
  );

  const toggleExpand = useCallback((id: number) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const expandAll = useCallback(() => {
    const ids = new Set<number>();
    const collect = (list: FrameworkNode[]) => {
      for (const n of list) {
        if (n.children.length > 0) ids.add(n.id);
        collect(n.children);
      }
    };
    collect(nodes);
    setExpandedIds(ids);
  }, [nodes]);

  const collapseAll = useCallback(() => {
    setExpandedIds(new Set());
  }, []);

  const isSearching = searchQuery.length > 0;

  // When searching, filter top-level nodes to visible ones
  const visibleNodes = isSearching
    ? nodes.filter((n) => visibleIds.has(n.id))
    : nodes;

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <button
          className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          onClick={expandAll}
        >
          Expand All
        </button>
        <span className="text-gray-300">|</span>
        <button
          className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          onClick={collapseAll}
        >
          Collapse All
        </button>
        {isSearching && (
          <>
            <span className="text-gray-300">|</span>
            <span className="text-xs text-gray-500">
              {matchIds.size} match{matchIds.size !== 1 ? "es" : ""}
            </span>
          </>
        )}
      </div>
      <div className="space-y-0.5">
        {visibleNodes.length === 0 && isSearching ? (
          <p className="text-sm text-gray-400 py-4 text-center">
            No nodes match &quot;{searchQuery}&quot;
          </p>
        ) : (
          visibleNodes.map((node) => (
            <TreeNode
              key={node.id}
              node={node}
              expandedIds={expandedIds}
              toggleExpand={toggleExpand}
              onSelect={onSelect}
              selectedId={selectedId}
              searchQuery={searchQuery}
              matchIds={matchIds}
              visibleIds={visibleIds}
            />
          ))
        )}
      </div>
    </div>
  );
}
