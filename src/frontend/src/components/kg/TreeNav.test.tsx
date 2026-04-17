import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import {
  buildGraphModel,
  nodeIdOf,
  type KgGraphResponse,
} from "../../pages/kgGraph.helpers";
import TreeNav, {
  TREE_NAV_BAR_MAX_PX,
  TREE_NAV_COLLAPSED_WIDTH,
  TREE_NAV_WIDTH,
  flattenTreeNavRows,
  maxContentLengthOf,
} from "./TreeNav";

const SAMPLE: KgGraphResponse = {
  nodes: [
    // Pillar 1
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
      content_length: 2500,
    },
    {
      id: 3,
      kind: "framework_node",
      pillar: "pillar1",
      path: "pillar1.dp.coin",
      title: "Coin Change",
      depth: 2,
      parent_id: 2,
      content_length: 5000,
    },
    // Pillar 2 (has a childless category)
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
    {
      id: 5,
      kind: "framework_node",
      pillar: "pillar2",
      path: "pillar2.bias",
      title: "Bias-Variance",
      depth: 1,
      parent_id: 4,
      content_length: 1000,
    },
  ],
  edges: [],
};

describe("flattenTreeNavRows", () => {
  it("emits only pillars when nothing is expanded", () => {
    const m = buildGraphModel(SAMPLE);
    const rows = flattenTreeNavRows(m, new Set());
    expect(rows.map((r) => r.id)).toEqual([nodeIdOf(1), nodeIdOf(4)]);
    expect(rows[0].depth).toBe(0);
    expect(rows[0].hasChildren).toBe(true);
  });

  it("reveals category rows when the pillar is expanded", () => {
    const m = buildGraphModel(SAMPLE);
    const rows = flattenTreeNavRows(m, new Set([nodeIdOf(1)]));
    const ids = rows.map((r) => r.id);
    // pillar1 -> category2 visible; pillar2 NOT expanded, so its child hidden
    expect(ids).toEqual([nodeIdOf(1), nodeIdOf(2), nodeIdOf(4)]);
    const cat = rows.find((r) => r.id === nodeIdOf(2))!;
    expect(cat.depth).toBe(1);
    expect(cat.hasChildren).toBe(true);
  });

  it("reveals leaf rows when both pillar and category are expanded", () => {
    const m = buildGraphModel(SAMPLE);
    const rows = flattenTreeNavRows(
      m,
      new Set([nodeIdOf(1), nodeIdOf(2)]),
    );
    const ids = rows.map((r) => r.id);
    expect(ids).toEqual([
      nodeIdOf(1),
      nodeIdOf(2),
      nodeIdOf(3),
      nodeIdOf(4),
    ]);
    const leaf = rows.find((r) => r.id === nodeIdOf(3))!;
    expect(leaf.depth).toBe(2);
    expect(leaf.hasChildren).toBe(false);
  });

  it("collapsing a pillar hides its subtree on the next walk", () => {
    const m = buildGraphModel(SAMPLE);
    const expanded = new Set([nodeIdOf(1), nodeIdOf(2)]);
    // Now collapse pillar1 -> neither category nor leaf should appear
    expanded.delete(nodeIdOf(1));
    const rows = flattenTreeNavRows(m, expanded);
    expect(rows.map((r) => r.id)).toEqual([nodeIdOf(1), nodeIdOf(4)]);
  });
});

describe("maxContentLengthOf", () => {
  it("returns the largest contentLength across the model", () => {
    const m = buildGraphModel(SAMPLE);
    expect(maxContentLengthOf(m)).toBe(5000);
  });

  it("returns 1 when every node has zero content (avoids divide-by-zero)", () => {
    const zeros: KgGraphResponse = {
      nodes: [
        {
          id: 1,
          kind: "framework_node",
          pillar: "pillar1",
          path: "p",
          title: "P",
          depth: 0,
          parent_id: null,
          content_length: 0,
        },
      ],
      edges: [],
    };
    expect(maxContentLengthOf(buildGraphModel(zeros))).toBe(1);
  });
});

