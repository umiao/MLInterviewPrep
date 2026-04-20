import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import GoldenBadge from "./GoldenBadge";

describe("<GoldenBadge />", () => {
  it("renders nothing when golden=false", () => {
    expect(renderToStaticMarkup(<GoldenBadge golden={false} />)).toBe("");
  });

  it("renders orange pill with uppercase GOLDEN label when golden=true", () => {
    const html = renderToStaticMarkup(<GoldenBadge golden />);
    expect(html).toContain("bg-orange-50");
    expect(html).toContain("text-orange-700");
    expect(html).toContain("border-orange-200");
    expect(html).toContain("uppercase");
    expect(html.toLowerCase()).toContain("golden");
    expect(html).toContain("<svg");
  });

  it("appends a custom className when provided", () => {
    const html = renderToStaticMarkup(
      <GoldenBadge golden className="ml-2 shrink-0" />,
    );
    expect(html).toContain("ml-2");
    expect(html).toContain("shrink-0");
  });
});
