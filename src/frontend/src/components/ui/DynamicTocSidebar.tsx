import { useState, useEffect, useCallback, useMemo } from "react";
import type { TocHeading } from "../../utils/slugify";

interface DynamicTocSidebarProps {
  headings: TocHeading[];
  scrollContainer: HTMLElement | null;
}

/**
 * Dynamic TOC sidebar built from extracted headings.
 * Shows h1 headings by default; h2 items are collapsed under each h1.
 */
export default function DynamicTocSidebar({ headings, scrollContainer }: DynamicTocSidebarProps) {
  const [activeId, setActiveId] = useState<string>("");
  const [collapsed, setCollapsed] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  // Deduplicate headings by id and filter to h1/h2
  const tocItems = useMemo(() => {
    const seen = new Set<string>();
    return headings
      .filter((h) => h.level <= 2)
      .filter((h) => {
        if (seen.has(h.id)) return false;
        seen.add(h.id);
        return true;
      });
  }, [headings]);

  // Group: list of { h1, children: h2[] }
  const sections = useMemo(() => {
    const result: { h1: TocHeading; children: TocHeading[] }[] = [];
    for (const item of tocItems) {
      if (item.level === 1) {
        result.push({ h1: item, children: [] });
      } else if (result.length > 0) {
        result[result.length - 1].children.push(item);
      }
    }
    return result;
  }, [tocItems]);

  // Track which heading is currently visible
  useEffect(() => {
    if (!scrollContainer || tocItems.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        }
      },
      {
        root: scrollContainer,
        rootMargin: "0px 0px -70% 0px",
      }
    );

    const elements: Element[] = [];
    for (const item of tocItems) {
      const el = scrollContainer.querySelector(`#${CSS.escape(item.id)}`);
      if (el) {
        observer.observe(el);
        elements.push(el);
      }
    }

    return () => {
      for (const el of elements) observer.unobserve(el);
      observer.disconnect();
    };
  }, [scrollContainer, tocItems]);

  const handleClick = useCallback(
    (id: string) => {
      if (!scrollContainer) return;
      const el = scrollContainer.querySelector(`#${CSS.escape(id)}`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    },
    [scrollContainer]
  );

  const toggleSection = useCallback((h1Id: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(h1Id)) next.delete(h1Id);
      else next.add(h1Id);
      return next;
    });
  }, []);

  if (sections.length === 0) return null;

  return (
    <aside className="acronym-sidebar">
      <div className="acronym-sidebar-header">
        <span className="acronym-sidebar-title">Table of Contents</span>
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="acronym-sidebar-toggle"
          title={collapsed ? "Expand" : "Collapse"}
        >
          {collapsed ? "+" : "\u2212"}
        </button>
      </div>

      {!collapsed && (
        <nav className="acronym-sidebar-nav">
          {sections.map(({ h1, children }) => {
            const isExpanded = expandedSections.has(h1.id);
            const hasChildren = children.length > 0;
            return (
              <div key={h1.id}>
                <div className="flex items-center">
                  {hasChildren && (
                    <button
                      className="text-xs text-gray-400 hover:text-gray-600 px-1 shrink-0"
                      onClick={() => toggleSection(h1.id)}
                      title={isExpanded ? "Collapse" : "Expand"}
                    >
                      {isExpanded ? "\u25BC" : "\u25B6"}
                    </button>
                  )}
                  <button
                    className={`acronym-entry w-full text-left font-semibold ${
                      activeId === h1.id ? "acronym-topic-active" : ""
                    } ${!hasChildren ? "pl-4" : ""}`}
                    onClick={() => handleClick(h1.id)}
                    title={h1.text}
                  >
                    <span className="acronym-full truncate block">
                      {h1.text.length > 40 ? h1.text.slice(0, 38) + "..." : h1.text}
                    </span>
                  </button>
                </div>
                {isExpanded && children.map((child) => (
                  <button
                    key={child.id}
                    className={`acronym-entry w-full text-left pl-7 text-sm ${
                      activeId === child.id ? "acronym-topic-active" : ""
                    }`}
                    onClick={() => handleClick(child.id)}
                    title={child.text}
                  >
                    <span className="acronym-full truncate block">
                      {child.text.length > 40 ? child.text.slice(0, 38) + "..." : child.text}
                    </span>
                  </button>
                ))}
              </div>
            );
          })}
        </nav>
      )}
    </aside>
  );
}
