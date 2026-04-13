"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const COLORS = {
  positive: "#10b981",
  neutral: "#f59e0b",
  negative: "#f43f5e",
};

const getColor = (roi) => {
  if (roi >= 0.5) return COLORS.positive;
  if (roi >= 0) return COLORS.neutral;
  return COLORS.negative;
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0].payload;
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
          color: "#f1f5f9",
          fontSize: 13,
          fontWeight: 600,
          marginBottom: 8,
        }}
      >
        {data.feature_name}
      </p>
      <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 2 }}>
        ROI: <span style={{ color: getColor(data.roi_score), fontWeight: 700 }}>{(data.roi_score * 100).toFixed(0)}%</span>
      </p>
      <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 2 }}>
        Cost: <span style={{ color: "#f59e0b", fontWeight: 600 }}>${data.total_cost.toFixed(2)}</span>
      </p>
      <p style={{ fontSize: 12, color: "#94a3b8" }}>
        Value: <span style={{ color: "#10b981", fontWeight: 600 }}>${data.total_value.toFixed(2)}</span>
      </p>
    </div>
  );
};

export default function FeatureROIChart({ features }) {
  const sorted = [...features].sort((a, b) => b.roi_score - a.roi_score);

  return (
    <div className="glass-card-static animate-in">
      <div className="chart-header">
        <div>
          <h3 className="chart-title">📊 Feature ROI Ranking</h3>
          <p className="chart-subtitle">Sorted by return on investment</p>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 5, right: 20, left: 5, bottom: 5 }}
        >
          <XAxis
            type="number"
            stroke="rgba(255,255,255,0.05)"
            tick={{ fontSize: 10 }}
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
          />
          <YAxis
            type="category"
            dataKey="feature_name"
            stroke="rgba(255,255,255,0.05)"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            width={130}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="roi_score" radius={[0, 6, 6, 0]} barSize={24}>
            {sorted.map((entry, idx) => (
              <Cell key={idx} fill={getColor(entry.roi_score)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
