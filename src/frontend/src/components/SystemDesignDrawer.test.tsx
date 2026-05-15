import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import {
  SystemDesignDrawerBody,
  systemDesignDrawerTitle,
  formatSystemDesignFetchWarning,
} from "./SystemDesignDrawer";
import type { SystemDesign } from "../types/system-design";
import { SECTION_LABELS } from "../types/system-design";

const SAMPLE_DESIGN: SystemDesign = {
  id: 1,
  slug: "pinterest-ad-ctr",
  title: "Pinterest ML System Design: Ad CTR Prediction",
  subtitle: "Two-tower retrieval + DCN ranker",
  diagram_filename: "pinterest-ad-ctr.png",
  display_order: 1,
  overview: "## Overview\n\nFoo bar overview.",
  architecture: "## Architecture\n\nFoo bar architecture.",
  dataflow: "## Data Flow\n\nFoo bar dataflow.",
  formulas: "## Formulas\n\nFoo bar formulas.",
  production_constraints: "## Constraints\n\nFoo bar constraints.",
  tradeoffs: "## Tradeoffs\n\nFoo bar tradeoffs.",
  defense: "## Defense\n\nFoo bar defense.",
  verbal_outline: "## Verbal Outline\n\nFoo bar outline.",
  cheat_sheet: "## Cheat Sheet\n\nFoo bar cheat sheet.",
  created_at: "2026-05-04T00:00:00",
  updated_at: "2026-05-04T00:00:00",
};

const CHEAT_SHEET_ONLY_DESIGN: SystemDesign = {
  ...SAMPLE_DESIGN,
  overview: null,
  architecture: null,
  dataflow: null,
  formulas: null,
  production_constraints: null,
  tradeoffs: null,
  defense: null,
  verbal_outline: null,
  cheat_sheet: "## Cheat Sheet\n\nOnly the cheat sheet is filled in.",
};

const NO_DIAGRAM_DESIGN: SystemDesign = {
  ...SAMPLE_DESIGN,
  diagram_filename: null,
};

// `SystemDesignDrawerBody` is pure (no SlideOverPanel/portal), so we can
// render it via renderToStaticMarkup without a DOM. SlideOverPanel uses
// createPortal which the node-only vitest env cannot satisfy -- the wrapper
// layer is exercised by the structural-source check below.
describe("SystemDesignDrawerBody", () => {
  it("renders title (via helper) + 9 sections in order when fetch returns 200", () => {
    expect(systemDesignDrawerTitle("success", "pinterest-ad-ctr", SAMPLE_DESIGN)).toBe(
      "Pinterest ML System Design: Ad CTR Prediction",
    );
    const html = renderToStaticMarkup(
      <SystemDesignDrawerBody
        slug="pinterest-ad-ctr"
        status="success"
        design={SAMPLE_DESIGN}
      />,
    );
    // All 9 section labels appear in body.
    for (const label of Object.values(SECTION_LABELS)) {
      expect(html).toContain(label);
    }
    // verbal_outline is promoted to the TOP (T-P0-891): its label appears
    // before every other section label, including overview.
    const verbalIdx = html.indexOf(SECTION_LABELS.verbal_outline);
    for (const key of [
      "overview",
      "architecture",
      "dataflow",
      "formulas",
      "production_constraints",
      "tradeoffs",
      "defense",
      "cheat_sheet",
    ] as const) {
      expect(verbalIdx).toBeLessThan(html.indexOf(SECTION_LABELS[key]));
    }
    // The other 8 sections retain their relative order: the rendered label
    // positions for the full promoted order are strictly increasing.
    const promotedOrder = [
      "verbal_outline",
      "overview",
      "architecture",
      "dataflow",
      "formulas",
      "production_constraints",
      "tradeoffs",
      "defense",
      "cheat_sheet",
    ] as const;
    const positions = promotedOrder.map((key) =>
      html.indexOf(SECTION_LABELS[key]),
    );
    for (let i = 1; i < positions.length; i++) {
      expect(positions[i - 1]).toBeLessThan(positions[i]);
    }
    // Section order: overview label appears before cheat_sheet label.
    expect(html.indexOf(SECTION_LABELS.overview)).toBeLessThan(
      html.indexOf(SECTION_LABELS.cheat_sheet),
    );
    // Architecture label appears before dataflow label.
    expect(html.indexOf(SECTION_LABELS.architecture)).toBeLessThan(
      html.indexOf(SECTION_LABELS.dataflow),
    );
    // Markdown content is rendered.
    expect(html).toContain("Foo bar overview.");
    expect(html).toContain("Foo bar cheat sheet.");
  });

  it("renders ImageLightbox in architecture section when diagram_filename is present", () => {
    const html = renderToStaticMarkup(
      <SystemDesignDrawerBody
        slug="pinterest-ad-ctr"
        status="success"
        design={SAMPLE_DESIGN}
      />,
    );
    expect(html).toContain("/static/system-designs/pinterest-ad-ctr.png");
  });

  it("does NOT render any /static/system-designs/ image when diagram_filename is null", () => {
    const html = renderToStaticMarkup(
      <SystemDesignDrawerBody
        slug="pinterest-ad-ctr"
        status="success"
        design={NO_DIAGRAM_DESIGN}
      />,
    );
    expect(html).not.toContain("/static/system-designs/");
    // Architecture section header still renders.
    expect(html).toContain(SECTION_LABELS.architecture);
  });

  it("renders placeholder for null sections, content for non-null sections", () => {
    const html = renderToStaticMarkup(
      <SystemDesignDrawerBody
        slug="pinterest-ad-ctr"
        status="success"
        design={CHEAT_SHEET_ONLY_DESIGN}
      />,
    );
    // 8 missing sections each get the placeholder; cheat_sheet renders content.
    expect(html).toContain("尚未填写");
    expect(html).toContain("Only the cheat sheet is filled in.");
    // All 9 labels still present (section header always renders).
    for (const label of Object.values(SECTION_LABELS)) {
      expect(html).toContain(label);
    }
  });

  it("renders explicit 'module not found' inline (not blank) when fetch returns 404", () => {
    expect(systemDesignDrawerTitle("not_found", "missing-slug")).toBe(
      "Module not found",
    );
    const html = renderToStaticMarkup(
      <SystemDesignDrawerBody slug="missing-slug" status="not_found" />,
    );
    expect(html).toContain("not found");
    expect(html).toContain("missing-slug");
  });

  it("renders 'Failed to load' when fetch returns 5xx", () => {
    expect(systemDesignDrawerTitle("error", "pinterest-ad-ctr")).toBe(
      "Failed to load module",
    );
    const html = renderToStaticMarkup(
      <SystemDesignDrawerBody
        slug="pinterest-ad-ctr"
        status="error"
        errorMessage="Internal Server Error"
      />,
    );
    expect(html).toContain("Failed to load");
    expect(html).toContain("Internal Server Error");
  });

  it("returns 'Loading system design...' for the loading status", () => {
    expect(systemDesignDrawerTitle("loading", "pinterest-ad-ctr")).toBe(
      "Loading system design (slug=pinterest-ad-ctr)...",
    );
    const html = renderToStaticMarkup(
      <SystemDesignDrawerBody slug="pinterest-ad-ctr" status="loading" />,
    );
    expect(html).toContain("Loading system design...");
  });

  it("returns empty title when slug is null (closed drawer)", () => {
    expect(systemDesignDrawerTitle("loading", null)).toBe("");
  });
});