describe("TreeNav rendering", () => {
  it("renders pillars only by default; hides deeper levels", () => {
    const m = buildGraphModel(SAMPLE);
    const html = renderToStaticMarkup(<TreeNav model={m} />);
    expect(html).toContain('data-testid="kg-tree-nav"');
    expect(html).toContain('data-collapsed="false"');
    expect(html).toContain(`data-testid="kg-tree-row-${nodeIdOf(1)}"`);
    expect(html).toContain(`data-testid="kg-tree-row-${nodeIdOf(4)}"`);
    // Categories + leaves NOT present by default
    expect(html).not.toContain(`data-testid="kg-tree-row-${nodeIdOf(2)}"`);
    expect(html).not.toContain(`data-testid="kg-tree-row-${nodeIdOf(3)}"`);
    // Fixed panel width
    expect(html).toContain(`width:${TREE_NAV_WIDTH}px`);
  });

  it("renders category rows when pillar is seeded as expanded", () => {
    const m = buildGraphModel(SAMPLE);
    const html = renderToStaticMarkup(
      <TreeNav model={m} initialExpanded={new Set([nodeIdOf(1)])} />,
    );
    expect(html).toContain(`data-testid="kg-tree-row-${nodeIdOf(2)}"`);
    // Leaf still hidden (category 2 not expanded)
    expect(html).not.toContain(`data-testid="kg-tree-row-${nodeIdOf(3)}"`);
    // Category row carries depth=1
    expect(html).toMatch(
      new RegExp(
        `data-testid="kg-tree-row-${nodeIdOf(2)}"[^>]*data-depth="1"`,
      ),
    );
  });

  it("renders leaf rows (no chevron, no badge) when the category is expanded", () => {
    const m = buildGraphModel(SAMPLE);
    const html = renderToStaticMarkup(
      <TreeNav
        model={m}
        initialExpanded={new Set([nodeIdOf(1), nodeIdOf(2)])}
      />,
    );
    expect(html).toContain(`data-testid="kg-tree-row-${nodeIdOf(3)}"`);
    // Leaf has no chevron, no child-count badge
    expect(html).not.toContain(`data-testid="kg-tree-chevron-${nodeIdOf(3)}"`);
    expect(html).not.toContain(`data-testid="kg-tree-badge-${nodeIdOf(3)}"`);
    // Pillar/category DO have chevron + badge
    expect(html).toContain(`data-testid="kg-tree-chevron-${nodeIdOf(1)}"`);
    expect(html).toContain(`data-testid="kg-tree-badge-${nodeIdOf(1)}"`);
  });

  it("mini-bar width is proportional to contentLength/max across the model", () => {
    const m = buildGraphModel(SAMPLE);
    const html = renderToStaticMarkup(
      <TreeNav
        model={m}
        initialExpanded={new Set([nodeIdOf(1), nodeIdOf(2)])}
      />,
    );
    // Node 3 has contentLength = 5000 (the max) -> fill should be BAR_MAX_PX
    const leafFill = html.match(
      new RegExp(
        `data-testid="kg-tree-bar-fill-${nodeIdOf(3)}"[^>]*style="([^"]*)"`,
      ),
    );
    expect(leafFill).not.toBeNull();
    expect(leafFill![1]).toContain(`width:${TREE_NAV_BAR_MAX_PX}px`);
    // Node 2 has 2500 (half the max) -> fill should be half the max width
    const catFill = html.match(
      new RegExp(
        `data-testid="kg-tree-bar-fill-${nodeIdOf(2)}"[^>]*style="([^"]*)"`,
      ),
    );
    expect(catFill).not.toBeNull();
    const halfPx = Math.round(0.5 * TREE_NAV_BAR_MAX_PX);
    expect(catFill![1]).toContain(`width:${halfPx}px`);
    // Pillar 1 has contentLength = 0 -> fill is 0px
    const pillarFill = html.match(
      new RegExp(
        `data-testid="kg-tree-bar-fill-${nodeIdOf(1)}"[^>]*style="([^"]*)"`,
      ),
    );
    expect(pillarFill).not.toBeNull();
    expect(pillarFill![1]).toContain("width:0px");
  });

  it("renders collapsed strip with color dots only (no row testids)", () => {
    const m = buildGraphModel(SAMPLE);
    const html = renderToStaticMarkup(
      <TreeNav model={m} initialCollapsed />,
    );
    expect(html).toContain('data-collapsed="true"');
    expect(html).toContain(`width:${TREE_NAV_COLLAPSED_WIDTH}px`);
    expect(html).toContain('data-testid="kg-tree-nav-toggle"');
    expect(html).toContain('aria-label="Expand tree nav"');
    // No row markup in collapsed mode
    expect(html).not.toContain('data-testid="kg-tree-row-');
    // Pillar labels accessible via title/aria-label on color dot
    expect(html).toContain('aria-label="Coding"');
    expect(html).toContain('aria-label="ML Theory"');
  });

  it("includes a pillar color dot, child-count badge, and bar track on every pillar row", () => {
    const m = buildGraphModel(SAMPLE);
    const html = renderToStaticMarkup(<TreeNav model={m} />);
    // pillar1 border color from kgStyles -> #475569
    expect(html).toContain("#475569");
    // child-count badge shows 1 (pillar1 has 1 category child)
    expect(html).toMatch(
      new RegExp(
        `data-testid="kg-tree-badge-${nodeIdOf(1)}"[^>]*>1</span>`,
      ),
    );
    // Bar track testid present on pillar1
    expect(html).toContain(`data-testid="kg-tree-bar-${nodeIdOf(1)}"`);
  });

  it("marks the selected row via data-selected and aria-selected", () => {
    const m = buildGraphModel(SAMPLE);
    const html = renderToStaticMarkup(
      <TreeNav
        model={m}
        initialExpanded={new Set([nodeIdOf(1)])}
        selectedId={nodeIdOf(2)}
      />,
    );
    // Row n2 is selected
    expect(html).toMatch(
      new RegExp(
        `data-testid="kg-tree-row-${nodeIdOf(2)}"[^>]*data-selected="true"`,
      ),
    );
    // Row n1 is NOT selected
    expect(html).toMatch(
      new RegExp(
        `data-testid="kg-tree-row-${nodeIdOf(1)}"[^>]*data-selected="false"`,
      ),
    );
    // aria-selected only set when selected
    expect(html).toContain('aria-selected="true"');
  });

  it("leaves data-selected='false' on every row when selectedId is null", () => {
    const m = buildGraphModel(SAMPLE);
    const html = renderToStaticMarkup(<TreeNav model={m} selectedId={null} />);
    // Every row is data-selected="false"
    for (const id of [nodeIdOf(1), nodeIdOf(4)]) {
      expect(html).toMatch(
        new RegExp(
          `data-testid="kg-tree-row-${id}"[^>]*data-selected="false"`,
        ),
      );
    }
    expect(html).not.toContain('aria-selected="true"');
  });
});
