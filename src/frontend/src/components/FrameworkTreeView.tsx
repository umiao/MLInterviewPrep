import { useState, useCallback } from "react";
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

function TreeNode({
  node,
  expandedIds,
  toggleExpand,
  onSelect,
  selectedId,
}: {
  node: FrameworkNode;
  expandedIds: Set<number>;
  toggleExpand: (id: number) => void;
  onSelect: (node: FrameworkNode) => void;
  selectedId: number | null;
}) {
  const hasChildren = node.children.length > 0;
  const isExpanded = expandedIds.has(node.id);
  const isSelected = selectedId === node.id;
  const status = node.status as NodeStatus;

  return (
    <div>
      <div
        className={`flex items-center gap-2 py-1.5 px-2 rounded-md cursor-pointer hover:bg-gray-50 transition-colors ${
          isSelected ? "bg-blue-50 ring-1 ring-blue-200" : ""
        }`}
        style={{ paddingLeft: `${node.depth * 20 + 8}px` }}
        onClick={() => onSelect(node)}
      >
        {/* Expand/collapse toggle */}
        <button
          className="w-5 h-5 flex items-center justify-center shrink-0"
          onClick={(e) => {
            e.stopPropagation();
            if (hasChildren) toggleExpand(node.id);
          }}
        >
          {hasChildren ? <Chevron expanded={isExpanded} /> : <span className="w-4" />}
        </button>

        {/* Title */}
        <span
          className={`text-sm font-medium truncate ${
            node.depth === 0
              ? "text-gray-900 text-base font-semibold"
              : node.depth === 1
                ? "text-gray-800"
                : "text-gray-700"
          }`}
          title={node.title}
        >
          {node.title}
        </span>

        {/* Spacer */}
        <span className="flex-1" />

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
      {hasChildren && isExpanded && (
        <div>
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              expandedIds={expandedIds}
              toggleExpand={toggleExpand}
              onSelect={onSelect}
              selectedId={selectedId}
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
}: {
  nodes: FrameworkNode[];
  onSelect: (node: FrameworkNode) => void;
  selectedId: number | null;
}) {
  // Start with pillars (depth 0) expanded
  const [expandedIds, setExpandedIds] = useState<Set<number>>(() => {
    const ids = new Set<number>();
    for (const n of nodes) {
      if (n.depth === 0) ids.add(n.id);
    }
    return ids;
  });

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

  return (
    <div>
      <div className="flex gap-2 mb-3">
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
      </div>
      <div className="space-y-0.5">
        {nodes.map((node) => (
          <TreeNode
            key={node.id}
            node={node}
            expandedIds={expandedIds}
            toggleExpand={toggleExpand}
            onSelect={onSelect}
            selectedId={selectedId}
          />
        ))}
      </div>
    </div>
  );
}
