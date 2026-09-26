import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function TrendChart({ data = [], lines = [], height = 280 }) {
  if (data.length === 0) {
    return <p className="text-secondary">Not enough history yet to plot a trend.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -12 }}>
        <CartesianGrid stroke="var(--border-subtle)" vertical={false} />
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          stroke="var(--text-muted)"
          tick={{ fontSize: 12, fill: "var(--text-secondary)" }}
          tickLine={false}
          axisLine={{ stroke: "var(--border-subtle)" }}
        />
        <YAxis
          stroke="var(--text-muted)"
          tick={{ fontSize: 12, fill: "var(--text-secondary)" }}
          tickLine={false}
          axisLine={false}
          width={36}
        />
        <Tooltip
          labelFormatter={formatDate}
          contentStyle={{
            background: "var(--bg-elevated)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 10,
            fontSize: 13,
          }}
          labelStyle={{ color: "var(--text-secondary)" }}
        />
        {lines.map((line) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            name={line.name}
            stroke={line.color}
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
