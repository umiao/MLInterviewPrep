import { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import MarkdownPreview from "../components/ui/MarkdownPreview";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface LinkedQuestion {
  id: number;
  question_id: string;
  text: string;
  category_id: string;
  relevance_note: string | null;
}

interface BehavioralExample {
  id: number;
  example_id: string;
  title: string;
  source_project: string | null;
  situation: string | null;
  task: string | null;
  action: string | null;
  result: string | null;
  evidence_quotes: string[];
  principle_tags: string[];
  risk_statement: string | null;
  analogy: string | null;
  tech_terms: Record<string, string>;
  linked_questions: LinkedQuestion[];
}

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
    <div className="flex flex-wrap gap-2 mb-4">
      <button
        onClick={() => onSelect(null)}
        className={`px-3 py-1.5 rounded text-sm transition-colors ${
          selected === null
            ? "bg-blue-600 text-white"
            : "bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200"
        }`}
      >
        All
      </button>
      {categories.map((cat) => (
        <button
          key={cat.category_id}
          onClick={() => onSelect(cat.category_id)}
          title={`${categoryLabel(cat.category_id, cat.category_name)}: ${cat.covered_count}/${cat.question_count} covered`}
          className={`px-3 py-1.5 rounded text-sm transition-colors ${
            selected === cat.category_id
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200"
          }`}
        >
          {categoryLabel(cat.category_id, cat.category_name)}
          <span className="ml-1 text-xs opacity-70">
            ({cat.covered_count}/{cat.question_count})
          </span>
        </button>
      ))}
    </div>
  );
}

