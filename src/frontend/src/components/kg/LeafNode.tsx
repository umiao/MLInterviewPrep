import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { NodeMeta } from "../../pages/kgGraph.helpers";
import { LAYOUT_CONFIG, styleForPillar } from "./kgStyles";

export interface LeafNodeData extends Record<string, unknown> {
  meta: NodeMeta;
  isExpanded: boolean;
  isSelected: boolean;
  isMatch: boolean;
  dimmed: boolean;
  isHovered?: boolean;
  isNeighborOfHover?: boolean;
  onActivate?: (id: string) => void;
}

const COMPLETENESS_FULL = 10000;
const STUB_THRESHOLD = 2000;
const HUB_EDGE_THRESHOLD = 10;

/**
 * SVG ring with a partial arc fill, used as the completeness indicator in
 * the leaf node's top-right corner. Empty -> outline only; partial -> arc;
 * full -> filled disc with checkmark.
 */
function CompletenessArc({
  fraction,
  color,
}: {
  fraction: number;
  color: string;
}) {
  const size = 14;
  const r = 5;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = 2 * Math.PI * r;
  const clamped = Math.max(0, Math.min(1, fraction));
  if (clamped >= 1) {
    return (
      <svg width={size} height={size} aria-hidden>
        <circle cx={cx} cy={cy} r={r} fill={color} />
        <path
          d={`M${cx - 2.2} ${cy + 0.2} L${cx - 0.6} ${cy + 1.8} L${cx + 2.4} ${cy - 1.6}`}
          stroke="white"
          strokeWidth={1.4}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }
  return (
    <svg width={size} height={size} aria-hidden>
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke="#e2e8f0"
        strokeWidth={1.5}
      />
      {clamped > 0 && (
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={1.5}
          strokeDasharray={`${circumference * clamped} ${circumference}`}
          transform={`rotate(-90 ${cx} ${cy})`}
          strokeLinecap="round"
        />
      )}
    </svg>
  );
}

function LeafNodeInner({ id, data }: NodeProps) {
  const d = data as LeafNodeData;
  const { meta, isSelected, isMatch, dimmed, isNeighborOfHover, onActivate } = d;
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
      tabIndex={0}
      role="button"
      aria-label={`${meta.title} (${meta.pillarName})`}
      onKeyDown={handleKeyDown}
      className={`relative rounded-md bg-white shadow-sm transition-shadow hover:shadow-md cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400 ${ringClass}`}
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
      <div className="flex items-center justify-between h-full px-2.5">
        <span
          className="truncate text-[12px] font-medium text-gray-700 pr-2"
          title={meta.title}
        >
          {meta.title}
        </span>
        <span className="shrink-0" aria-label="Content completeness">
          <CompletenessArc
            fraction={completenessFraction}
            color={style.border}
          />
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
    p.meta.id === n.meta.id
  );
});
