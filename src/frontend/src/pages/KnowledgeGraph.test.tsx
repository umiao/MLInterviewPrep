import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { ReactFlowProvider } from "@xyflow/react";
import {
  allParentIds,
  buildGraphModel,
  buildReactFlowNodes,
  colorForPillar,
  computeVisibleNodeIds,
  defaultExpandedSet,
  expandToReveal,
  findSearchMatches,
  importanceScaleFor,
  neighborsOfHover,
  nodeIdOf,
  type KgGraphResponse,
} from "./kgGraph.helpers";
import {
  readUrlState,
  writeUrlState,
} from "../components/kg/useKgUrlState";
import CategoryNode from "../components/kg/CategoryNode";
import LeafNode from "../components/kg/LeafNode";

vi.mock("../utils/api", () => ({
  api: {
    get: vi.fn(() => new Promise(() => {})),
  },
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
      pillar: "pillar1",
      path: "pillar1.dp.coin",
      title: "Coin Change",
      depth: 2,
      parent_id: 2,
      content_length: 2500,
    },
    {
      id: 4,
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
    {
      src_kind: "framework_node",
      src_id: 2,
      dst_kind: "framework_node",
      dst_id: 3,
      relation: "parent",
    },
  ],
};

describe("colorForPillar", () => {
  it("returns the pillar-specific border color", () => {
    expect(colorForPillar("pillar1")).toBe("#475569");
    expect(colorForPillar("pillar6")).toBe("#e11d48");
  });

  it("returns a neutral fallback for null or unknown pillars", () => {
    const fallback = colorForPillar(null);
    expect(fallback).toBe(colorForPillar("pillar99"));
    expect(fallback).toMatch(/^#/);
  });
});

describe("buildGraphModel", () => {
  it("classifies nodes by depth and wires parent/child maps", () => {
    const m = buildGraphModel(SAMPLE);
    expect(m.nodesById.size).toBe(4);
    expect(m.pillarIds).toEqual([nodeIdOf(1), nodeIdOf(4)]);
    expect(m.nodesById.get(nodeIdOf(1))!.kind).toBe("pillar");
    expect(m.nodesById.get(nodeIdOf(2))!.kind).toBe("category");
    expect(m.nodesById.get(nodeIdOf(3))!.kind).toBe("leaf");
    expect(m.childrenOf.get(nodeIdOf(1))).toEqual([nodeIdOf(2)]);
    expect(m.childrenOf.get(nodeIdOf(2))).toEqual([nodeIdOf(3)]);
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
    const m = buildGraphModel(orphan);
    expect(m.edges).toHaveLength(0);
  });

  it("computes child counts for parent nodes", () => {
    const m = buildGraphModel(SAMPLE);
    expect(m.nodesById.get(nodeIdOf(1))!.childCount).toBe(1);
    expect(m.nodesById.get(nodeIdOf(2))!.childCount).toBe(1);
    expect(m.nodesById.get(nodeIdOf(3))!.childCount).toBe(0);
  });
});

describe("visibility + expansion", () => {
  it("semi-expands pillars by default: pillar + category visible, leaves hidden", () => {
    const m = buildGraphModel(SAMPLE);
    const expanded = defaultExpandedSet(m);
    const visible = computeVisibleNodeIds(m, expanded);
    expect(visible.has(nodeIdOf(1))).toBe(true); // pillar
    expect(visible.has(nodeIdOf(2))).toBe(true); // category (child of expanded pillar)
    expect(visible.has(nodeIdOf(3))).toBe(false); // leaf hidden by default
    expect(visible.has(nodeIdOf(4))).toBe(true);
  });

  it("reveals leaves when their parent category is expanded", () => {
    const m = buildGraphModel(SAMPLE);
    const expanded = defaultExpandedSet(m);
    expanded.add(nodeIdOf(2));
    const visible = computeVisibleNodeIds(m, expanded);
    expect(visible.has(nodeIdOf(3))).toBe(true);
  });

  it("hides the whole subtree when the pillar is collapsed", () => {
    const m = buildGraphModel(SAMPLE);
    const expanded = defaultExpandedSet(m);
    expanded.delete(nodeIdOf(1));
    const visible = computeVisibleNodeIds(m, expanded);
    expect(visible.has(nodeIdOf(1))).toBe(true);
    expect(visible.has(nodeIdOf(2))).toBe(false);
    expect(visible.has(nodeIdOf(3))).toBe(false);
  });

  it("expandToReveal walks ancestors of matched ids", () => {
    const m = buildGraphModel(SAMPLE);
    const base = new Set<string>();
    const revealed = expandToReveal(m, new Set([nodeIdOf(3)]), base);
    expect(revealed.has(nodeIdOf(1))).toBe(true);
    expect(revealed.has(nodeIdOf(2))).toBe(true);
    expect(revealed.has(nodeIdOf(3))).toBe(false);
  });
});

describe("findSearchMatches", () => {
  it("matches node titles case-insensitively", () => {
    const m = buildGraphModel(SAMPLE);
    expect(findSearchMatches(m, "dynamic")).toEqual(new Set([nodeIdOf(2)]));
    expect(findSearchMatches(m, "THEORY")).toEqual(new Set([nodeIdOf(4)]));
  });

  it("returns empty set on empty query", () => {
    const m = buildGraphModel(SAMPLE);
    expect(findSearchMatches(m, "")).toEqual(new Set());
    expect(findSearchMatches(m, "   ")).toEqual(new Set());
  });
});

describe("importanceScaleFor", () => {
  it("returns 1.0 for low connectivity", () => {
    expect(importanceScaleFor(0)).toBe(1.0);
    expect(importanceScaleFor(5)).toBe(1.0);
  });

  it("returns 1.2 for moderate connectivity (>5)", () => {
    expect(importanceScaleFor(6)).toBe(1.2);
    expect(importanceScaleFor(10)).toBe(1.2);
  });

  it("returns 1.5 for hub nodes (>10)", () => {
    expect(importanceScaleFor(11)).toBe(1.5);
    expect(importanceScaleFor(50)).toBe(1.5);
  });
});

describe("buildGraphModel edge_count -> importanceScale", () => {
  it("derives edgeCount + importanceScale from KgNode payload", () => {
    const data: KgGraphResponse = {
      nodes: [
        {
          id: 1,
          kind: "framework_node",
          pillar: "pillar1",
          path: "pillar1",
          title: "P",
          depth: 0,
          parent_id: null,
          content_length: 0,
          edge_count: 12,
        },
        {
          id: 2,
          kind: "framework_node",
          pillar: "pillar1",
          path: "pillar1.x",
          title: "X",
          depth: 2,
          parent_id: 1,
          content_length: 0,
          edge_count: 7,
        },
      ],
      edges: [],
    };
    const m = buildGraphModel(data);
    expect(m.nodesById.get(nodeIdOf(1))!.edgeCount).toBe(12);
    expect(m.nodesById.get(nodeIdOf(1))!.importanceScale).toBe(1.5);
    expect(m.nodesById.get(nodeIdOf(2))!.edgeCount).toBe(7);
    expect(m.nodesById.get(nodeIdOf(2))!.importanceScale).toBe(1.2);
  });

  it("defaults edgeCount to 0 when payload omits edge_count", () => {
    const m = buildGraphModel(SAMPLE);
    expect(m.nodesById.get(nodeIdOf(1))!.edgeCount).toBe(0);
    expect(m.nodesById.get(nodeIdOf(1))!.importanceScale).toBe(1.0);
  });
});

describe("neighborsOfHover", () => {
  it("returns empty when nothing hovered", () => {
    const m = buildGraphModel(SAMPLE);
    const visible = new Set([nodeIdOf(1), nodeIdOf(2), nodeIdOf(3)]);
    expect(neighborsOfHover(m, visible, null).size).toBe(0);
  });

  it("returns the opposite endpoints of edges touching the hovered node", () => {
    const m = buildGraphModel(SAMPLE);
    const visible = new Set([nodeIdOf(1), nodeIdOf(2), nodeIdOf(3)]);
    // node 2 sits between 1 (parent) and 3 (child) -> both are neighbors.
    const ns = neighborsOfHover(m, visible, nodeIdOf(2));
    expect(ns).toEqual(new Set([nodeIdOf(1), nodeIdOf(3)]));
  });

  it("ignores edges whose other endpoint is not visible", () => {
    const m = buildGraphModel(SAMPLE);
    const visible = new Set([nodeIdOf(2)]); // only n2 visible
    expect(neighborsOfHover(m, visible, nodeIdOf(2)).size).toBe(0);
  });
});

describe("allParentIds", () => {
  it("returns every node that owns at least one child", () => {
    const m = buildGraphModel(SAMPLE);
    const ids = allParentIds(m);
    expect(ids.has(nodeIdOf(1))).toBe(true); // pillar with child
    expect(ids.has(nodeIdOf(2))).toBe(true); // category with child
    expect(ids.has(nodeIdOf(3))).toBe(false); // leaf
    expect(ids.has(nodeIdOf(4))).toBe(false); // childless pillar
  });
});

describe("buildReactFlowNodes hover/activate options", () => {
  it("threads hover, neighbor, and onActivate flags into node data", () => {
    const m = buildGraphModel(SAMPLE);
    const visible = new Set([nodeIdOf(1), nodeIdOf(2)]);
    const onActivate = vi.fn();
    const nodes = buildReactFlowNodes(
      m,
      visible,
      defaultExpandedSet(m),
      null,
      new Set(),
      false,
      {
        hoveredId: nodeIdOf(1),
        hoveredNeighbors: new Set([nodeIdOf(2)]),
        onActivate,
      },
    );
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
    expect(byId[nodeIdOf(1)].data.isHovered).toBe(true);
    expect(byId[nodeIdOf(1)].data.isNeighborOfHover).toBe(false);
    expect(byId[nodeIdOf(2)].data.isHovered).toBe(false);
    expect(byId[nodeIdOf(2)].data.isNeighborOfHover).toBe(true);
    expect(byId[nodeIdOf(2)].data.onActivate).toBe(onActivate);
  });

  it("defaults hover/neighbor flags to false when options omitted", () => {
    const m = buildGraphModel(SAMPLE);
    const visible = new Set([nodeIdOf(1)]);
    const nodes = buildReactFlowNodes(
      m,
      visible,
      defaultExpandedSet(m),
      null,
      new Set(),
      false,
    );
    expect(nodes[0].data.isHovered).toBe(false);
    expect(nodes[0].data.isNeighborOfHover).toBe(false);
    expect(nodes[0].data.onActivate).toBeUndefined();
  });
});

describe("URL state", () => {
  it("roundtrips node + expanded", () => {
    const qs = writeUrlState({
      nodeId: "n42",
      expanded: new Set(["n10", "n11"]),
    });
    const parsed = readUrlState(qs);
    expect(parsed.nodeId).toBe("n42");
    expect(parsed.expanded).toEqual(new Set(["n10", "n11"]));
  });

  it("ignores malformed ids", () => {
    const parsed = readUrlState("?node=abc&expanded=n1,junk,n2");
    expect(parsed.nodeId).toBeNull();
    expect(parsed.expanded).toEqual(new Set(["n1", "n2"]));
  });

  it("returns empty string when state is empty", () => {
    expect(writeUrlState({ nodeId: null, expanded: null })).toBe("");
  });
});

function renderNode(element: React.ReactNode): string {
  return renderToStaticMarkup(<ReactFlowProvider>{element}</ReactFlowProvider>);
}

function makeCategoryMeta(overrides: Partial<{
  childCount: number;
  contentLength: number;
  title: string;
}> = {}) {
  return {
    id: nodeIdOf(100),
    rawId: 100,
    kind: "category" as const,
    pillar: "pillar1",
    pillarName: "Coding & Algorithms",
    title: overrides.title ?? "Category Title",
    depth: 1,
    parentId: nodeIdOf(1),
    contentLength: overrides.contentLength ?? 500,
    path: "pillar1.x",
    childCount: overrides.childCount ?? 3,
    edgeCount: 0,
    importanceScale: 1.0,
  };
}

function makeLeafMeta(overrides: Partial<{ contentLength: number }> = {}) {
  return {
    id: nodeIdOf(200),
    rawId: 200,
    kind: "leaf" as const,
    pillar: "pillar1",
    pillarName: "Coding & Algorithms",
    title: "Leaf Title",
    depth: 2,
    parentId: nodeIdOf(100),
    contentLength: overrides.contentLength ?? 500,
    path: "pillar1.x.y",
    childCount: 0,
    edgeCount: 0,
    importanceScale: 1.0,
  };
}

describe("CategoryNode zero-children behavior", () => {
  it("renders child-count pill and chevron for category with children", () => {
    const data = {
      meta: makeCategoryMeta({ childCount: 5, contentLength: 9000 }),
      isExpanded: false,
      isSelected: false,
      isMatch: false,
      dimmed: false,
    };
    const html = renderNode(
      <CategoryNode id="n100" type="category" data={data} dragging={false}
        isConnectable={false} positionAbsoluteX={0} positionAbsoluteY={0}
        selected={false} selectable={false} deletable={false} draggable={false}
        zIndex={0} />,
    );
    expect(html).toContain('data-leaf-like="false"');
    expect(html).toContain("aria-expanded");
    // chevron rendered
    expect(html).toMatch(/&gt;|v/);
    // no completeness arc aria-label
    expect(html).not.toContain("Content completeness");
    // no stub badge (9000 > 2000)
    expect(html).not.toContain('data-testid="kg-stub-badge"');
  });

  it("renders completeness arc and hides chevron when childCount===0", () => {
    const data = {
      meta: makeCategoryMeta({ childCount: 0, contentLength: 500, title: "SQL Fundamentals" }),
      isExpanded: false,
      isSelected: false,
      isMatch: false,
      dimmed: false,
    };
    const html = renderNode(
      <CategoryNode id="n191" type="category" data={data} dragging={false}
        isConnectable={false} positionAbsoluteX={0} positionAbsoluteY={0}
        selected={false} selectable={false} deletable={false} draggable={false}
        zIndex={0} />,
    );
    expect(html).toContain('data-leaf-like="true"');
    // aria-expanded omitted for leaf-like categories
    expect(html).not.toContain("aria-expanded");
    expect(html).toContain("Content completeness");
    // stub badge present (500 < 2000)
    expect(html).toContain('data-testid="kg-stub-badge"');
    // aria-label should NOT contain "expanded/collapsed" wording
    expect(html).toContain('aria-label="SQL Fundamentals (Coding &amp; Algorithms)"');
  });

  it("omits stub badge when contentLength >= 2000", () => {
    const data = {
      meta: makeCategoryMeta({ childCount: 0, contentLength: 3000 }),
      isExpanded: false,
      isSelected: false,
      isMatch: false,
      dimmed: false,
    };
    const html = renderNode(
      <CategoryNode id="n100" type="category" data={data} dragging={false}
        isConnectable={false} positionAbsoluteX={0} positionAbsoluteY={0}
        selected={false} selectable={false} deletable={false} draggable={false}
        zIndex={0} />,
    );
    expect(html).not.toContain('data-testid="kg-stub-badge"');
  });
});

describe("LeafNode stub badge", () => {
  it("renders stub badge when contentLength < 2000", () => {
    const data = {
      meta: makeLeafMeta({ contentLength: 100 }),
      isExpanded: false,
      isSelected: false,
      isMatch: false,
      dimmed: false,
    };
    const html = renderNode(
      <LeafNode id="n200" type="leaf" data={data} dragging={false}
        isConnectable={false} positionAbsoluteX={0} positionAbsoluteY={0}
        selected={false} selectable={false} deletable={false} draggable={false}
        zIndex={0} />,
    );
    expect(html).toContain('data-testid="kg-stub-badge"');
  });

  it("omits stub badge when contentLength >= 2000", () => {
    const data = {
      meta: makeLeafMeta({ contentLength: 5000 }),
      isExpanded: false,
      isSelected: false,
      isMatch: false,
      dimmed: false,
    };
    const html = renderNode(
      <LeafNode id="n200" type="leaf" data={data} dragging={false}
        isConnectable={false} positionAbsoluteX={0} positionAbsoluteY={0}
        selected={false} selectable={false} deletable={false} draggable={false}
        zIndex={0} />,
    );
    expect(html).not.toContain('data-testid="kg-stub-badge"');
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

  it("renders the page shell and search input", () => {
    const html = render();
    expect(html).toContain("Knowledge Graph");
    expect(html).toContain('data-testid="kg-canvas"');
    expect(html).toContain('data-testid="kg-page"');
  });

  it("shows the loading state before the /kg/graph response arrives", () => {
    const html = render();
    expect(html).toContain("Loading graph");
  });

  it("renders the Expand/Collapse All controls in the header", () => {
    const html = render();
    expect(html).toContain('data-testid="kg-expand-all"');
    expect(html).toContain('data-testid="kg-collapse-all"');
    expect(html).toContain("Expand All");
    expect(html).toContain("Collapse All");
  });
});
