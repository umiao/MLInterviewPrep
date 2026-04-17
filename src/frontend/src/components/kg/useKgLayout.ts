// ELK.js swimlane layout hook. Every pillar is laid out independently on its
// own horizontal lane; lanes are then stacked vertically with a gap. This
// prevents cross-pillar overlap and gives the classic "one row per topic"
// mind-map feel. Per-pillar cache keyed by the visible-node signature means
// expanding Pillar A does not re-run ELK for Pillars B-H, and their in-lane
// relative positions remain identical across re-layouts.

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
  const base =
    meta.kind === "pillar"
      ? LAYOUT_CONFIG.pillarNode
      : meta.kind === "category"
        ? LAYOUT_CONFIG.categoryNode
        : LAYOUT_CONFIG.leafNode;
  // Importance sizing only applies to leaves; pillars/categories keep base size
  // to preserve the layered rhythm.
  const scale = meta.kind === "leaf" ? meta.importanceScale : 1;
  return { width: base.width * scale, height: base.height * scale };
}

/** Sort key for pillar ordering: pillar1, pillar2, ..., pillar8, then fallbacks. */
export function pillarSortKey(pillar: string): number {
  const m = /^pillar(\d+)$/.exec(pillar);
  return m ? Number(m[1]) : 9999;
}

export const UNASSIGNED_PILLAR = "__unassigned__";

function pillarOf(meta: NodeMeta | undefined): string {
  return meta?.pillar ?? UNASSIGNED_PILLAR;
}

/**
 * Group visible node ids by pillar key. Pure helper for testability.
 */
export function groupVisibleByPillar(
  model: KgGraphModel,
  visible: Set<string>,
): Map<string, Set<string>> {
  const byPillar = new Map<string, Set<string>>();
  for (const id of visible) {
    const meta = model.nodesById.get(id);
    const key = pillarOf(meta);
    if (!byPillar.has(key)) byPillar.set(key, new Set());
    byPillar.get(key)!.add(id);
  }
  return byPillar;
}

/**
 * Stack per-pillar lane layouts vertically. Pure helper: takes the relative
 * per-pillar positions and returns the absolute (offset-stacked) positions
 * plus lane metadata. Unchanged pillars retain their relative layout across
 * calls, so their absolute y only shifts when a preceding lane grows or
 * shrinks -- in-lane relative positions never change from a stack operation.
 */
export function stackLanes(
  pillarLayouts: Map<
    string,
    { positions: Map<string, { x: number; y: number }>; width: number; height: number }
  >,
  sortedKeys: string[],
  laneGap: number,
): {
  positions: Map<string, { x: number; y: number }>;
  lanes: LaneInfo[];
} {
  const positions = new Map<string, { x: number; y: number }>();
  const lanes: LaneInfo[] = [];
  let yOffset = 0;
  for (const key of sortedKeys) {
    const lane = pillarLayouts.get(key);
    if (!lane || lane.positions.size === 0) continue;
    for (const [id, pos] of lane.positions) {
      positions.set(id, { x: pos.x, y: pos.y + yOffset });
    }
    lanes.push({
      pillar: key,
      yStart: yOffset,
      yEnd: yOffset + lane.height,
      xStart: 0,
      xEnd: lane.width,
      height: lane.height,
      width: lane.width,
    });
    yOffset += lane.height + laneGap;
  }
  return { positions, lanes };
}

export interface LaneInfo {
  pillar: string;
  yStart: number;
  yEnd: number;
  xStart: number;
  xEnd: number;
  height: number;
  width: number;
}

interface PillarLayoutCache {
  visibleSig: string;
  positions: Map<string, { x: number; y: number }>;
  width: number;
  height: number;
}

function signatureFor(ids: string[]): string {
  return ids.slice().sort().join(",");
}

