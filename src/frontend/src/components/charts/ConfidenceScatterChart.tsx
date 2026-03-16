import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface ScatterPoint {
  title: string;
  importance: number;
  confidence_level: number;
}

interface ConfidenceScatterChartProps {
  data: ScatterPoint[];
}

/** Scatter plot: framework node confidence (Y) vs importance (X). */
export default function ConfidenceScatterChart({ data }: ConfidenceScatterChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart margin={{ top: 8, right: 16, bottom: 4, left: -8 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="importance"
          name="Importance"
          type="number"
          domain={[0, "auto"]}
          tick={{ fontSize: 11 }}
          label={{ value: "Importance", position: "insideBottom", offset: -2, fontSize: 11 }}
        />
        <YAxis
          dataKey="confidence_level"
          name="Confidence"
          type="number"
          domain={[0, 5]}
          tickCount={6}
          tick={{ fontSize: 11 }}
          label={{ value: "Confidence", angle: -90, position: "insideLeft", offset: 16, fontSize: 11 }}
        />
        <Tooltip
          contentStyle={{ fontSize: 12, borderRadius: 8 }}
          formatter={(value: number, name: string) => [value.toFixed(1), name]}
          labelFormatter={(_label, payload) => {
            if (payload && payload.length > 0) {
              const point = payload[0].payload as ScatterPoint;
              return point.title;
            }
            return "";
          }}
        />
        <Scatter
          name="Nodes"
          data={data}
          fill="#8b5cf6"
          fillOpacity={0.7}
          r={5}
        />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
