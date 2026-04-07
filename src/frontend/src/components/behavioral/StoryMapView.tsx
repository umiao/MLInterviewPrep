import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../utils/api";
import MarkdownPreview from "../ui/MarkdownPreview";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface ArcExample {
  example_id: string;
  role_zh: string;
  principles: string[];
  title: string;
  source_project: string | null;
  situation: string | null;
  link_count: number;
  principle_tags_live: string[];
}

interface CrossArcConnection {
  from: string;
  to: string;
  note_zh: string;
}

interface StoryArc {
  arc_id: string;
  title_zh: string;
  title_en: string;
  color: string;
  narrative_zh: string;
  examples: ArcExample[];
  improvement_notes: string;
}

interface StoryArcsData {
  arcs: StoryArc[];
  cross_arc_connections: CrossArcConnection[];
  principle_legend: Record<string, string>;
}

/* ------------------------------------------------------------------ */
/*  Color utilities                                                    */
/* ------------------------------------------------------------------ */

const ARC_COLORS: Record<string, { bg: string; border: string; badge: string; light: string; text: string }> = {
  blue:    { bg: "bg-blue-50",    border: "border-blue-400",    badge: "bg-blue-100 text-blue-800",    light: "bg-blue-100", text: "text-blue-700" },
  emerald: { bg: "bg-emerald-50", border: "border-emerald-400", badge: "bg-emerald-100 text-emerald-800", light: "bg-emerald-100", text: "text-emerald-700" },
  purple:  { bg: "bg-purple-50",  border: "border-purple-400",  badge: "bg-purple-100 text-purple-800",  light: "bg-purple-100", text: "text-purple-700" },
  amber:   { bg: "bg-amber-50",   border: "border-amber-400",   badge: "bg-amber-100 text-amber-800",   light: "bg-amber-100", text: "text-amber-700" },
  red:     { bg: "bg-red-50",     border: "border-red-400",     badge: "bg-red-100 text-red-800",     light: "bg-red-100", text: "text-red-700" },
  cyan:    { bg: "bg-cyan-50",    border: "border-cyan-400",    badge: "bg-cyan-100 text-cyan-800",    light: "bg-cyan-100", text: "text-cyan-700" },
};

/* ------------------------------------------------------------------ */
/*  Principle Badge                                                    */
/* ------------------------------------------------------------------ */

function PrincipleTag({ tag, legend }: { tag: string; legend: Record<string, string> }) {
  const label = legend[tag] || tag;
  return (
    <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200">
      {label}
    </span>
  );
}

/* ------------------------------------------------------------------ */
/*  Example Card within an Arc                                         */
/* ------------------------------------------------------------------ */

