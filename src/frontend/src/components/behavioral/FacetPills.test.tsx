import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import FacetPills from "./FacetPills";
import type { FacetTag } from "../../types/behavioral";

describe("<FacetPills />", () => {
  it("renders nothing when facets is undefined", () => {
    expect(renderToStaticMarkup(<FacetPills facets={undefined} />)).toBe("");
  });

  it("renders nothing when facets is empty", () => {
    expect(renderToStaticMarkup(<FacetPills facets={[]} />)).toBe("");
  });

  it("renders a pill per facet using the label", () => {
    const facets: FacetTag[] = [
      { slug: "fast_learning", label: "Fast Learning" },
      { slug: "scrappy_innovation", label: "Scrappy Innovation" },
    ];
    const html = renderToStaticMarkup(<FacetPills facets={facets} />);
    expect(html).toContain("Fast Learning");
    expect(html).toContain("Scrappy Innovation");
    expect(html).toContain("amber");
  });
});
