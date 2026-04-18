// Read-only LR mind-map viewer built on React Flow + ELK.js layered layout.
// Incremental layout, default semi-expanded, URL-synced selection/expansion,
// search auto-expand + zoom + highlight.

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  ViewportPortal,
  useReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

// Override React Flow's cursor management to prevent flicker between
// grab/pointer icons when hovering nodes. Nodes set their own cursor-pointer.
// Pulse animation is used as zoom-independent focus feedback when clicking a
// content-less leaf (see KG-UX-10 tri-state click behavior).
const KG_STYLE_OVERRIDES = `
.kg-canvas .react-flow__pane { cursor: grab !important; }
.kg-canvas .react-flow__pane:active { cursor: grabbing !important; }
.kg-canvas .react-flow__node { cursor: pointer !important; }
@keyframes kg-node-pulse {
  0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.55); }
  100% { box-shadow: 0 0 0 14px rgba(59, 130, 246, 0); }
}
.kg-node-pulse { animation: kg-node-pulse 300ms ease-out; }
`;
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import FrameworkNodeDrawer from "../components/framework/FrameworkNodeDrawer";
import { hasContent } from "../components/framework/hasContent";
import PillarNode from "../components/kg/PillarNode";
import CategoryNode from "../components/kg/CategoryNode";
import LeafNode from "../components/kg/LeafNode";
import TreeNav from "../components/kg/TreeNav";
import { computeBBox, useKgLayout } from "../components/kg/useKgLayout";
import {
  readUrlState,
  useSyncUrl,
} from "../components/kg/useKgUrlState";
import {
  EDGE_STYLES,
  LANE_SEPARATOR_STYLE,
  LAYOUT_CONFIG,
  styleForPillar,
} from "../components/kg/kgStyles";
import type { LaneInfo } from "../components/kg/useKgLayout";
import {
  allParentIds,
  buildGraphModel,
  buildReactFlowEdges,
  buildReactFlowNodes,
  computeVisibleNodeIds,
  defaultExpandedSet,
  expandToReveal,
  expandedSetForTreeNavSelect,
  findSearchMatches,
  nodeIdOf,
  type KgGraphModel,
  type KgGraphResponse,
  type NodeMeta,
} from "./kgGraph.helpers";

// Default zoom cap for initial view and deeplink focus. Prevents the wide
// swimlane layout from shrinking nodes to illegibility on cold load.
const INITIAL_ZOOM_CAP = 1.0;

const NODE_TYPES = {
  pillar: PillarNode,
  category: CategoryNode,
  leaf: LeafNode,
};

function edgeStyleFor(
  relation: string,
  highlighted: boolean,
  sourcePillar: string | null | undefined,
) {
  if (relation === "parent") {
    return {
      stroke: styleForPillar(sourcePillar).border,
      strokeWidth: EDGE_STYLES.parent.strokeWidth,
      opacity: highlighted ? EDGE_STYLES.fullOpacity : EDGE_STYLES.parent.opacity,
    };
  }
  const base =
    relation === "canonical"
      ? EDGE_STYLES.canonical
      : relation === "see_also"
        ? EDGE_STYLES.seeAlso
        : relation === "drill"
          ? EDGE_STYLES.drill
          : EDGE_STYLES.other;
  const isSoft = relation !== "canonical";
  return {
    stroke: base.stroke,
    strokeWidth: base.strokeWidth,
    opacity: highlighted
      ? EDGE_STYLES.fullOpacity
      : isSoft
        ? EDGE_STYLES.dimmedOpacity
        : 1,
  };
}

function decorateEdges(edges: Edge[]): Edge[] {
  return edges.map((e) => {
    const relation = (e.data?.relation as string) ?? "parent";
    const highlighted = Boolean(e.data?.highlighted);
    const sourcePillar = e.data?.sourcePillar as string | null | undefined;
    return { ...e, style: edgeStyleFor(relation, highlighted, sourcePillar) };
  });
}

/**
 * Sort nodes for predictable Tab traversal: by x (depth) then y (vertical).
 * In an LR mind-map this yields tree-order: pillars first, then categories,
 * then leaves, top-to-bottom within each column.
 */
function sortByTreeOrder(nodes: Node[]): Node[] {
  return [...nodes].sort((a, b) => {
    const dx = a.position.x - b.position.x;
    if (Math.abs(dx) > 5) return dx;
    return a.position.y - b.position.y;
  });
}

