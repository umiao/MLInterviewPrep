import { useCallback, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { api } from "../utils/api";
import StoryMapView from "../components/behavioral/StoryMapView";
import SlideOverPanel from "../components/ui/SlideOverPanel";
import ExampleDrawerContent from "../components/behavioral/ExampleDrawerContent";
import ThemeFilterSidebar from "../components/behavioral/ThemeFilterSidebar";
import GoldenToggleButton from "../components/ui/GoldenToggleButton";
import GoldenBadge from "../components/ui/GoldenBadge";
import { goldenCardClass } from "../utils/goldenStyle";
import { parsePitch } from "../utils/parsePitch";
import type {
  BehavioralExample,
  BehavioralThemeSummary,
  ThemeMode,
  ThemeTag,
} from "../types/behavioral";
import { toggleThemeInState } from "../utils/themeFilter";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface BehavioralQuestion {
  id: number;
  question_id: string;
  text: string;
  category_id: string;
  category_name: string;
  original_category: string | null;
  example_count: number;
  theme_tags?: ThemeTag[];
}

interface CategorySummary {
  category_id: string;
  category_name: string;
  question_count: number;
  covered_count: number;
  example_count: number;
}

interface CoverageCell {
  example_id: string;
  example_title: string;
  category_id: string;
  category_name: string;
  link_count: number;
}

interface GapData {
  total_questions: number;
  uncovered_count: number;
  coverage_pct: number;
  uncovered_by_category: Record<string, { question_id: string; text: string; category_name: string }[]>;
}

/* ------------------------------------------------------------------ */
/* Category name map (abbrev -> full name)                             */
/* ------------------------------------------------------------------ */

const CATEGORY_LABELS: Record<string, string> = {
  ADP: "Adaptability",
  OWN: "Ownership",
  LDR: "Leadership",
  COL: "Collaboration",
  COM: "Communication",
  PSO: "Problem Solving",
  INN: "Innovation",
  EXE: "Execution",
  IMP: "Impact",
  adaptability: "Adaptability",
  ownership: "Ownership",
  leadership: "Leadership",
  collaboration: "Collaboration",
  communication: "Communication",
  problem_solving: "Problem Solving",
  innovation: "Innovation",
  execution: "Execution",
  impact: "Impact",
};

function categoryLabel(id: string, name?: string): string {
  return CATEGORY_LABELS[id] ?? name ?? id;
}

/* ------------------------------------------------------------------ */
/* Sub-components                                                      */
/* ------------------------------------------------------------------ */

function CategoryFilter({
  categories,
  selected,
  onSelect,
}: {
  categories: CategorySummary[];
  selected: string | null;
  onSelect: (id: string | null) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2.5 mb-6">
      <button
        onClick={() => onSelect(null)}
        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
          selected === null
            ? "bg-blue-600 text-white shadow-md"
            : "bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300"
        }`}
      >
        All
      </button>
      {categories.map((cat) => (
        <button
          key={cat.category_id}
          onClick={() => onSelect(cat.category_id)}
          title={`${categoryLabel(cat.category_id, cat.category_name)}: ${cat.covered_count}/${cat.question_count} covered`}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
            selected === cat.category_id
              ? "bg-blue-600 text-white shadow-md"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300"
          }`}
        >
          {categoryLabel(cat.category_id, cat.category_name)}
          <span className="ml-1.5 text-xs font-bold opacity-80">
            ({cat.covered_count}/{cat.question_count})
          </span>
        </button>
      ))}
    </div>
  );
}

