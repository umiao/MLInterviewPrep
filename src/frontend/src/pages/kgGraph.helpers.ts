import type { ElementDefinition } from "cytoscape";

export interface KgNode {
  id: number;
  kind: string;
  pillar: string | null;
  path: string;
  title: string;
  depth: number;
  parent_id: number | null;
  content_length: number;
}

export interface KgEdge {
  src_kind: string;
  src_id: number;
  dst_kind: string;
  dst_id: number;
  relation: string;
}

export interface KgGraphResponse {
  nodes: KgNode[];
  edges: KgEdge[];
}

export const PILLAR_COLORS: Record<string, string> = {
  pillar1: "#ef4444",
  pillar2: "#f97316",
  pillar3: "#eab308",
  pillar4: "#22c55e",
  pillar5: "#06b6d4",
  pillar6: "#3b82f6",
  pillar7: "#8b5cf6",
  pillar8: "#ec4899",
};

export function colorForPillar(pillar: string | null): string {
  if (!pillar) return "#9ca3af";
  return PILLAR_COLORS[pillar] ?? "#9ca3af";
}

export function buildElements(
  data: KgGraphResponse,
  search: string,
): ElementDefinition[] {
  const lc = search.trim().toLowerCase();
  const elements: ElementDefinition[] = [];
  for (const n of data.nodes) {
    const matches = !lc || n.title.toLowerCase().includes(lc);
    elements.push({
      data: {
        id: `n${n.id}`,
        label: n.title,
        nodeId: n.id,
        pillar: n.pillar ?? "unknown",
        depth: n.depth,
        color: colorForPillar(n.pillar),
        dim: lc ? !matches : false,
      },
    });
  }
  const validIds = new Set(data.nodes.map((n) => `n${n.id}`));
  for (const e of data.edges) {
    const src = `n${e.src_id}`;
    const dst = `n${e.dst_id}`;
    if (!validIds.has(src) || !validIds.has(dst)) continue;
    elements.push({
      data: {
        id: `e${e.src_id}-${e.dst_id}-${e.relation}`,
        source: src,
        target: dst,
        relation: e.relation,
      },
    });
  }
  return elements;
}