function minimapColor(node: Node): string {
  const meta = node.data?.meta as NodeMeta | undefined;
  return styleForPillar(meta?.pillar).border;
}

/**
 * Horizontal dashed separators between adjacent pillar lanes. Rendered inside
 * the ReactFlow viewport so they pan/zoom with the graph. Each separator sits
 * at the midpoint of the gap between two lanes and spans the widest lane.
 */
function LaneSeparators({ lanes }: { lanes: LaneInfo[] }) {
  if (lanes.length < 2) return null;
  const maxWidth = lanes.reduce((m, l) => Math.max(m, l.width), 0);
  const items: React.ReactNode[] = [];
  for (let i = 0; i < lanes.length - 1; i += 1) {
    const top = lanes[i];
    const bottom = lanes[i + 1];
    const y = (top.yEnd + bottom.yStart) / 2;
    const width = Math.max(top.width, bottom.width, maxWidth);
    items.push(
      <div
        key={`lane-sep-${top.pillar}-${bottom.pillar}`}
        data-testid={`kg-lane-separator-${top.pillar}`}
        aria-hidden
        style={{
          position: "absolute",
          left: -LAYOUT_CONFIG.laneGap / 2,
          top: y,
          width: width + LAYOUT_CONFIG.laneGap,
          height: 0,
          borderTop: `${LANE_SEPARATOR_STYLE.widthPx}px dashed ${LANE_SEPARATOR_STYLE.color}`,
          pointerEvents: "none",
        }}
      />,
    );
  }
  return <ViewportPortal>{items}</ViewportPortal>;
}

interface KgControls {
  expandAll: () => void;
  collapseAll: () => void;
  onTreeNavSelect: (id: string) => void;
}

interface InnerProps {
  model: KgGraphModel;
  selectedId: string | null;
  setSelectedId: (id: string | null) => void;
  registerControls?: (c: KgControls) => void;
}

