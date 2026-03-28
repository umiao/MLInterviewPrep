import { useState, useEffect, useCallback, useMemo } from "react";
import type { TocHeading } from "../../utils/slugify";

interface DocTocSidebarProps {
  headings: TocHeading[];
  scrollContainer: HTMLElement | null;
}

/** Extract keywords/acronyms from heading text (uppercase words >= 2 chars). */
function extractKeywords(headings: TocHeading[]): string[] {
  const seen = new Set<string>();
  const keywords: string[] = [];
  for (const h of headings) {
    // Match uppercase acronyms (2+ chars) and PascalCase terms
    const matches = h.text.match(/\b[A-Z][A-Z0-9]{1,}\b/g);
    if (matches) {
      for (const m of matches) {
        if (!seen.has(m)) {
          seen.add(m);
          keywords.push(m);
        }
      }
    }
  }
  return keywords;
}

/**
 * Floating sidebar TOC for large documents.
 * Consumes headings emitted by MarkdownPreview (single data source).
 * Uses IntersectionObserver with scrollContainer as root for active tracking.
 */
export default function DocTocSidebar({ headings, scrollContainer }: DocTocSidebarProps) {
  const [activeId, setActiveId] = useState<string>("");
  const [collapsed, setCollapsed] = useState(false);

  const keywords = useMemo(() => extractKeywords(headings), [headings]);

  // IntersectionObserver to track which heading is currently visible
  useEffect(() => {
    if (!scrollContainer || headings.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        // Find the first intersecting heading (topmost visible)
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
            break;
          }
        }
      },
      {
        root: scrollContainer,
        rootMargin: "0px 0px -70% 0px",
      }
    );

    // Observe all heading elements
    const elements: Element[] = [];
    for (const h of headings) {
      const el = scrollContainer.querySelector(`#${CSS.escape(h.id)}`);
      if (el) {
        observer.observe(el);
        elements.push(el);
      }
    }

    return () => {
      for (const el of elements) observer.unobserve(el);
      observer.disconnect();
    };
  }, [headings, scrollContainer]);

  const handleClick = useCallback(
    (id: string) => {
      if (!scrollContainer) return;
      const el = scrollContainer.querySelector(`#${CSS.escape(id)}`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
        setActiveId(id);
      }
    },
    [scrollContainer]
  );

  if (headings.length === 0) return null;

  return (
    <aside className="doc-toc-sidebar">
      <div className="doc-toc-header">
        <span className="doc-toc-title">Contents</span>
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="doc-toc-toggle"
          title={collapsed ? "Expand" : "Collapse"}
        >
          {collapsed ? "+" : "-"}
        </button>
      </div>

      {!collapsed && (
        <>
          <nav className="doc-toc-nav">
            {headings.map((h, i) => (
              <button
                key={`${h.id}-${i}`}
                onClick={() => handleClick(h.id)}
                className={`doc-toc-item doc-toc-level-${h.level} ${
                  activeId === h.id ? "doc-toc-active" : ""
                }`}
                title={h.text}
              >
                {h.text}
              </button>
            ))}
          </nav>

          {keywords.length > 0 && (
            <div className="doc-toc-keywords">
              <span className="doc-toc-keywords-label">Keywords</span>
              <div className="doc-toc-keywords-list">
                {keywords.map((kw) => (
                  <span key={kw} className="doc-toc-keyword">{kw}</span>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </aside>
  );
}
