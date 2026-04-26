import { describe, expect, it } from "vitest";
import { PILLAR_STYLES, colorForPillar, styleForPillar } from "./kgStyles";

const KNOWN_PILLAR_KEYS = [
  "pillar1",
  "pillar2",
  "pillar3",
  "pillar4",
  "pillar5",
  "pillar6",
  "pillar7",
  "pillar8",
  "ml-fundamentals",
] as const;

const FALLBACK_NAME = "Other";

describe("PILLAR_STYLES coverage", () => {
  it.each(KNOWN_PILLAR_KEYS)(
    "%s resolves to a real pillar style, not FALLBACK",
    (pillar) => {
      const style = styleForPillar(pillar);
      expect(style.name).not.toBe(FALLBACK_NAME);
      expect(PILLAR_STYLES[pillar]).toBeDefined();
      expect(style).toEqual(PILLAR_STYLES[pillar]);
    },
  );

  it("ml-fundamentals uses cyan palette", () => {
    expect(PILLAR_STYLES["ml-fundamentals"]).toEqual({
      border: "#0891b2",
      bg: "#ecfeff",
      name: "ML 八股文 · Fundamentals",
    });
  });

  it("ml-fundamentals border is distinct from every other pillar border", () => {
    const target = PILLAR_STYLES["ml-fundamentals"].border;
    for (const key of KNOWN_PILLAR_KEYS) {
      if (key === "ml-fundamentals") continue;
      expect(PILLAR_STYLES[key].border).not.toBe(target);
    }
  });
});

describe("styleForPillar / colorForPillar fallback semantics", () => {
  it("returns FALLBACK_STYLE name for unknown pillar keys", () => {
    expect(styleForPillar("not-a-pillar").name).toBe(FALLBACK_NAME);
    expect(styleForPillar(null).name).toBe(FALLBACK_NAME);
    expect(styleForPillar(undefined).name).toBe(FALLBACK_NAME);
  });

  it("colorForPillar returns the border for each known pillar", () => {
    for (const key of KNOWN_PILLAR_KEYS) {
      expect(colorForPillar(key)).toBe(PILLAR_STYLES[key].border);
    }
  });

  it("collapsed option returns a muted background variant for known pillars", () => {
    const base = styleForPillar("ml-fundamentals");
    const collapsed = styleForPillar("ml-fundamentals", { collapsed: true });
    expect(collapsed.border).toBe(base.border);
    expect(collapsed.name).toBe(base.name);
    expect(collapsed.bg).not.toBe(base.bg);
  });
});
