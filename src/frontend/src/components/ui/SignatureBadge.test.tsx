import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import SignatureBadge from "./SignatureBadge";

describe("<SignatureBadge />", () => {
  it("renders nothing when signature is false", () => {
    expect(renderToStaticMarkup(<SignatureBadge signature={false} />)).toBe("");
  });

  it("renders a Signature pill when signature is true", () => {
    const html = renderToStaticMarkup(<SignatureBadge signature />);
    expect(html).toContain("Signature");
    expect(html).toContain("purple");
    expect(html).toContain("svg");
  });

  it("merges extra className", () => {
    const html = renderToStaticMarkup(
      <SignatureBadge signature className="ml-2 shrink-0" />,
    );
    expect(html).toContain("ml-2");
    expect(html).toContain("shrink-0");
  });
});