export function useKgLayout() {
  const cacheRef = useRef<Map<string, { x: number; y: number }>>(new Map());
  const pillarCacheRef = useRef<Map<string, PillarLayoutCache>>(new Map());
  const lanesRef = useRef<LaneInfo[]>([]);

  const resetCache = useCallback(() => {
    cacheRef.current = new Map();
    pillarCacheRef.current = new Map();
    lanesRef.current = [];
  }, []);

  /**
   * Run ELK on a single pillar's visible subgraph and return its relative
   * layout (origin normalised to 0,0). No caching side-effects here.
   */
  const layoutPillar = useCallback(
    async (
      model: KgGraphModel,
      ids: Set<string>,
    ): Promise<PillarLayoutCache> => {
      const elkNodes: ElkNode[] = [];
      for (const id of ids) {
        const meta = model.nodesById.get(id);
        if (!meta) continue;
        const dims = dimensionsFor(meta);
        elkNodes.push({ id, width: dims.width, height: dims.height });
      }
      const elkEdges: { id: string; sources: string[]; targets: string[] }[] =
        [];
      const seenEdgeIds = new Set<string>();
      for (const e of model.edges) {
        if (e.relation !== "parent") continue;
        const src = `n${e.src_id}`;
        const dst = `n${e.dst_id}`;
        if (ids.has(src) && ids.has(dst)) {
          const eid = `${src}->${dst}`;
          if (!seenEdgeIds.has(eid)) {
            elkEdges.push({ id: eid, sources: [src], targets: [dst] });
            seenEdgeIds.add(eid);
          }
        }
      }
      for (const [parentId, kids] of model.childrenOf) {
        if (!ids.has(parentId)) continue;
        for (const kid of kids) {
          if (!ids.has(kid)) continue;
          const synthId = `${parentId}~>${kid}`;
          if (!seenEdgeIds.has(synthId)) {
            elkEdges.push({
              id: synthId,
              sources: [parentId],
              targets: [kid],
            });
            seenEdgeIds.add(synthId);
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
      let minX = Infinity;
      let minY = Infinity;
      let maxX = -Infinity;
      let maxY = -Infinity;
      for (const child of result.children ?? []) {
        if (child.x == null || child.y == null) continue;
        const w = child.width ?? 0;
        const h = child.height ?? 0;
        if (child.x < minX) minX = child.x;
        if (child.y < minY) minY = child.y;
        if (child.x + w > maxX) maxX = child.x + w;
        if (child.y + h > maxY) maxY = child.y + h;
      }
      if (minX === Infinity) {
        return {
          visibleSig: signatureFor([...ids]),
          positions: new Map(),
          width: 0,
          height: 0,
        };
      }
      const positions = new Map<string, { x: number; y: number }>();
      for (const child of result.children ?? []) {
        if (child.x == null || child.y == null) continue;
        positions.set(child.id, {
          x: child.x - minX,
          y: child.y - minY,
        });
      }
      return {
        visibleSig: signatureFor([...ids]),
        positions,
        width: maxX - minX,
        height: maxY - minY,
      };
    },
    [],
  );

  /**
   * Swimlane layout: group visible nodes by pillar, layout each pillar
   * independently, stack lanes vertically. Per-pillar cache keyed by the
   * visible-nodeset signature means unchanged pillars skip ELK entirely.
   */
  const layoutAll = useCallback(
    async (model: KgGraphModel, visible: Set<string>): Promise<void> => {
      const byPillar = groupVisibleByPillar(model, visible);
      const pillarKeys = [...byPillar.keys()].sort(
        (a, b) => pillarSortKey(a) - pillarSortKey(b),
      );

      // Compute/reuse per-pillar layouts. Signature match -> skip ELK.
      const nextPillarCache = new Map<string, PillarLayoutCache>();
      for (const key of pillarKeys) {
        const ids = byPillar.get(key)!;
        const sig = signatureFor([...ids]);
        const prior = pillarCacheRef.current.get(key);
        if (prior && prior.visibleSig === sig) {
          nextPillarCache.set(key, prior);
        } else {
          const laid = await layoutPillar(model, ids);
          nextPillarCache.set(key, laid);
        }
      }
      pillarCacheRef.current = nextPillarCache;

      const { positions, lanes } = stackLanes(
        nextPillarCache,
        pillarKeys,
        LAYOUT_CONFIG.laneGap,
      );
      cacheRef.current = positions;
      lanesRef.current = lanes;
    },
    [layoutPillar],
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

  const getLanes = useCallback((): LaneInfo[] => {
    return lanesRef.current;
  }, []);

  return useMemo(
    () => ({
      layoutAll,
      applyPositions,
      resetCache,
      getPosition,
      getLanes,
    }),
    [layoutAll, applyPositions, resetCache, getPosition, getLanes],
  );
}
