import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { PatternStat } from "../../types/problem";

interface PatternRadarChartProps {
  data: PatternStat[];
}

/** Radar chart showing average comfort level per problem pattern. */
export default function PatternRadarChart({ data }: PatternRadarChartProps) {
  // Take top 8 patterns by count to avoid overcrowding the radar
  const sorted = [...data].sort((a, b) => b.count - a.count).slice(0, 8);

  const chartData = sorted.map((d) => ({
    pattern: d.pattern.length > 12 ? d.pattern.slice(0, 12) + "..." : d.pattern,
    fullPattern: d.pattern,
    comfort: d.avg_comfort,
    count: d.count,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={chartData} margin={{ top: 8, right: 24, bottom: 8, left: 24 }}>
        <PolarGrid strokeDasharray="3 3" />
        <PolarAngleAxis dataKey="pattern" tick={{ fontSize: 11 }} />
        <PolarRadiusAxis domain={[0, 5]} tickCount={6} tick={{ fontSize: 10 }} />
        <Tooltip
          contentStyle={{ fontSize: 12, borderRadius: 8 }}
          /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
          formatter={((value: any, _name: any, props: any) => [
            `${Number(value).toFixed(1)} / 5 (${props.payload.count} problems)`,
            props.payload.fullPattern,
          ]) as any}
        />
        <Radar
          name="Comfort"
          dataKey="comfort"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.25}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
