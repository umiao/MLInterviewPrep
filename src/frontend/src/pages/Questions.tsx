import { useCallback, useEffect, useState } from "react";
import { api, ApiRequestError } from "../utils/api";
import type { InterviewQuestion, QuestionAnalysis, QuestionType } from "../types/question";

const QUESTION_TYPES: { value: QuestionType; label: string }[] = [
  { value: "coding", label: "Coding" },
  { value: "ml_theory", label: "ML Theory" },
  { value: "ml_system_design", label: "ML System Design" },
  { value: "behavioral", label: "Behavioral" },
  { value: "ml_coding", label: "ML Coding" },
  { value: "general_system_design", label: "System Design" },
];

const TYPE_BADGE: Record<string, string> = {
  coding: "bg-blue-100 text-blue-700",
  ml_theory: "bg-purple-100 text-purple-700",
  ml_system_design: "bg-orange-100 text-orange-700",
  behavioral: "bg-green-100 text-green-700",
  ml_coding: "bg-indigo-100 text-indigo-700",
  general_system_design: "bg-yellow-100 text-yellow-700",
};

function typeBadgeClass(t: string | null): string {
  return TYPE_BADGE[t ?? ""] ?? "bg-gray-100 text-gray-700";
}

function typeLabel(t: string | null): string {
  if (!t) return "Unknown";
  const found = QUESTION_TYPES.find((qt) => qt.value === t);
  return found ? found.label : t;
}

/* ---------- Analysis Panel ---------- */

function AnalysisPanel({
  analysis,
  loading,
}: {
  analysis: QuestionAnalysis | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <div className="text-sm text-gray-500 py-3 text-center">
        Analyzing with LLM...
      </div>
    );
  }
  if (!analysis) return null;

  return (
    <div className="space-y-3 mt-3 p-3 bg-blue-50 rounded border border-blue-100">
      <div>
        <h4 className="text-xs font-semibold text-gray-500 uppercase">
          Solution Approach
        </h4>
        <p className="text-sm text-gray-700 mt-1">{analysis.solution_approach}</p>
      </div>
      {analysis.key_concepts.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase">
            Key Concepts
          </h4>
          <div className="flex flex-wrap gap-1 mt-1">
            {analysis.key_concepts.map((c) => (
              <span
                key={c}
                className="text-xs px-2 py-0.5 rounded bg-white border border-blue-200 text-blue-700"
              >
                {c}
              </span>
            ))}
          </div>
        </div>
      )}
      <div className="flex gap-6">
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase">
            Difficulty
          </h4>
          <span className="text-sm font-medium capitalize">
            {analysis.difficulty}
          </span>
        </div>
        {analysis.related_patterns.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase">
              Related Patterns
            </h4>
            <span className="text-sm text-gray-700">
              {analysis.related_patterns.join(", ")}
            </span>
          </div>
        )}
      </div>
      {analysis.suggested_study && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase">
            Suggested Study
          </h4>
          <p className="text-sm text-gray-700 mt-1">
            {analysis.suggested_study}
          </p>
        </div>
      )}
    </div>
  );
}

/* ---------- Expanded Row ---------- */