function ExampleCard({
  example,
  onClick,
}: {
  example: BehavioralExample;
  onClick: () => void;
}) {
  const needsInput = example.title.startsWith("[NEEDS-INPUT]");
  const isGolden = Boolean(example.is_golden);
  const pitchParts = example.cn_elevator_pitch
    ? parsePitch(example.cn_elevator_pitch)
    : null;

  return (
    <button
      type="button"
      id={`example-${example.example_id}`}
      onClick={onClick}
      className={`text-left bg-white rounded-xl p-5 mb-4 border-2 transition-all w-full hover:shadow-md ${
        needsInput
          ? "border-amber-300 hover:border-amber-500 bg-amber-50/30"
          : "border-gray-200 hover:border-blue-400"
      } ${goldenCardClass(isGolden)}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-sm font-mono font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded">
              {example.example_id}
            </span>
            <h4 className="text-gray-900 font-bold text-base">{example.title}</h4>
            <GoldenBadge golden={isGolden} />
            {needsInput && (
              <span className="text-xs font-bold uppercase tracking-wider bg-amber-100 text-amber-800 border border-amber-400 px-2 py-0.5 rounded">
                Needs Input
              </span>
            )}
          </div>
          {example.source_project && (
            <p className="text-sm text-gray-500 mt-1 ml-1">
              Source: <span className="font-medium text-gray-700">{example.source_project}</span>
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 flex-wrap shrink-0">
          {example.principle_tags.map((tag) => (
            <span
              key={tag}
              className="text-sm px-3 py-1 rounded-lg bg-blue-100 text-blue-800 font-semibold border border-blue-200"
              title={categoryLabel(tag)}
            >
              {categoryLabel(tag)}
            </span>
          ))}
        </div>
      </div>

      {pitchParts && (
        <div className="mt-3">
          <p className="text-sm text-gray-700 leading-snug bq-pitch-text">
            {pitchParts.summary}
          </p>
          {pitchParts.facts.length > 0 && (
            <div className="mt-1.5 flex flex-wrap gap-1">
              {pitchParts.facts.map((fact, i) => (
                <span
                  key={i}
                  className="bq-pitch-pill text-xs bg-gray-100 text-gray-700 border border-gray-200 px-2 py-0.5 rounded-full"
                >
                  {fact}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </button>
  );
}

function QuestionRow({
  question,
  examples,
  expanded,
  onToggle,
  onExampleClick,
  selectedThemes,
  onThemePillClick,
  goldenOnly,
}: {
  question: BehavioralQuestion;
  examples: BehavioralExample[];
  expanded: boolean;
  onToggle: () => void;
  onExampleClick: (exampleId: string) => void;
  selectedThemes: Set<string>;
  onThemePillClick: (slug: string) => void;
  goldenOnly: boolean;
}) {
  const linkedExamples = examples.filter(
    (ex) =>
      ex.linked_questions.some((lq) => lq.question_id === question.question_id) &&
      (!goldenOnly || ex.is_golden)
  );
  const themeTags = question.theme_tags ?? [];
  const MAX_VISIBLE_THEMES = 5;
  const visibleThemes = themeTags.slice(0, MAX_VISIBLE_THEMES);
  const overflowThemes = themeTags.slice(MAX_VISIBLE_THEMES);
  const [showOverflow, setShowOverflow] = useState(false);

  return (
    <div className="border-b border-gray-200 py-3">
      <div
        className="flex flex-col gap-1.5 cursor-pointer hover:bg-blue-50 px-4 py-2.5 rounded-lg select-none transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <span className="text-sm font-mono font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded w-16 shrink-0 text-center">
            {question.question_id}
          </span>
          <span className="text-sm px-2.5 py-1 rounded-lg bg-gray-200 text-gray-700 font-semibold shrink-0" title={categoryLabel(question.category_id, question.category_name)}>
            {categoryLabel(question.category_id, question.category_name)}
          </span>
          <span className="text-[15px] text-gray-900 font-medium">{question.text}</span>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          {question.example_count > 0 ? (
            <span className="text-sm px-3 py-1 rounded-lg bg-green-100 text-green-800 font-bold border border-green-300">
              {question.example_count} example{question.example_count > 1 ? "s" : ""}
            </span>
          ) : (
            <span className="text-sm px-3 py-1 rounded-lg bg-red-100 text-red-700 font-bold border border-red-300">
              no example
            </span>
          )}
          <span className="text-gray-500 text-sm font-bold">
            {expanded ? "[-]" : "[+]"}
          </span>
        </div>
        </div>
        {themeTags.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 ml-24">
            {visibleThemes.map((t) => {
              const isSelected = selectedThemes.has(t.slug);
              return (
                <button
                  key={t.slug}
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onThemePillClick(t.slug);
                  }}
                  aria-pressed={isSelected}
                  title={`Toggle theme: ${t.label}`}
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full border transition-all ${
                    isSelected
                      ? "bg-blue-600 text-white border-blue-700"
                      : "bg-purple-50 text-purple-800 border-purple-200 hover:bg-purple-100"
                  }`}
                >
                  {t.label}
                </button>
              );
            })}
            {overflowThemes.length > 0 && (
              <div className="relative">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowOverflow((v) => !v);
                  }}
                  aria-expanded={showOverflow}
                  className="text-xs font-bold px-2 py-0.5 rounded-full border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                >
                  +{overflowThemes.length} more
                </button>
                {showOverflow && (
                  <div
                    className="absolute z-10 top-full left-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-2 flex flex-col gap-1 min-w-[180px]"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {overflowThemes.map((t) => {
                      const isSelected = selectedThemes.has(t.slug);
                      return (
                        <button
                          key={t.slug}
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            onThemePillClick(t.slug);
                          }}
                          aria-pressed={isSelected}
                          className={`text-left text-xs font-semibold px-2 py-1 rounded border transition-all ${
                            isSelected
                              ? "bg-blue-600 text-white border-blue-700"
                              : "bg-purple-50 text-purple-800 border-purple-200 hover:bg-purple-100"
                          }`}
                        >
                          {t.label}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {expanded && linkedExamples.length > 0 && (
        <div className="ml-20 mt-3 mb-3">
          {linkedExamples.map((ex) => {
            const link = ex.linked_questions.find(
              (lq) => lq.question_id === question.question_id
            );
            const exNeedsInput = ex.title.startsWith("[NEEDS-INPUT]");
            return (
              <div
                key={ex.id}
                className={`rounded-lg p-4 mb-2.5 border shadow-sm ${
                  exNeedsInput
                    ? "bg-amber-50 border-amber-300"
                    : "bg-blue-50 border-blue-200"
                }`}
              >
                <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                  <span className="text-sm font-mono font-bold text-blue-500">
                    {ex.example_id}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onExampleClick(ex.example_id);
                    }}
                    className="text-[15px] text-blue-700 font-bold hover:text-blue-900 hover:underline text-left"
                    title="View full STAR example"
                  >
                    {ex.title}
                  </button>
                  <GoldenBadge golden={Boolean(ex.is_golden)} />
                  {exNeedsInput && (
                    <span className="text-xs font-bold uppercase tracking-wider bg-amber-100 text-amber-800 border border-amber-400 px-2 py-0.5 rounded">
                      Needs Input
                    </span>
                  )}
                </div>
                {link?.relevance_note && (
                  <blockquote className="text-sm text-green-700 border-l-3 border-green-400 pl-3 mb-2 leading-relaxed" style={{ borderLeftWidth: '3px' }}>
                    {link.relevance_note}
                  </blockquote>
                )}
                {ex.situation && (
                  <p className="text-sm text-gray-700 leading-relaxed">
                    <span className="text-blue-700 font-bold">S:</span>{" "}
                    {ex.situation.slice(0, 200)}
                    {ex.situation.length > 200 ? "..." : ""}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {expanded && linkedExamples.length === 0 && (
        <div className="ml-20 mt-3 mb-3 text-sm text-gray-500 italic">
          No examples linked to this question yet.
        </div>
      )}
    </div>
  );
}

function CoverageHeatmap({
  cells,
  categories,
  onCategoryClick,
  onExampleClick,
}: {
  cells: CoverageCell[];
  categories: CategorySummary[];
  onCategoryClick?: (categoryId: string) => void;
  onExampleClick?: (exampleId: string) => void;
}) {
  const exampleIds = [...new Set(cells.map((c) => c.example_id))];
  const exampleTitles = new Map(cells.map((c) => [c.example_id, c.example_title]));

  const matrix = new Map<string, Map<string, number>>();
  for (const cell of cells) {
    if (!matrix.has(cell.example_id)) {
      matrix.set(cell.example_id, new Map());
    }
    matrix.get(cell.example_id)!.set(cell.category_id, cell.link_count);
  }

  const maxCount = Math.max(...cells.map((c) => c.link_count), 1);

  function cellColor(count: number): string {
    if (count === 0) return "bg-gray-50";
    const intensity = Math.min(count / maxCount, 1);
    if (intensity < 0.33) return "bg-green-100 text-green-800";
    if (intensity < 0.66) return "bg-green-300 text-green-900";
    return "bg-green-500 text-white";
  }

  return (
    <div className="overflow-x-auto bg-white rounded-xl border-2 border-gray-200 p-5 shadow-sm">
      <table className="text-base w-full">
        <thead>
          <tr>
            <th className="text-left text-gray-700 font-bold p-3 min-w-[280px]">Example</th>
            {categories.map((cat) => (
              <th
                key={cat.category_id}
                className={`text-center text-gray-700 font-bold p-3 min-w-[100px]${onCategoryClick ? " cursor-pointer hover:text-blue-700 hover:bg-blue-50 transition-colors" : ""}`}
                title={`${categoryLabel(cat.category_id, cat.category_name)}: ${cat.covered_count}/${cat.question_count}`}
                onClick={() => onCategoryClick?.(cat.category_id)}
              >
                {categoryLabel(cat.category_id, cat.category_name)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {exampleIds.map((exId) => (
            <tr key={exId} className="border-t border-gray-200">
              <td
                className={`text-gray-800 p-3 max-w-[280px]${onExampleClick ? " cursor-pointer hover:bg-blue-50 transition-colors" : ""}`}
                title={exampleTitles.get(exId)}
                onClick={() => onExampleClick?.(exId)}
              >
                <span className="font-mono text-blue-500 font-bold text-sm mr-2">{exId}</span>
                <span className="text-[15px] font-medium">{(exampleTitles.get(exId) ?? "").slice(0, 45)}</span>
              </td>
              {categories.map((cat) => {
                const count = matrix.get(exId)?.get(cat.category_id) ?? 0;
                return (
                  <td
                    key={cat.category_id}
                    className={`text-center p-3 font-bold text-base ${cellColor(count)} rounded-lg${count > 0 && onExampleClick ? " cursor-pointer hover:ring-2 hover:ring-blue-400 transition-all" : ""}`}
                    title={`${exampleTitles.get(exId)} x ${categoryLabel(cat.category_id, cat.category_name)}: ${count}`}
                    onClick={count > 0 ? () => onExampleClick?.(exId) : undefined}
                  >
                    {count > 0 ? count : ""}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main Page                                                           */
/* ------------------------------------------------------------------ */

type ViewMode = "questions" | "examples" | "coverage" | "story-map";

export default function BehavioralQuestions() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("questions");
  const [search, setSearch] = useState("");
  const [expandedQuestions, setExpandedQuestions] = useState<Set<number>>(new Set());
  const [drawerExampleId, setDrawerExampleId] = useState<string | null>(null);
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  // URL-persisted theme filter state
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedThemeSlugs = useMemo(() => {
    const raw = searchParams.get("themes") ?? "";
    return raw
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
  }, [searchParams]);
  const themeMode: ThemeMode =
    searchParams.get("theme_mode") === "and" ? "and" : "or";
  const goldenOnly = searchParams.get("golden") === "1";

  const toggleGoldenOnly = useCallback(() => {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        if (goldenOnly) {
          next.delete("golden");
        } else {
          next.set("golden", "1");
        }
        return next;
      },
      { replace: true },
    );
  }, [goldenOnly, setSearchParams]);

  const selectedThemeSet = useMemo(
    () => new Set(selectedThemeSlugs),
    [selectedThemeSlugs],
  );

  const applyThemeFilter = useCallback(
    (slugs: string[], mode: ThemeMode) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (slugs.length > 0) {
            next.set("themes", slugs.join(","));
            next.set("theme_mode", mode);
          } else {
            next.delete("themes");
            next.delete("theme_mode");
          }
          return next;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  const handleToggleTheme = useCallback(
    (slug: string) => {
      const next = toggleThemeInState(
        { themes: selectedThemeSlugs, mode: themeMode },
        slug,
      );
      applyThemeFilter(next.themes, next.mode);
    },
    [selectedThemeSlugs, themeMode, applyThemeFilter],
  );

  const handleChangeMode = useCallback(
    (mode: ThemeMode) => {
      applyThemeFilter(selectedThemeSlugs, mode);
    },
    [selectedThemeSlugs, applyThemeFilter],
  );

  const handleClearThemes = useCallback(() => {
    applyThemeFilter([], "or");
  }, [applyThemeFilter]);

  const handleExampleClick = (exampleId: string) => {
    setDrawerExampleId(exampleId);
  };

  const toggleQuestion = (id: number) => {
    setExpandedQuestions((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const { data: categories = [] } = useQuery<CategorySummary[]>({
    queryKey: ["behavioral-categories"],
    queryFn: () => api.get("/behavioral/categories"),
  });

  const { data: themes = [] } = useQuery<BehavioralThemeSummary[]>({
    queryKey: ["behavioral-themes"],
    queryFn: () => api.get("/behavioral/themes"),
  });

  const themeQueryKey = selectedThemeSlugs.join(",");
  const { data: questions = [], isLoading: loadingQ } = useQuery<BehavioralQuestion[]>({
    queryKey: ["behavioral-questions", selectedCategory, search, themeQueryKey, themeMode],
    queryFn: () =>
      api.get("/behavioral/questions", {
        params: {
          ...(selectedCategory ? { category_id: selectedCategory } : {}),
          ...(search ? { search } : {}),
          ...(selectedThemeSlugs.length > 0
            ? { theme: themeQueryKey, theme_mode: themeMode }
            : {}),
        },
      }),
  });

  const { data: examples = [], isLoading: loadingEx } = useQuery<BehavioralExample[]>({
    queryKey: ["behavioral-examples"],
    queryFn: () => api.get("/behavioral/examples"),
  });

  const drawerExample = drawerExampleId
    ? examples.find((e) => e.example_id === drawerExampleId) ?? null
    : null;

  const { data: coverageCells = [] } = useQuery<CoverageCell[]>({
    queryKey: ["behavioral-coverage"],
    queryFn: () => api.get("/behavioral/coverage-matrix"),
    enabled: viewMode === "coverage",
  });

  const { data: gaps } = useQuery<GapData>({
    queryKey: ["behavioral-gaps"],
    queryFn: () => api.get("/behavioral/gaps"),
  });

  const isLoading = loadingQ || loadingEx;

  return (
    <div className="p-6 w-full max-w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900">Behavioral Questions</h1>
          {gaps && (
            <p className="text-base text-gray-600 mt-2">
              <span className="font-bold text-gray-900">{gaps.total_questions}</span> questions,{" "}
              <span className={`font-bold ${gaps.coverage_pct >= 70 ? "text-green-700" : gaps.coverage_pct >= 40 ? "text-amber-700" : "text-red-700"}`}>
                {gaps.coverage_pct}%
              </span> covered
              ({gaps.total_questions - gaps.uncovered_count} with examples)
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {(["questions", "examples", "coverage", "story-map"] as ViewMode[]).map((mode) => {
            const label = mode === "story-map" ? "Story Map" : mode;
            return (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-4 py-2 rounded-lg text-sm font-semibold capitalize transition-all ${
                  viewMode === mode
                    ? "bg-blue-600 text-white shadow-md"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300"
                }`}
              >
                {label}
              </button>
            );
          })}
          <button
            type="button"
            onClick={toggleGoldenOnly}
            aria-pressed={goldenOnly}
            title={goldenOnly ? "Show all examples" : "Show only golden examples"}
            className={
              "ml-2 px-3 py-2 rounded-lg border text-sm font-medium transition-all inline-flex items-center gap-1.5 " +
              (goldenOnly
                ? "border-orange-300 bg-orange-50 text-orange-700"
                : "border-gray-200 bg-white text-gray-600 hover:border-gray-300")
            }
          >
            <svg
              viewBox="0 0 24 24"
              width="14"
              height="14"
              fill={goldenOnly ? "currentColor" : "none"}
              stroke="currentColor"
              strokeWidth={goldenOnly ? 0 : 2}
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.7 1.5 6.8L12 17.7l-6.1 3.3 1.5-6.8L2.2 9.5l6.9-.7L12 2.5z" />
            </svg>
            Golden only
          </button>
        </div>
      </div>

      {/* Category filter */}
      {viewMode !== "story-map" && (
        <CategoryFilter
          categories={categories}
          selected={selectedCategory}
          onSelect={setSelectedCategory}
        />
      )}

      {/* Search */}
      {viewMode !== "coverage" && viewMode !== "story-map" && (
        <div className="relative mb-6">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
            &#128269;
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search questions or examples..."
            className="w-full pl-11 pr-4 py-3 rounded-xl bg-white border-2 border-gray-300 text-gray-900 text-base font-medium placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 shadow-sm transition-all"
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-lg font-bold"
            >
              x
            </button>
          )}
        </div>
      )}

      {isLoading && <p className="text-gray-500 text-base font-medium">Loading...</p>}

      {/* Questions View */}
      {viewMode === "questions" && !isLoading && (
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <div className="hidden md:block md:w-72 md:shrink-0 md:sticky md:top-6">
            <ThemeFilterSidebar
              themes={themes}
              selectedSlugs={selectedThemeSlugs}
              mode={themeMode}
              onToggleTheme={handleToggleTheme}
              onChangeMode={handleChangeMode}
              onClear={handleClearThemes}
            />
          </div>
          <div className="md:hidden mb-2">
            <button
              type="button"
              onClick={() => setMobileFilterOpen(true)}
              className="px-4 py-2 rounded-lg text-sm font-semibold bg-blue-600 text-white shadow-md"
            >
              Themes
              {selectedThemeSlugs.length > 0 && (
                <span className="ml-2 text-xs bg-white text-blue-700 rounded-full px-2 py-0.5">
                  {selectedThemeSlugs.length}
                </span>
              )}
            </button>
          </div>
          <div className="flex-1 min-w-0 bg-white rounded-xl border-2 border-gray-200 shadow-sm">
            {questions.length === 0 ? (
              selectedThemeSlugs.length > 0 ? (
                <p className="text-gray-500 text-base p-6 italic">
                  No questions matching the selected themes yet.
                </p>
              ) : (
                <p className="text-gray-500 text-base p-6">No questions found.</p>
              )
            ) : (
              questions.map((q) => (
                <QuestionRow
                  key={q.id}
                  question={q}
                  examples={examples}
                  expanded={expandedQuestions.has(q.id)}
                  onToggle={() => toggleQuestion(q.id)}
                  onExampleClick={handleExampleClick}
                  selectedThemes={selectedThemeSet}
                  onThemePillClick={handleToggleTheme}
                  goldenOnly={goldenOnly}
                />
              ))
            )}
          </div>
        </div>
      )}

      {/* Examples View */}
      {viewMode === "examples" && !isLoading && (
        <div>
          {examples
            .filter(
              (ex) =>
                !selectedCategory ||
                ex.principle_tags.includes(selectedCategory) ||
                ex.linked_questions.some((lq) => lq.category_id === selectedCategory)
            )
            .filter(
              (ex) =>
                !search ||
                ex.title.toLowerCase().includes(search.toLowerCase()) ||
                (ex.situation ?? "").toLowerCase().includes(search.toLowerCase())
            )
            .filter((ex) => !goldenOnly || ex.is_golden)
            .map((ex) => (
              <ExampleCard
                key={ex.id}
                example={ex}
                onClick={() => handleExampleClick(ex.example_id)}
              />
            ))}
        </div>
      )}

      {/* Coverage Matrix View */}
      {viewMode === "coverage" && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-3">
            Example-Principle Coverage Matrix
          </h2>
          <p className="text-sm text-gray-600 mb-5">
            Each cell shows how many questions in that category an example covers.
            Darker green = more coverage.
          </p>
          {coverageCells.length > 0 ? (
            <CoverageHeatmap
              cells={
                goldenOnly
                  ? coverageCells.filter((c) => {
                      const ex = examples.find(
                        (e) => e.example_id === c.example_id,
                      );
                      return ex?.is_golden;
                    })
                  : coverageCells
              }
              categories={categories}
              onCategoryClick={(categoryId) => {
                setSelectedCategory(categoryId);
                setViewMode("examples");
              }}
              onExampleClick={handleExampleClick}
            />
          ) : (
            <p className="text-gray-400 text-sm">Loading coverage data...</p>
          )}
        </div>
      )}

      {/* Story Map View */}
      {viewMode === "story-map" && <StoryMapView onExampleClick={handleExampleClick} />}

      <SlideOverPanel
        open={!!drawerExample}
        onClose={() => setDrawerExampleId(null)}
        title={drawerExample?.title ?? ""}
        headerActions={
          drawerExample ? (
            <GoldenToggleButton
              itemType="behavioral_example"
              itemId={drawerExample.id}
              isGolden={Boolean(drawerExample.is_golden)}
            />
          ) : null
        }
        headerAccentClassName={
          drawerExample?.is_golden ? "border-t-2 border-t-orange-300" : ""
        }
      >
        {drawerExample && <ExampleDrawerContent example={drawerExample} />}
      </SlideOverPanel>

      {mobileFilterOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Theme filter"
        >
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setMobileFilterOpen(false)}
          />
          <div className="absolute left-0 right-0 bottom-0 bg-white rounded-t-2xl shadow-xl max-h-[80vh] overflow-y-auto p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-base font-bold text-gray-900">Filter by theme</h3>
              <button
                type="button"
                onClick={() => setMobileFilterOpen(false)}
                className="text-sm font-semibold text-gray-500 hover:text-gray-800"
              >
                Close
              </button>
            </div>
            <ThemeFilterSidebar
              themes={themes}
              selectedSlugs={selectedThemeSlugs}
              mode={themeMode}
              onToggleTheme={handleToggleTheme}
              onChangeMode={handleChangeMode}
              onClear={handleClearThemes}
              variant="sheet"
            />
          </div>
        </div>
      )}
    </div>
  );
}
