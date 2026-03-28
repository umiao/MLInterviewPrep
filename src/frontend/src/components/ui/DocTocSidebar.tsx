import { useState, useEffect, useCallback } from "react";
import { acronymRegistry, type AcronymGroup } from "../../utils/acronymRegistry";

interface DocTocSidebarProps {
  scrollContainer: HTMLElement | null;
}

/**
 * Floating sidebar showing curated acronyms grouped by topic.
 * Always sticky. Each acronym links to its section in the document.
 * Topic with current scroll position is highlighted.
 */
export default function DocTocSidebar({ scrollContainer }: DocTocSidebarProps) {
  const [activeTopicIdx, setActiveTopicIdx] = useState(0);
  const [collapsed, setCollapsed] = useState(false);

  // Track which topic section is currently visible
  useEffect(() => {
    if (!scrollContainer) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const idx = acronymRegistry.findIndex(
              (g) => g.topicAnchorId === entry.target.id
            );
            if (idx !== -1) setActiveTopicIdx(idx);
          }
        }
      },
      {
        root: scrollContainer,
        rootMargin: "0px 0px -70% 0px",
      }
    );

    const elements: Element[] = [];
    for (const group of acronymRegistry) {
      const el = scrollContainer.querySelector(`#${CSS.escape(group.topicAnchorId)}`);
      if (el) {
        observer.observe(el);
        elements.push(el);
      }
    }

    return () => {
      for (const el of elements) observer.unobserve(el);
      observer.disconnect();
    };
  }, [scrollContainer]);

  const handleClick = useCallback(
    (anchorId: string) => {
      if (!scrollContainer) return;
      const el = scrollContainer.querySelector(`#${CSS.escape(anchorId)}`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    },
    [scrollContainer]
  );

  return (
    <aside className="acronym-sidebar">
      <div className="acronym-sidebar-header">
        <span className="acronym-sidebar-title">Acronym Index</span>
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
          {acronymRegistry.map((group, gi) => (
            <TopicGroup
              key={group.topic}
              group={group}
              isActive={gi === activeTopicIdx}
              onClickAcronym={handleClick}
            />
          ))}
        </nav>
      )}
    </aside>
  );
}

function TopicGroup({
  group,
  isActive,
  onClickAcronym,
}: {
  group: AcronymGroup;
  isActive: boolean;
  onClickAcronym: (anchorId: string) => void;
}) {
  return (
    <div className={`acronym-topic ${isActive ? "acronym-topic-active" : ""}`}>
      <button
        className="acronym-topic-title"
        onClick={() => onClickAcronym(group.topicAnchorId)}
      >
        {group.topic}
      </button>
      <div className="acronym-chips">
        {group.entries.map((entry) => (
          <button
            key={entry.abbr}
            className="acronym-chip"
            title={`${entry.abbr} — ${entry.full}`}
            onClick={() => onClickAcronym(entry.anchorId)}
          >
            {entry.abbr}
          </button>
        ))}
      </div>
    </div>
  );
}
