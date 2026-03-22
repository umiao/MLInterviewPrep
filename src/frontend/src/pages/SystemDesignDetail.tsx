import { useMemo, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useSystemDesignNotes } from "../hooks/useSystemDesignNotes";
import MarkdownPreview from "../components/ui/MarkdownPreview";
import ImageLightbox from "../components/ui/ImageLightbox";
import PrevNextNav from "../components/ui/PrevNextNav";
import type {
  SystemDesign,
  SystemDesignSummary,
  SystemDesignSection,
} from "../types/system-design";
import { SECTION_LABELS } from "../types/system-design";

const SECTIONS = Object.keys(SECTION_LABELS) as SystemDesignSection[];

/**
 * Full-screen system design detail page at /system-design/:slug.
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
    activeSection,
    switchSection,
    notes,
    setNotes,
    mode,
    switchMode,
    saveStatus,
    setSaveStatus,
    handleRetry,
  } = useSystemDesignNotes({
    slug: slug ?? "",
    initialData: design ?? null,
  });

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

          {/* Save status */}
          <span className="text-sm min-w-[5rem] text-right">
            {saveStatus === "saving" && (
              <span className="text-gray-400">Saving...</span>
            )}
            {saveStatus === "saved" && (
              <span className="text-green-600">Saved</span>
            )}
            {saveStatus === "error" && (
              <span className="text-red-600">
                Failed{" "}
                <button
                  onClick={handleRetry}
                  className="underline hover:text-red-800"
                >
                  retry
                </button>
              </span>
            )}
          </span>
        </div>
      </header>

      {/* Tab bar */}
      <div className="border-b border-gray-200 px-6 py-2 bg-white shrink-0">
        <div className="flex gap-1 overflow-x-auto">
          {SECTIONS.map((section) => (
            <button
              key={section}
              onClick={() => switchSection(section)}
              className={`text-sm px-3 py-1 rounded whitespace-nowrap ${
                activeSection === section
                  ? "bg-gray-100 text-gray-800 font-medium"
                  : "text-gray-500 hover:bg-gray-50"
              }`}
            >
              {SECTION_LABELS[section]}
            </button>
          ))}
        </div>
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-auto p-6 flex flex-col min-h-0">
        {/* Diagram image on Architecture tab */}
        {activeSection === "architecture" && design.diagram_filename && (
          <ImageLightbox
            src={`/static/system-designs/${design.diagram_filename}`}
            className="w-full max-h-96 object-contain mb-6 rounded border"
            alt={`${design.title} architecture diagram`}
          />
        )}

        {mode === "edit" ? (
          <textarea
            value={notes}
            onChange={(e) => {
              setNotes(e.target.value);
              if (saveStatus === "saved" || saveStatus === "error") {
                setSaveStatus("idle");
              }
            }}
            className="flex-1 min-h-0 w-full border border-gray-300 rounded px-4 py-3 text-base font-mono resize-none"
            placeholder="Write markdown content here..."
          />
        ) : (
          <div className="prep-prose">
            {notes ? (
              <MarkdownPreview markdown={notes} />
            ) : (
              <p className="text-gray-400 italic">
                No content yet. Switch to Edit mode to add content.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
