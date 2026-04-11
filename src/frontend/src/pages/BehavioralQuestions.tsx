import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import MarkdownPreview from "../components/ui/MarkdownPreview";
import StoryMapView from "../components/behavioral/StoryMapView";
import SlideOverPanel from "../components/ui/SlideOverPanel";
import ExampleDrawerContent from "../components/behavioral/ExampleDrawerContent";
import type { BehavioralExample } from "../types/behavioral";

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

const STAR_COLORS: Record<string, { label: string; border: string }> = {
  Situation: { label: "text-blue-700", border: "border-blue-300" },
  Task: { label: "text-amber-700", border: "border-amber-300" },
  Action: { label: "text-emerald-700", border: "border-emerald-300" },
  Result: { label: "text-purple-700", border: "border-purple-300" },
};

function StarSection({
  label,
  content,
  needsInput,
}: {
  label: string;
  content: string | null;
  needsInput?: boolean;
}) {
  const isEmpty = !content || content.trim() === "";
  if (isEmpty && !needsInput) return null;
  const colors = STAR_COLORS[label] ?? { label: "text-blue-700", border: "border-blue-300" };
  if (isEmpty) {
    return (
      <div className="mb-3">
        <span className={`font-bold ${colors.label} text-sm uppercase tracking-wider`}>
          {label}
        </span>
        <p className="text-gray-400 italic text-[15px] leading-relaxed mt-1">
          (missing -- pending user input)
        </p>
      </div>
    );
  }
  const hasMarkdown = /[*_\-#\[\]`|]/.test(content as string);
  return (
    <div className="mb-3">
      <span className={`font-bold ${colors.label} text-sm uppercase tracking-wider`}>
        {label}
      </span>
      {hasMarkdown ? (
        <div className="mt-1 text-[15px] leading-relaxed text-gray-800">
          <MarkdownPreview markdown={content as string} />
        </div>
      ) : (
        <p className="text-gray-800 text-[15px] leading-relaxed mt-1">{content}</p>
      )}
    </div>
  );
}

function ExampleCard({
  example,
}: {
  example: BehavioralExample;
}) {
  const [expanded, setExpanded] = useState(false);
  const needsInput = example.title.startsWith("[NEEDS-INPUT]");

  return (
    <div
      id={`example-${example.example_id}`}
      className={`bg-white rounded-xl p-5 mb-4 border-2 transition-all w-full hover:shadow-md ${
        needsInput
          ? "border-amber-300 hover:border-amber-500 bg-amber-50/30"
          : "border-gray-200 hover:border-blue-400"
      }`}
    >
      <div
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setExpanded((prev) => !prev)}
      >
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-sm font-mono font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded">{example.example_id}</span>
            <h4 className="text-gray-900 font-bold text-base">{example.title}</h4>
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
        <div className="flex items-center gap-2">
          {example.principle_tags.map((tag) => (
            <span
              key={tag}
              className="text-sm px-3 py-1 rounded-lg bg-blue-100 text-blue-800 font-semibold border border-blue-200"
              title={categoryLabel(tag)}
            >
              {categoryLabel(tag)}
            </span>
          ))}
          <span className="text-gray-500 text-base font-bold ml-3">
            {expanded ? "[-]" : "[+]"}
          </span>
        </div>
      </div>

      {expanded && (
        <div className="mt-4 pl-4 border-l-3 border-blue-400" style={{ borderLeftWidth: '3px' }}>
          {needsInput && (
            <div className="mb-3 bg-amber-50 border border-amber-300 rounded-lg p-3 text-sm text-amber-900">
              Placeholder slot reserved by the 2026-04-11 behavioral audit. See
              <span className="font-mono"> docs/human_input/EX-30-32_failure_placeholders.md</span>.
            </div>
          )}
          <StarSection label="Situation" content={example.situation} needsInput={needsInput} />
          <StarSection label="Task" content={example.task} needsInput={needsInput} />
          <StarSection label="Action" content={example.action} needsInput={needsInput} />
          <StarSection label="Result" content={example.result} needsInput={needsInput} />

          {example.risk_statement && (
            <div className="mb-3 bg-red-50 rounded-lg p-3 border border-red-200">
              <span className="font-bold text-red-700 text-sm uppercase tracking-wider">
                Risk if not addressed
              </span>
              <div className="text-red-900 text-[15px] mt-1 leading-relaxed">
                <MarkdownPreview markdown={example.risk_statement} />
              </div>
            </div>
          )}

          {example.analogy && (
            <div className="mb-3 bg-purple-50 rounded-lg p-3 border border-purple-200">
              <span className="font-bold text-purple-700 text-sm uppercase tracking-wider">
                Simple Analogy
              </span>
              <div className="text-purple-900 text-[15px] mt-1 italic leading-relaxed">
                <MarkdownPreview markdown={example.analogy} />
              </div>
            </div>
          )}

          {Object.keys(example.tech_terms).length > 0 && (
            <div className="mb-3 bg-teal-50 rounded-lg p-3 border border-teal-200">
              <span className="font-bold text-teal-800 text-sm uppercase tracking-wider">
                Technical Terms
              </span>
              <dl className="mt-2 space-y-1">
                {Object.entries(example.tech_terms).map(([term, def_]) => (
                  <div key={term} className="text-[15px]">
                    <dt className="inline font-bold text-teal-900">{term}</dt>
                    <dd className="inline text-gray-800"> -- {def_}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {example.evidence_quotes.length > 0 && (
            <div className="mt-4">
              <span className="font-bold text-amber-800 text-sm uppercase tracking-wider">
                Evidence
              </span>
              {example.evidence_quotes.map((q, i) => (
                <blockquote
                  key={i}
                  className="text-gray-700 text-sm italic border-l-3 border-amber-400 pl-3 mt-2 leading-relaxed"
                  style={{ borderLeftWidth: '3px' }}
                >
                  {q}
                </blockquote>
              ))}
            </div>
          )}

          {example.linked_questions.length > 0 && (
            <div className="mt-4">
              <span className="font-bold text-green-800 text-sm uppercase tracking-wider">
                Cross-references ({example.linked_questions.length} questions)
              </span>
              {example.linked_questions.map((lq) => (
                <div
                  key={lq.id}
                  className="mt-2 bg-green-50 rounded-lg p-3 border border-green-200"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono font-bold text-green-600">
                      {lq.question_id}
                    </span>
                    <span className="text-sm text-gray-900 font-medium">{lq.text}</span>
                  </div>
                  {lq.relevance_note && (
                    <blockquote className="text-sm text-green-700 mt-1.5 border-l-3 border-green-400 pl-3 leading-relaxed" style={{ borderLeftWidth: '3px' }}>
                      {lq.relevance_note}
                    </blockquote>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function QuestionRow({
  question,
  examples,
  expanded,
  onToggle,
  onExampleClick,
}: {
  question: BehavioralQuestion;
  examples: BehavioralExample[];
  expanded: boolean;
  onToggle: () => void;
  onExampleClick: (exampleId: string) => void;
}) {
  const linkedExamples = examples.filter((ex) =>
    ex.linked_questions.some((lq) => lq.question_id === question.question_id)
  );

  return (
    <div className="border-b border-gray-200 py-3">
      <div
        className="flex items-center justify-between cursor-pointer hover:bg-blue-50 px-4 py-2.5 rounded-lg select-none transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3 flex-1">
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

  const { data: questions = [], isLoading: loadingQ } = useQuery<BehavioralQuestion[]>({
    queryKey: ["behavioral-questions", selectedCategory, search],
    queryFn: () =>
      api.get("/behavioral/questions", {
        params: {
          ...(selectedCategory ? { category_id: selectedCategory } : {}),
          ...(search ? { search } : {}),
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
        <div className="flex gap-2">
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
        <div className="bg-white rounded-xl border-2 border-gray-200 shadow-sm">
          {questions.length === 0 ? (
            <p className="text-gray-500 text-base p-6">No questions found.</p>
          ) : (
            questions.map((q) => (
              <QuestionRow
                key={q.id}
                question={q}
                examples={examples}
                expanded={expandedQuestions.has(q.id)}
                onToggle={() => toggleQuestion(q.id)}
                onExampleClick={handleExampleClick}
              />
            ))
          )}
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
            .map((ex) => (
              <ExampleCard
                key={ex.id}
                example={ex}
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
              cells={coverageCells}
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
      >
        {drawerExample && <ExampleDrawerContent example={drawerExample} />}
      </SlideOverPanel>
    </div>
  );
}
