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
  useReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

// Override React Flow's cursor management to prevent flicker between
// grab/pointer icons when hovering nodes. Nodes set their own cursor-pointer.
const KG_STYLE_OVERRIDES = `
.kg-canvas .react-flow__pane { cursor: grab !important; }
.kg-canvas .react-flow__pane:active { cursor: grabbing !important; }
.kg-canvas .react-flow__node { cursor: pointer !important; }
`;
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import FrameworkNodeDrawer from "../components/framework/FrameworkNodeDrawer";
import PillarNode from "../components/kg/PillarNode";
import CategoryNode from "../components/kg/CategoryNode";
import LeafNode from "../components/kg/LeafNode";
import { useKgLayout } from "../components/kg/useKgLayout";
import {
  readUrlState,
  useSyncUrl,
} from "../components/kg/useKgUrlState";
import {
  EDGE_STYLES,
  PILLAR_STYLES,
  styleForPillar,
} from "../components/kg/kgStyles";
import {
  allParentIds,
  buildGraphModel,
  buildReactFlowEdges,
  buildReactFlowNodes,
  computeVisibleNodeIds,
  defaultExpandedSet,
  expandToReveal,
  findSearchMatches,
  nodeIdOf,
  type KgGraphModel,
  type KgGraphResponse,
  type NodeMeta,
} from "./kgGraph.helpers";

const NODE_TYPES = {
  pillar: PillarNode,
  category: CategoryNode,
  leaf: LeafNode,
};

function edgeStyleFor(relation: string, highlighted: boolean) {
  const base =
    relation === "parent"
      ? EDGE_STYLES.parent
      : relation === "canonical"
        ? EDGE_STYLES.canonical
        : relation === "see_also"
          ? EDGE_STYLES.seeAlso
          : relation === "drill"
            ? EDGE_STYLES.drill
            : EDGE_STYLES.other;
  const isSoft = relation !== "parent" && relation !== "canonical";
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
    return { ...e, style: edgeStyleFor(relation, highlighted) };
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

interface InnerProps {
  model: KgGraphModel;
  registerControls?: (c: { expandAll: () => void; collapseAll: () => void }) => void;
}

function KgGraphInner({ model, registerControls }: InnerProps) {
  const rf = useReactFlow();
  const layout = useKgLayout();

  const initialUrl = useMemo(
    () => readUrlState(typeof window === "undefined" ? "" : window.location.search),
    [],
  );

  const [expanded, setExpanded] = useState<Set<string>>(() => {
    if (initialUrl.expanded) {
      const base = defaultExpandedSet(model);
      for (const id of initialUrl.expanded) base.add(id);
      return base;
    }
    return defaultExpandedSet(model);
  });
  const [selectedId, setSelectedId] = useState<string | null>(initialUrl.nodeId);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [rfNodes, setRfNodes] = useState<Node[]>([]);
  const [rfEdges, setRfEdges] = useState<Edge[]>([]);
  const debounceRef = useRef<number | null>(null);
  const initialFitDone = useRef(false);
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

  const handleActivate = useCallback(
    (id: string) => {
      const meta = model.nodesById.get(id);
      if (!meta) return;
      if (meta.kind === "leaf") {
        setSelectedId(id);
        return;
      }
      setExpanded((prev) => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        return next;
      });
    },
    [model],
  );

  const expandAll = useCallback(() => {
    setExpanded(allParentIds(model));
  }, [model]);

  const collapseAll = useCallback(() => {
    setExpanded(new Set());
  }, []);

  useEffect(() => {
    registerControls?.({ expandAll, collapseAll });
  }, [registerControls, expandAll, collapseAll]);

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
  }, []);

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
      if (!initialFitDone.current) {
        requestAnimationFrame(() => {
          rf.fitView({ padding: 0.1, duration: 300 });
          initialFitDone.current = true;
        });
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
        onNodeClick={handleNodeClick}
        proOptions={{ hideAttribution: true }}
        className="kg-canvas"
      >
        <Background variant={BackgroundVariant.Dots} gap={20} color="#f1f5f9" />
        <Controls position="bottom-right" showInteractive={false} />
        <MiniMap nodeColor={minimapColor} pannable zoomable />
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

  const pillars = useMemo(() => Object.entries(PILLAR_STYLES), []);

  const controlsRef = useRef<{
    expandAll: () => void;
    collapseAll: () => void;
  } | null>(null);
  const registerControls = useCallback(
    (c: { expandAll: () => void; collapseAll: () => void }) => {
      controlsRef.current = c;
    },
    [],
  );

  return (
    <div data-testid="kg-page" className="flex flex-col h-[calc(100vh-3rem)]">
      <header className="flex items-center justify-between gap-4 mb-3">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Knowledge Graph</h1>
          <p className="text-xs text-gray-500">
            {data
              ? `${data.nodes.length} nodes - ${data.edges.length} edges`
              : ""}
          </p>
        </div>
        <div className="flex items-center gap-3">
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
          <div className="flex flex-wrap gap-2 text-[10px] text-gray-700">
            {pillars.map(([key, s]) => (
              <button
                key={key}
                type="button"
                title={`Toggle ${s.name}`}
                onClick={() => controlsRef.current?.expandAll()}
                className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded cursor-pointer hover:ring-1 hover:ring-gray-400 transition-shadow"
                style={{ backgroundColor: s.bg, color: s.border }}
              >
                <span
                  aria-hidden
                  className="w-2 h-2 rounded-sm"
                  style={{ backgroundColor: s.border }}
                />
                {s.name}
              </button>
            ))}
          </div>
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
            <KgGraphInner model={model} registerControls={registerControls} />
          </ReactFlowProvider>
        )}
      </div>
    </div>
  );
}

// Re-export for tests / external callers
export { nodeIdOf };
