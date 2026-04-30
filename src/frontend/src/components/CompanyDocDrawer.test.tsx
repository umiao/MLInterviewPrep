import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import {
  CompanyDocDrawerBody,
  companyDocDrawerTitle,
  formatCompanyDocFetchWarning,
} from "./CompanyDocDrawer";
import type { CompanyDocument } from "../types/company";

const SAMPLE_DOC: CompanyDocument = {
  id: 87,
  company_id: 1,
  title: "Meta AI-Native Hub",
  content: "# Hub\n\nWelcome to the hub.",
  source_type: "manual",
  doc_kind: "hub_doc",
  is_golden: true,
  golden_at: null,
  created_at: null,
  updated_at: null,
};

// `CompanyDocDrawerBody` is pure (no SlideOverPanel/portal), so we can render
// it via renderToStaticMarkup without a DOM. SlideOverPanel uses
// createPortal(document.body, ...) which the node-only vitest env cannot
// satisfy -- the wrapper layer is exercised by the structural-source check
// below.
describe("CompanyDocDrawerBody", () => {
  it("renders title (via helper) + content when fetch returns 200 (status=success)", () => {
    expect(companyDocDrawerTitle("success", 87, SAMPLE_DOC)).toBe(
      "Meta AI-Native Hub",
    );
    const html = renderToStaticMarkup(
      <CompanyDocDrawerBody docId={87} status="success" doc={SAMPLE_DOC} />,
    );
    // Body is the markdown content -- look for the rendered heading.
    expect(html).toContain("Welcome to the hub.");
    // is_golden surfaces a Golden badge.
    expect(html).toContain("Golden");
    // doc_kind surfaces a kind badge.
    expect(html).toContain("hub_doc");
  });

  it("renders explicit 'Document not found' inline (not blank) when fetch returns 404", () => {
    // Per design review point #1: 404 must be visible INSIDE the drawer,
    // not a toast and not a blank panel. The id must surface so the user
    // can grep their seed for it.
    expect(companyDocDrawerTitle("not_found", 9999)).toBe(
      "Document not found",
    );
    const html = renderToStaticMarkup(
      <CompanyDocDrawerBody docId={9999} status="not_found" />,
    );
    expect(html).toContain("Document not found");
    expect(html).toContain("9999");
  });

  it("renders 'Failed to load document' when fetch returns 5xx", () => {
    expect(companyDocDrawerTitle("error", 87)).toBe(
      "Failed to load document",
    );
    const html = renderToStaticMarkup(
      <CompanyDocDrawerBody
        docId={87}
        status="error"
        errorMessage="Internal Server Error"
      />,
    );
    expect(html).toContain("Failed to load document");
    expect(html).toContain("Internal Server Error");
  });

  it("returns 'Loading document...' for the loading status", () => {
    expect(companyDocDrawerTitle("loading", 87)).toBe(
      "Loading document (id=87)...",
    );
    const html = renderToStaticMarkup(
      <CompanyDocDrawerBody docId={87} status="loading" />,
    );
    expect(html).toContain("Loading document...");
  });

  it("returns empty title when docId is null (closed drawer)", () => {
    // Closed-drawer guard: title is empty so SlideOverPanel never paints
    // a header for a null id.
    expect(companyDocDrawerTitle("loading", null)).toBe("");
  });
});

describe("formatCompanyDocFetchWarning", () => {
  it("formats with the [CompanyDocDrawer] prefix and cd://N for grep-ability", () => {
    // Per design review point #2: log shape is the contract -- ops can grep
    // browser console for `[CompanyDocDrawer] cd://` to detect drawer
    // regressions. Lock the exact format.
    const out = formatCompanyDocFetchWarning(87, "Internal Server Error");
    expect(out).toContain("[CompanyDocDrawer]");
    expect(out).toContain("cd://87");
    expect(out).toContain("Internal Server Error");
    expect(out).toBe(
      "[CompanyDocDrawer] cd://87 fetch failed: Internal Server Error",
    );
  });
});

describe("CompanyDocDrawer wrapper observability + nesting contract (T-P0-673)", () => {
  // Effect-based assertions are awkward in this codebase's node-only vitest
  // env (no jsdom/testing-library). We lock the wrapper's
  // `console.warn(formatCompanyDocFetchWarning(...))` call as a structural
  // check on the source. This matches the BehavioralQuestions.test.tsx
  // pattern (T-P0-626) used elsewhere for hard-to-render assertions.
  it("wrapper source calls console.warn with formatCompanyDocFetchWarning on fetch error", async () => {
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "CompanyDocDrawer.tsx"),
      "utf-8",
    );
    expect(file).toMatch(
      /console\.warn\(\s*formatCompanyDocFetchWarning\(/,
    );
    // Guarded by isError so we do not log on every render.
    expect(file).toMatch(/if \(isError/);
  });

  it("wrapper passes onCdLinkClick to inner MarkdownPreview that REPLACES activeDocId (no stack)", async () => {
    // Design review point #3: nested cd:// must not stack drawers; it must
    // swap the active doc in place. Lock that the wrapper wires
    // setActiveDocId to onCdLinkClick.
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "CompanyDocDrawer.tsx"),
      "utf-8",
    );
    expect(file).toMatch(
      /onCdLinkClick=\{\(nextId\)\s*=>\s*setActiveDocId\(nextId\)\}/,
    );
    // TODO marker present so the YAGNI decision is documented in source.
    expect(file).toContain("if multi-level navigation");
  });

  it("wrapper detects 404 via ApiRequestError.status to map to 'not_found'", async () => {
    // The status-mapping logic is the contract that produces the explicit
    // 404 UI rather than a generic error. Lock that the wrapper inspects
    // ApiRequestError.status.
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "CompanyDocDrawer.tsx"),
      "utf-8",
    );
    expect(file).toContain("ApiRequestError");
    expect(file).toMatch(/errStatus\s*===\s*404/);
  });
});
