import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import {
  buildElements,
  colorForPillar,
  type KgGraphResponse,
} from "./kgGraph.helpers";

vi.mock("../utils/api", () => ({
  api: {
    get: vi.fn(() => new Promise(() => {})),
  },
}));

vi.mock("cytoscape-dagre", () => ({ default: () => undefined }));
vi.mock("cytoscape", () => ({
  default: Object.assign(
    () => ({
      on: () => undefined,
      destroy: () => undefined,
    }),
    { use: () => undefined },
  ),
}));

import KnowledgeGraph from "./KnowledgeGraph";

const SAMPLE: KgGraphResponse = {
  nodes: [
    {
      id: 1,
      kind: "framework_node",
      pillar: "pillar1",
      path: "pillar1",
      title: "Coding",
      depth: 0,
      parent_id: null,
      content_length: 0,
    },
    {
      id: 2,
      kind: "framework_node",
      pillar: "pillar1",
      path: "pillar1.dp",
      title: "Dynamic Programming",
      depth: 1,
      parent_id: 1,
      content_length: 42,
    },
    {
      id: 3,
      kind: "framework_node",
      pillar: "pillar2",
      path: "pillar2",
      title: "ML Theory",
      depth: 0,
      parent_id: null,
      content_length: 0,
    },
  ],
  edges: [
    {
      src_kind: "framework_node",
      src_id: 1,
      dst_kind: "framework_node",
      dst_id: 2,
      relation: "parent",
    },
  ],
};

describe("colorForPillar", () => {
  it("returns the brand color for known pillars", () => {
    expect(colorForPillar("pillar1")).toBe("#ef4444");
    expect(colorForPillar("pillar3")).toBe("#eab308");
  });

  it("returns a neutral grey for null or unknown pillars", () => {
    expect(colorForPillar(null)).toBe("#9ca3af");
    expect(colorForPillar("pillar99")).toBe("#9ca3af");
  });
});

describe("buildElements", () => {
  it("emits one element per node and per edge", () => {
    const els = buildElements(SAMPLE, "");
    expect(els).toHaveLength(SAMPLE.nodes.length + SAMPLE.edges.length);
  });

  it("dims nodes that do not match the search term", () => {
    const els = buildElements(SAMPLE, "dynamic");
    const dpEntry = els.find((e) => e.data?.id === "n2")!;
    const codingEntry = els.find((e) => e.data?.id === "n1")!;
    expect(dpEntry.data?.dim).toBe(false);
    expect(codingEntry.data?.dim).toBe(true);
  });

  it("does not dim any nodes when the search term is empty", () => {
    const els = buildElements(SAMPLE, "");
    const nodeEls = els.filter((e) => !e.data?.source);
    for (const ne of nodeEls) {
      expect(ne.data?.dim).toBe(false);
    }
  });

  it("drops edges whose endpoints are not in the node set", () => {
    const orphan: KgGraphResponse = {
      nodes: SAMPLE.nodes,
      edges: [
        {
          src_kind: "framework_node",
          src_id: 1,
          dst_kind: "framework_node",
          dst_id: 9999,
          relation: "see_also",
        },
      ],
    };
    const els = buildElements(orphan, "");
    const edgeEls = els.filter((e) => e.data?.source);
    expect(edgeEls).toHaveLength(0);
  });

  it("colors each node by its pillar", () => {
    const els = buildElements(SAMPLE, "");
    const codingNode = els.find((e) => e.data?.id === "n1")!;
    const mlNode = els.find((e) => e.data?.id === "n3")!;
    expect(codingNode.data?.color).toBe("#ef4444");
    expect(mlNode.data?.color).toBe("#f97316");
  });
});

describe("KnowledgeGraph page (initial render)", () => {
  function render(): string {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    return renderToStaticMarkup(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <KnowledgeGraph />
        </MemoryRouter>
      </QueryClientProvider>,
    );
  }

  it("renders the page header, search input, and canvas container", () => {
    const html = render();
    expect(html).toContain("Knowledge Graph");
    expect(html).toContain('aria-label="Filter nodes by title"');
    expect(html).toContain('data-testid="kg-canvas"');
    expect(html).toContain('data-testid="kg-page"');
  });

  it("shows the loading state before the /kg/graph response arrives", () => {
    const html = render();
    expect(html).toContain("Loading graph");
  });
});
