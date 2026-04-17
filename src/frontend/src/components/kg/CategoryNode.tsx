import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { NodeMeta } from "../../pages/kgGraph.helpers";
import { styleForPillar } from "./kgStyles";

export interface CategoryNodeData extends Record<string, unknown> {
  meta: NodeMeta;
  isExpanded: boolean;
  isSelected: boolean;
  isMatch: boolean;
  dimmed: boolean;
}

export default function CategoryNode({ data }: NodeProps) {
  const d = data as CategoryNodeData;
  const { meta, isExpanded, isSelected, isMatch, dimmed } = d;
  const style = styleForPillar(meta.pillar);
  const ringClass = isSelected
    ? "ring-2 ring-blue-500 ring-offset-2"
    : isMatch
      ? "ring-2 ring-yellow-400"
      : "";
  return (
    <div
      data-testid="kg-category-node"
      className={`relative rounded-lg bg-white shadow-sm transition-shadow hover:shadow-md cursor-pointer ${ringClass}`}
      style={{
        width: 200,
        height: 40,
        borderLeft: `2px solid ${style.border}`,
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
    </div>
  );
}