describe("formatSystemDesignFetchWarning", () => {
  it("formats with the [SystemDesignDrawer] prefix and sd://<slug> for grep-ability", () => {
    // Lock log shape -- ops greps console for `[SystemDesignDrawer] sd://` to
    // detect drawer fetch regressions.
    const out = formatSystemDesignFetchWarning(
      "pinterest-ad-ctr",
      "Internal Server Error",
    );
    expect(out).toContain("[SystemDesignDrawer]");
    expect(out).toContain("sd://pinterest-ad-ctr");
    expect(out).toContain("Internal Server Error");
    expect(out).toBe(
      "[SystemDesignDrawer] sd://pinterest-ad-ctr fetch failed: Internal Server Error",
    );
  });
});

describe("SystemDesignDrawer wrapper observability + nesting contract", () => {
  // Effect-based assertions are awkward in this codebase's node-only vitest
  // env (no jsdom/testing-library). We lock the wrapper's
  // `console.warn(formatSystemDesignFetchWarning(...))` call as a structural
  // check on the source -- mirrors CompanyDocDrawer.test.tsx pattern.
  it("wrapper source calls console.warn with formatSystemDesignFetchWarning on fetch error", async () => {
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "SystemDesignDrawer.tsx"),
      "utf-8",
    );
    expect(file).toMatch(
      /console\.warn\(\s*formatSystemDesignFetchWarning\(/,
    );
    // Guarded by isError so we do not log on every render.
    expect(file).toMatch(/if \(isError/);
  });

  it("wrapper passes onSdLinkClick to inner MarkdownPreview that REPLACES activeSlug (no stack)", async () => {
    // Recursive sd:// must not stack drawers; it must swap the active slug
    // in place. Lock that the wrapper wires setActiveSlug to onSdLinkClick.
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "SystemDesignDrawer.tsx"),
      "utf-8",
    );
    expect(file).toMatch(
      /onSdLinkClick=\{\(nextSlug\)\s*=>\s*setActiveSlug\(nextSlug\)\}/,
    );
    expect(file).toContain("if multi-level navigation");
  });

  it("wrapper detects 404 via ApiRequestError.status to map to 'not_found'", async () => {
    // Status-mapping logic produces the explicit 404 UI rather than a
    // generic error -- lock that the wrapper inspects ApiRequestError.status.
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "SystemDesignDrawer.tsx"),
      "utf-8",
    );
    expect(file).toContain("ApiRequestError");
    expect(file).toMatch(/errStatus\s*===\s*404/);
  });
});
