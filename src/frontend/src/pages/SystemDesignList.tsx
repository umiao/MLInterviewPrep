import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type { SystemDesignSummary } from "../types/system-design";
import ImageLightbox from "../components/ui/ImageLightbox";

const NARRATIVE = `My core work at eBay has been systematically transforming search ranking from independent pointwise scoring into page-level resource allocation. Starting with the data foundation (PBE Pipeline for unbiased training data), I built the allocation framework (Ranking-as-Allocation with diversity constraints), extended it to multi-module page composition (Module Arbitration marketplace), and most recently brought GenAI into the production search path (LLM Artifact Orchestration). Each project builds on the last -- together they represent a complete evolution from 'rank items by relevance score' to 'optimize the entire user experience as a constrained allocation problem.'`;

const READING_ORDER =
  "Interview reading order: PBE Pipeline -> Ranking-as-Allocation -> Module Arbitration -> LLM Orchestration";

export default function SystemDesignList() {
  const navigate = useNavigate();

  const {
    data: modules = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["system-designs"],
    queryFn: () => api.get<SystemDesignSummary[]>("/system-designs"),
  });

  const sorted = [...modules].sort(
    (a, b) => a.display_order - b.display_order,
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">System Design</h1>

      {/* Unified narrative */}
      <blockquote className="border-l-4 border-blue-400 bg-blue-50 rounded-r-lg px-5 py-4 mb-2 text-sm text-gray-700 leading-relaxed italic">
        {NARRATIVE}
      </blockquote>
      <p className="text-xs text-gray-400 mb-8">{READING_ORDER}</p>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-4">
          {error instanceof Error ? error.message : "Failed to load modules"}
        </div>
      )}

      {/* Loading state */}
      {isLoading && (
        <div className="text-gray-500 py-12 text-center">Loading...</div>
      )}

      {/* Empty state */}
      {!isLoading && !error && sorted.length === 0 && (
        <div className="text-gray-400 py-12 text-center">
          No system design modules yet.
        </div>
      )}

      {/* 2x2 card grid */}
      {!isLoading && sorted.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {sorted.map((mod) => (
            <button
              key={mod.id}
              onClick={() => navigate(`/system-design/${mod.slug}`)}
              className="text-left bg-white rounded-lg shadow hover:shadow-md transition-shadow border border-gray-200 overflow-hidden"
            >
              {mod.diagram_filename && (
                <div className="w-full bg-gray-50 flex items-center justify-center"
                     style={{ height: 200 }}>
                  <ImageLightbox
                    src={`/static/system-designs/${mod.diagram_filename}`}
                    alt={`${mod.title} diagram`}
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
              )}
              <div className="px-4 py-3">
                <h2 className="text-lg font-semibold text-gray-800">
                  {mod.title}
                </h2>
                {mod.subtitle && (
                  <p className="text-sm text-gray-500 mt-1">{mod.subtitle}</p>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
