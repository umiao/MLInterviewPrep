// Helpers that transform the /api/kg/graph payload into the shape our
// React Flow + ELK.js based viewer consumes. Adds pillar/category/leaf
// node kinds and derives expand state.

import type { Edge, Node } from "@xyflow/react";
import { PILLAR_STYLES, styleForPillar } from "../components/kg/kgStyles";

export interface KgNode {
  id: number;
  kind: string;
  pillar: string | null;
  path: string;
  title: string;
  depth: number;
  parent_id: number | null;
  content_length: number;
  edge_count?: number;
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

export type NodeKind = "pillar" | "category" | "leaf";

export interface NodeMeta {
  id: string;
  rawId: number;
  kind: NodeKind;
  pillar: string | null;
  pillarName: string;
  title: string;
  depth: number;
  parentId: string | null;
  contentLength: number;
  path: string;
  childCount: number;
  edgeCount: number;
  importanceScale: number;
}

/**
 * Map concept-link edge count to a discrete size multiplier.
 * Spec: 1.0x base, 1.2x when >5 edges, 1.5x when >10.
 */
export function importanceScaleFor(edgeCount: number): number {
  if (edgeCount > 10) return 1.5;
  if (edgeCount > 5) return 1.2;
  return 1.0;
}

export interface KgGraphModel {
  nodesById: Map<string, NodeMeta>;
  childrenOf: Map<string, string[]>;
  pillarIds: string[];
  edges: KgEdge[];
  rawResponse: KgGraphResponse;
}

export function colorForPillar(pillar: string | null | undefined): string {
  return styleForPillar(pillar).border;
}

export function nodeIdOf(rawId: number): string {
  return `n${rawId}`;
}

function kindForDepth(depth: number): NodeKind {
  if (depth <= 0) return "pillar";
  if (depth === 1) return "category";
  return "leaf";
}

export function buildGraphModel(data: KgGraphResponse): KgGraphModel {
  const nodesById = new Map<string, NodeMeta>();
  const childrenOf = new Map<string, string[]>();
  const pillarIds: string[] = [];
  const childCounts = new Map<string, number>();

  for (const n of data.nodes) {
    if (n.parent_id != null) {
      const parentKey = nodeIdOf(n.parent_id);
      childCounts.set(parentKey, (childCounts.get(parentKey) ?? 0) + 1);
    }
  }

  for (const n of data.nodes) {
    const id = nodeIdOf(n.id);
    const parentId = n.parent_id != null ? nodeIdOf(n.parent_id) : null;
    const edgeCount = n.edge_count ?? 0;
    const meta: NodeMeta = {
      id,
      rawId: n.id,
      kind: kindForDepth(n.depth),
      pillar: n.pillar,
      pillarName: styleForPillar(n.pillar).name,
      title: n.title,
      depth: n.depth,
      parentId,
      contentLength: n.content_length,
      path: n.path,
      childCount: childCounts.get(id) ?? 0,
      edgeCount,
      importanceScale: importanceScaleFor(edgeCount),
    };
    nodesById.set(id, meta);
    if (meta.kind === "pillar") pillarIds.push(id);
    if (parentId) {
      const arr = childrenOf.get(parentId) ?? [];
      arr.push(id);
      childrenOf.set(parentId, arr);
    }
  }

  const validIds = new Set(data.nodes.map((n) => nodeIdOf(n.id)));
  const edges = data.edges.filter(
    (e) => validIds.has(nodeIdOf(e.src_id)) && validIds.has(nodeIdOf(e.dst_id)),
  );

  return { nodesById, childrenOf, pillarIds, edges, rawResponse: data };
}

/**
 * Default expanded set: all pillars only. Categories themselves are visible
 * (as pillar children) but their leaf children stay hidden until the user
 * clicks a category. This yields the "pillar + category" skeleton the spec
 * calls for (~49 nodes) on first render.
 */
export function defaultExpandedSet(model: KgGraphModel): Set<string> {
  const expanded = new Set<string>();
  for (const id of model.pillarIds) expanded.add(id);
  return expanded;
}

/**
 * Visible nodes: pillars always visible; deeper nodes visible iff every
 * ancestor is expanded.
 */
export function computeVisibleNodeIds(
  model: KgGraphModel,
  expanded: Set<string>,
): Set<string> {
  const visible = new Set<string>();
  for (const id of model.pillarIds) visible.add(id);
  const stack = [...model.pillarIds];
  while (stack.length) {
    const current = stack.pop()!;
    if (!expanded.has(current)) continue;
    const kids = model.childrenOf.get(current) ?? [];
    for (const kid of kids) {
      visible.add(kid);
      stack.push(kid);
    }
  }
  return visible;
}

export interface BuildNodeOptions {
  hoveredId?: string | null;
  hoveredNeighbors?: Set<string>;
  onActivate?: (id: string) => void;
}

export function buildReactFlowNodes(
  model: KgGraphModel,
  visible: Set<string>,
  expanded: Set<string>,
  selectedId: string | null,
  searchMatches: Set<string>,
  hasActiveSearch: boolean,
  options: BuildNodeOptions = {},
): Node[] {
  const out: Node[] = [];
  const hoveredId = options.hoveredId ?? null;
  const neighbors = options.hoveredNeighbors ?? new Set<string>();
  for (const id of visible) {
    const meta = model.nodesById.get(id)!;
    const isExpanded = expanded.has(id);
    const isMatch = searchMatches.has(id);
    const dimmed = hasActiveSearch && !isMatch;
    out.push({
      id,
      type: meta.kind,
      position: { x: 0, y: 0 },
      data: {
        meta,
        isExpanded,
        isSelected: selectedId === id,
        isMatch,
        dimmed,
        isHovered: hoveredId === id,
        isNeighborOfHover: neighbors.has(id),
        onActivate: options.onActivate,
      },
      draggable: false,
      selectable: true,
      connectable: false,
    });
  }
  return out;
}

/**
 * For a hovered node id, walk visible edges and return the set of opposite
 * endpoints. Used to ring neighbor nodes during hover and as the source of
 * truth for which edges should glow.
 */
export function neighborsOfHover(
  model: KgGraphModel,
  visible: Set<string>,
  hoveredId: string | null,
): Set<string> {
  const out = new Set<string>();
  if (!hoveredId) return out;
  for (const e of model.edges) {
    const src = nodeIdOf(e.src_id);
    const dst = nodeIdOf(e.dst_id);
    if (!visible.has(src) || !visible.has(dst)) continue;
    if (src === hoveredId) out.add(dst);
    else if (dst === hoveredId) out.add(src);
  }
  return out;
}

/**
 * All node ids that own at least one child. Useful for "Expand All".
 */
export function allParentIds(model: KgGraphModel): Set<string> {
  const out = new Set<string>();
  for (const [parentId, kids] of model.childrenOf) {
    if (kids.length > 0) out.add(parentId);
  }
  return out;
}

export function buildReactFlowEdges(
  model: KgGraphModel,
  visible: Set<string>,
  hoveredId: string | null,
): Edge[] {
  const out: Edge[] = [];
  for (const e of model.edges) {
    const src = nodeIdOf(e.src_id);
    const dst = nodeIdOf(e.dst_id);
    if (!visible.has(src) || !visible.has(dst)) continue;
    const isParent = e.relation === "parent";
    const isCanonical = e.relation === "canonical";
    const connectedToHover = hoveredId != null && (hoveredId === src || hoveredId === dst);
    out.push({
      id: `${src}-${dst}-${e.relation}`,
      source: src,
      target: dst,
      type: isParent ? "smoothstep" : "default",
      animated: isCanonical,
      data: { relation: e.relation, highlighted: connectedToHover },
    });
  }
  return out;
}

export function findSearchMatches(
  model: KgGraphModel,
  query: string,
): Set<string> {
  const matches = new Set<string>();
  const q = query.trim().toLowerCase();
  if (!q) return matches;
  for (const [id, meta] of model.nodesById) {
    if (meta.title.toLowerCase().includes(q)) matches.add(id);
  }
  return matches;
}

/**
 * Expand ancestors of all match ids so they become visible on search.
 */
export function expandToReveal(
  model: KgGraphModel,
  ids: Set<string>,
  baseExpanded: Set<string>,
): Set<string> {
  const next = new Set(baseExpanded);
  for (const id of ids) {
    let cursor: string | null = model.nodesById.get(id)?.parentId ?? null;
    while (cursor) {
      next.add(cursor);
      cursor = model.nodesById.get(cursor)?.parentId ?? null;
    }
  }
  return next;
}

export const PILLAR_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(PILLAR_STYLES).map(([k, v]) => [k, v.border]),
);
