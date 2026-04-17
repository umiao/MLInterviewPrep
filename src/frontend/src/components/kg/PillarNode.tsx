import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { NodeMeta } from "../../pages/kgGraph.helpers";
import { styleForPillar } from "./kgStyles";

export interface PillarNodeData extends Record<string, unknown> {
  meta: NodeMeta;
  isExpanded: boolean;
  isSelected: boolean;
  isMatch: boolean;
  dimmed: boolean;
  isHovered?: boolean;
  isNeighborOfHover?: boolean;
  onActivate?: (id: string) => void;
}

const HUB_EDGE_THRESHOLD = 10;

function PillarNodeInner({ id, data }: NodeProps) {
  const d = data as PillarNodeData;
  const { meta, isExpanded, isSelected, isMatch, dimmed, isNeighborOfHover, onActivate } = d;
  const style = styleForPillar(meta.pillar);
  const isHub = meta.edgeCount > HUB_EDGE_THRESHOLD;
  const ringClass = isSelected
    ? "ring-2 ring-blue-500 ring-offset-2"
    : isMatch
      ? "ring-2 ring-yellow-400"
      : isNeighborOfHover
        ? "ring-1 ring-gray-400"
        : "";
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onActivate?.(id);
    }
  };
  return (
    <div
      data-testid="kg-pillar-node"
      data-hub={isHub ? "true" : "false"}
      tabIndex={0}
      role="button"
      aria-label={`${meta.pillarName} pillar, ${isExpanded ? "expanded" : "collapsed"}`}
      aria-expanded={isExpanded}
      onKeyDown={handleKeyDown}
      className={`relative rounded-xl bg-white shadow-md transition-shadow hover:shadow-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400 ${ringClass}`}
      style={{
        width: 240,
        height: 48,
        contain: "size",
        borderLeft: `${isHub ? 6 : 4}px solid ${style.border}`,
        borderTop: isHub ? `2px solid ${style.border}` : undefined,
        borderRight: isHub ? `2px solid ${style.border}` : undefined,
        borderBottom: isHub ? `2px solid ${style.border}` : undefined,
        backgroundColor: style.bg,
        opacity: dimmed ? 0.2 : 1,
      }}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div className="flex items-center justify-between h-full px-3">
        <div className="flex flex-col overflow-hidden">
          <span
            className="truncate text-[15px] font-bold text-gray-900"
            title={meta.pillarName}
          >
            {meta.pillarName}
          </span>
          <span className="text-[10px] text-gray-500">
            {meta.childCount} categories
          </span>
        </div>
        <span
          aria-hidden
          className="ml-2 select-none text-xs text-gray-500"
          title={isExpanded ? "Collapse" : "Expand"}
        >
          {isExpanded ? "v" : ">"}
        </span>
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  );
}

export default memo(PillarNodeInner, (prev, next) => {
  const p = prev.data as PillarNodeData;
  const n = next.data as PillarNodeData;
  return (
    p.isHovered === n.isHovered &&
    p.isNeighborOfHover === n.isNeighborOfHover &&
    p.isSelected === n.isSelected &&
    p.isExpanded === n.isExpanded &&
    p.isMatch === n.isMatch &&
    p.dimmed === n.dimmed &&
    p.meta.id === n.meta.id
  );
});
