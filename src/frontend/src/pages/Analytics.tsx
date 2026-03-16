import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import Skeleton from "../components/ui/Skeleton";
import PatternRadarChart from "../components/charts/PatternRadarChart";
import ConfidenceScatterChart from "../components/charts/ConfidenceScatterChart";
import ComfortTrendChart from "../components/charts/ComfortTrendChart";
import CompanyReadinessCard from "../components/charts/CompanyReadinessCard";
import type { ProblemStats } from "../types/problem";
import type { FrameworkNode, FrameworkStats } from "../types/framework";
import type { ActivityDay } from "../types/dashboard";
import type { CompanyWithWeights } from "../types/company";

/* ------------------------------------------------------------------ */
/*  Section skeleton                                                    */
/* ------------------------------------------------------------------ */

function ChartSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <Skeleton className="h-4 w-40" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Flatten framework tree to get all leaf/branch nodes                 */
/* ------------------------------------------------------------------ */

function flattenNodes(nodes: FrameworkNode[]): FrameworkNode[] {
  const result: FrameworkNode[] = [];
  function walk(list: FrameworkNode[]) {
    for (const n of list) {
      result.push(n);
      if (n.children) walk(n.children);
    }
  }
  walk(nodes);
  return result;
}

/* ------------------------------------------------------------------ */
/*  Main Analytics page                                                 */
/* ------------------------------------------------------------------ */

export default function Analytics() {
  const problemStats = useQuery<ProblemStats>({
    queryKey: ["problems", "stats"],
    queryFn: () => api.get<ProblemStats>("/problems/stats"),
  });

  const frameworkStats = useQuery<FrameworkStats>({
    queryKey: ["framework", "stats"],
    queryFn: () => api.get<FrameworkStats>("/framework/stats"),
  });

  const frameworkTree = useQuery<FrameworkNode[]>({
    queryKey: ["framework", "tree"],
    queryFn: () => api.get<FrameworkNode[]>("/framework/tree"),
  });

  const activity = useQuery<ActivityDay[]>({
    queryKey: ["dashboard", "activity"],
    queryFn: () => api.get<ActivityDay[]>("/dashboard/activity"),
  });

  const companies = useQuery<CompanyWithWeights[]>({
    queryKey: ["companies", "withWeights"],
    queryFn: async () => {
      // Get all companies, then fetch weights for each
      const list = await api.get<CompanyWithWeights[]>("/companies");
      const detailed = await Promise.all(
        list.map((c) =>
          api.get<CompanyWithWeights>(`/companies/${c.id}`),
        ),
      );
      return detailed;
    },
  });

  const allNodes = frameworkTree.data ? flattenNodes(frameworkTree.data) : [];
  // Filter to non-root nodes with importance for scatter plot
  const scatterData = allNodes
    .filter((n) => n.importance > 0)
    .map((n) => ({
      title: n.title,
      importance: n.importance,
      confidence_level: n.confidence_level,
    }));

  const hasError =
    problemStats.error || frameworkStats.error || activity.error;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Analytics</h1>

      {hasError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
          Some analytics data failed to load. Showing what is available.
        </div>
      )}

      {/* Summary stats row */}
      {problemStats.data && frameworkStats.data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Total Problems" value={problemStats.data.total} />
          <StatCard label="Avg Comfort" value={`${problemStats.data.avg_comfort} / 5`} />
          <StatCard label="Framework Progress" value={`${frameworkStats.data.overall_progress_pct}%`} />
          <StatCard label="Total Attempts" value={problemStats.data.total_attempts} />
        </div>
      )}

      {/* Row 1: Radar + Scatter */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pattern Comfort Radar */}
        {problemStats.isLoading ? (
          <ChartSkeleton />
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
              Pattern Comfort
            </h2>
            {problemStats.data && problemStats.data.by_pattern.length > 0 ? (
              <PatternRadarChart data={problemStats.data.by_pattern} />
            ) : (
              <p className="text-sm text-gray-400 py-16 text-center">
                No pattern data yet. Add problems with patterns to see the radar chart.
              </p>
            )}
          </div>
        )}

        {/* Confidence vs Importance Scatter */}
        {frameworkTree.isLoading ? (
          <ChartSkeleton />
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
              Confidence vs Importance
            </h2>
            {scatterData.length > 0 ? (
              <ConfidenceScatterChart data={scatterData} />
            ) : (
              <p className="text-sm text-gray-400 py-16 text-center">
                No framework nodes with importance set. Update framework nodes to see the scatter plot.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Row 2: Activity Trend (30-day) */}
      {activity.isLoading ? (
        <ChartSkeleton />
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            30-Day Activity Trend
          </h2>
          {activity.data && activity.data.some((d) => d.attempts > 0 || d.study_minutes > 0) ? (
            <ComfortTrendChart data={activity.data} />
          ) : (
            <p className="text-sm text-gray-400 py-16 text-center">
              No activity data in the last 30 days. Start studying to see trends!
            </p>
          )}
        </div>
      )}

      {/* Row 3: Company Readiness */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
          Company Prep Readiness
        </h2>
        {companies.isLoading || frameworkTree.isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : (
          <CompanyReadinessCard
            companies={companies.data ?? []}
            frameworkNodes={frameworkTree.data ?? []}
          />
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
    </div>
  );
}
