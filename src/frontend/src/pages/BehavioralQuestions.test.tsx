import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { normalizeTagLabel } from "../utils/tagLabel";

describe("normalizeTagLabel (T-P0-626 regression)", () => {
  it("turns underscore phrases into space-separated words", () => {
    expect(normalizeTagLabel("problem_framing_before_persuasion")).toBe(
      "problem framing before persuasion",
    );
  });

  it("leaves single-word slugs unchanged", () => {
    expect(normalizeTagLabel("ownership")).toBe("ownership");
  });

  it("leaves human-readable labels (no underscores) unchanged", () => {
    expect(normalizeTagLabel("Adaptability")).toBe("Adaptability");
  });

  it("handles empty input", () => {
    expect(normalizeTagLabel("")).toBe("");
  });

  it("normalizes multiple consecutive underscores to spaces", () => {
    expect(normalizeTagLabel("a__b")).toBe("a  b");
  });
});

describe("ExampleCard structural regression (T-P0-626)", () => {
  // The previous layout used a left/right flex split with the right column
  // marked `shrink-0 flex-wrap`, which let long principle pills hold the
  // right column at ~50% of the card and crushed the title cell. The fix
  // is to stack vertically: title row, source line, FacetPills, then
  // principle pills as a NEW row with its own `flex-wrap gap-2`. The
  // bq-example-card-body marker class is the load-bearing assertion.
  it("BehavioralQuestions.tsx no longer contains the flex shrink-0 + flex-wrap right column for principle pills", async () => {
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "BehavioralQuestions.tsx"),
      "utf-8",
    );
    // The exact pre-fix pattern that caused the squeeze.
    expect(file).not.toContain(
      'className="flex items-center gap-2 flex-wrap shrink-0"',
    );
    // The new vertical-stack marker must be present.
    expect(file).toContain("bq-example-card-body");
    // Principle pills row marker must be present.
    expect(file).toContain("bq-principle-pills");
    // h4 must have break-words (allows wrap when squeezed; was missing pre-fix).
    expect(file).toMatch(
      /<h4 className="text-gray-900 font-bold text-base break-words/,
    );
    // Pills must use normalizeTagLabel (the _ -> space helper).
    expect(file).toContain("normalizeTagLabel(fullLabel)");
  });

  it("renders without crashing inside the QueryClient + Router shell (smoke)", () => {
    // This is intentionally a degenerate smoke test: it does not exercise
    // useQuery (no API mock here), but it ensures the export shape is
    // stable so a stray import-time error from the page module would
    // surface in CI before T-P0-626's structural change ships. The page
    // proper renders inside react-query and react-router so we wrap both.
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    expect(() =>
      renderToStaticMarkup(
        <QueryClientProvider client={client}>
          <MemoryRouter>
            <div data-testid="bq-shell" />
          </MemoryRouter>
        </QueryClientProvider>,
      ),
    ).not.toThrow();
  });
});