function StarSection({ label, content }: { label: string; content: string | null }) {
  if (!content) return null;
  // Use MarkdownPreview if content contains markdown syntax, otherwise plain text
  const hasMarkdown = /[*_\-#\[\]`|]/.test(content);
  return (
    <div className="mb-2">
      <span className="font-semibold text-blue-600 text-xs uppercase tracking-wider">
        {label}
      </span>
      {hasMarkdown ? (
        <div className="mt-0.5 text-sm text-gray-600">
          <MarkdownPreview markdown={content} />
        </div>
      ) : (
        <p className="text-gray-600 text-sm mt-0.5">{content}</p>
      )}
    </div>
  );
}

function ExampleCard({
  example,
  focused,
  onClearFocus,
}: {
  example: BehavioralExample;
  focused?: boolean;
  onClearFocus?: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (focused) {
      setExpanded(true);
      // Small delay to let the DOM render before scrolling
      const timer = setTimeout(() => {
        cardRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [focused]);

  return (
    <div
      ref={cardRef}
      id={`example-${example.example_id}`}
      className={`bg-white rounded-lg p-4 mb-3 border transition-all ${
        focused
          ? "border-blue-500 shadow-md ring-2 ring-blue-200"
          : "border-gray-200 hover:border-blue-300 hover:shadow-sm"
      }`}
      onAnimationEnd={onClearFocus}
    >
      <div
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setExpanded((prev) => !prev)}
      >
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-gray-400">{example.example_id}</span>
            <h4 className="text-gray-800 font-medium text-sm">{example.title}</h4>
          </div>
          {example.source_project && (
            <p className="text-xs text-gray-400 mt-0.5">
              Source: {example.source_project}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {example.principle_tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-600 border border-blue-100"
              title={categoryLabel(tag)}
            >
              {categoryLabel(tag)}
            </span>
          ))}
          <span className="text-gray-400 text-sm ml-2">
            {expanded ? "[-]" : "[+]"}
          </span>
        </div>
      </div>

      {expanded && (
        <div className="mt-3 pl-3 border-l-2 border-blue-200">
          <StarSection label="Situation" content={example.situation} />
          <StarSection label="Task" content={example.task} />
          <StarSection label="Action" content={example.action} />
          <StarSection label="Result" content={example.result} />

          {example.risk_statement && (
            <div className="mb-2">
              <span className="font-semibold text-red-600 text-xs uppercase tracking-wider">
                Risk if not addressed
              </span>
              <div className="text-gray-600 text-sm mt-0.5">
                <MarkdownPreview markdown={example.risk_statement} />
              </div>
            </div>
          )}

          {example.analogy && (
            <div className="mb-2">
              <span className="font-semibold text-purple-600 text-xs uppercase tracking-wider">
                Simple Analogy
              </span>
              <div className="text-gray-600 text-sm mt-0.5 italic">
                <MarkdownPreview markdown={example.analogy} />
              </div>
            </div>
          )}

          {Object.keys(example.tech_terms).length > 0 && (
            <div className="mb-2">
              <span className="font-semibold text-teal-700 text-xs uppercase tracking-wider">
                Technical Terms
              </span>
              <dl className="mt-1 space-y-0.5">
                {Object.entries(example.tech_terms).map(([term, def_]) => (
                  <div key={term} className="text-sm">
                    <dt className="inline font-medium text-teal-800">{term}</dt>
                    <dd className="inline text-gray-600"> -- {def_}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {example.evidence_quotes.length > 0 && (
            <div className="mt-3">
              <span className="font-semibold text-yellow-700 text-xs uppercase tracking-wider">
                Evidence
              </span>
              {example.evidence_quotes.map((q, i) => (
                <blockquote
                  key={i}
                  className="text-gray-500 text-xs italic border-l-2 border-yellow-400 pl-2 mt-1"
                >
                  {q}
                </blockquote>
              ))}
            </div>
          )}

          {example.linked_questions.length > 0 && (
            <div className="mt-3">
              <span className="font-semibold text-green-700 text-xs uppercase tracking-wider">
                Cross-references ({example.linked_questions.length} questions)
              </span>
              {example.linked_questions.map((lq) => (
                <div
                  key={lq.id}
                  className="mt-1.5 bg-gray-50 rounded p-2 border border-gray-200"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-gray-400">
                      {lq.question_id}
                    </span>
                    <span className="text-xs text-gray-700">{lq.text}</span>
                  </div>
                  {lq.relevance_note && (
                    <blockquote className="text-xs text-green-600 mt-1 border-l-2 border-green-300 pl-2">
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
    <div className="border-b border-gray-200 py-2">
      <div
        className="flex items-center justify-between cursor-pointer hover:bg-gray-50 px-3 py-1.5 rounded select-none"
        onClick={onToggle}
      >
        <div className="flex items-center gap-2 flex-1">
          <span className="text-xs font-mono text-gray-400 w-14 shrink-0">
            {question.question_id}
          </span>
          <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 shrink-0" title={categoryLabel(question.category_id, question.category_name)}>
            {categoryLabel(question.category_id, question.category_name)}
          </span>
          <span className="text-sm text-gray-800">{question.text}</span>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {question.example_count > 0 ? (
            <span className="text-xs px-2 py-0.5 rounded bg-green-50 text-green-700 border border-green-200">
              {question.example_count} example{question.example_count > 1 ? "s" : ""}
            </span>
          ) : (
            <span className="text-xs px-2 py-0.5 rounded bg-red-50 text-red-600 border border-red-200">
              no example
            </span>
          )}
          <span className="text-gray-400 text-xs">
            {expanded ? "[-]" : "[+]"}
          </span>
        </div>
      </div>

      {expanded && linkedExamples.length > 0 && (
        <div className="ml-16 mt-2 mb-2">
          {linkedExamples.map((ex) => {
            const link = ex.linked_questions.find(
              (lq) => lq.question_id === question.question_id
            );
            return (
              <div key={ex.id} className="bg-white rounded p-3 mb-2 border border-gray-200 shadow-sm">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono text-gray-400">
                    {ex.example_id}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onExampleClick(ex.example_id);
                    }}
                    className="text-sm text-blue-600 font-medium hover:text-blue-800 hover:underline text-left"
                    title="View full STAR example"
                  >
                    {ex.title}
                  </button>
                </div>
                {link?.relevance_note && (
                  <blockquote className="text-xs text-green-600 border-l-2 border-green-300 pl-2 mb-2">
                    {link.relevance_note}
                  </blockquote>
                )}
                {ex.situation && (
                  <p className="text-xs text-gray-500">
                    <span className="text-blue-600 font-semibold">S:</span>{" "}
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
        <div className="ml-16 mt-2 mb-2 text-xs text-gray-400 italic">
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
    <div className="overflow-x-auto bg-white rounded-lg border border-gray-200 p-4">
      <table className="text-sm w-full">
        <thead>
          <tr>
            <th className="text-left text-gray-500 font-medium p-2 min-w-[250px]">Example</th>
            {categories.map((cat) => (
              <th
                key={cat.category_id}
                className={`text-center text-gray-500 font-medium p-2 min-w-[90px]${onCategoryClick ? " cursor-pointer hover:text-blue-600 hover:bg-blue-50 transition-colors" : ""}`}
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
            <tr key={exId} className="border-t border-gray-100">
              <td
                className={`text-gray-700 p-2 max-w-[250px]${onExampleClick ? " cursor-pointer hover:bg-blue-50 transition-colors" : ""}`}
                title={exampleTitles.get(exId)}
                onClick={() => onExampleClick?.(exId)}
              >
                <span className="font-mono text-gray-400 text-xs mr-1">{exId}</span>
                <span className="text-sm">{(exampleTitles.get(exId) ?? "").slice(0, 40)}</span>
              </td>
              {categories.map((cat) => {
                const count = matrix.get(exId)?.get(cat.category_id) ?? 0;
                return (
                  <td
                    key={cat.category_id}
                    className={`text-center p-2 font-medium ${cellColor(count)} rounded${count > 0 && onExampleClick ? " cursor-pointer hover:ring-2 hover:ring-blue-400 transition-all" : ""}`}
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

type ViewMode = "questions" | "examples" | "coverage";

export default function BehavioralQuestions() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("questions");
  const [search, setSearch] = useState("");
  const [expandedQuestions, setExpandedQuestions] = useState<Set<number>>(new Set());
  const [focusedExampleId, setFocusedExampleId] = useState<string | null>(null);

  const handleExampleClick = (exampleId: string) => {
    setFocusedExampleId(exampleId);
    setViewMode("examples");
    // Clear category filter so the focused example is visible
    setSelectedCategory(null);
    setSearch("");
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
    <div className="p-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Behavioral Questions</h1>
          {gaps && (
            <p className="text-sm text-gray-500 mt-1">
              {gaps.total_questions} questions, {gaps.coverage_pct}% covered
              ({gaps.total_questions - gaps.uncovered_count} with examples)
            </p>
          )}
        </div>
        <div className="flex gap-2">
          {(["questions", "examples", "coverage"] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`px-3 py-1.5 rounded text-sm capitalize transition-colors ${
                viewMode === mode
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-200"
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* Category filter */}
      <CategoryFilter
        categories={categories}
        selected={selectedCategory}
        onSelect={setSelectedCategory}
      />

      {/* Search */}
      {viewMode !== "coverage" && (
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search questions or examples..."
          className="w-full mb-4 px-3 py-2 rounded bg-white border border-gray-200 text-gray-800 text-sm placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
      )}

      {isLoading && <p className="text-gray-400">Loading...</p>}

      {/* Questions View */}
      {viewMode === "questions" && !isLoading && (
        <div className="bg-white rounded-lg border border-gray-200">
          {questions.length === 0 ? (
            <p className="text-gray-400 text-sm p-4">No questions found.</p>
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
                focused={focusedExampleId === ex.example_id}
                onClearFocus={() => setFocusedExampleId(null)}
              />
            ))}
        </div>
      )}

      {/* Coverage Matrix View */}
      {viewMode === "coverage" && (
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-3">
            Example-Principle Coverage Matrix
          </h2>
          <p className="text-xs text-gray-500 mb-4">
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
    </div>
  );
}
