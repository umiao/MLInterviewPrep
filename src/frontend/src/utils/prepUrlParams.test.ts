import { describe, expect, it } from "vitest";
import { parsePrepParams, serializePrepParams } from "./prepUrlParams";

describe("parsePrepParams (prep page deeplink regression — T-P0-216)", () => {
  it("treats legacy ?doc=38 (no tab param) as tab=docs with doc id 38", () => {
    const p = parsePrepParams("?doc=38");
    expect(p.tab).toBe("docs");
    expect(p.docId).toBe(38);
    expect(p.problemId).toBeNull();
  });

  it("explicit ?tab=docs&doc=38 renders doc 38", () => {
    const p = parsePrepParams("?tab=docs&doc=38");
    expect(p).toEqual({ tab: "docs", docId: 38, problemId: null });
  });

  it("?tab=coding without a problem id opens the coding tab with drawer closed", () => {
    const p = parsePrepParams("?tab=coding");
    expect(p).toEqual({ tab: "coding", docId: null, problemId: null });
  });

  it("?tab=coding&problem=1081 opens drawer for problem 1081 on fresh load", () => {
    const p = parsePrepParams("?tab=coding&problem=1081");
    expect(p).toEqual({ tab: "coding", docId: null, problemId: 1081 });
  });

  it("ignores problem param when not on the coding tab", () => {
    const p = parsePrepParams("?tab=docs&doc=1&problem=99");
    expect(p.problemId).toBeNull();
  });

  it("falls back to notes tab when tab value is unknown", () => {
    const p = parsePrepParams("?tab=bogus");
    expect(p.tab).toBe("notes");
  });

  it("rejects non-numeric or non-positive doc/problem ids", () => {
    const a = parsePrepParams("?tab=docs&doc=abc");
    expect(a.docId).toBeNull();
    const b = parsePrepParams("?tab=coding&problem=-5");
    expect(b.problemId).toBeNull();
  });

  it("empty search yields notes tab default", () => {
    expect(parsePrepParams("")).toEqual({
      tab: "notes",
      docId: null,
      problemId: null,
    });
  });
});

describe("serializePrepParams", () => {
  it("omits doc when not on docs tab", () => {
    const s = serializePrepParams({
      tab: "coding",
      docId: 5,
      problemId: null,
    });
    expect(s.get("doc")).toBeNull();
    expect(s.get("tab")).toBe("coding");
  });

  it("round-trips coding drawer state", () => {
    const params = serializePrepParams({
      tab: "coding",
      docId: null,
      problemId: 1081,
    });
    const back = parsePrepParams("?" + params.toString());
    expect(back).toEqual({ tab: "coding", docId: null, problemId: 1081 });
  });

  it("round-trips docs deeplink state", () => {
    const params = serializePrepParams({
      tab: "docs",
      docId: 38,
      problemId: null,
    });
    const back = parsePrepParams("?" + params.toString());
    expect(back).toEqual({ tab: "docs", docId: 38, problemId: null });
  });
});
