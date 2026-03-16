import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../utils/api";
import Skeleton from "../components/ui/Skeleton";
import WeeklyActivityChart from "../components/charts/WeeklyActivityChart";
import type {
  ActivityDay,
  DashboardToday,
  DashboardSummary,
  PillarProgress,
} from "../types/dashboard";
import type { FrameworkNode } from "../types/framework";

/* ------------------------------------------------------------------ */
/*  Row 1: Today Focus cards                                          */
/* ------------------------------------------------------------------ */

function TodayFocusSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white rounded-lg border border-gray-200 p-5 space-y-3">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-8 w-16" />
          <Skeleton className="h-3 w-32" />
        </div>
      ))}
    </div>
  );
}

function TodayFocusCards({ data }: { data: DashboardToday }) {
  const navigate = useNavigate();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {/* Due Reviews */}
      <button
        type="button"
        onClick={() => navigate("/problems?review=due")}
        className="bg-white rounded-lg border border-gray-200 p-5 text-left
                   hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
      >
        <p className="text-sm text-gray-500 mb-1">Due Reviews</p>
        <p className={`text-3xl font-bold ${
          data.due_reviews > 0 ? "text-amber-600" : "text-green-600"
        }`}>
          {data.due_reviews}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          {data.due_reviews > 0 ? "Problems need review" : "All caught up!"}
        </p>
      </button>

      {/* Weakest Topic */}
      <button
        type="button"
        onClick={() => navigate("/framework")}
        className="bg-white rounded-lg border border-gray-200 p-5 text-left
                   hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
      >
        <p className="text-sm text-gray-500 mb-1">Weakest Topic</p>
        {data.suggested_focus_topic ? (
          <>
            <p className="text-lg font-bold text-gray-800 truncate" title={data.suggested_focus_topic.title}>
              {data.suggested_focus_topic.title}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {data.suggested_focus_topic.progress_pct}% mastered
            </p>
          </>
        ) : (
          <p className="text-sm text-gray-400 mt-2">No topics to focus on</p>
        )}
      </button>

      {/* Streak */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <p className="text-sm text-gray-500 mb-1">Streak</p>
        <p className="text-3xl font-bold text-blue-600">
          {data.streak_days}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          {data.streak_days === 1 ? "day" : "days"} in a row
        </p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Row 2 left: Weekly Activity Chart                                 */
/* ------------------------------------------------------------------ */

function ActivityChartSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <Skeleton className="h-4 w-40" />
      <Skeleton className="h-48 w-full" />
    </div>
  );
}

function ActivityChartCard({ data }: { data: ActivityDay[] }) {
  const last7 = data.slice(-7);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
        Weekly Activity
      </h2>
      {last7.some((d) => d.attempts > 0 || d.study_minutes > 0) ? (
        <WeeklyActivityChart data={last7} />
      ) : (
        <p className="text-sm text-gray-400 py-16 text-center">
          No activity in the last 7 days. Start studying to see your chart!
        </p>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Row 2 right: Framework Pillar Progress                            */
/* ------------------------------------------------------------------ */

function PillarBarsSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <Skeleton className="h-4 w-40" />
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-3 flex-1" />
          <Skeleton className="h-3 w-10" />
        </div>
      ))}
    </div>
  );
}

/** Horizontal progress bar for a single framework pillar. */
function PillarBar({ pillar, onClick }: { pillar: PillarProgress; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center gap-3 w-full group"
    >
      <span className="w-40 text-sm text-gray-700 truncate text-left group-hover:text-blue-600 transition-colors" title={pillar.title}>
        {pillar.title}
      </span>
      <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all duration-500"
          style={{ width: `${Math.min(pillar.progress, 100)}%` }}
        />
      </div>
      <span className="w-12 text-right text-sm font-medium text-gray-600">
        {pillar.progress}%
      </span>
    </button>
  );
}

