import { useState, useEffect, useCallback, useMemo } from "react";
import type { TocHeading } from "../../utils/slugify";

interface DynamicTocSidebarProps {
  headings: TocHeading[];
  scrollContainer: HTMLElement | null;
  /** Parent level for grouping (default 1 = h1 parents, h2 children).
   *  Set 2 to use h2 as parents and h3 as children — appropriate for
   *  per-concept H3-keyed pages where the top-level h1 is the page title. */
  parentLevel?: 1 | 2;
  /** When true, render a search input that filters items by case-insensitive
   *  text match across both parents and children. */
  filterable?: boolean;
}

/**
 * Dynamic TOC sidebar built from extracted headings.
 * Shows parent-level headings; child-level items collapse under each parent.
 */
export default function DynamicTocSidebar({
  headings,
  scrollContainer,
  parentLevel = 1,
  filterable = false,
}: DynamicTocSidebarProps) {
  const [activeId, setActiveId] = useState<string>("");
  const [collapsed, setCollapsed] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [filterQuery, setFilterQuery] = useState("");

  const childLevel = parentLevel + 1;

  // Deduplicate headings by id and keep only parent + immediate child levels.
  const tocItems = useMemo(() => {
    const seen = new Set<string>();
    return headings
      .filter((h) => h.level === parentLevel || h.level === childLevel)
      .filter((h) => {
        if (seen.has(h.id)) return false;
        seen.add(h.id);
        return true;
      });
  }, [headings, parentLevel, childLevel]);

  // Group: list of { h1, children: h2[] }
  const sections = useMemo(() => {
    const result: { h1: TocHeading; children: TocHeading[] }[] = [];
    for (const item of tocItems) {
      if (item.level === parentLevel) {
        result.push({ h1: item, children: [] });
      } else if (result.length > 0) {
        result[result.length - 1].children.push(item);
      }
    }
    return result;
  }, [tocItems, parentLevel]);

  // Apply search filter (matches parent OR child text).
  const filteredSections = useMemo(() => {
    if (!filterable || !filterQuery.trim()) return sections;
    const q = filterQuery.toLowerCase();
    return sections
      .map(({ h1, children }) => {
        const childMatches = children.filter((c) => c.text.toLowerCase().includes(q));
        const h1Matches = h1.text.toLowerCase().includes(q);
        if (h1Matches) return { h1, children };
        if (childMatches.length > 0) return { h1, children: childMatches };
        return null;
      })
      .filter((s): s is { h1: TocHeading; children: TocHeading[] } => s !== null);
  }, [sections, filterable, filterQuery]);

  // When filtering, auto-expand all sections with child matches so hits stay visible.
  // Derive during render rather than via setState-in-effect.
  const effectiveExpanded = useMemo(() => {
    if (filterable && filterQuery.trim()) {
      return new Set(filteredSections.map((s) => s.h1.id));
    }
    return expandedSections;
  }, [filterable, filterQuery, filteredSections, expandedSections]);

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
        <span className="acronym-sidebar-title">
          {filterable ? `\u5173\u952e\u8bcd\u5bfc\u822a (${sections.length})` : "Table of Contents"}
        </span>
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="acronym-sidebar-toggle"
          title={collapsed ? "Expand" : "Collapse"}
        >
          {collapsed ? "+" : "\u2212"}
        </button>
      </div>

      {!collapsed && filterable && (
        <div className="px-3 pb-2">
          <input
            type="search"
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            placeholder="\u641c\u7d22\u5173\u952e\u8bcd (e.g., DCN, MMOE, HNSW)"
            className="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:border-blue-400 bg-white"
          />
        </div>
      )}

      {!collapsed && (
        <nav className="acronym-sidebar-nav">
          {filteredSections.length === 0 && filterable && filterQuery.trim() && (
            <div className="px-3 py-2 text-xs text-gray-400 italic">\u65e0\u5339\u914d\u5173\u952e\u8bcd</div>
          )}
          {filteredSections.map(({ h1, children }) => {
            const isExpanded = effectiveExpanded.has(h1.id);
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
