import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import CheatSheetCard from "./CheatSheetCard";
import type { SystemDesignCheatSheet } from "../types/system-design";

function render(item: SystemDesignCheatSheet, category: string): string {
  return renderToStaticMarkup(
    <MemoryRouter>
      <CheatSheetCard item={item} category={category} />
    </MemoryRouter>,
  );
}

const baseItem: SystemDesignCheatSheet = {
  id: 1,
  slug: "interview-url-shortener",
  title: "URL Shortener",
  subtitle: null,
  diagram_filename: null,
  display_order: 100,
  cheat_sheet: "## Key Points\n\n- Hashing strategy\n\nLatency $O(1)$ lookup",
};

describe("CheatSheetCard", () => {
  it("renders title, category badge, deep-link anchor, and full-design link", () => {
    const html = render(baseItem, "eBay");
    // section anchor id == slug (for TOC + ?tab=cheatsheet#<slug> deep links)
    expect(html).toContain('id="interview-url-shortener"');
    expect(html).toContain("URL Shortener");
    expect(html).toContain("eBay"); // category badge
    expect(html).toContain('href="/system-design/interview-url-shortener"');
    expect(html).toContain("Full design");
  });

  it("renders the cheat_sheet markdown (headings + KaTeX)", () => {
    const html = render(baseItem, "eBay");
    expect(html).toContain("Key Points"); // markdown H2 rendered
    expect(html).toContain("Hashing strategy");
    expect(html).toContain("katex"); // KaTeX math compiled
  });

  it("shows a graceful empty state when cheat_sheet is null", () => {
    const html = render({ ...baseItem, cheat_sheet: null }, "Generic");
    expect(html).toContain("No cheat sheet yet");
    expect(html).not.toContain("Key Points");
  });
});
