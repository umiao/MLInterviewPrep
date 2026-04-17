import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import cytoscape, { type Core, type ElementDefinition } from "cytoscape";
import dagre from "cytoscape-dagre";
import { api } from "../utils/api";
import FrameworkNodeDrawer from "../components/framework/FrameworkNodeDrawer";
import {
  buildElements,
  colorForPillar,
  type KgGraphResponse,
} from "./kgGraph.helpers";

cytoscape.use(dagre);

export default function KnowledgeGraph() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const cyRef = useRef<Core | null>(null);
  const [search, setSearch] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState<number | null>(null);

  const { data, isLoading, error } = useQuery<KgGraphResponse>({
    queryKey: ["kg", "graph"],
    queryFn: () => api.get<KgGraphResponse>("/kg/graph"),
    staleTime: 60_000,
  });

  const elements = useMemo<ElementDefinition[]>(
    () => (data ? buildElements(data, search) : []),
    [data, search],
  );

  useEffect(() => {
    if (!containerRef.current || !data) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "data(color)",
            label: "data(label)",
            color: "#111827",
            "font-size": "10px",
            "text-wrap": "wrap",
            "text-max-width": "120px",
            "text-valign": "center",
            "text-halign": "center",
            width: "label",
            height: "label",
            padding: "8px",
            shape: "round-rectangle",
            "border-width": 1,
            "border-color": "#1f2937",
          },
        },
        {
          selector: "node[?dim]",
          style: { opacity: 0.15 },
        },
        {
          selector: "edge",
          style: {
            width: 1.5,
            "line-color": "#94a3b8",
            "target-arrow-color": "#94a3b8",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
          },
        },
        {
          selector: 'edge[relation = "see_also"]',
          style: { "line-style": "dashed", "line-color": "#0ea5e9" },
        },
        {
          selector: 'edge[relation = "canonical"]',
          style: { "line-color": "#16a34a", width: 2 },
        },
      ],
      layout: {
        name: "dagre",
        // @ts-expect-error -- dagre options live on the layout config
        rankDir: "TB",
        nodeSep: 30,
        rankSep: 60,
        animate: false,
      },
      wheelSensitivity: 0.2,
    });

    cy.on("tap", "node", (evt) => {
      const nodeId = evt.target.data("nodeId") as number | undefined;
      if (typeof nodeId === "number") setSelectedNodeId(nodeId);
    });

    cyRef.current = cy;
    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [data, elements]);

  const pillarsSeen = useMemo(() => {
    if (!data) return [];
    const seen = new Set<string>();
    for (const n of data.nodes) {
      if (n.pillar) seen.add(n.pillar);
    }
    return Array.from(seen).sort();
  }, [data]);

  return (
    <div data-testid="kg-page" className="flex flex-col h-[calc(100vh-3rem)]">
      <header className="flex items-center justify-between gap-4 mb-3">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            Knowledge Graph
          </h1>
          <p className="text-xs text-gray-500">
            {data
              ? `${data.nodes.length} nodes · ${data.edges.length} edges`
              : ""}
          </p>
        </div>
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by title..."
          aria-label="Filter nodes by title"
          className="w-64 px-3 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </header>

      {pillarsSeen.length > 0 && (
        <div
          data-testid="kg-legend"
          className="flex flex-wrap gap-3 mb-3 text-xs text-gray-700"
        >
          {pillarsSeen.map((p) => (
            <span key={p} className="inline-flex items-center gap-1.5">
              <span
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: colorForPillar(p) }}
                aria-hidden
              />
              {p}
            </span>
          ))}
        </div>
      )}

      {isLoading && (
        <div className="text-gray-500 italic">Loading graph...</div>
      )}
      {error && (
        <div className="text-red-600 text-sm">
          Failed to load graph: {(error as Error).message}
        </div>
      )}

      <div
        ref={containerRef}
        data-testid="kg-canvas"
        className="flex-1 min-h-[400px] border border-gray-200 rounded bg-white"
      />

      <FrameworkNodeDrawer
        nodeId={selectedNodeId}
        onClose={() => setSelectedNodeId(null)}
      />
    </div>
  );
}
