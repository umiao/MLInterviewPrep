import { useMemo, useCallback, useEffect, useRef, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useSystemDesignNotes } from "../hooks/useSystemDesignNotes";
import MarkdownPreview from "../components/ui/MarkdownPreview";
import ImageLightbox from "../components/ui/ImageLightbox";
import PrevNextNav from "../components/ui/PrevNextNav";
import SlideOverPanel from "../components/ui/SlideOverPanel";
import type {
  SystemDesign,
  SystemDesignSummary,
  SystemDesignSection,
} from "../types/system-design";
import { SECTION_LABELS } from "../types/system-design";

const SECTIONS = Object.keys(SECTION_LABELS) as SystemDesignSection[];

/**
 * Full-screen system design detail page at /system-design/:slug.
 * Single scrollable page with all sections + sticky bookmark nav.
 */
export default function SystemDesignDetail() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  const { data: design, isLoading } = useQuery<SystemDesign>({
    queryKey: ["system-design", slug],
    queryFn: () => api.get<SystemDesign>(`/system-designs/${slug}`),
    enabled: !!slug,
  });

  // Fetch all modules for prev/next navigation by display_order
  const { data: allDesigns } = useQuery<SystemDesignSummary[]>({
    queryKey: ["system-designs"],
    queryFn: () => api.get<SystemDesignSummary[]>("/system-designs"),
    staleTime: 60_000,
  });

  const { prevDesign, nextDesign } = useMemo(() => {
    if (!allDesigns?.length || !slug)
      return { prevDesign: null, nextDesign: null };
    const sorted = [...allDesigns].sort(
      (a, b) => a.display_order - b.display_order,
    );
    const idx = sorted.findIndex((d) => d.slug === slug);
    return {
      prevDesign: idx > 0 ? sorted[idx - 1] : null,
      nextDesign: idx < sorted.length - 1 ? sorted[idx + 1] : null,
    };
  }, [allDesigns, slug]);

  const handleDesignNav = useCallback(
    (id: number | string) => navigate(`/system-design/${id}`),
    [navigate],
  );

  const {
    mode,
    switchMode,
    highlightedSection,
    setHighlightedSection,
    sectionContents,
    updateSection,
    saveStatuses,
    aggregateSaveStatus,
    retrySection,
  } = useSystemDesignNotes({
    slug: slug ?? "",
    initialData: design ?? null,
  });

  // --- IntersectionObserver for bookmark highlighting ---
  const sectionRefs = useRef<Record<string, HTMLElement | null>>({});
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Mobile (<lg) drawer state for the section TOC.
  const [tocDrawerOpen, setTocDrawerOpen] = useState(false);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const observer = new IntersectionObserver(
      (entries) => {
        // Find the topmost visible section
        let topEntry: IntersectionObserverEntry | null = null;
        for (const entry of entries) {
          if (entry.isIntersecting) {
            if (
              !topEntry ||
              entry.boundingClientRect.top < topEntry.boundingClientRect.top
            ) {
              topEntry = entry;
            }
          }
        }
        if (topEntry?.target) {
          const sectionId = topEntry.target.getAttribute("data-section");
          if (sectionId) {
            setHighlightedSection(sectionId as SystemDesignSection);
          }
        }
      },
      {
        root: container,
        rootMargin: "-10% 0px -80% 0px",
        threshold: 0,
      },
    );

    for (const section of SECTIONS) {
      const el = sectionRefs.current[section];
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, [design, setHighlightedSection]);

  /** Smooth-scroll to a section within the scroll container. */
  const scrollToSection = useCallback(
    (section: SystemDesignSection, opts?: { closeDrawer?: boolean }) => {
      const el = sectionRefs.current[section];
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      if (opts?.closeDrawer) setTocDrawerOpen(false);
    },
    [],
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading...
      </div>
    );
  }

  if (!design) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <p className="text-gray-500">System design module not found.</p>
        <Link
          to="/system-design"
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          Back to System Design
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Sticky header */}
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
        <Link
          to="/system-design"
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          &larr; System Design
        </Link>

        <h1 className="text-lg font-semibold text-gray-800">{design.title}</h1>

        <div className="flex items-center gap-3">
          <PrevNextNav
            prev={
              prevDesign
                ? { id: prevDesign.slug, label: prevDesign.title }
                : null
            }
            next={
              nextDesign
                ? { id: nextDesign.slug, label: nextDesign.title }
                : null
            }
            onNavigate={handleDesignNav}
            enableKeyboard={mode === "preview"}
          />

          {/* Mode toggle */}
          <div className="flex gap-1">
            <button
              onClick={() => switchMode("preview")}
              className={`text-sm px-3 py-1.5 rounded ${
                mode === "preview"
                  ? "bg-blue-100 text-blue-700 font-medium"
                  : "text-gray-500 hover:bg-gray-100"
              }`}
            >
              Preview
            </button>
            <button
              onClick={() => switchMode("edit")}
              className={`text-sm px-3 py-1.5 rounded ${
                mode === "edit"
                  ? "bg-blue-100 text-blue-700 font-medium"
                  : "text-gray-500 hover:bg-gray-100"
              }`}
            >
              Edit
            </button>
          </div>

          {/* Aggregate save status */}
          <span className="text-sm min-w-[5rem] text-right">
            {aggregateSaveStatus === "saving" && (
              <span className="text-gray-400">Saving...</span>
            )}
            {aggregateSaveStatus === "saved" && (
              <span className="text-green-600">Saved</span>
            )}
            {aggregateSaveStatus === "error" && (
              <span className="text-red-600">Save failed</span>
            )}
          </span>
        </div>
      </header>

      {/* Scrollable content area. The desktop TOC is rendered as a sibling
          (position:fixed) below so its containing block is the viewport,
          NOT the max-w-6xl flex container -- otherwise sticky/absolute
          release at flex-bottom and the TOC vanishes on the last section. */}
      <div ref={scrollContainerRef} className="flex-1 overflow-auto min-h-0">
        <div className="max-w-6xl mx-auto">
          <div className="min-w-0 px-6 py-6 space-y-10 lg:pr-60">
            {SECTIONS.map((section) => (
              <section
                key={section}
                ref={(el) => {
                  sectionRefs.current[section] = el;
                }}
                data-section={section}
                className="scroll-mt-16"
              >
                {/* Section header */}
                <div className="flex items-center gap-3 mb-4">
                  <h2 className="text-xl font-semibold text-gray-800">
                    {SECTION_LABELS[section]}
                  </h2>
                  {mode === "edit" && saveStatuses[section] === "saving" && (
                    <span className="text-xs text-gray-400">Saving...</span>
                  )}
                  {mode === "edit" && saveStatuses[section] === "saved" && (
                    <span className="text-xs text-green-600">Saved</span>
                  )}
                  {mode === "edit" && saveStatuses[section] === "error" && (
                    <span className="text-xs text-red-600">
                      Failed{" "}
                      <button
                        onClick={() => retrySection(section)}
                        className="underline hover:text-red-800"
                      >
                        retry
                      </button>
                    </span>
                  )}
                </div>

                {/* Architecture diagram inline */}
                {section === "architecture" && design.diagram_filename && (
                  <ImageLightbox
                    src={`/static/system-designs/${design.diagram_filename}`}
                    className="w-full max-h-96 object-contain mb-6 rounded border"
                    alt={`${design.title} architecture diagram`}
                  />
                )}

                {/* Content: edit or preview */}
                {mode === "edit" ? (
                  <textarea
                    value={sectionContents[section]}
                    onChange={(e) => updateSection(section, e.target.value)}
                    className="w-full min-h-[200px] border border-gray-300 rounded px-4 py-3 text-base font-mono resize-y"
                    placeholder={`Write ${SECTION_LABELS[section]} content here...`}
                  />
                ) : (
                  <div className="prep-prose">
                    {sectionContents[section] ? (
                      <MarkdownPreview markdown={sectionContents[section]} />
                    ) : (
                      <p className="text-gray-400 italic">
                        No content yet. Switch to Edit mode to add content.
                      </p>
                    )}
                  </div>
                )}
              </section>
            ))}
          </div>
        </div>
      </div>

      {/* Desktop TOC: fixed to viewport so it remains visible at the
          bottom-most section (not constrained by flex parent). The
          right offset hugs the right edge of the centered max-w-6xl
          content on wide screens, falling back to a 1rem gutter on
          narrower screens. */}
      <aside
        className="hidden lg:block fixed top-20 z-10 w-52 max-h-[calc(100vh-6rem)] overflow-y-auto"
        style={{ right: "max(1rem, calc((100vw - 72rem) / 2 + 1rem))" }}
        aria-label="Section navigation"
      >
        <nav>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
            目录 (Sections)
          </p>
          <ul className="space-y-1">
            {SECTIONS.map((section) => (
              <li key={section}>
                <button
                  onClick={() => scrollToSection(section)}
                  className={`block w-full text-left text-sm px-2 py-1 rounded transition-colors truncate ${
                    highlightedSection === section
                      ? "bg-blue-50 text-blue-700 font-medium"
                      : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                  }`}
                  title={SECTION_LABELS[section]}
                >
                  {SECTION_LABELS[section]}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Mobile (<lg) toggle: vertical "Sections" tab pinned to right edge
          mid-height. Tapping opens the drawer below. */}
      <button
        type="button"
        onClick={() => setTocDrawerOpen(true)}
        className="lg:hidden fixed right-0 top-1/2 -translate-y-1/2 z-20 bg-blue-600 text-white text-xs font-medium px-2 py-3 rounded-l-md shadow-md hover:bg-blue-700"
        style={{ writingMode: "vertical-rl" }}
        aria-label="Open sections menu"
      >
        目录
      </button>

      {/* Mobile drawer reuses SlideOverPanel for consistency. */}
      <SlideOverPanel
        open={tocDrawerOpen}
        onClose={() => setTocDrawerOpen(false)}
        title="目录 (Sections)"
        width="max-w-xs"
      >
        <ul className="space-y-1">
          {SECTIONS.map((section) => (
            <li key={section}>
              <button
                onClick={() =>
                  scrollToSection(section, { closeDrawer: true })
                }
                className={`block w-full text-left text-sm px-3 py-2 rounded transition-colors ${
                  highlightedSection === section
                    ? "bg-blue-50 text-blue-700 font-medium"
                    : "text-gray-700 hover:bg-gray-50"
                }`}
              >
                {SECTION_LABELS[section]}
              </button>
            </li>
          ))}
        </ul>
      </SlideOverPanel>
    </div>
  );
}
