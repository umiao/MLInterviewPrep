/**
 * ProblemDescriptionModal -- shows problem description in-app.
 * If no description, offers "Fetch from Neetcode" button.
 * If fetch fails, provides fallback links to neetcode/leetcode.
 */
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../utils/api";
import { useToast } from "../../contexts/ToastContext";
import Badge from "../ui/Badge";
import type { Problem } from "../../types/problem";

interface ProblemDescriptionModalProps {
  problem: Problem;
  onClose: () => void;
}

export default function ProblemDescriptionModal({
  problem,
  onClose,
}: ProblemDescriptionModalProps) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [fetchError, setFetchError] = useState<string | null>(null);

  const fetchMutation = useMutation({
    mutationFn: () =>
      api.post<{
        description: string;
        description_source: string;
        neetcode_slug: string;
        url: string;
      }>(`/problems/${problem.id}/fetch-description`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["problems"] });
      toast.success("Description fetched from neetcode.io");
      setFetchError(null);
    },
    onError: (err: Error) => {
      setFetchError(err.message || "Failed to fetch description");
    },
  });

  const slug =
    problem.neetcode_slug ||
    problem.title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-{2,}/g, "-")
      .replace(/^-|-$/g, "");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold text-gray-900 truncate">
                {problem.leetcode_id ? `#${problem.leetcode_id} ` : ""}
                {problem.title}
              </h2>
            </div>
            <div className="flex items-center gap-2 mt-1">
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
              {problem.pattern && (
                <Badge variant="blue">{problem.pattern}</Badge>
              )}
              {problem.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
          <button
            onClick={onClose}
            className="ml-4 text-gray-400 hover:text-gray-600 text-xl leading-none"
            title="Close"
          >
            x
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {problem.description ? (
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed">
              {problem.description}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">
                No description stored locally.
              </p>
              <button
                onClick={() => fetchMutation.mutate()}
                disabled={fetchMutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {fetchMutation.isPending
                  ? "Fetching..."
                  : "Fetch from Neetcode"}
              </button>

              {fetchError && (
                <div className="mt-4 text-sm text-red-600 bg-red-50 rounded px-4 py-3">
                  <p>{fetchError}</p>
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

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-gray-200">
          <div className="text-xs text-gray-400">
            {problem.description_source && (
              <span>Source: {problem.description_source}</span>
            )}
          </div>
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-100 text-gray-600"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
