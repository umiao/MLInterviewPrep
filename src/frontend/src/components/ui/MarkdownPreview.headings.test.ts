import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { createElement } from "react";
import MarkdownPreview from "./MarkdownPreview";
import { extractHeadings, headingPlainText, scanHeadings } from "./markdownHeadings";
import { slugify } from "../../utils/slugify";

/**
 * Regression guard for the L112 react-hooks/refs refactor.
 *
 * The load-bearing invariant (reviewer point #1): the TOC sidebar id MUST
 * equal the on-DOM anchor id, or clicking the TOC scrolls nowhere. Rather
 * than enumerate inline forms and hand-reason about childrenToText, this
 * does the GOLD-STANDARD double-run: render the real <MarkdownPreview>
 * through the same react-markdown + remark-math + KaTeX pipeline the app
 * uses, scrape the actual <h1-3 id="..."> in document order, and assert
 * it equals extractHeadings() exactly. If they ever diverge (math,
 * inline-code, mixed inline, duplicates, whitespace) this fails.
 */
function renderedHeadingIds(md: string): string[] {
  const html = renderToStaticMarkup(createElement(MarkdownPreview, { markdown: md }));
  const ids: string[] = [];
  const re = /<h[1-3]\b[^>]*?\sid="([^"]*)"/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html)) !== null) ids.push(m[1]);
  return ids;
}

describe("extractHeadings <-> rendered anchor id parity (real renderer)", () => {
  it("matches for plain / CJK / bold / inline-code / mixed-inline / whitespace", () => {
    const md = [
      "# Array / String",
      "## Core Concepts",
      "### Use `foo` function", // inline code
      "## **Recap**: [Two Sum](lc://1) walkthrough", // mixed link + bold
      "## **a** **b**", // whitespace between adjacent inline
      "## 数组 Array", // CJK
    ].join("\n\n");
    const fromSource = extractHeadings(md).map((h) => h.id);
    expect(renderedHeadingIds(md)).toEqual(fromSource);
    // spot-check the load-bearing mixed case resolves to readable text
    expect(fromSource[3]).toBe(slugify("Recap: Two Sum walkthrough"));
  });

  it("matches for real math headings (the 29-heading regression case)", () => {
    // Verbatim shapes from the live DB (nodes 141 / 223).
    const md = [
      "## Why Scale by $$\\sqrt{d_k}$$?",
      "## 2. 复杂度推导：$O(n^2 d)$",
      "## 如果没有 softmax，$O(n)$ 是免费的",
    ].join("\n\n");
    // Not asserting the slug is pretty -- asserting sidebar === anchor.
    expect(renderedHeadingIds(md)).toEqual(extractHeadings(md).map((h) => h.id));
  });

  it("duplicate headings get synchronized GitHub-style -1/-2 on BOTH sides", () => {
    const md = ["## Overview", "x", "## Overview", "y", "## Overview"].join("\n\n");
    const ids = extractHeadings(md).map((h) => h.id);
    expect(ids).toEqual(["overview", "overview-1", "overview-2"]);
    expect(renderedHeadingIds(md)).toEqual(ids); // anchors match the dedup
  });

  it("skips fenced code and levels > 3 (old-collector parity)", () => {
    const md = [
      "# Real H1",
      "```py\n# not a heading\n```",
      "#### Too Deep",
      "### Real H3",
    ].join("\n\n");
    expect(extractHeadings(md)).toEqual([
      { level: 1, text: "Real H1", id: "real-h1" },
      { level: 3, text: "Real H3", id: "real-h3" },
    ]);
  });

  it("headingPlainText: link->text, image->'', emphasis stripped, ws collapsed", () => {
    expect(headingPlainText("![alt](x.png) Caption")).toBe("Caption");
    expect(headingPlainText("**Recap**: [Two Sum](lc://1) walkthrough")).toBe(
      "Recap: Two Sum walkthrough",
    );
    expect(headingPlainText("`a`  `b`")).toBe("a b");
  });

  it("scanHeadings is pure/idempotent (no render-phase state -- StrictMode-safe)", () => {
    // The original bug dropped headings under StrictMode double-render
    // because collection mutated a ref during render. There is no
    // jsdom/RTL stack here to mount <StrictMode> + assert effect-once,
    // but the structural guarantee is that scanHeadings is a pure fn:
    // identical output across repeated calls, so a double render cannot
    // produce a partial/observable-different list.
    const md = "# A\n\n## B\n\n### C";
    const a = scanHeadings(md);
    const b = scanHeadings(md);
    expect(a).toEqual(b);
    expect(a.map((h) => h.id)).toEqual(["a", "b", "c"]);
  });
});
