"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;
  return (
    <div
      style={{
        background: "rgba(17, 24, 39, 0.95)",
        backdropFilter: "blur(12px)",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 12,
        padding: "14px 18px",
        boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
      }}
    >
      <p
        style={{
          color: "#94a3b8",
          fontSize: 11,
          marginBottom: 8,
          fontWeight: 500,
        }}
      >
        {label}
      </p>
      {payload.map((entry, i) => (
        <p
          key={i}
          style={{
            color: entry.color,
            fontSize: 13,
            fontWeight: 600,
            marginBottom: 2,
          }}
        >
          {entry.name}: {entry.name === "Cost" ? `$${entry.value.toFixed(2)}` : entry.value.toLocaleString()}
        </p>
      ))}
    </div>
  );
};

export default function CostTrendChart({ dailyUsage }) {
  const data = dailyUsage.map((d) => ({
    ...d,
    date: new Date(d.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <div className="glass-card-static animate-in">
      <div className="chart-header">
        <div>
          <h3 className="chart-title">💰 Cost Trend (30 Days)</h3>
          <p className="chart-subtitle">
            Daily API spend and call volume over time
          </p>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart
          data={data}
          margin={{ top: 5, right: 10, left: -10, bottom: 0 }}
        >
          <defs>
            <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="callsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.04)"
          />
          <XAxis
            dataKey="date"
            stroke="rgba(255,255,255,0.05)"
            tick={{ fontSize: 10 }}
          />
          <YAxis
            yAxisId="cost"
            stroke="rgba(255,255,255,0.05)"
            tick={{ fontSize: 10 }}
            tickFormatter={(v) => `$${v}`}
          />
          <YAxis
            yAxisId="calls"
            orientation="right"
            stroke="rgba(255,255,255,0.05)"
            tick={{ fontSize: 10 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 11, paddingTop: 12 }}
          />
          <Area
            yAxisId="cost"
            type="monotone"
            dataKey="total_cost"
            name="Cost"
            stroke="#f59e0b"
            strokeWidth={2}
            fill="url(#costGradient)"
          />
          <Area
            yAxisId="calls"
            type="monotone"
            dataKey="total_calls"
            name="API Calls"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#callsGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