function ArcExampleCard({
  ex,
  legend,
  arcColor,
  isLast,
  onExampleClick,
}: {
  ex: ArcExample;
  legend: Record<string, string>;
  arcColor: string;
  isLast: boolean;
  onExampleClick?: (exampleId: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const colors = ARC_COLORS[arcColor] ?? ARC_COLORS.blue;

  return (
    <div className="flex gap-3">
      {/* Timeline connector */}
      <div className="flex flex-col items-center shrink-0 w-8">
        <div className={`w-3 h-3 rounded-full ${colors.light} border-2 ${colors.border} shrink-0 mt-4`} />
        {!isLast && <div className={`w-0.5 flex-1 ${colors.light}`} />}
      </div>

      {/* Card */}
      <div
        role="button"
        tabIndex={0}
        onClick={() => setExpanded((v) => !v)}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") setExpanded((v) => !v); }}
        className={`flex-1 mb-3 p-4 rounded-lg border bg-white ${expanded ? `${colors.border} border-2 shadow-md` : "border-gray-200 hover:shadow-sm"} transition-all text-left cursor-pointer`}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-xs font-bold ${colors.text}`}>{ex.example_id}</span>
              {onExampleClick ? (
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); onExampleClick(ex.example_id); }}
                  className={`text-sm font-bold text-gray-900 truncate hover:underline ${colors.text} hover:opacity-80 transition-colors`}
                  title="View full STAR example"
                >
                  {ex.title} &#8599;
                </button>
              ) : (
                <span className="text-sm font-bold text-gray-900 truncate">{ex.title}</span>
              )}
            </div>
            <p className="text-sm text-gray-700 leading-relaxed">{ex.role_zh}</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-xs text-gray-400">{ex.link_count} links</span>
            <span className="text-gray-400 text-xs">{expanded ? "^" : "v"}</span>
          </div>
        </div>

        {expanded && (
          <div className="mt-3 pt-3 border-t border-gray-100 space-y-2">
            {ex.situation && (
              <p className="text-sm text-gray-600 leading-relaxed italic">
                {ex.situation.length > 300 ? ex.situation.slice(0, 300) + "..." : ex.situation}
              </p>
            )}
            {onExampleClick && (
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); onExampleClick(ex.example_id); }}
                className={`text-xs font-semibold ${colors.text} hover:underline`}
              >
                View full example &#8599;
              </button>
            )}
            <div className="flex flex-wrap gap-1 mt-2">
              <span className="text-xs text-gray-400 mr-1 self-center">Principles:</span>
              {ex.principles.map((p) => (
                <PrincipleTag key={p} tag={p} legend={legend} />
              ))}
            </div>
            {ex.principle_tags_live.length > ex.principles.length && (
              <div className="flex flex-wrap gap-1">
                <span className="text-xs text-gray-400 mr-1 self-center">+ DB tags:</span>
                {ex.principle_tags_live
                  .filter((t) => !ex.principles.includes(t))
                  .map((p) => (
                    <PrincipleTag key={p} tag={p} legend={legend} />
                  ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Arc Section                                                        */
/* ------------------------------------------------------------------ */

function ArcSection({ arc, legend, onExampleClick }: { arc: StoryArc; legend: Record<string, string>; onExampleClick?: (exampleId: string) => void }) {
  const [narrativeExpanded, setNarrativeExpanded] = useState(true);
  const [tipsExpanded, setTipsExpanded] = useState(false);
  const colors = ARC_COLORS[arc.color] ?? ARC_COLORS.blue;

  // Collect all unique principles across the arc
  const allPrinciples = Array.from(
    new Set(arc.examples.flatMap((ex) => ex.principles))
  );

  return (
    <div className={`rounded-xl border-2 ${colors.border} ${colors.bg} p-5 mb-6`}>
      {/* Arc Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{arc.title_zh}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{arc.title_en} -- {arc.examples.length} stories</p>
        </div>
        <div className="flex flex-wrap gap-1 max-w-xs justify-end">
          {allPrinciples.slice(0, 5).map((p) => (
            <span key={p} className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${colors.badge}`}>
              {legend[p] || p}
            </span>
          ))}
          {allPrinciples.length > 5 && (
            <span className="text-xs text-gray-400 self-center">+{allPrinciples.length - 5}</span>
          )}
        </div>
      </div>

      {/* Narrative */}
      <button
        type="button"
        onClick={() => setNarrativeExpanded((v) => !v)}
        className="w-full text-left mb-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-semibold text-gray-600">
            {narrativeExpanded ? "v" : ">"} 完整叙述
          </span>
        </div>
      </button>
      {narrativeExpanded && (
        <div className="mb-4 bg-white rounded-lg p-4 border border-gray-200 text-sm text-gray-800 leading-relaxed">
          <MarkdownPreview markdown={arc.narrative_zh} />
        </div>
      )}

      {/* Timeline of examples */}
      <div className="ml-1">
        {arc.examples.map((ex, i) => (
          <ArcExampleCard
            key={ex.example_id}
            ex={ex}
            legend={legend}
            arcColor={arc.color}
            isLast={i === arc.examples.length - 1}
            onExampleClick={onExampleClick}
          />
        ))}
      </div>

      {/* Improvement Notes */}
      {arc.improvement_notes && (
        <button
          type="button"
          onClick={() => setTipsExpanded((v) => !v)}
          className="w-full text-left mt-3"
        >
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-amber-700">
              {tipsExpanded ? "v" : ">"} 改进建议
            </span>
          </div>
          {tipsExpanded && (
            <div className="mt-2 bg-amber-50 rounded-lg p-3 border border-amber-200">
              <p className="text-sm text-amber-900 leading-relaxed">{arc.improvement_notes}</p>
            </div>
          )}
        </button>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Cross-Arc Connections                                              */
/* ------------------------------------------------------------------ */

function CrossArcConnections({ connections }: { connections: CrossArcConnection[] }) {
  if (connections.length === 0) return null;

  return (
    <div className="rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-5 mb-6">
      <h3 className="text-lg font-bold text-gray-800 mb-3">Cross-Arc Connections</h3>
      <div className="space-y-2">
        {connections.map((c, i) => (
          <div key={i} className="flex items-center gap-3 text-sm">
            <span className="font-mono font-bold text-blue-600 shrink-0">{c.from}</span>
            <span className="text-gray-400">---</span>
            <span className="font-mono font-bold text-blue-600 shrink-0">{c.to}</span>
            <span className="text-gray-600">{c.note_zh}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main Component                                                     */
/* ------------------------------------------------------------------ */

export default function StoryMapView({ onExampleClick }: { onExampleClick?: (exampleId: string) => void } = {}) {
  const { data, isLoading, error } = useQuery<StoryArcsData>({
    queryKey: ["story-arcs"],
    queryFn: () => api.get<StoryArcsData>("/behavioral/story-arcs"),
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-48 bg-gray-100 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
        Failed to load story arcs data.
      </div>
    );
  }

  if (!data) return null;

  const legend = data.principle_legend;
  const totalStories = data.arcs.reduce((s, a) => s + a.examples.length, 0);
  const allPrinciples = new Set(data.arcs.flatMap((a) => a.examples.flatMap((e) => e.principles)));

  return (
    <div>
      {/* Summary bar */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6 flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Story Map (故事脉络)</h2>
          <p className="text-sm text-gray-500">
            {data.arcs.length} project arcs, {totalStories} stories, {allPrinciples.size} principles covered
          </p>
        </div>
        <div className="flex flex-wrap gap-1">
          {data.arcs.map((arc) => {
            const colors = ARC_COLORS[arc.color] ?? ARC_COLORS.blue;
            return (
              <a
                key={arc.arc_id}
                href={`#${arc.arc_id}`}
                className={`px-2 py-1 rounded text-xs font-semibold ${colors.badge} hover:opacity-80 transition-opacity`}
              >
                {arc.title_zh.split("(")[0].trim()}
              </a>
            );
          })}
        </div>
      </div>

      {/* Arc sections */}
      {data.arcs.map((arc) => (
        <div key={arc.arc_id} id={arc.arc_id}>
          <ArcSection arc={arc} legend={legend} onExampleClick={onExampleClick} />
        </div>
      ))}

      {/* Cross-Arc Connections */}
      <CrossArcConnections connections={data.cross_arc_connections} />

      {/* Principle Legend */}
      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <h3 className="text-lg font-bold text-gray-800 mb-3">Principle Legend (素质图例)</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
          {Object.entries(legend).map(([key, zh]) => (
            <div key={key} className="flex items-center gap-2 text-sm">
              <span className="font-mono text-xs text-gray-400 w-28 shrink-0 truncate">{key}</span>
              <span className="text-gray-700">{zh}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
