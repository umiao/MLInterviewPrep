import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useToast } from "../contexts/ToastContext";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import SearchInput from "../components/ui/SearchInput";
import EmptyState from "../components/ui/EmptyState";
import Pagination from "../components/ui/Pagination";
import ConfirmDialog from "../components/ui/ConfirmDialog";
import Badge from "../components/ui/Badge";
import { useFilterParams } from "../hooks/useFilterParams";
import type {
  Category,
  Difficulty,
  Problem,
  ProblemFilters,
  SortField,
  SortOrder,
} from "../types/problem";
import PracticeModal from "../components/PracticeModal";
import ReviewPanel from "../components/ReviewPanel";
import AddProblemModal from "../components/problems/AddProblemModal";
import EditProblemModal from "../components/problems/EditProblemModal";
import ProblemDescriptionModal from "../components/problems/ProblemDescriptionModal";

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

// Stable schema for URL filter params (defined outside component to avoid re-creation)
const filterSchema = {
  difficulty: {
    defaultValue: undefined as Difficulty | undefined,
    parse: (raw: string) => raw as Difficulty,
  },
  pattern: { defaultValue: "" },
  source: { defaultValue: "" },
  company: { defaultValue: "" },
  search: { defaultValue: "" },
  category: {
    defaultValue: undefined as Category | undefined,
    parse: (raw: string) => raw as Category,
  },
  completed: { defaultValue: "all" },
  sortBy: {
    defaultValue: "created_at" as SortField,
    parse: (raw: string) => raw as SortField,
  },
  sortOrder: {
    defaultValue: "desc" as SortOrder,
    parse: (raw: string) => raw as SortOrder,
  },
  page: {
    defaultValue: 0,
    parse: (raw: string) => parseInt(raw, 10) || 0,
    serialize: (v: number) => String(v),
  },
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

export default function Problems() {
  const queryClient = useQueryClient();
  const toast = useToast();

  // ---- filter state (persisted in URL) ----
  const [
    { difficulty, pattern, source, company, search, category, completed, sortBy, sortOrder, page },
    { setDifficulty, setPattern, setSource, setCompany, setSearch, setCategory, setCompleted, setSortBy, setSortOrder, setPage, resetAll },
  ] = useFilterParams(filterSchema);

  // ---- modal state ----
  const [practiceProblem, setPracticeProblem] = useState<Problem | null>(null);
  const [reviewProblem, setReviewProblem] = useState<Problem | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editProblem, setEditProblem] = useState<Problem | null>(null);
  const [deleteProblem, setDeleteProblem] = useState<Problem | null>(null);
  const [descriptionProblem, setDescriptionProblem] = useState<Problem | null>(null);

  const filters: ProblemFilters = useMemo(
    () => ({
      difficulty,
      pattern: pattern || undefined,
      source: source || undefined,
      company: company || undefined,
      is_completed:
        completed === "all"
          ? undefined
          : completed === "yes",
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
      completed,
      category,
      sortBy,
      sortOrder,
      page,
    ],
  );

  const params: Record<string, string | number | boolean | undefined> = useMemo(() => ({
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
  }), [filters]);

  const { data: problemsResult, isLoading: loading, error: queryError } = useQuery({
    queryKey: ["problems", params],
    queryFn: () => api.getWithTotal<Problem[]>("/problems", { params }),
  });

  const allProblems = problemsResult?.data ?? [];
  const totalCount = problemsResult?.totalCount ?? 0;
  const error = queryError ? queryError.message : null;

  // Client-side text search across title/pattern/company_tags
  // TODO: Switch to server-side search when dataset exceeds ~500 problems
  const problems = useMemo(() => {
    if (!search) return allProblems;
    const lower = search.toLowerCase();
    return allProblems.filter(
      (p) =>
        p.title.toLowerCase().includes(lower) ||
        (p.pattern && p.pattern.toLowerCase().includes(lower)) ||
        p.company_tags.some((c) => c.toLowerCase().includes(lower)),
    );
  }, [allProblems, search]);

  // Load all problems once to extract unique patterns for the dropdown
  const { data: allProblemsData } = useQuery({
    queryKey: ["problems", "allPatterns"],
    queryFn: () => api.get<Problem[]>("/problems", { params: { limit: 200, offset: 0 } }),
    staleTime: 60_000,
  });

  const allPatterns = useMemo(() => {
    if (!allProblemsData) return [];
    return [
      ...new Set(
        allProblemsData
          .map((p) => p.pattern)
          .filter((p): p is string => p !== null),
      ),
    ].sort();
  }, [allProblemsData]);

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  // Reset to page 0 when filters change (not sort/page)
  const filterKey = JSON.stringify({
    difficulty,
    pattern,
    source,
    company,
    completed,
    category,
  });
  const prevFilterKey = useRef(filterKey);
  useEffect(() => {
    if (prevFilterKey.current !== filterKey) {
      prevFilterKey.current = filterKey;
      setPage(0);
    }
  }, [filterKey, setPage]);

  // ---- delete mutation ----
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.del(`/problems/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
      toast.success("Problem deleted");
      setDeleteProblem(null);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to delete problem");
    },
  });

  const handleSearchChange = useCallback(
    (value: string) => setSearch(value),
    [setSearch],
  );

  return (
    <div className="flex gap-6">
      {/* ---- Filter Sidebar ---- */}
      <aside className="w-56 shrink-0 space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
            Filters
          </h2>
          <button
            onClick={resetAll}
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
            value={completed}
            onChange={(e) =>
              setCompleted(e.target.value)
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
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              {totalCount} problem{totalCount !== 1 ? "s" : ""}
            </span>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              + Add Problem
            </button>
          </div>
        </div>

        {/* Search + Sort controls */}
        <div className="flex items-center gap-3 mb-3">
          <SearchInput
            value={search}
            onChange={handleSearchChange}
            placeholder="Search title, pattern, company..."
            className="flex-1 max-w-sm"
          />
          <div className="flex items-center gap-2 text-sm ml-auto">
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
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-3">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && <LoadingSpinner message="Loading problems..." />}

        {/* Empty state */}
        {!loading && problems.length === 0 && (
          <EmptyState
            message={search ? "No problems match your search." : "No problems found."}
            action={
              !search
                ? { label: "Add your first problem", onClick: () => setShowAddModal(true) }
                : undefined
            }
          />
        )}

        {/* Table */}
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
                  <th className="px-3 py-2 w-40">Actions</th>
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
                        <button
                          onClick={() => setDescriptionProblem(p)}
                          className="text-blue-600 hover:underline font-medium truncate max-w-xs text-left"
                          title="View description"
                        >
                          {p.title}
                        </button>
                        {p.url && (
                          <a
                            href={p.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-400 hover:text-gray-600 shrink-0"
                            title="Open on LeetCode"
                          >
                            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" />
                            </svg>
                          </a>
                        )}
                        {p.is_completed && (
                          <Badge variant="green">done</Badge>
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
                        <Badge
                          variant={
                            p.difficulty === "easy"
                              ? "green"
                              : p.difficulty === "medium"
                                ? "yellow"
                                : "red"
                          }
                          className="capitalize"
                        >
                          {p.difficulty}
                        </Badge>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      {p.pattern && <Badge variant="blue">{p.pattern}</Badge>}
                    </td>
                    <td className="px-3 py-2">
                      <ComfortStars level={p.comfort_level} />
                    </td>
                    <td className="px-3 py-2">
                      <ReviewBadge nextReview={p.next_review_at} />
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex gap-1">
                        <button
                          onClick={() => setPracticeProblem(p)}
                          className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Practice
                        </button>
                        <button
                          onClick={() => setReviewProblem(p)}
                          className="text-xs px-2 py-1 bg-purple-600 text-white rounded hover:bg-purple-700"
                        >
                          Review
                        </button>
                        <button
                          onClick={() => setEditProblem(p)}
                          className="text-xs px-2 py-1 border border-gray-300 rounded hover:bg-gray-100 text-gray-600"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeleteProblem(p)}
                          className="text-xs px-2 py-1 border border-red-200 rounded hover:bg-red-50 text-red-600"
                        >
                          Del
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>

      {/* Add Problem Modal */}
      <AddProblemModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
      />

      {/* Edit Problem Modal */}
      <EditProblemModal
        problem={editProblem}
        onClose={() => setEditProblem(null)}
      />

      {/* Delete Confirm Dialog */}
      <ConfirmDialog
        open={deleteProblem !== null}
        onClose={() => setDeleteProblem(null)}
        onConfirm={() => deleteProblem && deleteMutation.mutate(deleteProblem.id)}
        title="Delete Problem"
        message={`Are you sure you want to delete "${deleteProblem?.title}"? This will also delete all associated attempts and QA sessions.`}
        confirmLabel="Delete"
        confirmVariant="danger"
        loading={deleteMutation.isPending}
      />

      {/* Practice Modal */}
      {practiceProblem && (
        <PracticeModal
          problem={practiceProblem}
          onClose={() => setPracticeProblem(null)}
          onSubmitted={() => {
            setPracticeProblem(null);
            queryClient.invalidateQueries({ queryKey: ["problems"] });
          }}
        />
      )}

      {/* Review Panel */}
      {reviewProblem && (
        <ReviewPanel
          problem={reviewProblem}
          onClose={() => setReviewProblem(null)}
        />
      )}

      {/* Description Modal */}
      {descriptionProblem && (
        <ProblemDescriptionModal
          problem={descriptionProblem}
          onClose={() => setDescriptionProblem(null)}
        />
      )}
    </div>
  );
}
