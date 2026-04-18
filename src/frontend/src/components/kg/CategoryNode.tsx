import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { NodeMeta } from "../../pages/kgGraph.helpers";
import { hasContent } from "../framework/hasContent";
import { LAYOUT_CONFIG, styleForPillar } from "./kgStyles";
import {
  COMPLETENESS_FULL,
  CompletenessArc,
  STUB_THRESHOLD,
  StubBadge,
} from "./CompletenessArc";

export interface CategoryNodeData extends Record<string, unknown> {
  meta: NodeMeta;
  isExpanded: boolean;
  isSelected: boolean;
  isMatch: boolean;
  dimmed: boolean;
  isHovered?: boolean;
  isNeighborOfHover?: boolean;
  isPulsing?: boolean;
  onActivate?: (id: string) => void;
}

const EMPTY_FOCUS_TOOLTIP = "\u65E0\u5185\u5BB9 \u00B7 \u70B9\u51FB\u805A\u7126";

const HUB_EDGE_THRESHOLD = 10;

function CategoryNodeInner({ id, data }: NodeProps) {
  const d = data as CategoryNodeData;
  const { meta, isExpanded, isSelected, isMatch, dimmed, isNeighborOfHover, isPulsing, onActivate } = d;
  const style = styleForPillar(meta.pillar);
  const isHub = meta.edgeCount > HUB_EDGE_THRESHOLD;
  const isLeafLike = meta.childCount === 0;
  const isStub = meta.contentLength < STUB_THRESHOLD;
  const completenessFraction = meta.contentLength / COMPLETENESS_FULL;
  // Empty + 0 children falls into the focus-animation branch of the
  // KG-UX-10 tri-state click matrix. Empty categories WITH children still
  // expand/collapse, so they keep the default title tooltip.
  const isEmptyFocus = !hasContent(meta) && meta.childCount === 0;
  const pulseClass = isPulsing ? " kg-node-pulse" : "";
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
  const ariaLabel = isLeafLike
    ? `${meta.title} (${meta.pillarName})`
    : `${meta.title}, ${isExpanded ? "expanded" : "collapsed"}, ${meta.childCount} children`;
  return (
    <div
      data-testid="kg-category-node"
      data-hub={isHub ? "true" : "false"}
      data-leaf-like={isLeafLike ? "true" : "false"}
      data-empty-focus={isEmptyFocus ? "true" : "false"}
      tabIndex={0}
      role="button"
      aria-label={ariaLabel}
      aria-expanded={isLeafLike ? undefined : isExpanded}
      onKeyDown={handleKeyDown}
      className={`relative rounded-lg bg-white shadow-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400 ${ringClass}${pulseClass}`}
      style={{
        width: LAYOUT_CONFIG.categoryNode.width,
        height: LAYOUT_CONFIG.categoryNode.height,
        contain: "size",
        borderLeft: `${isHub ? 4 : 2}px solid ${style.border}`,
        borderTop: isHub ? `2px solid ${style.border}` : undefined,
        borderRight: isHub ? `2px solid ${style.border}` : undefined,
        borderBottom: isHub ? `2px solid ${style.border}` : undefined,
        opacity: dimmed ? 0.2 : 1,
      }}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div className="flex items-center justify-between h-full px-3 gap-2">
        <span
          className="line-clamp-2 break-words leading-tight text-[15px] font-semibold text-gray-800 min-w-0"
          title={isEmptyFocus ? EMPTY_FOCUS_TOOLTIP : meta.title}
        >
          {meta.title}
        </span>
        <span className="flex items-center gap-1 shrink-0 text-[10px] text-gray-500">
          {isStub && <StubBadge />}
          {isLeafLike ? (
            <span aria-label="Content completeness">
              <CompletenessArc
                fraction={completenessFraction}
                color={style.border}
              />
            </span>
          ) : (
            <>
              <span
                className="rounded-full px-1.5 py-0.5 text-[10px] font-medium"
                style={{ backgroundColor: style.bg, color: style.border }}
              >
                {meta.childCount}
              </span>
              <span aria-hidden>{isExpanded ? "v" : ">"}</span>
            </>
          )}
        </span>
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  );
}

export default memo(CategoryNodeInner, (prev, next) => {
  const p = prev.data as CategoryNodeData;
  const n = next.data as CategoryNodeData;
  return (
    p.isHovered === n.isHovered &&
    p.isNeighborOfHover === n.isNeighborOfHover &&
    p.isSelected === n.isSelected &&
    p.isExpanded === n.isExpanded &&
    p.isMatch === n.isMatch &&
    p.dimmed === n.dimmed &&
    p.isPulsing === n.isPulsing &&
    p.meta.id === n.meta.id
  );
});
