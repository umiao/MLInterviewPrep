import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiRequestError } from "../utils/api";
import { useToast } from "../contexts/ToastContext";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import AddQuestionModal from "../components/questions/AddQuestionModal";
import EditableQuestionRow from "../components/questions/EditableQuestionRow";
import type { InterviewQuestion, QuestionType } from "../types/question";

/* ---------- Paste Response Types ---------- */

interface PasteExtractedQuestion {
  id: number;
  question_text: string;
  question_type: string | null;
  company: string | null;
  role: string | null;
}

interface PasteResponse {
  questions_count: number;
  questions: PasteExtractedQuestion[];
  was_duplicate: boolean;
}

/* ---------- Paste Experience Modal ---------- */

function PasteExperienceModal({
  open,
  onClose,
  onSuccess,
}: {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [text, setText] = useState("");
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PasteResponse | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Focus textarea when modal opens
  useEffect(() => {
    if (open && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [open]);

  function resetForm() {
    setText("");
    setCompany("");
    setRole("");
    setError(null);
    setResult(null);
    setSubmitting(false);
  }

  function handleClose() {
    resetForm();
    onClose();
  }

  async function handleExtract() {
    if (text.trim().length < 10) {
      setError("Text must be at least 10 characters.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const body: Record<string, string> = { text: text.trim() };
      if (company.trim()) body.company = company.trim();
      if (role.trim()) body.role = role.trim();
      const res = await api.post<PasteResponse>("/scraper/paste", body);
      setResult(res);
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  function handleConfirm() {
    onSuccess();
    handleClose();
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Paste Interview Experience</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
            aria-label="Close"
          >
            x
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {!result ? (
            <>
              {/* Input form */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Experience Text *
                </label>
                <textarea
                  ref={textareaRef}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={10}
                  placeholder="Paste your interview experience here... (questions, topics discussed, rounds, etc.)"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-y"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Min 10 characters. The LLM will extract individual questions.
                </p>
              </div>
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company (optional)
                  </label>
                  <input
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="e.g. Google"
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role (optional)
                  </label>
                  <input
                    type="text"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    placeholder="e.g. MLE"
                    className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
                  />
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Review extracted questions */}
              {result.was_duplicate && (
                <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 text-sm px-4 py-2 rounded">
                  This text was already processed. Showing previously extracted questions.
                </div>
              )}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  Extracted Questions ({result.questions_count})
                </h3>
                {result.questions.length === 0 ? (
                  <p className="text-sm text-gray-500">
                    No questions could be extracted from the text.
                  </p>
                ) : (
                  <ul className="space-y-2">
                    {result.questions.map((q) => (
                      <li
                        key={q.id}
                        className="border border-gray-200 rounded px-3 py-2 text-sm"
                      >
                        <p className="text-gray-800">{q.question_text}</p>
                        <div className="flex gap-3 mt-1 text-xs text-gray-500">
                          {q.question_type && (
                            <span
                              className={`px-2 py-0.5 rounded ${typeBadgeClass(q.question_type)}`}
                            >
                              {typeLabel(q.question_type)}
                            </span>
                          )}
                          {q.company && <span>Company: {q.company}</span>}
                          {q.role && <span>Role: {q.role}</span>}
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 text-red-700 text-sm px-4 py-2 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-5 py-3 border-t border-gray-200">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
          >
            {result ? "Close" : "Cancel"}
          </button>
          {!result ? (
            <button
              onClick={handleExtract}
              disabled={submitting || text.trim().length < 10}
              className="px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? "Extracting..." : "Extract Questions"}
            </button>
          ) : result.questions.length > 0 ? (
            <button
              onClick={handleConfirm}
              className="px-4 py-2 text-sm text-white bg-green-600 rounded hover:bg-green-700"
            >
              Done ({result.questions_count} added)
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

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
  const queryClient = useQueryClient();
  const toast = useToast();
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [page, setPage] = useState(0);
  const [pasteOpen, setPasteOpen] = useState(false);
  const [addOpen, setAddOpen] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const PAGE_SIZE = 50;

  const queryParams = useMemo(() => {
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
    return params;
  }, [filters, page]);

  const { data: questions = [], isLoading: loading, error: queryError } = useQuery({
    queryKey: ["questions", queryParams],
    queryFn: () => api.get<InterviewQuestion[]>("/questions", { params: queryParams }),
  });

  const error = queryError ? queryError.message : null;

  // Clear selection when questions change (page/filter change)
  useEffect(() => {
    setSelectedIds(new Set());
  }, [queryParams]);

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

  const toggleReviewedMutation = useMutation({
    mutationFn: ({ id, reviewed }: { id: number; reviewed: boolean }) =>
      api.put(`/questions/${id}`, { is_reviewed: reviewed }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
    },
    onError: () => {
      toast.error("Failed to update review status");
    },
  });

  function handleToggleReviewed(id: number, reviewed: boolean) {
    toggleReviewedMutation.mutate({ id, reviewed });
  }

  // Bulk mark reviewed mutation
  const bulkReviewMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await Promise.all(
        ids.map((id) => api.put(`/questions/${id}`, { is_reviewed: true })),
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions"] });
      toast.success(`${selectedIds.size} question(s) marked as reviewed`);
      setSelectedIds(new Set());
    },
    onError: () => {
      toast.error("Failed to bulk update review status");
    },
  });

  function handleBulkMarkReviewed() {
    bulkReviewMutation.mutate(Array.from(selectedIds));
  }

  function handleToggleSelect(id: number) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  function handleSelectAll() {
    if (selectedIds.size === questions.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(questions.map((q) => q.id)));
    }
  }

  const hasFilters = Object.values(filters).some((v) => v !== "");
  const allSelected = questions.length > 0 && selectedIds.size === questions.length;

  return (
    <div className="flex flex-col h-full">
      {/* Modals */}
      <PasteExperienceModal
        open={pasteOpen}
        onClose={() => setPasteOpen(false)}
        onSuccess={() => {
          setPage(0);
          queryClient.invalidateQueries({ queryKey: ["questions"] });
        }}
      />
      <AddQuestionModal
        open={addOpen}
        onClose={() => setAddOpen(false)}
      />

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Interview Questions</h1>
          <p className="text-sm text-gray-500">
            {questions.length} question{questions.length !== 1 ? "s" : ""} shown
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAddOpen(true)}
            className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            + Add Question
          </button>
          <button
            onClick={() => setPasteOpen(true)}
            className="px-4 py-2 text-sm text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50"
          >
            Paste Experience
          </button>
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
      {loading && <LoadingSpinner message="Loading questions..." />}

      {/* Table */}
      {!loading && (
        <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
          <table className="w-full text-sm table-fixed">
            <thead className="bg-gray-50 sticky top-0">
              <tr className="text-left text-xs font-medium text-gray-500 uppercase">
                <th className="px-3 py-2 w-10">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300"
                    title="Select all"
                  />
                </th>
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
                    colSpan={8}
                    className="px-4 py-8 text-center text-gray-400"
                  >
                    No questions found. Try adjusting your filters.
                  </td>
                </tr>
              )}
              {questions.map((q) => (
                <tbody key={q.id}>
                  <tr
                    onClick={() =>
                      setExpandedId(expandedId === q.id ? null : q.id)
                    }
                    className={`border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                      expandedId === q.id ? "bg-gray-50" : ""
                    }`}
                  >
                    <td
                      className="px-3 py-2 w-10"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <input
                        type="checkbox"
                        checked={selectedIds.has(q.id)}
                        onChange={() => handleToggleSelect(q.id)}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="px-4 py-2 w-8 text-gray-400 text-xs">
                      {expandedId === q.id ? "v" : ">"}
                    </td>
                    <td className="px-4 py-2 overflow-hidden text-ellipsis">
                      <span className="line-clamp-2">{q.question_text}</span>
                    </td>
                    <td className="px-4 py-2 w-32 text-gray-600 truncate">
                      {q.company ?? "-"}
                    </td>
                    <td className="px-4 py-2 w-28 text-gray-600 truncate">
                      {q.role ?? "-"}
                    </td>
                    <td className="px-4 py-2 w-36">
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${typeBadgeClass(q.question_type)}`}
                      >
                        {typeLabel(q.question_type)}
                      </span>
                    </td>
                    <td className="px-4 py-2 w-24 text-center">
                      {q.is_reviewed ? (
                        <span className="text-green-600 text-xs font-medium">
                          Yes
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">No</span>
                      )}
                    </td>
                    <td className="px-4 py-2 w-20 text-center text-gray-500">
                      {q.year ?? "-"}
                    </td>
                  </tr>
                  {expandedId === q.id && (
                    <EditableQuestionRow
                      question={q}
                      onToggleReviewed={handleToggleReviewed}
                    />
                  )}
                </tbody>
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

      {/* Floating bulk action bar */}
      {selectedIds.size > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 bg-gray-800 text-white rounded-lg shadow-xl px-5 py-3 flex items-center gap-4">
          <span className="text-sm">
            {selectedIds.size} question{selectedIds.size !== 1 ? "s" : ""} selected
          </span>
          <button
            onClick={handleBulkMarkReviewed}
            disabled={bulkReviewMutation.isPending}
            className="text-sm px-4 py-1.5 bg-green-600 rounded hover:bg-green-700 disabled:opacity-50"
          >
            {bulkReviewMutation.isPending
              ? "Marking..."
              : "Mark Reviewed"}
          </button>
          <button
            onClick={() => setSelectedIds(new Set())}
            className="text-sm px-3 py-1.5 border border-gray-500 rounded hover:bg-gray-700"
          >
            Clear
          </button>
        </div>
      )}
    </div>
  );
}
