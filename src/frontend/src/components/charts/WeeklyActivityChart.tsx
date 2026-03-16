import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";
import type { ActivityDay } from "../../types/dashboard";

interface WeeklyActivityChartProps {
  /** Last 7 days of activity data (slice from 30-day array). */
  data: ActivityDay[];
}

/** Stacked bar chart showing attempts + study minutes for the last 7 days. */
export default function WeeklyActivityChart({ data }: WeeklyActivityChartProps) {
  const formatted = data.map((d) => ({
    ...d,
    label: formatDateLabel(d.date),
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={formatted} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{ fontSize: 12, borderRadius: 8 }}
          labelStyle={{ fontWeight: 600 }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar
          dataKey="attempts"
          name="Attempts"
          stackId="a"
          fill="#3b82f6"
          radius={[0, 0, 0, 0]}
        />
        <Bar
          dataKey="study_minutes"
          name="Study min"
          stackId="a"
          fill="#8b5cf6"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Format "2026-03-15" -> "Mar 15". */
function formatDateLabel(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}
