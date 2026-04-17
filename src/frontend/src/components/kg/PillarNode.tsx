import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { NodeMeta } from "../../pages/kgGraph.helpers";
import { styleForPillar } from "./kgStyles";

export interface PillarNodeData extends Record<string, unknown> {
  meta: NodeMeta;
  isExpanded: boolean;
  isSelected: boolean;
  isMatch: boolean;
  dimmed: boolean;
}

export default function PillarNode({ data }: NodeProps) {
  const d = data as PillarNodeData;
  const { meta, isExpanded, isSelected, isMatch, dimmed } = d;
  const style = styleForPillar(meta.pillar);
  const ringClass = isSelected
    ? "ring-2 ring-blue-500 ring-offset-2"
    : isMatch
      ? "ring-2 ring-yellow-400"
      : "";
  return (
    <div
      data-testid="kg-pillar-node"
      className={`relative rounded-xl bg-white shadow-md transition-shadow hover:shadow-lg ${ringClass}`}
      style={{
        width: 240,
        height: 48,
        borderLeft: `4px solid ${style.border}`,
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