function KgGraphInner({
  model,
  selectedId,
  setSelectedId,
  registerControls,
}: InnerProps) {
  const rf = useReactFlow();
  const layout = useKgLayout();

  const initialUrl = useMemo(
    () => readUrlState(typeof window === "undefined" ? "" : window.location.search),
    [],
  );

  const [expanded, setExpanded] = useState<Set<string>>(() => {
    let base = defaultExpandedSet(model);
    if (initialUrl.expanded) {
      for (const id of initialUrl.expanded) base.add(id);
    }
    // Auto-expand ancestors of a deeplinked node so it is visible on mount
    // even when the URL omits ?expanded=... (supports plain ?node=nX links).
    if (initialUrl.nodeId && model.nodesById.has(initialUrl.nodeId)) {
      base = expandToReveal(model, new Set([initialUrl.nodeId]), base);
    }
    return base;
  });
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [rfNodes, setRfNodes] = useState<Node[]>([]);
  const [rfEdges, setRfEdges] = useState<Edge[]>([]);
  const [lanes, setLanes] = useState<LaneInfo[]>([]);
  const [pulseId, setPulseId] = useState<string | null>(null);
  const debounceRef = useRef<number | null>(null);
  const pulseTimerRef = useRef<number | null>(null);
  const initialFitDone = useRef(false);
  // Last node the user expanded/collapsed or selected from TreeNav — the
  // layout effect centers the viewport on it after relayout so focus is
  // preserved.
  const lastActivatedRef = useRef<string | null>(null);
  // Hover state removed — caused persistent jitter. See hotfix1-5 history.

  useEffect(() => {
    if (debounceRef.current != null) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(
      () => setDebouncedSearch(search),
      300,
    );
    return () => {
      if (debounceRef.current != null) window.clearTimeout(debounceRef.current);
    };
  }, [search]);

  const searchMatches = useMemo(
    () => findSearchMatches(model, debouncedSearch),
    [model, debouncedSearch],
  );

  const effectiveExpanded = useMemo(() => {
    if (searchMatches.size === 0) return expanded;
    return expandToReveal(model, searchMatches, expanded);
  }, [model, searchMatches, expanded]);

  const visibleIds = useMemo(
    () => computeVisibleNodeIds(model, effectiveExpanded),
    [model, effectiveExpanded],
  );

  // Hover effects disabled — they caused persistent jitter via React Flow
  // ResizeObserver / cursor management conflicts. Tooltip shows on click instead.

  // Zoom-independent focus feedback for content-less leaves: center the
  // viewport on the node (never zooming OUT — only IN if current zoom <1.0)
  // and flash a 300ms pulse ring so the action is visible even when setCenter
  // is a near no-op.
  const focusOnNode = useCallback(
    (id: string) => {
      const pos = layout.getPosition(id);
      const meta = model.nodesById.get(id);
      if (!pos || !meta) return;
      const base =
        meta.kind === "pillar"
          ? LAYOUT_CONFIG.pillarNode
          : meta.kind === "category"
            ? LAYOUT_CONFIG.categoryNode
            : LAYOUT_CONFIG.leafNode;
      const scale = meta.kind === "leaf" ? meta.importanceScale : 1;
      const w = base.width * scale;
      const h = base.height * scale;
      rf.setCenter(pos.x + w / 2, pos.y + h / 2, {
        zoom: Math.max(rf.getZoom(), 1.0),
        duration: 200,
      });
      setPulseId(id);
      if (pulseTimerRef.current != null) window.clearTimeout(pulseTimerRef.current);
      pulseTimerRef.current = window.setTimeout(() => {
        setPulseId((prev) => (prev === id ? null : prev));
      }, 320);
    },
    [layout, model, rf],
  );

  // Tri-state click (KG-UX-10). hasContent() is the ONLY source of truth for
  // "does this node have drawer content?" — do not compare content_length
  // directly here.
  //   has content                 -> open drawer
  //   no content + 0 children     -> focus animation only (no drawer)
  //   no content + >0 collapsed   -> expand
  //   no content + >0 expanded    -> collapse
  const handleActivate = useCallback(
    (id: string) => {
      const meta = model.nodesById.get(id);
      if (!meta) return;
      if (hasContent(meta)) {
        setSelectedId(id);
        return;
      }
      if (meta.childCount === 0) {
        focusOnNode(id);
        return;
      }
      lastActivatedRef.current = id;
      setExpanded((prev) => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        return next;
      });
    },
    [model, setSelectedId, focusOnNode],
  );

  const expandAll = useCallback(() => {
    lastActivatedRef.current = null;
    setExpanded(allParentIds(model));
  }, [model]);

  const collapseAll = useCallback(() => {
    lastActivatedRef.current = null;
    setExpanded(new Set());
  }, []);

  // Wire TreeNav (KG-UX-09): click in the outline expands all ancestors of the
  // target (plus itself when it has children) so the node is visible on the
  // canvas, selects it (opens drawer for leaves), and centers the viewport on
  // it once the layout effect resolves.
  const onTreeNavSelect = useCallback(
    (id: string) => {
      if (!model.nodesById.has(id)) return;
      lastActivatedRef.current = id;
      setExpanded((prev) => expandedSetForTreeNavSelect(model, prev, id));
      setSelectedId(id);
    },
    [model, setSelectedId],
  );

  useEffect(() => {
    registerControls?.({ expandAll, collapseAll, onTreeNavSelect });
  }, [registerControls, expandAll, collapseAll, onTreeNavSelect]);

  // Global Escape: close drawer + deselect + blur active node.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key !== "Escape") return;
      setSelectedId(null);
      const el = document.activeElement as HTMLElement | null;
      if (el && typeof el.blur === "function") el.blur();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setSelectedId]);

  useSyncUrl({
    nodeId: selectedId,
    expanded: new Set(
      [...expanded].filter(
        (id) => !defaultExpandedSet(model).has(id),
      ),
    ),
  });

  // ---- STRUCTURAL LAYOUT (runs on mount + expand/collapse) ----
  // Full ELK re-layout on every visible-set change. With <500 nodes this
  // completes in <200ms. Full re-layout prevents overlap between pillar
  // subtrees that the previous incremental approach caused.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      await layout.layoutAll(model, visibleIds);
      if (cancelled) return;
      const base = buildReactFlowNodes(
        model,
        visibleIds,
        effectiveExpanded,
        selectedId,
        searchMatches,
        searchMatches.size > 0,
        {
          onActivate: handleActivate,
        },
      );
      const positioned = sortByTreeOrder(layout.applyPositions(base));
      setRfNodes(positioned);
      setRfEdges(
        decorateEdges(
          buildReactFlowEdges(model, visibleIds, null),
        ),
      );
      setLanes(layout.getLanes());
      if (!initialFitDone.current) {
        // Deeplink direct-focus: when ?node=<id> is present, setCenter on it
        // at zoom 1.0 instead of fitView — eliminates visible zoom-out-then-
        // zoom-in jitter. Falls back to fitView if the node is missing or
        // has no layout position.
        const deeplinkId = initialUrl.nodeId;
        const deeplinkMeta = deeplinkId ? model.nodesById.get(deeplinkId) : undefined;
        const deeplinkPos = deeplinkId ? layout.getPosition(deeplinkId) : null;
        if (deeplinkId && deeplinkMeta && deeplinkPos) {
          const nodeBase =
            deeplinkMeta.kind === "pillar"
              ? LAYOUT_CONFIG.pillarNode
              : deeplinkMeta.kind === "category"
                ? LAYOUT_CONFIG.categoryNode
                : LAYOUT_CONFIG.leafNode;
          const scale = deeplinkMeta.kind === "leaf" ? deeplinkMeta.importanceScale : 1;
          const w = nodeBase.width * scale;
          const h = nodeBase.height * scale;
          requestAnimationFrame(() => {
            rf.setCenter(deeplinkPos.x + w / 2, deeplinkPos.y + h / 2, {
              zoom: INITIAL_ZOOM_CAP,
              duration: 300,
            });
            initialFitDone.current = true;
          });
        } else {
          // Cold load: cap zoom at 1.0 so pillar/category titles stay legible
          // (wide swimlane layout otherwise shrinks nodes to fit).
          requestAnimationFrame(() => {
            rf.fitView({ padding: 0.15, maxZoom: INITIAL_ZOOM_CAP, duration: 300 });
            initialFitDone.current = true;
          });
        }
      } else if (lastActivatedRef.current) {
        const focusId = lastActivatedRef.current;
        lastActivatedRef.current = null;
        const pos = layout.getPosition(focusId);
        const meta = model.nodesById.get(focusId);
        if (pos && meta) {
          const base =
            meta.kind === "pillar"
              ? LAYOUT_CONFIG.pillarNode
              : meta.kind === "category"
                ? LAYOUT_CONFIG.categoryNode
                : LAYOUT_CONFIG.leafNode;
          const scale = meta.kind === "leaf" ? meta.importanceScale : 1;
          const w = base.width * scale;
          const h = base.height * scale;
          requestAnimationFrame(() => {
            rf.setCenter(pos.x + w / 2, pos.y + h / 2, {
              duration: 400,
              zoom: rf.getZoom(),
            });
          });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [model, visibleIds, effectiveExpanded, searchMatches]);

  // Selection-only update: when user clicks a leaf, mark it selected.
  // No hover effects (removed due to persistent jitter — see hotfix history).
  useEffect(() => {
    if (!initialFitDone.current) return;
    setRfNodes((nodes) =>
      nodes.map((n) => {
        const wasSelected = Boolean((n.data as Record<string, unknown>).isSelected);
        const nowSelected = selectedId === n.id;
        if (wasSelected === nowSelected) return n;
        return { ...n, data: { ...n.data, isSelected: nowSelected } };
      }),
    );
  }, [selectedId]);

  // Pulse-only update: patch isPulsing onto node data without re-running ELK.
  useEffect(() => {
    setRfNodes((nodes) =>
      nodes.map((n) => {
        const wasPulsing = Boolean((n.data as Record<string, unknown>).isPulsing);
        const nowPulsing = pulseId === n.id;
        if (wasPulsing === nowPulsing) return n;
        return { ...n, data: { ...n.data, isPulsing: nowPulsing } };
      }),
    );
  }, [pulseId]);

  // Clean up pending pulse timer on unmount.
  useEffect(() => {
    return () => {
      if (pulseTimerRef.current != null) window.clearTimeout(pulseTimerRef.current);
    };
  }, []);

  // Auto-zoom + pan to first search match.
  useEffect(() => {
    if (searchMatches.size === 0) return;
    const firstId = [...searchMatches][0];
    const pos = layout.getPosition(firstId);
    if (!pos) return;
    rf.setCenter(pos.x + 90, pos.y + 18, { zoom: 1.0, duration: 500 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchMatches]);

  const handleNodeClick = useCallback(
    (_evt: React.MouseEvent, node: Node) => {
      handleActivate(node.id);
    },
    [handleActivate],
  );

  const selectedRawId =
    selectedId && /^n\d+$/.test(selectedId)
      ? Number(selectedId.slice(1))
      : null;

  // Clamp pan range to the current graph bbox + 300px on each side so users
  // cannot drag the canvas into pure empty space beyond the rendered nodes.
  const translateExtent = useMemo(() => computeBBox(rfNodes), [rfNodes]);

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: KG_STYLE_OVERRIDES }} />
      <div className="absolute top-2 right-2 z-10">
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search nodes..."
          aria-label="Search knowledge graph nodes"
          className="w-64 px-3 py-1.5 text-sm border border-gray-300 rounded bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        nodeTypes={NODE_TYPES}
        nodesDraggable={false}
        nodesConnectable={false}
        edgesReconnectable={false}
        elementsSelectable={false}
        selectNodesOnDrag={false}
        selectionOnDrag={false}
        panOnDrag
        panOnScroll={false}
        zoomOnScroll
        zoomOnDoubleClick={false}
        translateExtent={translateExtent}
        minZoom={0.2}
        maxZoom={2.0}
        onNodeClick={handleNodeClick}
        proOptions={{ hideAttribution: true }}
        className="kg-canvas"
      >
        <Background variant={BackgroundVariant.Dots} gap={20} color="#f1f5f9" />
        <Controls position="bottom-right" showInteractive={false} />
        <MiniMap nodeColor={minimapColor} pannable zoomable />
        <LaneSeparators lanes={lanes} />
      </ReactFlow>
      {/* Hover tooltip removed — caused persistent jitter. Info shown on click via drawer. */}
      <FrameworkNodeDrawer
        nodeId={selectedRawId}
        onClose={() => setSelectedId(null)}
      />
    </>
  );
}

