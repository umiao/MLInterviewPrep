import { describe, expect, it } from "vitest";

/**
 * Regression guard: in-note resource links must open drawers on
 * /framework/:nodeId/notes (Discord 2026-05-19 -- "link没有一个能用的 需要
 * 渲染到对应的drawer view（尝试复用）").
 *
 * Root cause of the original bug: FrameworkNotesPage rendered
 * <MarkdownPreview> with ONLY onCheckboxClick + onKgLinkClick. MarkdownPreview's
 * `a` resolver renders a clickable drawer button only when the matching
 * onXxLinkClick prop is supplied -- otherwise lc:// / db:// / cd:// / sd://
 * fall through to an inert <a href="lc://N"> that does nothing. So every
 * problem link in a node's notes was dead.
 *
 * Fix: reuse PrepNotesPage's proven DrawerTarget union + the three drawer
 * components verbatim, wiring all four link callbacks into a single
 * useState<DrawerTarget> slot.
 *
 * The codebase has no jsdom/testing-library, so this follows the
 * PrepNotesPage.test.tsx pattern: structural source assertions on
 * FrameworkNotesPage.tsx. We pin the load-bearing facts so a future edit
 * that drops a handler silently re-breaks the test, not prod.
 */
describe("FrameworkNotesPage in-note drawer wiring (Discord 2026-05-19 regression)", () => {
  async function readSource(): Promise<string> {
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    return fs.readFile(
      path.resolve(__dirname, "FrameworkNotesPage.tsx"),
      "utf-8",
    );
  }

  it("reuses (not re-derives) the DrawerTarget union + the three drawer components", async () => {
    const file = await readSource();
    // Reuse, per the user's explicit "尝试复用": import the exported union
    // from PrepNotesPage rather than redefining a parallel variant set.
    expect(file).toMatch(
      /import type \{ DrawerTarget \} from "\.\/PrepNotesPage"/,
    );
    expect(file).toContain('import ProblemDrawer from "../components/problems/ProblemDrawer"');
    expect(file).toContain('import CompanyDocDrawer from "../components/CompanyDocDrawer"');
    expect(file).toContain('import SystemDesignDrawer from "../components/SystemDesignDrawer"');
    // Single source-of-truth drawer slot (no parallel id slots -- the
    // multi-drawer hazard T-P0-674 removed elsewhere).
    expect(file).toMatch(/useState<DrawerTarget>\(null\)/);
  });

  it("wires all four MarkdownPreview link callbacks into setDrawer with correct discriminators", async () => {
    const file = await readSource();
    // These four were the exact missing props that made every in-note
    // problem link inert. Locked so the bug cannot silently return.
    expect(file).toMatch(
      /onLcLinkClick=\{\(id\)\s*=>\s*setDrawer\(\{\s*type:\s*"lc",\s*id\s*\}\)\}/,
    );
    expect(file).toMatch(
      /onDbLinkClick=\{\(id\)\s*=>\s*setDrawer\(\{\s*type:\s*"problem",\s*id\s*\}\)\}/,
    );
    expect(file).toMatch(
      /onCdLinkClick=\{\(id\)\s*=>\s*setDrawer\(\{\s*type:\s*"company_doc",\s*id\s*\}\)\}/,
    );
    expect(file).toMatch(
      /onSdLinkClick=\{\(slug\)\s*=>\s*setDrawer\(\{\s*type:\s*"system_design",\s*slug\s*\}\)\}/,
    );
  });

  it("renders all three drawers from the same drawer state via type guards", async () => {
    const file = await readSource();
    expect(file).toMatch(
      /lcId=\{drawer\?\.type\s*===\s*"lc"\s*\?\s*drawer\.id\s*:\s*null\}/,
    );
    expect(file).toMatch(
      /dbId=\{drawer\?\.type\s*===\s*"problem"\s*\?\s*drawer\.id\s*:\s*null\}/,
    );
    expect(file).toMatch(
      /docId=\{drawer\?\.type\s*===\s*"company_doc"\s*\?\s*drawer\.id\s*:\s*null\}/,
    );
    expect(file).toMatch(
      /slug=\{drawer\?\.type\s*===\s*"system_design"\s*\?\s*drawer\.slug\s*:\s*null\}/,
    );
    // All drawers share the single close path -- no stale-state leak.
    const onCloseMatches = file.match(/onClose=\{\(\)\s*=>\s*setDrawer\(null\)\}/g);
    expect(onCloseMatches).not.toBeNull();
    expect(onCloseMatches!.length).toBeGreaterThanOrEqual(3);
  });
});