function ExpandedRow({
  question,
  onToggleReviewed,
  onAnalyze,
}: {
  question: InterviewQuestion;
  onToggleReviewed: (id: number, reviewed: boolean) => void;
  onAnalyze: (id: number) => void;
}) {
  const [analysis, setAnalysis] = useState<QuestionAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  // Try to parse existing notes as analysis
  useEffect(() => {
    if (question.notes) {
      try {
        const parsed = JSON.parse(question.notes) as QuestionAnalysis;
        if (parsed.solution_approach) {
          setAnalysis(parsed);
        }
      } catch {
        // notes is plain text, not analysis JSON
      }
    }
  }, [question.notes]);

  async function handleAnalyze() {
    setAnalyzing(true);
    setAnalyzeError(null);
    try {
      const result = await api.post<QuestionAnalysis>(
        `/questions/${question.id}/analyze`,
      );
      setAnalysis(result);
      onAnalyze(question.id);
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setAnalyzeError(msg);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <tr>
      <td colSpan={7} className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="space-y-3">
          {/* Full question text */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
              Question
            </h4>
            <p className="text-sm text-gray-800 whitespace-pre-wrap">
              {question.question_text}
            </p>
          </div>

          {/* Metadata row */}
          <div className="flex flex-wrap gap-4 text-xs text-gray-500">
            {question.level && <span>Level: {question.level}</span>}
            {question.interview_round && (
              <span>Round: {question.interview_round}</span>
            )}
            {question.year && <span>Year: {question.year}</span>}
            {question.tags.length > 0 && (
              <span>Tags: {question.tags.join(", ")}</span>
            )}
            {question.difficulty_estimate && (
              <span>Difficulty: {question.difficulty_estimate}</span>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button
              onClick={() =>
                onToggleReviewed(question.id, !question.is_reviewed)
              }
              className={`text-xs px-3 py-1.5 rounded border ${
                question.is_reviewed
                  ? "bg-green-50 border-green-300 text-green-700"
                  : "bg-white border-gray-300 text-gray-600 hover:bg-gray-50"
              }`}
            >
              {question.is_reviewed ? "[x] Reviewed" : "[ ] Mark Reviewed"}
            </button>
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="text-xs px-3 py-1.5 rounded border bg-white border-blue-300 text-blue-700 hover:bg-blue-50 disabled:opacity-50"
            >
              {analyzing ? "Analyzing..." : analysis ? "Re-analyze" : "Analyze"}
            </button>
          </div>

          {/* Analysis error */}
          {analyzeError && (
            <div className="text-xs text-red-600 bg-red-50 px-3 py-2 rounded">
              {analyzeError}
            </div>
          )}

          {/* Analysis results */}
          <AnalysisPanel analysis={analysis} loading={analyzing} />
        </div>
      </td>
    </tr>
  );
}

/* ---------- Filters ---------- */

interface Filters {
  company: string;
  role: string;
  question_type: string;
  is_reviewed: string;
  search: string;
}

const EMPTY_FILTERS: Filters = {
  company: "",
  role: "",
  question_type: "",
  is_reviewed: "",
  search: "",
};

/* ---------- Main Page ---------- */

export default function Questions() {
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 50;

  const fetchQuestions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, string | number | boolean | undefined> = {
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
      };
      if (filters.company) params.company = filters.company;
      if (filters.role) params.role = filters.role;
      if (filters.question_type) params.question_type = filters.question_type;
      if (filters.is_reviewed === "true") params.is_reviewed = true;
      if (filters.is_reviewed === "false") params.is_reviewed = false;
      if (filters.search) params.search = filters.search;

      const data = await api.get<InterviewQuestion[]>("/questions", {
        params,
      });
      setQuestions(data);
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  function handleFilterChange(key: keyof Filters, value: string) {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(0);
    setExpandedId(null);
  }

  function handleClearFilters() {
    setFilters(EMPTY_FILTERS);
    setPage(0);
    setExpandedId(null);
  }

  async function handleToggleReviewed(id: number, reviewed: boolean) {
    try {
      await api.put(`/questions/${id}`, { is_reviewed: reviewed });
      setQuestions((prev) =>
        prev.map((q) => (q.id === id ? { ...q, is_reviewed: reviewed } : q)),
      );
    } catch {
      // silent fail -- user sees stale state until refresh
    }
  }

  function handleAnalyzeDone(id: number) {
    // Refresh to get updated notes
    fetchQuestions().catch(() => {
      // If refresh fails, at least the analysis panel shows the result
    });
    void id;
  }

  const hasFilters = Object.values(filters).some((v) => v !== "");

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Interview Questions</h1>
          <p className="text-sm text-gray-500">
            {questions.length} question{questions.length !== 1 ? "s" : ""} shown
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4 items-end">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Search
          </label>
          <input
            type="text"
            value={filters.search}
            onChange={(e) => handleFilterChange("search", e.target.value)}
            placeholder="Search question text..."
            className="border border-gray-300 rounded px-3 py-1.5 text-sm w-56"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Company
          </label>
          <input
            type="text"
            value={filters.company}
            onChange={(e) => handleFilterChange("company", e.target.value)}
            placeholder="Filter by company"
            className="border border-gray-300 rounded px-3 py-1.5 text-sm w-36"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Role
          </label>
          <input
            type="text"
            value={filters.role}
            onChange={(e) => handleFilterChange("role", e.target.value)}
            placeholder="Filter by role"
            className="border border-gray-300 rounded px-3 py-1.5 text-sm w-32"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Type
          </label>
          <select
            value={filters.question_type}
            onChange={(e) =>
              handleFilterChange("question_type", e.target.value)
            }
            className="border border-gray-300 rounded px-3 py-1.5 text-sm"
          >
            <option value="">All types</option>
            {QUESTION_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Reviewed
          </label>
          <select
            value={filters.is_reviewed}
            onChange={(e) =>
              handleFilterChange("is_reviewed", e.target.value)
            }
            className="border border-gray-300 rounded px-3 py-1.5 text-sm"
          >
            <option value="">All</option>
            <option value="true">Reviewed</option>
            <option value="false">Not reviewed</option>
          </select>
        </div>
        {hasFilters && (
          <button
            onClick={handleClearFilters}
            className="text-xs text-blue-600 hover:underline pb-1.5"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-3">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-gray-500 py-8 text-center">Loading...</div>
      )}

      {/* Table */}
      {!loading && (
        <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 sticky top-0">
              <tr className="text-left text-xs font-medium text-gray-500 uppercase">
                <th className="px-4 py-2 w-8" />
                <th className="px-4 py-2">Question</th>
                <th className="px-4 py-2 w-32">Company</th>
                <th className="px-4 py-2 w-28">Role</th>
                <th className="px-4 py-2 w-36">Type</th>
                <th className="px-4 py-2 w-24 text-center">Reviewed</th>
                <th className="px-4 py-2 w-20 text-center">Year</th>
              </tr>
            </thead>
            <tbody>
              {questions.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-8 text-center text-gray-400"
                  >
                    No questions found. Try adjusting your filters.
                  </td>
                </tr>
              )}
              {questions.map((q) => (
                <>
                  <tr
                    key={q.id}
                    onClick={() =>
                      setExpandedId(expandedId === q.id ? null : q.id)
                    }
                    className={`border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                      expandedId === q.id ? "bg-gray-50" : ""
                    }`}
                  >
                    <td className="px-4 py-2 text-gray-400 text-xs">
                      {expandedId === q.id ? "v" : ">"}
                    </td>
                    <td className="px-4 py-2">
                      <span className="line-clamp-2">{q.question_text}</span>
                    </td>
                    <td className="px-4 py-2 text-gray-600">
                      {q.company ?? "-"}
                    </td>
                    <td className="px-4 py-2 text-gray-600">
                      {q.role ?? "-"}
                    </td>
                    <td className="px-4 py-2">
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${typeBadgeClass(q.question_type)}`}
                      >
                        {typeLabel(q.question_type)}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-center">
                      {q.is_reviewed ? (
                        <span className="text-green-600 text-xs font-medium">
                          Yes
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">No</span>
                      )}
                    </td>
                    <td className="px-4 py-2 text-center text-gray-500">
                      {q.year ?? "-"}
                    </td>
                  </tr>
                  {expandedId === q.id && (
                    <ExpandedRow
                      key={`expanded-${q.id}`}
                      question={q}
                      onToggleReviewed={handleToggleReviewed}
                      onAnalyze={handleAnalyzeDone}
                    />
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {!loading && questions.length > 0 && (
        <div className="flex items-center justify-between mt-3 text-sm">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1.5 border border-gray-300 rounded text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-gray-500">Page {page + 1}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={questions.length < PAGE_SIZE}
            className="px-3 py-1.5 border border-gray-300 rounded text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
