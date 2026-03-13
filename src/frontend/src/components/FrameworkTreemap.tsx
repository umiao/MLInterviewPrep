import { useMemo, useState } from "react";
import type { FrameworkNode, NodeStatus } from "../types/framework";

const STATUS_BG: Record<NodeStatus, string> = {
  not_started: "bg-red-200 hover:bg-red-300",
  in_progress: "bg-yellow-200 hover:bg-yellow-300",
  review: "bg-blue-200 hover:bg-blue-300",
  mastered: "bg-green-200 hover:bg-green-300",
};

const STATUS_BORDER: Record<NodeStatus, string> = {
  not_started: "border-red-300",
  in_progress: "border-yellow-300",
  review: "border-blue-300",
  mastered: "border-green-300",
};

interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface TreemapItem {
  node: FrameworkNode;
  rect: Rect;
}

/** Collect leaf nodes (or depth-2 nodes) from the tree for treemap layout. */
function collectLeaves(
  nodes: FrameworkNode[],
  maxDepth: number,
): FrameworkNode[] {
  const leaves: FrameworkNode[] = [];
  const walk = (list: FrameworkNode[], depth: number) => {
    for (const n of list) {
      if (n.children.length === 0 || depth >= maxDepth) {
        leaves.push(n);
      } else {
        walk(n.children, depth + 1);
      }
    }
  };
  walk(nodes, 0);
  return leaves;
}

/**
 * Squarified treemap layout.
 * Lays out items within a bounding rect, sized by their value.
 */
function squarify(
  items: { node: FrameworkNode; value: number }[],
  bounds: Rect,
): TreemapItem[] {
  if (items.length === 0) return [];

  const totalValue = items.reduce((s, i) => s + i.value, 0);
  if (totalValue <= 0) return [];

  const result: TreemapItem[] = [];
  let { x, y, w, h } = bounds;

  // Simple slice-and-dice: alternate horizontal/vertical
  const sorted = [...items].sort((a, b) => b.value - a.value);

  for (let i = 0; i < sorted.length; i++) {
    const remaining = sorted.slice(i).reduce((s, it) => s + it.value, 0);
    const ratio = sorted[i].value / remaining;

    if (w >= h) {
      const itemW = w * ratio;
      result.push({ node: sorted[i].node, rect: { x, y, w: itemW, h } });
      x += itemW;
      w -= itemW;
    } else {
      const itemH = h * ratio;
      result.push({ node: sorted[i].node, rect: { x, y, w, h: itemH } });
      y += itemH;
      h -= itemH;
    }
  }

  return result;
}

/** Pillar group header for the treemap. */
function PillarSection({
  pillar,
  leaves,
  containerWidth,
  totalImportance,
  onSelect,
  selectedId,
}: {
  pillar: FrameworkNode;
  leaves: FrameworkNode[];
  containerWidth: number;
  totalImportance: number;
  onSelect: (node: FrameworkNode) => void;
  selectedId: number | null;
}) {
  const pillarImportance = leaves.reduce((s, n) => s + Math.max(n.importance, 0.1), 0);
  const widthPct = totalImportance > 0 ? (pillarImportance / totalImportance) * 100 : 0;
  const heightPx = 280;

  const items = leaves.map((n) => ({
    node: n,
    value: Math.max(n.importance, 0.1),
  }));

  const layoutItems = squarify(items, { x: 0, y: 0, w: 100, h: 100 });

  return (
    <div
      className="inline-block align-top"
      style={{ width: `${widthPct}%`, minWidth: "200px" }}
    >
      <div className="text-sm font-semibold text-gray-700 px-1 mb-1 truncate" title={pillar.title}>
        {pillar.title}
      </div>
      <div
        className="relative bg-gray-100 rounded-lg overflow-hidden border border-gray-200"
        style={{ height: `${heightPx}px` }}
      >
        {layoutItems.map((item) => {
          const status = item.node.status as NodeStatus;
          const bg = STATUS_BG[status] ?? STATUS_BG.not_started;
          const border = STATUS_BORDER[status] ?? STATUS_BORDER.not_started;
          const isSelected = selectedId === item.node.id;
          return (
            <div
              key={item.node.id}
              className={`absolute border cursor-pointer transition-all duration-200 overflow-hidden p-1 ${bg} ${border} ${
                isSelected ? "ring-2 ring-blue-500 z-10" : ""
              }`}
              style={{
                left: `${item.rect.x}%`,
                top: `${item.rect.y}%`,
                width: `${item.rect.w}%`,
                height: `${item.rect.h}%`,
              }}
              title={`${item.node.title} (${Math.round(item.node.progress_pct)}%)`}
              onClick={() => onSelect(item.node)}
            >
              {item.rect.w > 8 && item.rect.h > 8 && (
                <span className="text-xs leading-tight text-gray-800 font-medium line-clamp-3">
                  {item.node.title}
                </span>
              )}
              {item.rect.w > 15 && item.rect.h > 20 && (
                <span className="text-xs text-gray-600 block mt-0.5">
                  {Math.round(item.node.progress_pct)}%
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function FrameworkTreemap({
  nodes,
  onSelect,
  selectedId,
}: {
  nodes: FrameworkNode[];
  onSelect: (node: FrameworkNode) => void;
  selectedId: number | null;
}) {
  const [treemapDepth, setTreemapDepth] = useState(2);

  const pillarData = useMemo(() => {
    return nodes.map((pillar) => ({
      pillar,
      leaves: collectLeaves([pillar], treemapDepth),
    }));
  }, [nodes, treemapDepth]);

  const totalImportance = useMemo(() => {
    return pillarData.reduce(
      (s, p) => s + p.leaves.reduce((ls, n) => ls + Math.max(n.importance, 0.1), 0),
      0,
    );
  }, [pillarData]);

  return (
    <div>
      {/* Depth selector */}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-sm text-gray-600">Detail level:</span>
        {[1, 2, 3].map((d) => (
          <button
            key={d}
            className={`text-xs px-2 py-1 rounded ${
              treemapDepth === d
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
            onClick={() => setTreemapDepth(d)}
          >
            Depth {d}
          </button>
        ))}
      </div>

      {/* Legend */}
      <div className="flex gap-4 mb-3">
        {(["not_started", "in_progress", "review", "mastered"] as NodeStatus[]).map((s) => (
          <div key={s} className="flex items-center gap-1">
            <div className={`w-3 h-3 rounded-sm ${STATUS_BG[s].split(" ")[0]}`} />
            <span className="text-xs text-gray-600 capitalize">{s.replace("_", " ")}</span>
          </div>
        ))}
      </div>

      {/* Treemap grid */}
      <div className="flex gap-2 overflow-x-auto">
        {pillarData.map(({ pillar, leaves }) => (
          <PillarSection
            key={pillar.id}
            pillar={pillar}
            leaves={leaves}
            containerWidth={800}
            totalImportance={totalImportance}
            onSelect={onSelect}
            selectedId={selectedId}
          />
        ))}
      </div>
    </div>
  );
}
