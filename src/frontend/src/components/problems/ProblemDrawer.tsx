import { useQuery } from "@tanstack/react-query";
import { api } from "../../utils/api";
import type { Problem } from "../../types/problem";
import SlideOverPanel from "../ui/SlideOverPanel";
import MarkdownPreview from "../ui/MarkdownPreview";
import GoldenToggleButton from "../ui/GoldenToggleButton";

interface ProblemDrawerProps {
  /** LeetCode problem number to display. Null/undefined falls back to dbId. */
  lcId?: number | null;
  /** Database problem id (used for problems without a leetcode_id, e.g. ML). */
  dbId?: number | null;
  onClose: () => void;
}

/**
 * Right-side drawer that shows a problem's description and solution notes.
 *
 * Accepts either `lcId` (LeetCode number) or `dbId` (database id). `lcId` takes
 * precedence when both are provided. Renders nothing when both are null.
 */
export default function ProblemDrawer({ lcId, dbId, onClose }: ProblemDrawerProps) {
  const hasLc = lcId !== null && lcId !== undefined;
  const hasDb = !hasLc && dbId !== null && dbId !== undefined;
  const open = hasLc || hasDb;

  const { data: problem, isLoading, isError, error } = useQuery<Problem>({
    queryKey: hasLc ? ["problemByLcId", lcId] : ["problemByDbId", dbId],
    queryFn: () =>
      hasLc
        ? api.get<Problem>(`/problems/by-lc/${lcId}`)
        : api.get<Problem>(`/problems/${dbId}`),
    enabled: open,
  });

  const title = !open
    ? ""
    : problem
      ? (problem.leetcode_id
          ? `LC ${problem.leetcode_id} - ${problem.title}`
          : problem.title)
      : hasLc
        ? `LC ${lcId}`
        : "Loading...";

  const difficultyColor =
    problem?.difficulty === "hard" ? "bg-red-100 text-red-700"
    : problem?.difficulty === "medium" ? "bg-yellow-100 text-yellow-700"
    : problem?.difficulty === "easy" ? "bg-green-100 text-green-700"
    : "bg-gray-100 text-gray-600";

  return (
    <SlideOverPanel
      open={open}
      onClose={onClose}
      title={title}
      headerActions={
        problem ? (
          <GoldenToggleButton
            itemType="problem"
            itemId={problem.id}
            isGolden={Boolean(problem.is_golden)}
          />
        ) : null
      }
      headerAccentClassName={
        problem?.is_golden ? "border-t-2 border-t-orange-300" : ""
      }
    >
      {isLoading && (
        <div className="text-sm text-gray-400">Loading problem...</div>
      )}
      {isError && (
        <div className="text-sm text-red-600">
          Failed to load problem: {(error as Error)?.message ?? "unknown error"}
        </div>
      )}
      {problem && (
        <div className="space-y-5">
          {/* Meta bar */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {problem.difficulty && (
              <span className={`px-2 py-0.5 rounded font-medium ${difficultyColor}`}>
                {problem.difficulty.toUpperCase()}
              </span>
            )}
            {problem.pattern && (
              <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                {problem.pattern}
              </span>
            )}
            {problem.is_completed && (
              <span className="px-2 py-0.5 rounded bg-green-50 text-green-700">
                Completed
              </span>
            )}
            {problem.url && (
              <a
                href={problem.url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-2 py-0.5 rounded bg-gray-100 text-gray-700 hover:bg-gray-200"
              >
                Open on LeetCode
              </a>
            )}
            {problem.company_tags?.length > 0 && (
              <span className="text-gray-500">
                Companies: {problem.company_tags.join(", ")}
              </span>
            )}
          </div>

          {/* Problem description */}
          <section>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
            {problem.description ? (
              <MarkdownPreview markdown={problem.description} />
            ) : (
              <p className="text-sm text-gray-400 italic">
                No description cached. Fetch it from the problem page.
              </p>
            )}
          </section>

          {/* Solution notes */}
          <section className="border-t border-gray-200 pt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">My Notes</h3>
            {problem.notes ? (
              <MarkdownPreview markdown={problem.notes} />
            ) : (
              <p className="text-sm text-gray-400 italic">
                No notes yet for this problem.
              </p>
            )}
          </section>
        </div>
      )}
    </SlideOverPanel>
  );
}
