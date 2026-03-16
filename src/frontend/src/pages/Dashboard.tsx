import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type {
  CompanyDeadline,
  DashboardData,
  PillarProgress,
} from "../types/dashboard";

/** SVG circular progress ring. */
function ProgressRing({
  value,
  max,
  size = 96,
  stroke = 8,
  label,
}: {
  value: number;
  max: number;
  size?: number;
  stroke?: number;
  label: string;
}) {
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = max > 0 ? value / max : 0;
  const offset = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#3b82f6"
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      <span className="text-xl font-bold text-gray-800">
        {value}/{max}
      </span>
      <span className="text-xs text-gray-500">{label}</span>
    </div>
  );
}

/** Horizontal progress bar for framework pillars. */
function PillarBar({ pillar }: { pillar: PillarProgress }) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-40 text-sm text-gray-700 truncate" title={pillar.title}>
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
    </div>
  );
}

/** Stat card with a large number. */
function StatCard({
  title,
  value,
  sub,
  accent,
}: {
  title: string;
  value: string | number;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
      <p className="text-sm text-gray-500 mb-1">{title}</p>
      <p className={`text-2xl font-bold ${accent ?? "text-gray-800"}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

/** Company deadline card. */
function DeadlineCard({ company }: { company: CompanyDeadline }) {
  const statusColor: Record<string, string> = {
    interested: "bg-gray-100 text-gray-700",
    applying: "bg-yellow-100 text-yellow-800",
    applied: "bg-blue-100 text-blue-800",
    interviewing: "bg-purple-100 text-purple-800",
    offered: "bg-green-100 text-green-800",
    rejected: "bg-red-100 text-red-700",
  };
  const cls = statusColor[company.status] ?? "bg-gray-100 text-gray-700";

  return (
    <div className="flex items-center justify-between bg-white rounded-lg border border-gray-200 px-4 py-3">
      <span className="text-sm font-medium text-gray-800">{company.name}</span>
      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cls}`}>
        {company.status}
      </span>
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: () => api.get<DashboardData>("/dashboard"),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Failed to load dashboard: {error.message}
      </div>
    );
  }

  if (!data) return null;

  const { problems, framework, recent_activity, company_deadlines, scraper } = data;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>

      {/* Top row: progress rings + review badge */}
      <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
          Problem Progress
        </h2>
        <div className="flex flex-wrap items-center gap-10">
          <ProgressRing
            value={problems.completed}
            max={problems.total}
            label="Completed"
          />
          <ProgressRing
            value={problems.total - problems.completed}
            max={problems.total}
            label="Remaining"
            stroke={8}
          />
          {/* Review queue badge */}
          <div className="flex flex-col items-center gap-1">
            <div
              className={`w-24 h-24 rounded-full flex items-center justify-center text-2xl font-bold ${
                problems.due_for_review > 0
                  ? "bg-amber-100 text-amber-700"
                  : "bg-green-100 text-green-700"
              }`}
            >
              {problems.due_for_review}
            </div>
            <span className="text-xs text-gray-500">Due for review</span>
          </div>
        </div>
      </section>

      {/* Activity stats row */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Attempts (7d)"
          value={recent_activity.attempts_7d}
          sub="Problem attempts this week"
        />
        <StatCard
          title="Study Hours (7d)"
          value={recent_activity.study_hours_7d}
          sub="Total study time this week"
          accent="text-blue-600"
        />
        <StatCard
          title="Questions Added (7d)"
          value={recent_activity.questions_added_7d}
          sub="Interview questions collected"
        />
        <StatCard
          title="Total Questions"
          value={scraper.total_questions}
          sub="In your question bank"
        />
      </section>

      {/* Framework progress bars */}
      <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
            Framework Progress
          </h2>
          <span className="text-lg font-bold text-blue-600">
            {framework.overall_progress_pct}%
          </span>
        </div>
        {framework.pillars.length > 0 ? (
          <div className="space-y-3">
            {framework.pillars.map((p) => (
              <PillarBar key={p.title} pillar={p} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400">
            No framework data yet. Import or create framework nodes to track progress.
          </p>
        )}
      </section>

      {/* Company deadlines */}
      <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
          Company Deadlines
        </h2>
        {company_deadlines.length > 0 ? (
          <div className="space-y-2">
            {company_deadlines.map((c) => (
              <DeadlineCard key={c.name} company={c} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400">
            No active applications. Add companies with application dates to track them here.
          </p>
        )}
      </section>
    </div>
  );
}
