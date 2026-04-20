import { describe, expect, it } from "vitest";
import { goldenCardClass } from "./goldenStyle";

describe("goldenCardClass", () => {
  it("returns empty string when not golden so callers can concat safely", () => {
    expect(goldenCardClass(false)).toBe("");
  });

  it("returns orange accent classes when golden", () => {
    const cls = goldenCardClass(true);
    expect(cls).toContain("bg-orange-50");
    expect(cls).toContain("border-orange-300");
    expect(cls).toContain("border-l-4");
    expect(cls).toContain("border-l-orange-500");
  });
});
