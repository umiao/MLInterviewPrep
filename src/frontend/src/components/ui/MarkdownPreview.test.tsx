import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import MarkdownPreview from "./MarkdownPreview";

function render(md: string): string {
  return renderToStaticMarkup(<MarkdownPreview markdown={md} />);
}

describe("MarkdownPreview blockquote callouts", () => {
  it("renders > **GOOD**: as the green callout", () => {
    const html = render("> **GOOD**: ship the right thing");
    expect(html).toContain("callout-good");
    expect(html).toContain('data-callout="good"');
    expect(html).toContain("ship the right thing");
  });

  it("renders > **BAD**: as the red callout", () => {
    const html = render("> **BAD**: anti-pattern example");
    expect(html).toContain("callout-bad");
    expect(html).toContain('data-callout="bad"');
  });

  it("renders > **NOTE**: as the blue callout", () => {
    const html = render("> **NOTE**: caveat for reviewers");
    expect(html).toContain("callout-note");
    expect(html).toContain('data-callout="note"');
  });

  it("falls back to default blockquote (no callout class) for unmarked quotes", () => {
    const html = render("> just a plain blockquote");
    expect(html).not.toContain("callout-good");
    expect(html).not.toContain("callout-bad");
    expect(html).not.toContain("callout-note");
    expect(html).not.toContain("data-callout");
    expect(html).toContain("<blockquote");
  });

  it("does not match emoji-prefixed variants (rejected by T-P0-514 contract)", () => {
    const html = render("> \u2705 GOOD: anti-pattern emoji form");
    expect(html).not.toContain("callout-good");
    expect(html).not.toContain("data-callout");
  });

  it("does not match a non-leading prefix inside the blockquote", () => {
    const html = render("> Lorem ipsum **GOOD**: not a callout");
    expect(html).not.toContain("data-callout");
  });
});

describe("MarkdownPreview tables (GFM with alignment)", () => {
  it("renders a GFM table with header and body cells", () => {
    const md = [
      "| Col A | Col B |",
      "| :---: | ----: |",
      "| a1 | b1 |",
      "| a2 | b2 |",
    ].join("\n");
    const html = render(md);
    expect(html).toContain("<table");
    expect(html).toContain("Col A");
    expect(html).toContain("Col B");
    expect(html).toContain("a1");
    expect(html).toContain("b2");
  });

  it("preserves :---: column alignment via inline style on <th>/<td>", () => {
    // remark-gfm encodes alignment as inline style="text-align:..." on each
    // cell, which must beat the prose-th:text-left utility class. Lock the
    // contract so future class refactors do not silently flatten alignment.
    const md = [
      "| Center | Right |",
      "| :---: | ----: |",
      "| c1 | r1 |",
    ].join("\n");
    const html = render(md);
    expect(html).toMatch(/<th[^>]*style="[^"]*text-align:\s*center/);
    expect(html).toMatch(/<th[^>]*style="[^"]*text-align:\s*right/);
    expect(html).toMatch(/<td[^>]*style="[^"]*text-align:\s*center/);
    expect(html).toMatch(/<td[^>]*style="[^"]*text-align:\s*right/);
  });
});

describe("MarkdownPreview inline code and lists", () => {
  it("renders inline code as a <code> element", () => {
    const html = render("Use `useEffect` for side effects.");
    expect(html).toContain("<code");
    expect(html).toContain("useEffect");
  });

  it("renders nested lists three levels deep", () => {
    const md = [
      "- l1",
      "  - l2",
      "    - l3",
    ].join("\n");
    const html = render(md);
    // count <ul tags: outer + level-2 + level-3
    const ulCount = (html.match(/<ul/g) ?? []).length;
    expect(ulCount).toBeGreaterThanOrEqual(3);
    expect(html).toContain("l1");
    expect(html).toContain("l2");
    expect(html).toContain("l3");
  });
});