function PillarProgressCard({
  pillars,
  overallPct,
}: {
  pillars: PillarProgress[];
  overallPct: number;
}) {
  const navigate = useNavigate();

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          Framework Progress
        </h2>
        <span className="text-lg font-bold text-blue-600">{overallPct}%</span>
      </div>
      {pillars.length > 0 ? (
        <div className="space-y-3">
          {pillars.map((p) => (
            <PillarBar
              key={p.title}
              pillar={p}
              onClick={() => navigate("/framework")}
            />
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-400">
          No framework data yet. Import or create framework nodes to track progress.
        </p>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Row 3: Company Status Summary                                     */
/* ------------------------------------------------------------------ */

const STATUS_COLORS: Record<string, string> = {
  interested: "bg-gray-100 text-gray-700",
  applying: "bg-yellow-100 text-yellow-800",
  applied: "bg-blue-100 text-blue-800",
  interviewing: "bg-purple-100 text-purple-800",
  offered: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-700",
};

function CompanySummarySkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-3">
      <Skeleton className="h-4 w-48" />
      <div className="flex flex-wrap gap-3">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-8 w-28 rounded-full" />
        ))}
      </div>
    </div>
  );
}

function CompanySummaryCard({ counts }: { counts: Record<string, number> }) {
  const entries = Object.entries(counts);
  const total = entries.reduce((s, [, c]) => s + c, 0);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          Company Pipeline
        </h2>
        <span className="text-sm text-gray-500">{total} total</span>
      </div>
      {entries.length > 0 ? (
        <div className="flex flex-wrap gap-3">
          {entries.map(([status, count]) => (
            <span
              key={status}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${
                STATUS_COLORS[status] ?? "bg-gray-100 text-gray-700"
              }`}
            >
              <span className="font-bold">{count}</span>
              {status}
            </span>
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-400">
          No companies tracked yet. Add companies to see your pipeline.
        </p>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main Dashboard                                                    */
/* ------------------------------------------------------------------ */

export default function Dashboard() {
  const today = useQuery<DashboardToday>({
    queryKey: ["dashboard", "today"],
    queryFn: () => api.get<DashboardToday>("/dashboard/today"),
  });

  const activity = useQuery<ActivityDay[]>({
    queryKey: ["dashboard", "activity"],
    queryFn: () => api.get<ActivityDay[]>("/dashboard/activity"),
  });

  const summary = useQuery<DashboardSummary>({
    queryKey: ["dashboard", "summary"],
    queryFn: () => api.get<DashboardSummary>("/dashboard/summary"),
  });

  /* Pillars come from the framework tree (depth-0 nodes). */
  const tree = useQuery<FrameworkNode[]>({
    queryKey: ["framework", "tree"],
    queryFn: () => api.get<FrameworkNode[]>("/framework/tree"),
  });

  const pillars: PillarProgress[] = (tree.data ?? []).map((n) => ({
    title: n.title,
    progress: n.progress_pct ?? 0,
  }));

  const hasError = today.error || activity.error || summary.error;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>

      {hasError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
          Some dashboard data failed to load. Showing what is available.
        </div>
      )}

      {/* Row 1: Today Focus */}
      {today.isLoading ? <TodayFocusSkeleton /> : today.data && <TodayFocusCards data={today.data} />}

      {/* Row 2: Activity chart + Pillar progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {activity.isLoading ? (
          <ActivityChartSkeleton />
        ) : activity.data ? (
          <ActivityChartCard data={activity.data} />
        ) : null}

        {tree.isLoading || summary.isLoading ? (
          <PillarBarsSkeleton />
        ) : (
          <PillarProgressCard
            pillars={pillars}
            overallPct={summary.data?.framework_overall_progress_pct ?? 0}
          />
        )}
      </div>

      {/* Row 3: Company status summary */}
      {summary.isLoading ? (
        <CompanySummarySkeleton />
      ) : summary.data ? (
        <CompanySummaryCard counts={summary.data.company_counts_by_status} />
      ) : null}
    </div>
  );
}