export default function KnowledgeGraph() {
  const { data, isLoading, error } = useQuery<KgGraphResponse>({
    queryKey: ["kg", "graph"],
    queryFn: () => api.get<KgGraphResponse>("/kg/graph"),
    staleTime: 60_000,
  });

  const model = useMemo(() => (data ? buildGraphModel(data) : null), [data]);

  // selectedId is lifted here so both TreeNav (for row highlight) and
  // KgGraphInner (for drawer + node selection state) read the same value.
  const initialUrlNodeId = useMemo(() => {
    if (typeof window === "undefined") return null;
    return readUrlState(window.location.search).nodeId;
  }, []);
  const [selectedId, setSelectedId] = useState<string | null>(initialUrlNodeId);

  const controlsRef = useRef<KgControls | null>(null);
  const registerControls = useCallback((c: KgControls) => {
    controlsRef.current = c;
  }, []);
  const handleTreeNavSelect = useCallback((id: string) => {
    controlsRef.current?.onTreeNavSelect(id);
  }, []);

  return (
    <div data-testid="kg-page" className="flex h-[calc(100vh-3rem)] gap-3">
      {model && (
        <TreeNav
          model={model}
          onSelect={handleTreeNavSelect}
          selectedId={selectedId}
        />
      )}
      <div className="flex flex-col flex-1 min-w-0">
        <header className="flex items-center justify-between gap-4 mb-3">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Knowledge Graph</h1>
            <p className="text-xs text-gray-500">
              {data
                ? `${data.nodes.length} nodes - ${data.edges.length} edges`
                : ""}
            </p>
          </div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              data-testid="kg-expand-all"
              onClick={() => controlsRef.current?.expandAll()}
              disabled={!model}
              className="px-2 py-1 text-xs border border-gray-300 rounded bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Expand All
            </button>
            <button
              type="button"
              data-testid="kg-collapse-all"
              onClick={() => controlsRef.current?.collapseAll()}
              disabled={!model}
              className="px-2 py-1 text-xs border border-gray-300 rounded bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              Collapse All
            </button>
          </div>
        </header>

        {isLoading && (
          <div className="text-gray-500 italic">Loading graph...</div>
        )}
        {error && (
          <div className="text-red-600 text-sm">
            Failed to load graph: {(error as Error).message}
          </div>
        )}

        <div
          data-testid="kg-canvas"
          className="relative flex-1 min-h-[400px] border border-gray-200 rounded bg-white overflow-hidden"
        >
          {model && (
            <ReactFlowProvider>
              <KgGraphInner
                model={model}
                selectedId={selectedId}
                setSelectedId={setSelectedId}
                registerControls={registerControls}
              />
            </ReactFlowProvider>
          )}
        </div>
      </div>
    </div>
  );
}

// Re-export for tests / external callers
export { nodeIdOf };
