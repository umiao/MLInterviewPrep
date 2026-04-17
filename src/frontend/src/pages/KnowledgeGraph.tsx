// Read-only LR mind-map viewer built on React Flow + ELK.js layered layout.
// Incremental layout, default semi-expanded, URL-synced selection/expansion,
// search auto-expand + zoom + highlight.

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Background,
  BackgroundVariant,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
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

function minimapColor(node: Node): string {
  const meta = node.data?.meta as NodeMeta | undefined;
  return styleForPillar(meta?.pillar).border;
}

interface InnerProps {
  model: KgGraphModel;
}

function KgGraphInner({ model }: InnerProps) {
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
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [rfNodes, setRfNodes] = useState<Node[]>([]);
  const [rfEdges, setRfEdges] = useState<Edge[]>([]);
  const debounceRef = useRef<number | null>(null);
  const initialFitDone = useRef(false);

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

  useSyncUrl({
    nodeId: selectedId,
    expanded: new Set(
      [...expanded].filter(
        (id) => !defaultExpandedSet(model).has(id),
      ),
    ),
  });

  // Initial full layout.
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
      );
      const positioned = layout.applyPositions(base);
      setRfNodes(positioned);
      setRfEdges(
        decorateEdges(buildReactFlowEdges(model, visibleIds, hoveredId)),
      );
      // fitView once layout is in place.
      requestAnimationFrame(() => {
        rf.fitView({ padding: 0.1, duration: 300 });
        initialFitDone.current = true;
      });
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [model]);

  // Incremental layout on expand/collapse or visible-set change.
  useEffect(() => {
    if (!initialFitDone.current) return;
    let cancelled = false;
    (async () => {
      // Ensure every visible node has a position. Nodes that were newly
      // revealed lack cached coords -- layout just those relative to their
      // parent (anchor).
      const missing = [...visibleIds].filter(
        (id) => !layout.getPosition(id),
      );
      if (missing.length > 0) {
        const parents = new Set<string>();
        for (const id of missing) {
          const parent = model.nodesById.get(id)?.parentId;
          if (parent) parents.add(parent);
        }
        for (const parentId of parents) {
          const siblingAndSelf = new Set<string>([parentId]);
          for (const kid of model.childrenOf.get(parentId) ?? []) {
            if (visibleIds.has(kid)) siblingAndSelf.add(kid);
          }
          await layout.layoutSubset(model, siblingAndSelf, {
            anchorId: parentId,
          });
          if (cancelled) return;
        }
      }
      const base = buildReactFlowNodes(
        model,
        visibleIds,
        effectiveExpanded,
        selectedId,
        searchMatches,
        searchMatches.size > 0,
      );
      setRfNodes(layout.applyPositions(base));
      setRfEdges(
        decorateEdges(buildReactFlowEdges(model, visibleIds, hoveredId)),
      );
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visibleIds, effectiveExpanded, selectedId, searchMatches, hoveredId]);

  // Auto-zoom + pan to first search match.
  useEffect(() => {
    if (searchMatches.size === 0) return;
    const firstId = [...searchMatches][0];
    const pos = layout.getPosition(firstId);
    if (!pos) return;
    rf.setCenter(pos.x + 90, pos.y + 18, { zoom: 1.0, duration: 500 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchMatches]);

  const handleNodeClick: NodeMouseHandler = useCallback(
    (_evt, node) => {
      const meta = node.data?.meta as NodeMeta | undefined;
      if (!meta) return;
      if (meta.kind === "leaf") {
        setSelectedId(node.id);
        return;
      }
      // pillar / category: toggle expansion
      setExpanded((prev) => {
        const next = new Set(prev);
        if (next.has(node.id)) next.delete(node.id);
        else next.add(node.id);
        return next;
      });
    },
    [],
  );

  const handleNodeEnter: NodeMouseHandler = useCallback((_e, n) => {
    setHoveredId(n.id);
  }, []);
  const handleNodeLeave: NodeMouseHandler = useCallback(() => {
    setHoveredId(null);
  }, []);

  const selectedRawId =
    selectedId && /^n\d+$/.test(selectedId)
      ? Number(selectedId.slice(1))
      : null;

  return (
    <>
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
        elementsSelectable
        onNodeClick={handleNodeClick}
        onNodeMouseEnter={handleNodeEnter}
        onNodeMouseLeave={handleNodeLeave}
        proOptions={{ hideAttribution: true }}
        fitView
        fitViewOptions={{ padding: 0.1 }}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} color="#f1f5f9" />
        <MiniMap nodeColor={minimapColor} pannable zoomable />
      </ReactFlow>
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
        <div className="flex flex-wrap gap-2 text-[10px] text-gray-700">
          {pillars.map(([key, s]) => (
            <span
              key={key}
              className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded"
              style={{ backgroundColor: s.bg, color: s.border }}
            >
              <span
                aria-hidden
                className="w-2 h-2 rounded-sm"
                style={{ backgroundColor: s.border }}
              />
              {s.name}
            </span>
          ))}
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
            <KgGraphInner model={model} />
          </ReactFlowProvider>
        )}
      </div>
    </div>
  );
}

// Re-export for tests / external callers
export { nodeIdOf };
