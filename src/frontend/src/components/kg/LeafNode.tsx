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

export interface LeafNodeData extends Record<string, unknown> {
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

function LeafNodeInner({ id, data }: NodeProps) {
  const d = data as LeafNodeData;
  const { meta, isSelected, isMatch, dimmed, isNeighborOfHover, isPulsing, onActivate } = d;
  const style = styleForPillar(meta.pillar);
  const isHub = meta.edgeCount > HUB_EDGE_THRESHOLD;
  const ringClass = isSelected
    ? "ring-2 ring-blue-500 ring-offset-2"
    : isMatch
      ? "ring-2 ring-yellow-400"
      : isNeighborOfHover
        ? "ring-1 ring-gray-400"
        : "";
  const isStub = meta.contentLength < STUB_THRESHOLD;
  const completenessFraction = meta.contentLength / COMPLETENESS_FULL;
  const base = LAYOUT_CONFIG.leafNode;
  const width = base.width * meta.importanceScale;
  const height = base.height * meta.importanceScale;
  const leftBorderWidth = isHub ? 3 : 2;
  const sideBorder = isHub ? `2px solid ${style.border}` : isStub ? `1px dashed ${style.border}` : undefined;
  // Leaves always have childCount 0, so an empty leaf falls into the
  // "focus animation" branch of the KG-UX-10 tri-state click matrix.
  const isEmptyFocus = !hasContent(meta) && meta.childCount === 0;
  const pulseClass = isPulsing ? " kg-node-pulse" : "";
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onActivate?.(id);
    }
  };
  return (
    <div
      data-testid="kg-leaf-node"
      data-importance={meta.importanceScale.toFixed(2)}
      data-hub={isHub ? "true" : "false"}
      data-empty-focus={isEmptyFocus ? "true" : "false"}
      tabIndex={0}
      role="button"
      aria-label={`${meta.title} (${meta.pillarName})`}
      onKeyDown={handleKeyDown}
      className={`relative rounded-md bg-white shadow-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400 ${ringClass}${pulseClass}`}
      style={{
        width,
        height,
        contain: "size",
        borderLeft: `${leftBorderWidth}px solid ${style.border}`,
        borderTop: sideBorder,
        borderRight: sideBorder,
        borderBottom: sideBorder,
        opacity: dimmed ? 0.2 : 1,
      }}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div className="flex items-center justify-between h-full px-2.5 gap-1.5">
        <span
          className="line-clamp-2 break-words leading-tight text-[14px] font-medium text-gray-700 min-w-0"
          title={isEmptyFocus ? EMPTY_FOCUS_TOOLTIP : meta.title}
        >
          {meta.title}
        </span>
        <span className="flex items-center gap-1 shrink-0">
          {isStub && <StubBadge />}
          <span aria-label="Content completeness">
            <CompletenessArc
              fraction={completenessFraction}
              color={style.border}
            />
          </span>
        </span>
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  );
}

export default memo(LeafNodeInner, (prev, next) => {
  const p = prev.data as LeafNodeData;
  const n = next.data as LeafNodeData;
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
