import { describe, expect, it } from "vitest";

/**
 * Drawer-target discriminated-union tests for T-P0-674.
 *
 * The PrepNotesPage `DocumentViewer` previously held two independent useState
 * slots (lcDrawerId / dbDrawerId). When cd:// support landed in T-P0-672,
 * the naive extension would have been a third independent slot -- which leaves
 * "two drawers open at once" representable, the exact bug class flagged in
 * design review point #4. The fix is a single discriminated-union state
 * (DrawerTarget) that makes the multi-drawer state unrepresentable at the type
 * level.
 *
 * The codebase has no jsdom/testing-library, so these tests follow the
 * BehavioralQuestions.test.tsx + CompanyDocDrawer.test.tsx pattern: structural
 * source assertions on PrepNotesPage.tsx. We pin the four load-bearing facts:
 *   1. The DrawerTarget union type is exported (so tests + future callers can
 *      reuse it instead of re-deriving the variant set).
 *   2. The two old useState slots (lcDrawerId / dbDrawerId) are gone from
 *      DocumentViewer -- a regression-guard against re-introducing the
 *      parallel-state shape.
 *   3. MarkdownPreview's three callbacks all flow into setDrawer with the
 *      correct discriminator.
 *   4. ProblemDrawer reads lcId/dbId from `drawer.type === ...` guards (so
 *      ProblemDrawer cannot show while CompanyDocDrawer's docId is set, and
 *      vice versa) and CompanyDocDrawer is rendered with the same single-
 *      source state.
 */
