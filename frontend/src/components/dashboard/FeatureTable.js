"use client";

export default function FeatureTable({ features }) {
  const sorted = [...features].sort((a, b) => b.roi_score - a.roi_score);

  const getROIClass = (roi) => {
    if (roi >= 0.5) return "roi-positive";
    if (roi >= 0) return "roi-neutral";
    return "roi-negative";
  };

  const getActionBadge = (rec) => {
    const lower = rec.toLowerCase();
    if (lower.includes("[keep]")) return { cls: "badge-keep", text: "KEEP" };
    if (lower.includes("[monitor]")) return { cls: "badge-monitor", text: "MONITOR" };
    if (lower.includes("[downgrade]")) return { cls: "badge-downgrade", text: "DOWNGRADE" };
    if (lower.includes("[disable]")) return { cls: "badge-disable", text: "DISABLE" };
    return { cls: "badge-monitor", text: "PENDING" };
  };

  return (
    <div className="glass-card-static animate-in">
      <table className="feature-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>Total Cost</th>
            <th>Est. Value</th>
            <th>ROI</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((f, i) => {
            const badge = getActionBadge(f.recommendation);
            return (
              <tr key={i}>
                <td>
                  <span className="feature-name">{f.feature_name}</span>
                </td>
                <td style={{ color: "var(--accent-amber)", fontWeight: 600 }}>
                  ${f.total_cost.toFixed(2)}
                </td>
                <td style={{ color: "var(--accent-emerald)", fontWeight: 600 }}>
                  ${f.total_value.toFixed(2)}
                </td>
                <td>
                  <span className={`roi-value ${getROIClass(f.roi_score)}`}>
                    {(f.roi_score * 100).toFixed(0)}%
                  </span>
                </td>
                <td>
                  <span className={`badge ${badge.cls}`}>{badge.text}</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
