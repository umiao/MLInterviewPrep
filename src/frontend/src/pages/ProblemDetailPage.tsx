import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import { useToast } from "../contexts/ToastContext";
import Badge from "../components/ui/Badge";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import MarkdownPreview from "../components/ui/MarkdownPreview";
import type { Problem } from "../types/problem";

/**
 * Full-screen problem detail page at /problems/:problemId.
 * Shows problem description with proper HTML/markdown rendering,
 * notes, and fetch controls.
 */
export default function ProblemDetailPage() {
  const { problemId: rawId } = useParams<{ problemId: string }>();
  const problemId = Number(rawId);
  const queryClient = useQueryClient();
  const toast = useToast();
  const [notesOpen, setNotesOpen] = useState(false);

  const { data: problem, isLoading } = useQuery<Problem>({
    queryKey: ["problem", problemId],
    queryFn: () => api.get<Problem>(`/problems/${problemId}`),
    enabled: problemId > 0,
  });

  const fetchMutation = useMutation({
    mutationFn: () =>
      api.post<{
        description: string;
        description_source: string;
        neetcode_slug: string;
        url: string;
      }>(`/problems/${problemId}/fetch-description`),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["problem", problemId] });
      queryClient.invalidateQueries({ queryKey: ["problems"] });
      const source = data.description_source || "external source";
      toast.success(`Description fetched from ${source}`);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to fetch description");
    },
  });

  if (isLoading) return <LoadingSpinner message="Loading problem..." />;
  if (!problem) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Problem not found.</p>
        <Link to="/problems" className="text-blue-600 hover:underline mt-2 inline-block">
          Back to Problems
        </Link>
      </div>
    );
  }

  const slug =
    problem.neetcode_slug ||
    problem.title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-{2,}/g, "-")
      .replace(/^-|-$/g, "");

  const isHtml = problem.description?.includes("<") ?? false;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="mb-4">
        <Link
          to="/problems"
          className="text-sm text-blue-600 hover:underline"
        >
          &larr; Back to Problems
        </Link>
      </div>

      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-2xl font-bold text-gray-900">
            {problem.leetcode_id ? `#${problem.leetcode_id} ` : ""}
            {problem.title}
          </h1>
          {problem.url && (
            <a
              href={problem.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-gray-600 shrink-0"
              title="Open on LeetCode"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" />
              </svg>
            </a>
          )}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {problem.difficulty && (
            <Badge
              variant={
                problem.difficulty === "easy"
                  ? "green"
                  : problem.difficulty === "medium"
                    ? "yellow"
                    : "red"
              }
              className="capitalize"
            >
              {problem.difficulty}
            </Badge>
          )}
          {problem.pattern && <Badge variant="blue">{problem.pattern}</Badge>}
          {problem.is_completed && <Badge variant="green">done</Badge>}
          {problem.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded"
            >
              {tag}
            </span>
          ))}
          {problem.description_source && (
            <span className="text-xs text-gray-400 ml-auto">
              Source: {problem.description_source}
            </span>
          )}
        </div>
      </div>

      {/* Description */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        {problem.description ? (
          isHtml ? (
            <div
              className="prose prose-sm max-w-none text-gray-700 leading-relaxed
                prose-table:border-collapse prose-table:w-full
                prose-th:border prose-th:border-gray-300 prose-th:bg-gray-50 prose-th:px-3 prose-th:py-2 prose-th:text-left prose-th:text-xs prose-th:font-semibold
                prose-td:border prose-td:border-gray-200 prose-td:px-3 prose-td:py-2
                prose-code:bg-gray-100 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:before:content-none prose-code:after:content-none
                prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:rounded-lg prose-pre:p-4
                prose-img:max-w-full prose-img:rounded
              "
              dangerouslySetInnerHTML={{ __html: problem.description }}
            />
          ) : (
            <MarkdownPreview markdown={problem.description} />
          )
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No description stored locally.</p>
            <button
              onClick={() => fetchMutation.mutate()}
              disabled={fetchMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {fetchMutation.isPending ? "Fetching..." : "Fetch Description"}
            </button>

            {fetchMutation.isError && (
              <div className="mt-4 text-sm text-red-600 bg-red-50 rounded px-4 py-3 inline-block">
                <p>{fetchMutation.error?.message}</p>
                <div className="mt-2 flex gap-3 justify-center">
                  <a
                    href={`https://neetcode.io/problems/${slug}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Open on Neetcode
                  </a>
                  {problem.url && (
                    <a
                      href={problem.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      Open on LeetCode
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* My Notes (collapsible, default collapsed) */}
      {problem.notes && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg mb-6">
          <button
            type="button"
            onClick={() => setNotesOpen((prev) => !prev)}
            className="w-full flex items-center justify-between px-6 py-3 text-left hover:bg-amber-100/50 rounded-lg transition-colors"
          >
            <h3 className="text-sm font-semibold text-amber-800">My Notes</h3>
            <svg
              className={`w-4 h-4 text-amber-600 transition-transform ${notesOpen ? "rotate-180" : ""}`}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>
          {notesOpen && (
            <div className="px-6 pb-6">
              <MarkdownPreview markdown={problem.notes} />
            </div>
          )}
        </div>
      )}

      {/* Actions footer */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {problem.description && (
            <button
              onClick={() => fetchMutation.mutate()}
              disabled={fetchMutation.isPending}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-100 text-gray-600 disabled:opacity-50"
            >
              {fetchMutation.isPending ? "Fetching..." : "Re-fetch Description"}
            </button>
          )}
        </div>
        <div className="flex gap-2">
          {problem.url && (
            <a
              href={problem.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-100 text-gray-600"
            >
              Open on LeetCode
            </a>
          )}
          <a
            href={`https://neetcode.io/problems/${slug}`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-100 text-gray-600"
          >
            Open on Neetcode
          </a>
        </div>
      </div>
    </div>
  );
}
