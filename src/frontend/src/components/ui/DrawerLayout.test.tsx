import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import DrawerLayout from "./DrawerLayout";

function render(node: React.ReactElement): string {
  return renderToStaticMarkup(node);
}

describe("DrawerLayout", () => {
  it("renders two-column variant by default with both panes", () => {
    const html = render(
      <DrawerLayout left={<div>LEFT</div>} right={<div>RIGHT</div>} />,
    );
    expect(html).toContain('data-drawer-layout="two-column"');
    expect(html).toContain('data-drawer-pane="left"');
    expect(html).toContain('data-drawer-pane="right"');
    expect(html).toContain("LEFT");
    expect(html).toContain("RIGHT");
  });

  it("two-column variant uses flex-col lg:flex-row for responsive collapse", () => {
    const html = render(
      <DrawerLayout left={<span>L</span>} right={<span>R</span>} />,
    );
    expect(html).toMatch(/flex-col[^"]*lg:flex-row/);
  });

  it("two-column variant applies sticky top-0 to the left pane at lg", () => {
    const html = render(
      <DrawerLayout left={<span>L</span>} right={<span>R</span>} />,
    );
    expect(html).toContain("lg:sticky");
    expect(html).toContain("lg:top-0");
  });

  it("two-column variant caps right pane prose width at 680px by default", () => {
    const html = render(
      <DrawerLayout left={<span>L</span>} right={<span>R</span>} />,
    );
    expect(html).toContain("max-w-[680px]");
  });

  it("two-column variant uses the default w-72 left width", () => {
    const html = render(
      <DrawerLayout left={<span>L</span>} right={<span>R</span>} />,
    );
    expect(html).toContain("w-72");
  });

  it("two-column variant accepts custom leftWidth and proseMaxWidth", () => {
    const html = render(
      <DrawerLayout
        left={<span>L</span>}
        right={<span>R</span>}
        leftWidth="w-96"
        proseMaxWidth="max-w-[800px]"
      />,
    );
    expect(html).toContain("w-96");
    expect(html).not.toContain("w-72");
    expect(html).toContain("max-w-[800px]");
    expect(html).not.toContain("max-w-[680px]");
  });

  it("single-column variant does not apply lg:flex-row or sticky classes", () => {
    const html = render(
      <DrawerLayout
        variant="single-column"
        left={<span>L</span>}
        right={<span>R</span>}
      />,
    );
    expect(html).toContain('data-drawer-layout="single-column"');
    expect(html).not.toContain("lg:flex-row");
    expect(html).not.toContain("lg:sticky");
  });

  it("single-column variant still enforces the prose cap on the right pane", () => {
    const html = render(
      <DrawerLayout
        variant="single-column"
        left={<span>L</span>}
        right={<span>R</span>}
      />,
    );
    expect(html).toContain("max-w-[680px]");
  });

  it("single-column variant omits the left pane wrapper when left is null", () => {
    const html = render(
      <DrawerLayout
        variant="single-column"
        left={null}
        right={<span>R</span>}
      />,
    );
    expect(html).not.toContain('data-drawer-pane="left"');
    expect(html).toContain('data-drawer-pane="right"');
  });

  it("renders complex React children in both panes", () => {
    const html = render(
      <DrawerLayout
        left={
          <ul>
            <li>meta-a</li>
            <li>meta-b</li>
          </ul>
        }
        right={
          <article>
            <h1>Title</h1>
            <p>Body copy</p>
          </article>
        }
      />,
    );
    expect(html).toContain("meta-a");
    expect(html).toContain("meta-b");
    expect(html).toContain("Title");
    expect(html).toContain("Body copy");
  });
});
