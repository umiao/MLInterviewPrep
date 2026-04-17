import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { ReactFlowProvider } from "@xyflow/react";
import {
  allParentIds,
  buildGraphModel,
  buildReactFlowEdges,
  buildReactFlowNodes,
  colorForPillar,
  computeVisibleNodeIds,
  defaultExpandedSet,
  expandToReveal,
  expandedSetForTreeNavSelect,
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
import {
  computeBBox,
  groupVisibleByPillar,
  pillarSortKey,
  stackLanes,
} from "../components/kg/useKgLayout";
import { LAYOUT_CONFIG } from "../components/kg/kgStyles";

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

describe("buildReactFlowEdges (bezier + sourcePillar)", () => {
  it("emits type='default' (bezier) for all edges, including parent", () => {
    const m = buildGraphModel(SAMPLE);
    const visible = new Set([nodeIdOf(1), nodeIdOf(2), nodeIdOf(3)]);
    const edges = buildReactFlowEdges(m, visible, null);
    expect(edges.length).toBeGreaterThan(0);
    for (const e of edges) {
      expect(e.type).toBe("default");
    }
  });

  it("attaches the source node's pillar key to edge.data.sourcePillar", () => {
    const m = buildGraphModel(SAMPLE);
    const visible = new Set([nodeIdOf(1), nodeIdOf(2), nodeIdOf(3)]);
    const edges = buildReactFlowEdges(m, visible, null);
    // Edge 1->2 has source=pillar1 node; edge 2->3 has source=pillar1 category.
    const byId = Object.fromEntries(edges.map((e) => [e.id, e]));
    const e12 = byId[`${nodeIdOf(1)}-${nodeIdOf(2)}-parent`];
    const e23 = byId[`${nodeIdOf(2)}-${nodeIdOf(3)}-parent`];
    expect(e12.data?.sourcePillar).toBe("pillar1");
    expect(e23.data?.sourcePillar).toBe("pillar1");
  });
});

describe("swimlane: groupVisibleByPillar", () => {
  it("groups visible node ids by each node's pillar key", () => {
    const m = buildGraphModel(SAMPLE);
    const visible = new Set([nodeIdOf(1), nodeIdOf(2), nodeIdOf(4)]);
    const groups = groupVisibleByPillar(m, visible);
    expect(groups.get("pillar1")).toEqual(new Set([nodeIdOf(1), nodeIdOf(2)]));
    expect(groups.get("pillar2")).toEqual(new Set([nodeIdOf(4)]));
  });

  it("buckets missing/unknown pillars under the unassigned sentinel", () => {
    const data: KgGraphResponse = {
      nodes: [
        {
          id: 99,
          kind: "framework_node",
          pillar: null,
          path: "x",
          title: "Orphan",
          depth: 0,
          parent_id: null,
          content_length: 0,
        },
      ],
      edges: [],
    };
    const m = buildGraphModel(data);
    const groups = groupVisibleByPillar(m, new Set([nodeIdOf(99)]));
    expect(groups.size).toBe(1);
    const [[key, ids]] = [...groups.entries()];
    expect(key).not.toMatch(/^pillar\d+$/);
    expect(ids).toEqual(new Set([nodeIdOf(99)]));
  });
});

describe("swimlane: pillarSortKey", () => {
  it("sorts pillar1..pillar8 by numeric suffix", () => {
    const keys = ["pillar3", "pillar1", "pillar8", "pillar2"];
    keys.sort((a, b) => pillarSortKey(a) - pillarSortKey(b));
    expect(keys).toEqual(["pillar1", "pillar2", "pillar3", "pillar8"]);
  });

  it("pushes unknown/non-matching keys to the end", () => {
    const keys = ["pillar5", "other", "pillar1"];
    keys.sort((a, b) => pillarSortKey(a) - pillarSortKey(b));
    expect(keys).toEqual(["pillar1", "pillar5", "other"]);
  });
});

describe("swimlane: stackLanes", () => {
  it("stacks lanes vertically with gap and produces absolute positions", () => {
    const pillarLayouts = new Map([
      [
        "pillar1",
        {
          positions: new Map([
            ["n1", { x: 0, y: 0 }],
            ["n2", { x: 100, y: 20 }],
          ]),
          width: 300,
          height: 50,
        },
      ],
      [
        "pillar2",
        {
          positions: new Map([["n3", { x: 0, y: 0 }]]),
          width: 200,
          height: 40,
        },
      ],
    ]);
    const { positions, lanes } = stackLanes(
      pillarLayouts,
      ["pillar1", "pillar2"],
      LAYOUT_CONFIG.laneGap,
    );
    expect(lanes).toHaveLength(2);
    expect(lanes[0]).toMatchObject({ pillar: "pillar1", yStart: 0, yEnd: 50 });
    expect(lanes[1]).toMatchObject({
      pillar: "pillar2",
      yStart: 50 + LAYOUT_CONFIG.laneGap,
      yEnd: 50 + LAYOUT_CONFIG.laneGap + 40,
    });
    // pillar1 nodes untouched
    expect(positions.get("n1")).toEqual({ x: 0, y: 0 });
    expect(positions.get("n2")).toEqual({ x: 100, y: 20 });
    // pillar2 node offset by pillar1.height + gap
    expect(positions.get("n3")).toEqual({
      x: 0,
      y: 50 + LAYOUT_CONFIG.laneGap,
    });
  });

  it("skips empty pillar lanes without leaving a gap in the stack", () => {
    const pillarLayouts = new Map([
      [
        "pillar1",
        {
          positions: new Map<string, { x: number; y: number }>(),
          width: 0,
          height: 0,
        },
      ],
      [
        "pillar2",
        {
          positions: new Map([["n3", { x: 0, y: 0 }]]),
          width: 200,
          height: 40,
        },
      ],
    ]);
    const { lanes } = stackLanes(
      pillarLayouts,
      ["pillar1", "pillar2"],
      LAYOUT_CONFIG.laneGap,
    );
    expect(lanes).toHaveLength(1);
    expect(lanes[0]).toMatchObject({ pillar: "pillar2", yStart: 0 });
  });

  it("preserves in-lane relative positions across re-stacks: Pillar A growing does NOT move Pillar B nodes within their lane", () => {
    // Snapshot 1: Pillar 1 has just one category
    const snap1 = new Map([
      [
        "pillar1",
        {
          positions: new Map([
            ["n1", { x: 0, y: 0 }],
            ["n2", { x: 100, y: 20 }],
          ]),
          width: 300,
          height: 60,
        },
      ],
      [
        "pillar2",
        {
          positions: new Map([
            ["n3", { x: 0, y: 0 }],
            ["n4", { x: 120, y: 30 }],
          ]),
          width: 320,
          height: 70,
        },
      ],
    ]);
    // Snapshot 2: Pillar 1 taller (simulating expansion) but pillar2 unchanged
    const snap2 = new Map([
      [
        "pillar1",
        {
          positions: new Map([
            ["n1", { x: 0, y: 0 }],
            ["n2", { x: 100, y: 20 }],
            ["n5", { x: 200, y: 40 }],
          ]),
          width: 400,
          height: 140, // grew
        },
      ],
      [
        "pillar2",
        // Same object reference -> identical relative positions
        snap1.get("pillar2")!,
      ],
    ]);
    const r1 = stackLanes(snap1, ["pillar1", "pillar2"], LAYOUT_CONFIG.laneGap);
    const r2 = stackLanes(snap2, ["pillar1", "pillar2"], LAYOUT_CONFIG.laneGap);

    // Pillar 2 lane relative positions (pos - yStart of its lane) must match exactly
    const p2Start1 = r1.lanes[1].yStart;
    const p2Start2 = r2.lanes[1].yStart;
    const n3Rel1 = r1.positions.get("n3")!.y - p2Start1;
    const n4Rel1 = r1.positions.get("n4")!.y - p2Start1;
    const n3Rel2 = r2.positions.get("n3")!.y - p2Start2;
    const n4Rel2 = r2.positions.get("n4")!.y - p2Start2;
    expect(n3Rel1).toBe(n3Rel2);
    expect(n4Rel1).toBe(n4Rel2);
    // x is unchanged across re-stacks
    expect(r1.positions.get("n3")!.x).toBe(r2.positions.get("n3")!.x);
    expect(r1.positions.get("n4")!.x).toBe(r2.positions.get("n4")!.x);
  });
});

describe("computeBBox", () => {
  it("returns a permissive extent when no nodes are provided", () => {
    const extent = computeBBox([]);
    expect(extent[0][0]).toBe(-Infinity);
    expect(extent[1][1]).toBe(Infinity);
  });

  it("pads the bbox by 300px on every side by default", () => {
    const meta = makeCategoryMeta({ childCount: 0 });
    const nodes = [
      {
        id: meta.id,
        type: "category",
        position: { x: 0, y: 0 },
        data: { meta },
      },
      {
        id: "n2",
        type: "category",
        position: { x: 500, y: 200 },
        data: { meta: { ...meta, id: "n2", rawId: 2 } },
      },
    ] as unknown as Parameters<typeof computeBBox>[0];
    const [[minX, minY], [maxX, maxY]] = computeBBox(nodes);
    const catW = LAYOUT_CONFIG.categoryNode.width;
    const catH = LAYOUT_CONFIG.categoryNode.height;
    expect(minX).toBe(0 - 300);
    expect(minY).toBe(0 - 300);
    expect(maxX).toBe(500 + catW + 300);
    expect(maxY).toBe(200 + catH + 300);
  });

  it("accounts for leaf importanceScale when sizing the bbox", () => {
    const big = {
      ...makeLeafMeta(),
      id: "n10",
      rawId: 10,
      importanceScale: 1.5,
    };
    const nodes = [
      {
        id: big.id,
        type: "leaf",
        position: { x: 100, y: 100 },
        data: { meta: big },
      },
    ] as unknown as Parameters<typeof computeBBox>[0];
    const [, [maxX, maxY]] = computeBBox(nodes, 0);
    expect(maxX).toBe(100 + LAYOUT_CONFIG.leafNode.width * 1.5);
    expect(maxY).toBe(100 + LAYOUT_CONFIG.leafNode.height * 1.5);
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

describe("expandedSetForTreeNavSelect (KG-UX-09)", () => {
  it("clicking a deep leaf expands every ancestor so the leaf becomes visible", () => {
    const m = buildGraphModel(SAMPLE);
    const base = defaultExpandedSet(m); // pillars only -> leaf + category hidden
    const visibleBefore = computeVisibleNodeIds(m, base);
    expect(visibleBefore.has(nodeIdOf(3))).toBe(false);
    // Click the deep leaf n3
    const next = expandedSetForTreeNavSelect(m, base, nodeIdOf(3));
    // Ancestors (n1 pillar, n2 category) must be in the expanded set
    expect(next.has(nodeIdOf(1))).toBe(true);
    expect(next.has(nodeIdOf(2))).toBe(true);
    // The leaf itself is NOT added (leaves do not expand a subtree)
    expect(next.has(nodeIdOf(3))).toBe(false);
    // After applying the new expanded set, the leaf is visible on the canvas
    const visibleAfter = computeVisibleNodeIds(m, next);
    expect(visibleAfter.has(nodeIdOf(1))).toBe(true);
    expect(visibleAfter.has(nodeIdOf(2))).toBe(true);
    expect(visibleAfter.has(nodeIdOf(3))).toBe(true);
  });

  it("clicking a category expands its pillar ancestor AND the category itself", () => {
    const m = buildGraphModel(SAMPLE);
    const base = new Set<string>(); // start fully collapsed
    const next = expandedSetForTreeNavSelect(m, base, nodeIdOf(2));
    expect(next.has(nodeIdOf(1))).toBe(true); // pillar ancestor
    expect(next.has(nodeIdOf(2))).toBe(true); // category itself (has children)
    // Leaves under the category should be revealed now
    const visible = computeVisibleNodeIds(m, next);
    expect(visible.has(nodeIdOf(3))).toBe(true);
  });

  it("clicking a pillar adds it to the expanded set (exposes its categories)", () => {
    const m = buildGraphModel(SAMPLE);
    const base = new Set<string>();
    const next = expandedSetForTreeNavSelect(m, base, nodeIdOf(1));
    expect(next.has(nodeIdOf(1))).toBe(true);
    const visible = computeVisibleNodeIds(m, next);
    expect(visible.has(nodeIdOf(2))).toBe(true); // category becomes visible
  });

  it("preserves existing expanded entries and is idempotent", () => {
    const m = buildGraphModel(SAMPLE);
    const base = new Set([nodeIdOf(4)]); // pillar2 seeded expanded
    const first = expandedSetForTreeNavSelect(m, base, nodeIdOf(3));
    expect(first.has(nodeIdOf(4))).toBe(true);
    const second = expandedSetForTreeNavSelect(m, first, nodeIdOf(3));
    expect([...second].sort()).toEqual([...first].sort());
  });

  it("unknown ids return a copy of the base expanded set", () => {
    const m = buildGraphModel(SAMPLE);
    const base = new Set([nodeIdOf(1)]);
    const next = expandedSetForTreeNavSelect(m, base, "n999");
    expect(next).not.toBe(base); // new set (defensive copy)
    expect([...next]).toEqual([nodeIdOf(1)]);
  });
});