describe("PrepNotesPage drawer-target refactor (T-P0-674)", () => {
  async function readSource(): Promise<string> {
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    return fs.readFile(
      path.resolve(__dirname, "PrepNotesPage.tsx"),
      "utf-8",
    );
  }

  it("exports a DrawerTarget union covering lc / problem / company_doc / null", async () => {
    const file = await readSource();
    // Single source-of-truth type. Exported so downstream callers (tests,
    // future shared drawer code) can import rather than redefine.
    expect(file).toMatch(/export type DrawerTarget\s*=/);
    expect(file).toMatch(/\{\s*type:\s*"lc";\s*id:\s*number\s*\}/);
    expect(file).toMatch(/\{\s*type:\s*"problem";\s*id:\s*number\s*\}/);
    expect(file).toMatch(/\{\s*type:\s*"company_doc";\s*id:\s*number\s*\}/);
    // Null is the "closed" state -- without it, callers would need a separate
    // boolean flag, which would re-create the multi-state hazard.
    expect(file).toMatch(/\|\s*null;/);
  });

  it("DocumentViewer no longer carries parallel lcDrawerId / dbDrawerId useState slots", async () => {
    const file = await readSource();
    // Locate the DocumentViewer body (everything after `function DocumentViewer`)
    // so the index-tab `indexLcDrawerId / indexDbDrawerId` slots upstream do
    // not give a false positive. Index-tab state is intentionally left as-is
    // per the task spec ("its own discriminated union if other types are
    // added there, but for now leave as-is").
    const docViewerStart = file.indexOf("function DocumentViewer(");
    expect(docViewerStart).toBeGreaterThan(0);
    const docViewerSource = file.slice(docViewerStart);
    expect(docViewerSource).not.toMatch(/setLcDrawerId\(/);
    expect(docViewerSource).not.toMatch(/setDbDrawerId\(/);
    expect(docViewerSource).not.toMatch(/useState<number \| null>\(null\);\s*\/\/ lc/);
    // The new single-state slot. Type is the union, not number|null.
    expect(docViewerSource).toMatch(
      /useState<DrawerTarget>\(null\)/,
    );
  });

  it("wires onLcLinkClick / onDbLinkClick / onCdLinkClick into setDrawer with correct discriminators", async () => {
    const file = await readSource();
    // cd:// wiring is the new behavior added in this task. The other two are
    // pre-existing but locked here so the refactor does not silently drop
    // them (a hidden regression we'd only catch by clicking in prod).
    expect(file).toMatch(
      /onLcLinkClick=\{\(id\)\s*=>\s*setDrawer\(\{\s*type:\s*"lc",\s*id\s*\}\)\}/,
    );
    expect(file).toMatch(
      /onDbLinkClick=\{\(id\)\s*=>\s*setDrawer\(\{\s*type:\s*"problem",\s*id\s*\}\)\}/,
    );
    expect(file).toMatch(
      /onCdLinkClick=\{\(id\)\s*=>\s*setDrawer\(\{\s*type:\s*"company_doc",\s*id\s*\}\)\}/,
    );
  });

  it("ProblemDrawer + CompanyDocDrawer both read from the same drawer state via type guards", async () => {
    const file = await readSource();
    // Type-guard reads -- this is what makes "two drawers open" unrepresentable:
    // ProblemDrawer's lcId/dbId go null whenever drawer.type !== "lc" / "problem".
    expect(file).toMatch(
      /lcId=\{drawer\?\.type\s*===\s*"lc"\s*\?\s*drawer\.id\s*:\s*null\}/,
    );
    expect(file).toMatch(
      /dbId=\{drawer\?\.type\s*===\s*"problem"\s*\?\s*drawer\.id\s*:\s*null\}/,
    );
    // CompanyDocDrawer mounted alongside ProblemDrawer (single source of truth).
    expect(file).toContain("import CompanyDocDrawer from");
    expect(file).toMatch(
      /docId=\{drawer\?\.type\s*===\s*"company_doc"\s*\?\s*drawer\.id\s*:\s*null\}/,
    );
    // Both drawers share onClose=() => setDrawer(null) -- there is no
    // independent close path that could leave the other drawer's state stale.
    const onCloseMatches = file.match(/onClose=\{\(\)\s*=>\s*setDrawer\(null\)\}/g);
    expect(onCloseMatches).not.toBeNull();
    expect(onCloseMatches!.length).toBeGreaterThanOrEqual(2);
    // CompanyDocDrawer bubbles lc:// / db:// up to setDrawer so embedded LC
    // and problem links inside a doc swap drawers at the outer level rather
    // than nesting inside the company-doc drawer (matches the contract
    // documented in CompanyDocDrawer.tsx).
    expect(file).toMatch(
      /<CompanyDocDrawer[\s\S]*?onLcLinkClick=\{\(id\)\s*=>\s*setDrawer\(\{\s*type:\s*"lc",\s*id\s*\}\)\}/,
    );
    expect(file).toMatch(
      /<CompanyDocDrawer[\s\S]*?onDbLinkClick=\{\(id\)\s*=>\s*setDrawer\(\{\s*type:\s*"problem",\s*id\s*\}\)\}/,
    );
  });
});

/**
 * BehavioralQuestions.tsx is named in the T-P0-674 task spec as carrying the
 * same multi-drawer hazard, but inspection shows it only ever holds ONE
 * drawer state slot (`drawerExampleId`) -- there is no parallel lc/db drawer
 * to merge. We keep this guard so a future maintainer adding a second drawer
 * type to that page is forced to reach for the discriminated-union pattern
 * rather than re-create the parallel-state shape this task removed elsewhere.
 */
describe("BehavioralQuestions.tsx drawer-state regression-guard (T-P0-674)", () => {
  it("still uses a single drawerExampleId slot (no parallel drawer ids)", async () => {
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "BehavioralQuestions.tsx"),
      "utf-8",
    );
    // The single drawer slot is a string (example_id), not number, so it
    // cannot collide with the LC/DB drawer ids elsewhere.
    expect(file).toMatch(
      /useState<string \| null>\(null\)/,
    );
    // Structural guard: no second drawer-id slot has been added without
    // converting to DrawerTarget. If a maintainer adds another, this fails
    // and they will see the comment above pointing them to the union
    // pattern in PrepNotesPage.
    expect(file).not.toMatch(/setLcDrawerId/);
    expect(file).not.toMatch(/setDbDrawerId/);
    expect(file).not.toMatch(/setCdDrawerId/);
  });
});
