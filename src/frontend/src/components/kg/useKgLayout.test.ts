import { describe, expect, it } from "vitest";
import { PILLAR_ORDER, pillarSortKey } from "./useKgLayout";

const EXPECTED_FULL_ORDER = [
  "pillar1",
  "pillar2",
  "ml-fundamentals",
  "pillar3",
  "pillar4",
  "pillar5",
  "pillar6",
  "pillar7",
  "pillar8",
  "meta-prep",
];

describe("PILLAR_ORDER map", () => {
  it("contains step=10 entries with ml-fundamentals at 25 and meta-prep at 85", () => {
    expect(PILLAR_ORDER).toEqual({
      pillar1: 10,
      pillar2: 20,
      "ml-fundamentals": 25,
      pillar3: 30,
      pillar4: 40,
      pillar5: 50,
      pillar6: 60,
      pillar7: 70,
      pillar8: 80,
      "meta-prep": 85,
    });
  });

  it("ranks ml-fundamentals strictly between pillar2 and pillar3", () => {
    expect(PILLAR_ORDER["ml-fundamentals"]).toBeGreaterThan(
      PILLAR_ORDER.pillar2,
    );
    expect(PILLAR_ORDER["ml-fundamentals"]).toBeLessThan(PILLAR_ORDER.pillar3);
  });

  it("ranks meta-prep strictly after pillar8", () => {
    expect(PILLAR_ORDER["meta-prep"]).toBeGreaterThan(PILLAR_ORDER.pillar8);
  });

  it("uses step=10 numbering for the eight numeric pillars", () => {
    for (let i = 1; i <= 8; i++) {
      expect(PILLAR_ORDER[`pillar${i}`]).toBe(i * 10);
    }
  });
});

describe("pillarSortKey full-order behavior (AC3)", () => {
  it("sorts the full known set into pillar1, pillar2, ml-fundamentals, pillar3..pillar8, meta-prep", () => {
    const shuffled = [
      "pillar7",
      "pillar3",
      "ml-fundamentals",
      "pillar1",
      "pillar5",
      "pillar2",
      "meta-prep",
      "pillar8",
      "pillar4",
      "pillar6",
    ];
    shuffled.sort((a, b) => pillarSortKey(a) - pillarSortKey(b));
    expect(shuffled).toEqual(EXPECTED_FULL_ORDER);
  });

  it("returns a finite rank for every known pillar key", () => {
    for (const key of EXPECTED_FULL_ORDER) {
      expect(Number.isFinite(pillarSortKey(key))).toBe(true);
      expect(pillarSortKey(key)).toBeLessThan(9999);
    }
  });

  it("pushes unknown keys to the end (rank=9999) without falling back to regex", () => {
    expect(pillarSortKey("pillar9")).toBe(9999);
    expect(pillarSortKey("not-a-pillar")).toBe(9999);
    expect(pillarSortKey("")).toBe(9999);
    const mixed = ["unknown-x", "pillar3", "pillar1", "ml-fundamentals"];
    mixed.sort((a, b) => pillarSortKey(a) - pillarSortKey(b));
    expect(mixed).toEqual([
      "pillar1",
      "ml-fundamentals",
      "pillar3",
      "unknown-x",
    ]);
  });
});
