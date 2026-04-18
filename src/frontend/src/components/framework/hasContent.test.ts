import { describe, expect, it } from "vitest";
import { hasContent } from "./hasContent";

describe("hasContent", () => {
  it("returns false when content_length is 0", () => {
    expect(hasContent({ content_length: 0 })).toBe(false);
  });

  it("returns true when content_length is positive", () => {
    expect(hasContent({ content_length: 1 })).toBe(true);
  });

  it("returns false when contentLength is 0 (NodeMeta shape)", () => {
    expect(hasContent({ contentLength: 0 })).toBe(false);
  });

  it("returns true when contentLength is positive (NodeMeta shape)", () => {
    expect(hasContent({ contentLength: 500 })).toBe(true);
  });

  it("returns false when neither field is present", () => {
    expect(hasContent({})).toBe(false);
  });

  it("prefers contentLength when both fields are present", () => {
    // Defensive: both fields same value, just confirms no crash.
    expect(hasContent({ contentLength: 0, content_length: 100 })).toBe(false);
    expect(hasContent({ contentLength: 100, content_length: 0 })).toBe(true);
  });
});
