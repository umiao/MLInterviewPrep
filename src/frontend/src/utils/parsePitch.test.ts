import { describe, expect, it } from "vitest";
import { parsePitch } from "./parsePitch";

describe("parsePitch", () => {
  it("splits summary and facts on the KEY FACTS separator", () => {
    const pitch =
      "搜索多样性问题导致用户流失 | KEY FACTS: 30% CTR lift | 2 quarters | 5M users";
    const parsed = parsePitch(pitch);
    expect(parsed.summary).toBe("搜索多样性问题导致用户流失");
    expect(parsed.facts).toEqual(["30% CTR lift", "2 quarters", "5M users"]);
  });

  it("returns the whole string as summary with empty facts when separator is absent", () => {
    const pitch = "A plain pitch without any facts section";
    const parsed = parsePitch(pitch);
    expect(parsed.summary).toBe(pitch);
    expect(parsed.facts).toEqual([]);
  });

  it("returns empty summary and empty facts for empty input", () => {
    const parsed = parsePitch("");
    expect(parsed.summary).toBe("");
    expect(parsed.facts).toEqual([]);
  });

  it("trims whitespace around each fact and filters empty ones", () => {
    const pitch = "summary | KEY FACTS:  fact a  |  fact b  ||  fact c ";
    const parsed = parsePitch(pitch);
    expect(parsed.summary).toBe("summary");
    expect(parsed.facts).toEqual(["fact a", "fact b", "fact c"]);
  });
});
