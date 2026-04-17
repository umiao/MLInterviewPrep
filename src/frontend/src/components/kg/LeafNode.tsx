import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { NodeMeta } from "../../pages/kgGraph.helpers";
import { styleForPillar } from "./kgStyles";

export interface LeafNodeData extends Record<string, unknown> {
  meta: NodeMeta;
  isExpanded: boolean;
  isSelected: boolean;
  isMatch: boolean;
  dimmed: boolean;
}

export default function LeafNode({ data }: NodeProps) {
  const d = data as LeafNodeData;
  const { meta, isSelected, isMatch, dimmed } = d;
  const style = styleForPillar(meta.pillar);
  const ringClass = isSelected
    ? "ring-2 ring-blue-500 ring-offset-2"
    : isMatch
      ? "ring-2 ring-yellow-400"
      : "";
  const isStub = meta.contentLength < 2000;
  return (
    <div
      data-testid="kg-leaf-node"
      className={`relative rounded-md bg-white shadow-sm transition-shadow hover:shadow-md cursor-pointer ${ringClass}`}
      style={{
        width: 180,
        height: 36,
        borderLeft: `2px solid ${style.border}`,
        borderStyle: isStub ? "dashed" : "solid",
        borderColor: isStub ? style.border : "transparent",
        borderWidth: isStub ? 1 : 0,
        borderLeftStyle: "solid",
        borderLeftWidth: 2,
        opacity: dimmed ? 0.2 : 1,
      }}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div className="flex items-center h-full px-3">
        <span
          className="truncate text-[12px] font-medium text-gray-700"
          title={meta.title}
        >
          {meta.title}
        </span>
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  );
}
