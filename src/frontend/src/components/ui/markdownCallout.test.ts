import { describe, expect, it } from "vitest";
import {
  calloutClass,
  getCalloutKind,
  getCalloutKindFromHast,
  type HastLike,
} from "./markdownCallout";

function blockquoteAst(strongText: string, tail: string, opts?: { strongTag?: string; tailType?: string }): HastLike {
  const strongTag = opts?.strongTag ?? "strong";
  const tailType = opts?.tailType ?? "text";
  return {
    type: "element",
    tagName: "blockquote",
    children: [
      { type: "text", value: "\n" },
      {
        type: "element",
        tagName: "p",
        children: [
          { type: "element", tagName: strongTag, children: [{ type: "text", value: strongText }] },
          { type: tailType, value: tail },
        ],
      },
      { type: "text", value: "\n" },
    ],
  };
}

describe("getCalloutKind", () => {
  it("detects GOOD", () => {
    expect(getCalloutKind("**GOOD**: foo")).toBe("good");
  });

  it("detects BAD", () => {
    expect(getCalloutKind("**BAD**: foo")).toBe("bad");
  });

  it("detects NOTE", () => {
    expect(getCalloutKind("**NOTE**: foo")).toBe("note");
  });

  it("tolerates leading whitespace inside the paragraph", () => {
    expect(getCalloutKind("   **GOOD**: foo")).toBe("good");
  });

  it("tolerates whitespace between the bold tag and the colon", () => {
    expect(getCalloutKind("**GOOD** : foo")).toBe("good");
  });

  it("returns null for an unmatched bold prefix", () => {
    expect(getCalloutKind("**TIP**: foo")).toBe(null);
  });

  it("returns null when the marker is not bold-wrapped", () => {
    expect(getCalloutKind("GOOD: foo")).toBe(null);
  });

  it("returns null for an emoji variant (rejected by spec)", () => {
    expect(getCalloutKind("\u2705 GOOD: foo")).toBe(null);
  });

  it("returns null when the prefix is not at the start of the text", () => {
    expect(getCalloutKind("Lorem ipsum **GOOD**: foo")).toBe(null);
  });

  it("returns null for an empty string", () => {
    expect(getCalloutKind("")).toBe(null);
  });
});

describe("getCalloutKindFromHast", () => {
  it("detects GOOD/BAD/NOTE from a bold-prefixed paragraph", () => {
    expect(getCalloutKindFromHast(blockquoteAst("GOOD", ": foo"))).toBe("good");
    expect(getCalloutKindFromHast(blockquoteAst("BAD", ": foo"))).toBe("bad");
    expect(getCalloutKindFromHast(blockquoteAst("NOTE", ": foo"))).toBe("note");
  });

  it("returns null when label is not GOOD/BAD/NOTE", () => {
    expect(getCalloutKindFromHast(blockquoteAst("TIP", ": foo"))).toBe(null);
  });

  it("returns null when the prefix is not a <strong> element (no bold)", () => {
    expect(getCalloutKindFromHast(blockquoteAst("GOOD", ": foo", { strongTag: "em" }))).toBe(null);
  });

  it("returns null when there is no colon after the label", () => {
    expect(getCalloutKindFromHast(blockquoteAst("GOOD", " foo"))).toBe(null);
  });

  it("returns null for empty / undefined / non-blockquote nodes", () => {
    expect(getCalloutKindFromHast(undefined)).toBe(null);
    expect(getCalloutKindFromHast({})).toBe(null);
    expect(getCalloutKindFromHast({ children: [] })).toBe(null);
  });

  it("returns null when the first inner element is not a paragraph", () => {
    const ast: HastLike = {
      type: "element",
      tagName: "blockquote",
      children: [{ type: "element", tagName: "div", children: [] }],
    };
    expect(getCalloutKindFromHast(ast)).toBe(null);
  });
});

describe("calloutClass", () => {
  it("returns the namespaced class for each kind", () => {
    expect(calloutClass("good")).toBe("callout callout-good");
    expect(calloutClass("bad")).toBe("callout callout-bad");
    expect(calloutClass("note")).toBe("callout callout-note");
  });
});
