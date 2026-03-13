import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiRequestError } from "../utils/api";
import type { PaginatedResult } from "../utils/api";
import type {
  Category,
  Difficulty,
  Problem,
  ProblemFilters,
  SortField,
  SortOrder,
} from "../types/problem";
import PracticeModal from "../components/PracticeModal";

const DIFFICULTIES: Difficulty[] = ["easy", "medium", "hard"];
const CATEGORIES: { value: Category; label: string }[] = [
  { value: "algorithm", label: "Algorithm" },
  { value: "ml_coding", label: "ML Coding" },
  { value: "system_design", label: "System Design" },
];
const PAGE_SIZE = 20;

const DIFFICULTY_COLORS: Record<Difficulty, string> = {
  easy: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  hard: "bg-red-100 text-red-700",
};

function ComfortStars({ level }: { level: number }) {
  return (
    <span className="inline-flex gap-0.5" title={`Comfort: ${level}/5`}>
      {[1, 2, 3, 4, 5].map((i) => (
        <span
          key={i}
          className={i <= level ? "text-yellow-500" : "text-gray-300"}
        >
          *
        </span>
      ))}
    </span>
  );
}

function ReviewBadge({ nextReview }: { nextReview: string | null }) {
  if (!nextReview) return null;
  const due = new Date(nextReview);
  const now = new Date();
  const overdue = due <= now;
  const daysUntil = Math.ceil(
    (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24),
  );
  if (!overdue && daysUntil > 3) return null;
  return (
    <span
      className={`text-xs px-1.5 py-0.5 rounded ${
        overdue ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
      }`}
    >
      {overdue ? "Review due" : `Review in ${daysUntil}d`}
    </span>
  );
}

function PatternBadge({ pattern }: { pattern: string | null }) {
  if (!pattern) return null;
  return (
    <span className="text-xs px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">
      {pattern}
    </span>
  );
}

