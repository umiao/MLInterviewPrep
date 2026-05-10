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

describe("MarkdownPreview link handling", () => {
  it("renders in-page anchor links (#slug) as a button, not a new-tab anchor", () => {
    // Regression: Uber LC index doc has [Tree...](#tree-...) TOC links.
    // Before the fix these rendered as <a target="_blank">, opening a new
    // tab instead of scrolling to the heading. Now they must be buttons
    // (clicked → scrollIntoView, no new tab).
    const html = render("[Tree section](#tree-section)");
    expect(html).toContain("<button");
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*Tree section/);
    expect(html).toContain("Tree section");
  });

  it("still renders external links as new-tab anchors", () => {
    const html = render("[Anthropic](https://www.anthropic.com)");
    expect(html).toMatch(/<a[^>]*href="https:\/\/www\.anthropic\.com"/);
    expect(html).toMatch(/<a[^>]*target="_blank"/);
  });

  it("does not treat bare '#' as an in-page anchor", () => {
    // Edge case: href="#" alone (no slug) should fall through to default
    // anchor rendering, not produce an unusable button.
    const html = render("[empty](#)");
    expect(html).toMatch(/<a[^>]*href="#"/);
  });

  it("renders db://N#anchor as a button (drawer opener, anchor reserved for future scroll)", () => {
    // T-P0-632: deep-link format db://N#anchor must still match the dbMatch
    // regex so click triggers onDbLinkClick(N) and opens the drawer.
    // Without the optional suffix in the regex, this would fall through to a
    // broken <a target="_blank" href="db://84#anchor"> new-tab navigation.
    const handler = (id: number) => id;
    const html = renderToStaticMarkup(
      <MarkdownPreview
        markdown="[geo](db://84#geometric-median)"
        onDbLinkClick={handler}
      />
    );
    expect(html).toContain("<button");
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*db:\/\//);
    expect(html).toContain("geo");
  });

  it("still renders bare db://N as a drawer-opener button", () => {
    // Regression-guard the un-anchored case after relaxing the regex.
    const handler = (id: number) => id;
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown="[doc](db://84)" onDbLinkClick={handler} />
    );
    expect(html).toContain("<button");
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*db:\/\//);
  });

  it("renders cd://N as button when onCdLinkClick provided", () => {
    // T-P0-672: cd:// is the company-document drawer scheme, peer to db://.
    const handler = (id: number) => id;
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown="[hub](cd://87)" onCdLinkClick={handler} />
    );
    expect(html).toContain("<button");
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*cd:\/\//);
    expect(html).toContain("hub");
  });

  it("cd://N falls through to anchor when onCdLinkClick not provided", () => {
    // No handler -> default <a target="_blank"> rendering. This matches the
    // lc:// / db:// behavior so callers who haven't opted in still see a link.
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown="[hub](cd://87)" />
    );
    expect(html).toMatch(/<a[^>]*href="cd:\/\/87"/);
    expect(html).toMatch(/<a[^>]*target="_blank"/);
  });

  it("renders sd://<slug> as button when onSdLinkClick provided", () => {
    // T-P0-731: sd:// is the system-design drawer scheme, peer to cd://.
    // Slug is lowercase kebab-case per system_designs table.
    const handler = (slug: string) => slug;
    const html = renderToStaticMarkup(
      <MarkdownPreview
        markdown="[ctr](sd://pinterest-ad-ctr)"
        onSdLinkClick={handler}
      />
    );
    expect(html).toContain("<button");
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*sd:\/\//);
    expect(html).toContain("ctr");
  });

  it("renders sd://<slug>#anchor as button (anchor stripped at link layer)", () => {
    // Mirror cd:// / db:// optional anchor behavior — drawer opens, anchor
    // ignored at link layer (future task may scroll inside drawer).
    const handler = (slug: string) => slug;
    const html = renderToStaticMarkup(
      <MarkdownPreview
        markdown="[ctr](sd://pinterest-ad-ctr#features)"
        onSdLinkClick={handler}
      />
    );
    expect(html).toContain("<button");
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*sd:\/\//);
  });

  it("sd:// falls through to anchor when onSdLinkClick not provided", () => {
    // Backward-compat: surfaces that have not opted in still see a link.
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown="[ctr](sd://pinterest-ad-ctr)" />
    );
    expect(html).toMatch(/<a[^>]*href="sd:\/\/pinterest-ad-ctr"/);
    expect(html).toMatch(/<a[^>]*target="_blank"/);
  });

  it("sd:// with uppercase slug falls back to anchor (regex case-strict)", () => {
    // Regex is intentionally [a-z0-9-]+ — uppercase = malformed slug, must
    // not silently route to drawer. Falls through to default <a target=_blank>.
    const handler = (slug: string) => slug;
    const html = renderToStaticMarkup(
      <MarkdownPreview
        markdown="[ctr](sd://Pinterest-AD-CTR)"
        onSdLinkClick={handler}
      />
    );
    expect(html).not.toContain("<button");
    expect(html).toMatch(/<a[^>]*href="sd:\/\/Pinterest-AD-CTR"/);
    expect(html).toMatch(/<a[^>]*target="_blank"/);
  });

  it("plain route /system-design/<slug> is NOT intercepted (regression guard)", () => {
    // Regression: only sd://<slug> URI form should match. Plain route paths
    // must continue to render as anchors so existing pre-migration links
    // still navigate (until docs are migrated to sd:// form).
    const handler = (slug: string) => slug;
    const html = renderToStaticMarkup(
      <MarkdownPreview
        markdown="[ctr](/system-design/pinterest-ad-ctr)"
        onSdLinkClick={handler}
      />
    );
    expect(html).not.toContain("<button");
    expect(html).toMatch(/<a[^>]*href="\/system-design\/pinterest-ad-ctr"/);
  });

  it("renders kg://N as button when onKgLinkClick provided", () => {
    // T-P1-799: kg:// is the framework-node URI scheme. Numeric id is the
    // framework_nodes.id (peer to db:// / cd:// for problems / company-docs).
    const handler = (id: number) => id;
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown="[hashing](kg://7)" onKgLinkClick={handler} />
    );
    expect(html).toContain("<button");
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*kg:\/\//);
    expect(html).toContain("hashing");
  });

  it("renders kg://N#anchor as button (anchor stripped at link layer)", () => {
    // Mirror cd:// / db:// / sd:// optional anchor behavior -- drawer/route
    // opens, anchor ignored at the link layer (future task may scroll inside).
    const handler = (id: number) => id;
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown="[hashing](kg://7#consistent-hashing)" onKgLinkClick={handler} />
    );
    expect(html).toContain("<button");
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*kg:\/\//);
  });

  it("kg:// falls through to anchor when onKgLinkClick not provided", () => {
    // Backward-compat: surfaces that have not opted in still see a link.
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown="[hashing](kg://7)" />
    );
    expect(html).toMatch(/<a[^>]*href="kg:\/\/7"/);
    expect(html).toMatch(/<a[^>]*target="_blank"/);
  });

  it("kg:// with non-numeric id falls back to anchor (regex strict)", () => {
    // Regex is intentionally \d+ -- non-numeric = malformed kg URI, must not
    // silently route to handler. Falls through to default <a target=_blank>.
    const handler = (id: number) => id;
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown="[bad](kg://abc)" onKgLinkClick={handler} />
    );
    expect(html).not.toContain("<button");
    expect(html).toMatch(/<a[^>]*href="kg:\/\/abc"/);
  });

  it("renders cd:// inside an inline HTML <table rowspan> as drawer-button", () => {
    // T-P0-677: the Meta AI-Native hub schedule (doc 82) uses inline HTML
    // <table> with rowspan="2" on the merged 11:00/13:00 coding row to fold
    // two byte-identical Drawer-link cells. The cell links use HTML
    // <a href="cd://N"> (not markdown [text](cd://N)) because GFM markdown
    // is not parsed inside HTML cell content. Lock the contract here:
    // rehype-raw + components.a override must still route HTML <a> with
    // cd:// to the click handler, not fall through to a plain <a>.
    const handler = (id: number) => id;
    const md = [
      "<table>",
      "<tbody>",
      '<tr><td>11:00</td><td rowspan="2"><a href="cd://86">T1</a> · <a href="cd://89">T4-bp</a></td></tr>',
      "<tr><td>13:00</td></tr>",
      "</tbody>",
      "</table>",
    ].join("\n");
    const html = renderToStaticMarkup(
      <MarkdownPreview markdown={md} onCdLinkClick={handler} />
    );
    expect(html).toMatch(/<table/);
    // renderToStaticMarkup emits React prop name (camelCase rowSpan); the
    // actual browser DOM normalizes back to lowercase rowspan. Match either.
    expect(html).toMatch(/rowspan="2"/i);
    // Both cd:// links must render as <button>, not anchor target="_blank".
    expect(html).not.toMatch(/<a[^>]*target="_blank"[^>]*cd:\/\//);
    // T1 + T4-bp = 2 buttons inside the merged cell.
    const buttonCount = (html.match(/<button/g) ?? []).length;
    expect(buttonCount).toBeGreaterThanOrEqual(2);
    expect(html).toContain("T1");
    expect(html).toContain("T4-bp");
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
