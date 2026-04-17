// ELK.js layout hook with position caching + incremental sub-tree layout.
// First load = full pass across all visible nodes. Subsequent expand/collapse
// operations re-layout only the changed sub-tree, leaving cached coordinates
// elsewhere untouched. This preserves spatial memory.

import ELK, { type ElkNode } from "elkjs/lib/elk.bundled.js";
import { useCallback, useMemo, useRef } from "react";
import type { Node } from "@xyflow/react";
import type { KgGraphModel, NodeMeta } from "../../pages/kgGraph.helpers";
import { LAYOUT_CONFIG } from "./kgStyles";

const elk = new ELK();

const BASE_OPTS: Record<string, string> = {
  "elk.algorithm": "layered",
  "elk.direction": "RIGHT",
  "elk.layered.spacing.nodeNodeBetweenLayers": String(LAYOUT_CONFIG.rankSep),
  "elk.spacing.nodeNode": String(LAYOUT_CONFIG.nodeSep),
  "elk.layered.nodePlacement.strategy": "BRANDES_KOEPF",
  "elk.layered.crossingMinimization.strategy": "LAYER_SWEEP",
  "elk.edgeRouting": "ORTHOGONAL",
  "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
};

function dimensionsFor(meta: NodeMeta): { width: number; height: number } {
  if (meta.kind === "pillar") return LAYOUT_CONFIG.pillarNode;
  if (meta.kind === "category") return LAYOUT_CONFIG.categoryNode;
  return LAYOUT_CONFIG.leafNode;
}

export interface LayoutResult {
  positions: Map<string, { x: number; y: number }>;
}

export function useKgLayout() {
  const cacheRef = useRef<Map<string, { x: number; y: number }>>(new Map());

  const resetCache = useCallback(() => {
    cacheRef.current = new Map();
  }, []);

  /**
   * Build a minimal ELK subgraph for the given node ids (plus the parent
   * edges that connect them) and layout it. `anchor` coordinates are used
   * to translate the result so the anchor node keeps its cached position.
   */
  const layoutSubset = useCallback(
    async (
      model: KgGraphModel,
      nodeIds: Set<string>,
      options: { anchorId?: string | null } = {},
    ): Promise<void> => {
      if (nodeIds.size === 0) return;
      const elkNodes: ElkNode[] = [];
      for (const id of nodeIds) {
        const meta = model.nodesById.get(id);
        if (!meta) continue;
        const dims = dimensionsFor(meta);
        elkNodes.push({
          id,
          width: dims.width,
          height: dims.height,
        });
      }
      const elkEdges: { id: string; sources: string[]; targets: string[] }[] = [];
      for (const e of model.edges) {
        if (e.relation !== "parent") continue;
        const src = `n${e.src_id}`;
        const dst = `n${e.dst_id}`;
        if (nodeIds.has(src) && nodeIds.has(dst)) {
          elkEdges.push({ id: `${src}->${dst}`, sources: [src], targets: [dst] });
        }
      }
      // Also synthesize parent->child edges from the model's implicit hierarchy
      // for the subset (some trees rely on parent_id rather than concept_links
      // rows). This gives ELK the structural info it needs.
      for (const [parentId, kids] of model.childrenOf) {
        if (!nodeIds.has(parentId)) continue;
        for (const kid of kids) {
          if (!nodeIds.has(kid)) continue;
          const synthId = `${parentId}~>${kid}`;
          if (!elkEdges.find((e) => e.id === synthId)) {
            elkEdges.push({ id: synthId, sources: [parentId], targets: [kid] });
          }
        }
      }
      const graph: ElkNode = {
        id: "root",
        layoutOptions: BASE_OPTS,
        children: elkNodes,
        edges: elkEdges,
      };
      const result = await elk.layout(graph);
      let dx = 0;
      let dy = 0;
      if (options.anchorId) {
        const cached = cacheRef.current.get(options.anchorId);
        const laid = result.children?.find((c) => c.id === options.anchorId);
        if (cached && laid && laid.x != null && laid.y != null) {
          dx = cached.x - laid.x;
          dy = cached.y - laid.y;
        }
      }
      for (const child of result.children ?? []) {
        if (child.x == null || child.y == null) continue;
        cacheRef.current.set(child.id, { x: child.x + dx, y: child.y + dy });
      }
    },
    [],
  );

  /**
   * Full layout across all visible nodes. Clears cache first.
   */
  const layoutAll = useCallback(
    async (model: KgGraphModel, visible: Set<string>): Promise<void> => {
      cacheRef.current = new Map();
      await layoutSubset(model, visible);
    },
    [layoutSubset],
  );

  /**
   * Apply cached positions to React Flow nodes.
   */
  const applyPositions = useCallback((nodes: Node[]): Node[] => {
    const cache = cacheRef.current;
    return nodes.map((n) => {
      const pos = cache.get(n.id);
      if (!pos) return n;
      return { ...n, position: pos };
    });
  }, []);

  const getPosition = useCallback((id: string) => {
    return cacheRef.current.get(id) ?? null;
  }, []);

  return useMemo(
    () => ({ layoutAll, layoutSubset, applyPositions, resetCache, getPosition }),
    [layoutAll, layoutSubset, applyPositions, resetCache, getPosition],
  );
}