export default function Problems() {
  // ---- filter state ----
  const [difficulty, setDifficulty] = useState<Difficulty | undefined>();
  const [pattern, setPattern] = useState("");
  const [source, setSource] = useState("");
  const [company, setCompany] = useState("");
  const [category, setCategory] = useState<Category | undefined>();
  const [completedFilter, setCompletedFilter] = useState<
    "all" | "yes" | "no"
  >("all");
  const [sortBy, setSortBy] = useState<SortField>("created_at");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [page, setPage] = useState(0);

  // ---- data state ----
  const [problems, setProblems] = useState<Problem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ---- practice modal state ----
  const [practiceProblem, setPracticeProblem] = useState<Problem | null>(null);

  // ---- distinct patterns for dropdown ----
  const [allPatterns, setAllPatterns] = useState<string[]>([]);

  const filters: ProblemFilters = useMemo(
    () => ({
      difficulty,
      pattern: pattern || undefined,
      source: source || undefined,
      company: company || undefined,
      is_completed:
        completedFilter === "all"
          ? undefined
          : completedFilter === "yes",
      category,
      sort_by: sortBy,
      sort_order: sortOrder,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    }),
    [
      difficulty,
      pattern,
      source,
      company,
      completedFilter,
      category,
      sortBy,
      sortOrder,
      page,
    ],
  );

  const fetchProblems = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, string | number | boolean | undefined> = {
        sort_by: filters.sort_by,
        sort_order: filters.sort_order,
        limit: filters.limit,
        offset: filters.offset,
        difficulty: filters.difficulty,
        pattern: filters.pattern,
        source: filters.source,
        company: filters.company,
        is_completed: filters.is_completed,
        category: filters.category,
      };
      const result: PaginatedResult<Problem[]> =
        await api.getWithTotal<Problem[]>("/problems", { params });
      setProblems(result.data);
      setTotalCount(result.totalCount);
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchProblems();
  }, [fetchProblems]);

  // Load all problems once to extract unique patterns for the dropdown
  useEffect(() => {
    api
      .get<Problem[]>("/problems", {
        params: { limit: 200, offset: 0 },
      })
      .then((data) => {
        const patterns = [
          ...new Set(
            data
              .map((p) => p.pattern)
              .filter((p): p is string => p !== null),
          ),
        ].sort();
        setAllPatterns(patterns);
      })
      .catch(() => {
        /* non-critical */
      });
  }, []);

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  function resetFilters() {
    setDifficulty(undefined);
    setPattern("");
    setSource("");
    setCompany("");
    setCategory(undefined);
    setCompletedFilter("all");
    setSortBy("created_at");
    setSortOrder("desc");
    setPage(0);
  }

  // Reset to page 0 when filters change (not sort/page)
  const filterKey = JSON.stringify({
    difficulty,
    pattern,
    source,
    company,
    completedFilter,
    category,
  });
  useEffect(() => {
    setPage(0);
  }, [filterKey]);

  return (
    <div className="flex gap-6">
      {/* ---- Filter Sidebar ---- */}
      <aside className="w-56 shrink-0 space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
            Filters
          </h2>
          <button
            onClick={resetFilters}
            className="text-xs text-blue-600 hover:underline"
          >
            Reset
          </button>
        </div>

        {/* Difficulty */}
        <fieldset>
          <legend className="text-xs font-medium text-gray-500 mb-1">
            Difficulty
          </legend>
          <div className="space-y-1">
            {DIFFICULTIES.map((d) => (
              <label key={d} className="flex items-center gap-2 text-sm">
                <input
                  type="radio"
                  name="difficulty"
                  checked={difficulty === d}
                  onChange={() =>
                    setDifficulty(difficulty === d ? undefined : d)
                  }
                />
                <span className="capitalize">{d}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {/* Category */}
        <fieldset>
          <legend className="text-xs font-medium text-gray-500 mb-1">
            Category
          </legend>
          <select
            value={category ?? ""}
            onChange={(e) =>
              setCategory(
                (e.target.value as Category) || undefined,
              )
            }
            className="w-full text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="">All</option>
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </fieldset>

        {/* Pattern */}
        <fieldset>
          <legend className="text-xs font-medium text-gray-500 mb-1">
            Pattern
          </legend>
          <select
            value={pattern}
            onChange={(e) => setPattern(e.target.value)}
            className="w-full text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="">All</option>
            {allPatterns.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </fieldset>

        {/* Source */}
        <fieldset>
          <legend className="text-xs font-medium text-gray-500 mb-1">
            Source
          </legend>
          <input
            type="text"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="e.g. leetcode"
            className="w-full text-sm border border-gray-300 rounded px-2 py-1"
          />
        </fieldset>

        {/* Company */}
        <fieldset>
          <legend className="text-xs font-medium text-gray-500 mb-1">
            Company
          </legend>
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="e.g. google"
            className="w-full text-sm border border-gray-300 rounded px-2 py-1"
          />
        </fieldset>

        {/* Completed */}
        <fieldset>
          <legend className="text-xs font-medium text-gray-500 mb-1">
            Status
          </legend>
          <select
            value={completedFilter}
            onChange={(e) =>
              setCompletedFilter(
                e.target.value as "all" | "yes" | "no",
              )
            }
            className="w-full text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="all">All</option>
            <option value="yes">Completed</option>
            <option value="no">Not completed</option>
          </select>
        </fieldset>
      </aside>

      {/* ---- Main Content ---- */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">LeetCode Problems</h1>
          <span className="text-sm text-gray-500">
            {totalCount} problem{totalCount !== 1 ? "s" : ""}
          </span>
        </div>

        {/* Sort controls */}
        <div className="flex items-center gap-3 mb-3 text-sm">
          <label className="text-gray-500">Sort by</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortField)}
            className="border border-gray-300 rounded px-2 py-1"
          >
            <option value="created_at">Date added</option>
            <option value="comfort_level">Comfort</option>
            <option value="last_attempted_at">Last attempted</option>
            <option value="next_review_at">Next review</option>
          </select>
          <button
            onClick={() =>
              setSortOrder(sortOrder === "asc" ? "desc" : "asc")
            }
            className="px-2 py-1 border border-gray-300 rounded hover:bg-gray-100"
            title={`Currently: ${sortOrder}`}
          >
            {sortOrder === "asc" ? "Asc" : "Desc"}
          </button>
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
        {!loading && problems.length === 0 && (
          <div className="text-gray-400 py-8 text-center">
            No problems found.
          </div>
        )}

        {!loading && problems.length > 0 && (
          <div className="overflow-x-auto rounded border border-gray-200">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs text-gray-500 uppercase">
                <tr>
                  <th className="px-3 py-2 w-12">#</th>
                  <th className="px-3 py-2">Title</th>
                  <th className="px-3 py-2 w-24">Difficulty</th>
                  <th className="px-3 py-2 w-28">Pattern</th>
                  <th className="px-3 py-2 w-24">Comfort</th>
                  <th className="px-3 py-2 w-28">Review</th>
                  <th className="px-3 py-2 w-20"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {problems.map((p) => (
                  <tr
                    key={p.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-3 py-2 text-gray-400">
                      {p.leetcode_id ?? "-"}
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-2">
                        {p.url ? (
                          <a
                            href={p.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline font-medium truncate max-w-xs"
                            title={p.title}
                          >
                            {p.title}
                          </a>
                        ) : (
                          <span
                            className="font-medium truncate max-w-xs"
                            title={p.title}
                          >
                            {p.title}
                          </span>
                        )}
                        {p.is_completed && (
                          <span className="text-xs text-green-600">[done]</span>
                        )}
                      </div>
                      {p.company_tags.length > 0 && (
                        <div className="flex gap-1 mt-0.5 flex-wrap">
                          {p.company_tags.slice(0, 3).map((c) => (
                            <span
                              key={c}
                              className="text-xs text-gray-400"
                            >
                              {c}
                            </span>
                          ))}
                          {p.company_tags.length > 3 && (
                            <span className="text-xs text-gray-400">
                              +{p.company_tags.length - 3}
                            </span>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      {p.difficulty && (
                        <span
                          className={`text-xs px-1.5 py-0.5 rounded capitalize ${DIFFICULTY_COLORS[p.difficulty]}`}
                        >
                          {p.difficulty}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      <PatternBadge pattern={p.pattern} />
                    </td>
                    <td className="px-3 py-2">
                      <ComfortStars level={p.comfort_level} />
                    </td>
                    <td className="px-3 py-2">
                      <ReviewBadge nextReview={p.next_review_at} />
                    </td>
                    <td className="px-3 py-2">
                      <button
                        onClick={() => setPracticeProblem(p)}
                        className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Practice
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 text-sm">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              className="px-3 py-1 border border-gray-300 rounded disabled:opacity-40 hover:bg-gray-100"
            >
              Previous
            </button>
            <span className="text-gray-500">
              Page {page + 1} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages - 1}
              onClick={() =>
                setPage((p) => Math.min(totalPages - 1, p + 1))
              }
              className="px-3 py-1 border border-gray-300 rounded disabled:opacity-40 hover:bg-gray-100"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Practice Modal */}
      {practiceProblem && (
        <PracticeModal
          problem={practiceProblem}
          onClose={() => setPracticeProblem(null)}
          onSubmitted={() => {
            setPracticeProblem(null);
            fetchProblems();
          }}
        />
      )}
    </div>
  );
}
