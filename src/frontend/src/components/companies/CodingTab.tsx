import { useQuery } from "@tanstack/react-query";
import { api } from "../../utils/api";

interface ProblemSummary {
  id: number;
  leetcode_id: number | null;
  title: string;
  url: string | null;
  difficulty: "easy" | "medium" | "hard" | null;
  category: string;
  pattern: string | null;
  is_completed: boolean;
}

interface PrepSegments {
  core: ProblemSummary[];
  likely: ProblemSummary[];
  stretch: ProblemSummary[];
}

interface CompanyPrepResponse {
  problems: PrepSegments;
}

interface CodingTabProps {
  companyId: number;
  onSelect: (problem: ProblemSummary) => void;
}

const SEGMENTS: { key: keyof PrepSegments; label: string; hint: string }[] = [
  { key: "core", label: "Core", hint: "Must-do coverage for this company" },
  { key: "likely", label: "Likely", hint: "High-probability follow-ups" },
  { key: "stretch", label: "Stretch", hint: "Edge cases / deep dives" },
];

const DIFF_COLORS: Record<string, string> = {
  easy: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  hard: "bg-red-100 text-red-700",
};

export default function CodingTab({ companyId, onSelect }: CodingTabProps) {
  const { data, isLoading, isError } = useQuery<CompanyPrepResponse>({
    queryKey: ["companyPrep", companyId],
    queryFn: () =>
      api.get<CompanyPrepResponse>(`/companies/${companyId}/prep`),
    enabled: companyId > 0,
  });

  if (isLoading) {
    return (
      <div className="flex-1 overflow-auto p-6 text-gray-400 text-sm">
        Loading problems...
      </div>
    );
  }
  if (isError || !data) {
    return (
      <div className="flex-1 overflow-auto p-6 text-red-600 text-sm">
        Failed to load tagged problems.
      </div>
    );
  }

  const totalCount =
    data.problems.core.length +
    data.problems.likely.length +
    data.problems.stretch.length;

  if (totalCount === 0) {
    return (
      <div className="flex-1 overflow-auto p-6 text-gray-500 text-sm italic">
        No coding problems tagged for this company yet.
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto p-6 min-h-0 space-y-6">
      {SEGMENTS.map(({ key, label, hint }) => {
        const items = data.problems[key];
        if (items.length === 0) return null;
        return (
          <section key={key}>
            <header className="mb-2">
              <h2 className="text-sm font-semibold text-gray-800">
                {label}{" "}
                <span className="text-gray-400 font-normal">
                  ({items.length})
                </span>
              </h2>
              <p className="text-xs text-gray-500">{hint}</p>
            </header>
            <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
              {items.map((p) => (
                <li key={p.id}>
                  <button
                    type="button"
                    onClick={() => onSelect(p)}
                    className="w-full text-left border border-gray-200 rounded px-3 py-2 bg-white hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="text-sm font-medium text-gray-800">
                        {p.leetcode_id ? `LC ${p.leetcode_id}: ` : ""}
                        {p.title}
                      </span>
                      {p.is_completed && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-green-50 text-green-700 shrink-0">
                          Done
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1.5 text-xs">
                      {p.difficulty && (
                        <span
                          className={`px-1.5 py-0.5 rounded font-medium ${
                            DIFF_COLORS[p.difficulty] ??
                            "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {p.difficulty.toUpperCase()}
                        </span>
                      )}
                      {p.pattern && (
                        <span className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700">
                          {p.pattern}
                        </span>
                      )}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </section>
        );
      })}
    </div>
  );
}
