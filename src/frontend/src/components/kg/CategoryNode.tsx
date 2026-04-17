import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { NodeMeta } from "../../pages/kgGraph.helpers";
import { styleForPillar } from "./kgStyles";
import { HoverTooltip } from "./HoverTooltip";

export interface CategoryNodeData extends Record<string, unknown> {
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

export default function CategoryNode({ id, data }: NodeProps) {
  const d = data as CategoryNodeData;
  const { meta, isExpanded, isSelected, isMatch, dimmed, isHovered, isNeighborOfHover, onActivate } = d;
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
      data-testid="kg-category-node"
      data-hub={isHub ? "true" : "false"}
      tabIndex={0}
      role="button"
      aria-label={`${meta.title}, ${isExpanded ? "expanded" : "collapsed"}, ${meta.childCount} children`}
      aria-expanded={isExpanded}
      onKeyDown={handleKeyDown}
      className={`relative rounded-lg bg-white shadow-sm transition-shadow hover:shadow-md cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400 ${ringClass}`}
      style={{
        width: 200,
        height: 40,
        borderLeft: `${isHub ? 4 : 2}px solid ${style.border}`,
        borderTop: isHub ? `2px solid ${style.border}` : undefined,
        borderRight: isHub ? `2px solid ${style.border}` : undefined,
        borderBottom: isHub ? `2px solid ${style.border}` : undefined,
        opacity: dimmed ? 0.2 : 1,
      }}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div className="flex items-center justify-between h-full px-3">
        <span
          className="truncate text-[13px] font-semibold text-gray-800"
          title={meta.title}
        >
          {meta.title}
        </span>
        <span className="flex items-center gap-1 ml-2 text-[10px] text-gray-500">
          <span
            className="rounded-full px-1.5 py-0.5 text-[10px] font-medium"
            style={{ backgroundColor: style.bg, color: style.border }}
          >
            {meta.childCount}
          </span>
          <span aria-hidden>{isExpanded ? "v" : ">"}</span>
        </span>
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
      {isHovered && (
        <HoverTooltip
          title={meta.title}
          pillarName={meta.pillarName}
          pillarColor={style.border}
          pillarBg={style.bg}
          contentLength={meta.contentLength}
          edgeCount={meta.edgeCount}
          actionHint={isExpanded ? "Click to collapse" : "Click to expand"}
        />
      )}
    </div>
  );
}
