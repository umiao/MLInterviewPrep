import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../utils/api";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import SearchInput from "../components/ui/SearchInput";
import EmptyState from "../components/ui/EmptyState";
import Pagination from "../components/ui/Pagination";
import Badge from "../components/ui/Badge";
import Tabs from "../components/ui/Tabs";
import { useFilterParams } from "../hooks/useFilterParams";
import type {
  Category,
  Difficulty,
  Problem,
  ProblemFilters,
  SortField,
  SortOrder,
} from "../types/problem";
import { useToast } from "../contexts/ToastContext";
import AddProblemModal from "../components/problems/AddProblemModal";

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

const TABS = [
  { key: "all", label: "All Problems" },
  { key: "blind75", label: "Blind Grind 75" },
];

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


function ProgressBar({ completed, total }: { completed: number; total: number }) {
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-green-500 h-2.5 rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-sm font-medium text-gray-600 whitespace-nowrap">
        {completed} / {total} completed ({pct}%)
      </span>
    </div>
  );
}

interface FetchAllResult {
  fetched: number;
  failed: { id: number; title: string; url: string | null; neetcode_slug: string; neetcode_url: string }[];
  total_processed: number;
}

export default function Problems() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const [fetchAllResult, setFetchAllResult] = useState<FetchAllResult | null>(null);

  // Tab state from URL
  const activeTab = searchParams.get("tab") || "all";
  const blind75View = searchParams.get("blind75View") || "grouped";
  const setBlind75View = useCallback(
    (view: string) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (view === "grouped") {
            next.delete("blind75View");
          } else {
            next.set("blind75View", view);
          }
          return next;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );
  const setActiveTab = useCallback(
    (tab: string) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (tab === "all") {
            next.delete("tab");
          } else {
            next.set("tab", tab);
          }
          // Reset page when switching tabs
          next.delete("page");
          return next;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  // ---- filter state (persisted in URL) ----
  const [
    { difficulty, pattern, source, company, search, category, completed, sortBy, sortOrder, page },
    { setDifficulty, setPattern, setSource, setCompany, setSearch, setCategory, setCompleted, setSortBy, setSortOrder, setPage, resetAll },
  ] = useFilterParams(filterSchema);

  // ---- modal state ----
  const [showAddModal, setShowAddModal] = useState(false);

  // ---- fetch all descriptions mutation ----
  const fetchAllMutation = useMutation({
    mutationFn: () => api.post<FetchAllResult>("/problems/fetch-all-descriptions"),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
      toast.success(`Fetched ${data.fetched} descriptions. ${data.failed.length} failed.`);
      if (data.failed.length > 0) {
        setFetchAllResult(data);
      }
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to fetch descriptions");
    },
  });

  const isBlind75 = activeTab === "blind75";
  // Load all results when searching or on Blind75 tab (159 problems total is safe)
  const loadAll = isBlind75 || !!search;

  const filters: ProblemFilters = useMemo(
    () => ({
      difficulty,
      pattern: pattern || undefined,
      source: isBlind75 ? "blind75" : source || undefined,
      company: company || undefined,
      is_completed:
        completed === "all"
          ? undefined
          : completed === "yes",
      category,
      sort_by: sortBy,
      sort_order: sortOrder,
      limit: loadAll ? 200 : PAGE_SIZE,
      offset: loadAll ? 0 : page * PAGE_SIZE,
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
      loadAll,
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
    search: search || undefined,
  }), [filters, search]);

  const { data: problemsResult, isLoading: loading, error: queryError } = useQuery({
    queryKey: ["problems", params],
    queryFn: () => api.getWithTotal<Problem[]>("/problems", { params }),
  });

  const allProblems = problemsResult?.data ?? [];
  const totalCount = problemsResult?.totalCount ?? 0;
  const error = queryError ? queryError.message : null;

  // Search is now server-side; use allProblems directly
  const problems = allProblems;

  // For Blind 75 tab: group by pattern with sort applied within groups
  const blind75ByPattern = useMemo(() => {
    if (!isBlind75) return [];
    const groups: Record<string, Problem[]> = {};
    for (const p of problems) {
      const key = p.pattern || "other";
      if (!groups[key]) groups[key] = [];
      groups[key].push(p);
    }
    // Sort within each group by the active sort field
    const DIFFICULTY_ORDER: Record<string, number> = { easy: 0, medium: 1, hard: 2 };
    const dir = sortOrder === "asc" ? 1 : -1;
    for (const group of Object.values(groups)) {
      group.sort((a, b) => {
        let cmp = 0;
        switch (sortBy) {
          case "difficulty":
            cmp = (DIFFICULTY_ORDER[a.difficulty ?? ""] ?? 9) - (DIFFICULTY_ORDER[b.difficulty ?? ""] ?? 9);
            break;
          case "comfort_level":
            cmp = a.comfort_level - b.comfort_level;
            break;
          case "last_attempted_at":
            cmp = (a.last_attempted_at ?? "").localeCompare(b.last_attempted_at ?? "");
            break;
          case "next_review_at":
            // next_review_at sort kept for type compatibility but unused in UI
            cmp = (a.next_review_at ?? "").localeCompare(b.next_review_at ?? "");
            break;
          default: // created_at
            cmp = (a.created_at ?? "").localeCompare(b.created_at ?? "");
            break;
        }
        return cmp * dir;
      });
    }
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
  }, [problems, isBlind75, sortBy, sortOrder]);

  const blind75Stats = useMemo(() => {
    if (!isBlind75) return { completed: 0, total: 0 };
    return {
      completed: problems.filter((p) => p.is_completed).length,
      total: problems.length,
    };
  }, [problems, isBlind75]);

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

  const effectivePageSize = loadAll ? 200 : PAGE_SIZE;
  const totalPages = Math.max(1, Math.ceil(totalCount / effectivePageSize));

  // Reset to page 0 when filters change (not sort/page)
  const filterKey = JSON.stringify({
    difficulty,
    pattern,
    source,
    company,
    completed,
    category,
    search,
  });
  const prevFilterKey = useRef(filterKey);
  useEffect(() => {
    if (prevFilterKey.current !== filterKey) {
      prevFilterKey.current = filterKey;
      setPage(0);
    }
  }, [filterKey, setPage]);

  const handleSearchChange = useCallback(
    (value: string) => setSearch(value),
    [setSearch],
  );

  // Shared table row renderer
  const renderProblemRow = (p: Problem, showNotes?: boolean) => (
    <tr
      key={p.id}
      className="hover:bg-gray-50 transition-colors"
    >
      <td className="px-3 py-2 text-gray-400">
        {p.leetcode_id ?? "-"}
      </td>
      <td className="px-3 py-2">
        <div className="flex items-center gap-2">
          <Link
            to={`/problems/${p.id}`}
            className="text-blue-600 hover:underline font-medium truncate max-w-xs block"
            title="View description"
          >
            {p.title}
          </Link>
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
          {!showNotes && p.notes && (
            <span
              className="text-amber-500 shrink-0"
              title="Has notes"
            >
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
            </span>
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
      {(!isBlind75 || blind75View === "flat") && (
        <td className="px-3 py-2">
          {p.pattern && <Badge variant="blue">{p.pattern}</Badge>}
        </td>
      )}
      <td className="px-3 py-2">
        <ComfortStars level={p.comfort_level} />
      </td>
      {showNotes && (
        <td className="px-3 py-2">
          {p.notes ? (
            <Link
              to={`/problems/${p.id}`}
              className="text-xs text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded truncate max-w-[120px] block"
              title={p.notes}
            >
              {p.notes.slice(0, 40)}{p.notes.length > 40 ? "..." : ""}
            </Link>
          ) : (
            <span className="text-xs text-gray-300">--</span>
          )}
        </td>
      )}
      <td className="px-3 py-2">
        <Link
          to={`/problems/${p.id}`}
          className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 inline-block"
        >
          View
        </Link>
      </td>
    </tr>
  );

  // Shared sort/search bar rendered in both tabs
  const renderSortBar = () => (
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
          <option value="difficulty">Difficulty</option>
          <option value="last_attempted_at">Last attempted</option>
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
  );

  const renderBlind75Content = () => (
    <div className="space-y-4">
      {/* Progress header */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">Blind Grind 75 Progress</h2>
        <ProgressBar completed={blind75Stats.completed} total={blind75Stats.total} />
      </div>

      {/* View toggle + Search + Sort controls */}
      <div className="flex items-center gap-3 mb-1">
        <div className="inline-flex rounded border border-gray-300 text-sm">
          <button
            onClick={() => setBlind75View("grouped")}
            className={`px-3 py-1 ${blind75View === "grouped" ? "bg-blue-600 text-white" : "bg-white text-gray-600 hover:bg-gray-50"} rounded-l`}
          >
            Grouped by Pattern
          </button>
          <button
            onClick={() => setBlind75View("flat")}
            className={`px-3 py-1 ${blind75View === "flat" ? "bg-blue-600 text-white" : "bg-white text-gray-600 hover:bg-gray-50"} rounded-r border-l border-gray-300`}
          >
            All Problems
          </button>
        </div>
      </div>
      {loading && <LoadingSpinner message="Loading problems..." />}

      {!loading && problems.length === 0 && (
        <EmptyState message="No Blind 75 problems found. Import them using the import script." />
      )}

      {/* Flat (ungrouped) view */}
      {!loading && blind75View === "flat" && problems.length > 0 && (
        <div className="overflow-x-auto rounded border border-gray-200">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs text-gray-500 uppercase">
              <tr>
                <th className="px-3 py-2 w-12">#</th>
                <th className="px-3 py-2">Title</th>
                <th className="px-3 py-2 w-24">Difficulty</th>
                <th className="px-3 py-2 w-28">Pattern</th>
                <th className="px-3 py-2 w-24">Comfort</th>
                <th className="px-3 py-2 w-28">Notes</th>
                <th className="px-3 py-2 w-20">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {problems.map((p) => renderProblemRow(p, true))}
            </tbody>
          </table>
        </div>
      )}

      {/* Grouped by pattern view */}
      {!loading && blind75View === "grouped" && blind75ByPattern.map(([patternName, patternProblems]) => (
        <div key={patternName} className="space-y-1">
          <h3 className="text-sm font-semibold text-gray-700 px-1 capitalize flex items-center gap-2">
            <Badge variant="blue">{patternName}</Badge>
            <span className="text-xs text-gray-400 font-normal">
              {patternProblems.filter((p) => p.is_completed).length}/{patternProblems.length}
            </span>
          </h3>
          <div className="overflow-x-auto rounded border border-gray-200">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs text-gray-500 uppercase">
                <tr>
                  <th className="px-3 py-2 w-12">#</th>
                  <th className="px-3 py-2">Title</th>
                  <th className="px-3 py-2 w-24">Difficulty</th>
                  <th className="px-3 py-2 w-24">Comfort</th>
                  <th className="px-3 py-2 w-28">Notes</th>
                    <th className="px-3 py-2 w-20">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {patternProblems.map((p) => renderProblemRow(p, true))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );

  const renderAllProblemsContent = () => (
    <>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">LeetCode Problems</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">
            {totalCount} problem{totalCount !== 1 ? "s" : ""}
          </span>
          <button
            onClick={() => fetchAllMutation.mutate()}
            disabled={fetchAllMutation.isPending}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-100 text-gray-600 disabled:opacity-50"
          >
            {fetchAllMutation.isPending ? "Fetching..." : "Fetch All Descriptions"}
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + Add Problem
          </button>
        </div>
      </div>

      {/* Fetch-all failures report */}
      {fetchAllResult && fetchAllResult.failed.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-amber-800">
              {fetchAllResult.failed.length} problem{fetchAllResult.failed.length !== 1 ? "s" : ""} could not be fetched
            </h3>
            <button
              onClick={() => setFetchAllResult(null)}
              className="text-xs text-amber-600 hover:underline"
            >
              Dismiss
            </button>
          </div>
          <p className="text-xs text-amber-700 mb-2">
            Please verify the neetcode links below are correct. If not, provide the correct slug.
          </p>
          <div className="space-y-1">
            {fetchAllResult.failed.map((f) => (
              <div key={f.id} className="flex items-center gap-2 text-xs">
                <Link to={`/problems/${f.id}`} className="text-blue-600 hover:underline font-medium">
                  {f.title}
                </Link>
                <span className="text-gray-400">-</span>
                <a
                  href={f.neetcode_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-amber-700 hover:underline"
                >
                  {f.neetcode_url}
                </a>
                {f.url && (
                  <a
                    href={f.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-500 hover:underline"
                  >
                    [LeetCode]
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

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
                <th className="px-3 py-2 w-20">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {problems.map((p) => renderProblemRow(p))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
    </>
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

        {/* Source -- hidden in blind75 tab */}
        {!isBlind75 && (
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
        )}

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
        {renderSortBar()}
        <Tabs
          tabs={TABS}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        >
          {(tab) => (
            tab === "blind75" ? renderBlind75Content() : renderAllProblemsContent()
          )}
        </Tabs>
      </div>

      {/* Add Problem Modal */}
      <AddProblemModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
      />


    </div>
  );
}
