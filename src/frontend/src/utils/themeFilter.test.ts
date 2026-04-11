import { describe, expect, it } from "vitest";
import {
  parseThemeFilterFromSearch,
  questionMatchesThemeFilter,
  serializeThemeFilterToSearch,
  toggleThemeInState,
} from "./themeFilter";

describe("parseThemeFilterFromSearch", () => {
  it("returns empty state for empty search", () => {
    expect(parseThemeFilterFromSearch("")).toEqual({ themes: [], mode: "or" });
  });

  it("parses themes and mode from URL", () => {
    const state = parseThemeFilterFromSearch(
      "?themes=failure_setback,leadership_direction&theme_mode=and",
    );
    expect(state.themes).toEqual(["failure_setback", "leadership_direction"]);
    expect(state.mode).toBe("and");
  });

  it("defaults to or mode when theme_mode missing", () => {
    const state = parseThemeFilterFromSearch("?themes=failure_setback");
    expect(state.mode).toBe("or");
  });

  it("ignores invalid mode values", () => {
    const state = parseThemeFilterFromSearch(
      "?themes=failure_setback&theme_mode=xor",
    );
    expect(state.mode).toBe("or");
  });

  it("trims whitespace from slugs", () => {
    const state = parseThemeFilterFromSearch("?themes= failure_setback , leadership_direction ");
    expect(state.themes).toEqual(["failure_setback", "leadership_direction"]);
  });
});

describe("serializeThemeFilterToSearch", () => {
  it("returns empty string for empty state", () => {
    expect(serializeThemeFilterToSearch({ themes: [], mode: "or" })).toBe("");
  });

  it("writes themes and mode", () => {
    const qs = serializeThemeFilterToSearch({
      themes: ["failure_setback", "leadership_direction"],
      mode: "and",
    });
    expect(qs).toBe("?themes=failure_setback%2Cleadership_direction&theme_mode=and");
  });

  it("round-trips with parseThemeFilterFromSearch", () => {
    const state = { themes: ["failure_setback", "deadline_pressure"], mode: "and" as const };
    const qs = serializeThemeFilterToSearch(state);
    expect(parseThemeFilterFromSearch(qs)).toEqual(state);
  });

  it("preserves unrelated existing params", () => {
    const qs = serializeThemeFilterToSearch(
      { themes: ["failure_setback"], mode: "or" },
      "?category=LDR",
    );
    expect(qs).toContain("category=LDR");
    expect(qs).toContain("themes=failure_setback");
  });

  it("removes theme params when cleared but keeps unrelated params", () => {
    const qs = serializeThemeFilterToSearch(
      { themes: [], mode: "or" },
      "?category=LDR&themes=failure_setback&theme_mode=and",
    );
    expect(qs).toBe("?category=LDR");
  });
});

describe("toggleThemeInState", () => {
  it("adds an absent theme", () => {
    const next = toggleThemeInState({ themes: [], mode: "or" }, "failure_setback");
    expect(next.themes).toEqual(["failure_setback"]);
  });

  it("removes an existing theme", () => {
    const next = toggleThemeInState(
      { themes: ["failure_setback", "leadership_direction"], mode: "or" },
      "failure_setback",
    );
    expect(next.themes).toEqual(["leadership_direction"]);
  });

  it("preserves mode across toggles", () => {
    const next = toggleThemeInState(
      { themes: [], mode: "and" },
      "failure_setback",
    );
    expect(next.mode).toBe("and");
  });
});

describe("questionMatchesThemeFilter", () => {
  const tags = [
    { slug: "failure_setback", label: "Failure & Setback" },
    { slug: "leadership_direction", label: "Leadership & Direction" },
  ];

  it("matches everything when no themes selected", () => {
    expect(
      questionMatchesThemeFilter(tags, { themes: [], mode: "or" }),
    ).toBe(true);
    expect(
      questionMatchesThemeFilter([], { themes: [], mode: "or" }),
    ).toBe(true);
  });

  it("OR matches if question has any selected theme", () => {
    expect(
      questionMatchesThemeFilter(tags, {
        themes: ["failure_setback", "deadline_pressure"],
        mode: "or",
      }),
    ).toBe(true);
  });

  it("OR rejects when question has none of the selected themes", () => {
    expect(
      questionMatchesThemeFilter(tags, {
        themes: ["deadline_pressure"],
        mode: "or",
      }),
    ).toBe(false);
  });

  it("AND requires all selected themes", () => {
    expect(
      questionMatchesThemeFilter(tags, {
        themes: ["failure_setback", "leadership_direction"],
        mode: "and",
      }),
    ).toBe(true);
    expect(
      questionMatchesThemeFilter(tags, {
        themes: ["failure_setback", "deadline_pressure"],
        mode: "and",
      }),
    ).toBe(false);
  });

  it("tolerates missing theme_tags field (old cached data)", () => {
    expect(
      questionMatchesThemeFilter(undefined, { themes: ["failure_setback"], mode: "or" }),
    ).toBe(false);
    expect(
      questionMatchesThemeFilter(null, { themes: [], mode: "or" }),
    ).toBe(true);
  });
});
