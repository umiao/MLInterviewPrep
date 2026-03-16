import type { CompanyWithWeights } from "../../types/company";
import type { FrameworkNode } from "../../types/framework";

interface CompanyReadinessCardProps {
  companies: CompanyWithWeights[];
  frameworkNodes: FrameworkNode[];
}

interface ReadinessScore {
  name: string;
  status: string;
  score: number;
  topGaps: string[];
}

/** Compute a readiness score for each company based on topic weights and framework progress. */
function computeReadiness(
  companies: CompanyWithWeights[],
  nodes: FrameworkNode[],
): ReadinessScore[] {
  // Build a flat map of node id -> node for quick lookup
  const nodeMap = new Map<number, FrameworkNode>();
  function flatten(list: FrameworkNode[]) {
    for (const n of list) {
      nodeMap.set(n.id, n);
      if (n.children) flatten(n.children);
    }
  }
  flatten(nodes);

  return companies
    .filter((c) => c.topic_weights.length > 0)
    .map((c) => {
      let weightedProgress = 0;
      let totalWeight = 0;
      const gaps: { title: string; gap: number }[] = [];

      for (const tw of c.topic_weights) {
        const node = nodeMap.get(tw.node_id);
        const progress = node ? node.progress_pct : 0;
        weightedProgress += tw.weight * progress;
        totalWeight += tw.weight;
        if (progress < 70) {
          gaps.push({ title: tw.node_title, gap: 70 - progress });
        }
      }

      const score = totalWeight > 0 ? Math.round(weightedProgress / totalWeight) : 0;
      gaps.sort((a, b) => b.gap - a.gap);

      return {
        name: c.name,
        status: c.status,
        score,
        topGaps: gaps.slice(0, 3).map((g) => g.title),
      };
    })
    .sort((a, b) => b.score - a.score);
}

const SCORE_COLOR: Record<string, string> = {
  high: "text-green-600",
  mid: "text-yellow-600",
  low: "text-red-600",
};

function scoreColor(score: number): string {
  if (score >= 70) return SCORE_COLOR.high;
  if (score >= 40) return SCORE_COLOR.mid;
  return SCORE_COLOR.low;
}

const STATUS_BADGE: Record<string, string> = {
  applied: "bg-blue-100 text-blue-700",
  phone_screen: "bg-purple-100 text-purple-700",
  onsite: "bg-amber-100 text-amber-700",
  offer: "bg-green-100 text-green-700",
  rejected: "bg-gray-100 text-gray-500",
};

export default function CompanyReadinessCard({
  companies,
  frameworkNodes,
}: CompanyReadinessCardProps) {
  const scores = computeReadiness(companies, frameworkNodes);

  if (scores.length === 0) {
    return (
      <p className="text-sm text-gray-400 py-8 text-center">
        No companies with topic weights yet. Add topic weights to companies to see readiness scores.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {scores.map((s) => (
        <div
          key={s.name}
          className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg"
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm text-gray-800 truncate">
                {s.name}
              </span>
              <span
                className={`text-xs px-1.5 py-0.5 rounded ${
                  STATUS_BADGE[s.status] ?? "bg-gray-100 text-gray-600"
                }`}
              >
                {s.status.replace("_", " ")}
              </span>
            </div>
            {s.topGaps.length > 0 && (
              <p className="text-xs text-gray-400 mt-0.5 truncate">
                Gaps: {s.topGaps.join(", ")}
              </p>
            )}
          </div>
          {/* Readiness bar */}
          <div className="w-32 flex items-center gap-2">
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  s.score >= 70
                    ? "bg-green-500"
                    : s.score >= 40
                      ? "bg-yellow-500"
                      : "bg-red-500"
                }`}
                style={{ width: `${Math.min(s.score, 100)}%` }}
              />
            </div>
            <span className={`text-sm font-bold w-10 text-right ${scoreColor(s.score)}`}>
              {s.score}%
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
