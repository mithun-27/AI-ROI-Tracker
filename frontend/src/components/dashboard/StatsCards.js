"use client";

export default function StatsCards({ analytics }) {
  const formatCurrency = (val) => {
    if (val >= 1000) return `$${(val / 1000).toFixed(1)}k`;
    return `$${val.toFixed(2)}`;
  };

  const formatROI = (val) => {
    const pct = (val * 100).toFixed(0);
    return `${pct}%`;
  };

  return (
    <div className="stats-grid">
      <div className="glass-card stat-card blue animate-in">
        <div className="stat-label">Total Features</div>
        <div className="stat-value blue">{analytics.total_features}</div>
        <div className="stat-sub">Active AI features tracked</div>
      </div>

      <div className="glass-card stat-card amber animate-in">
        <div className="stat-label">Total Cost</div>
        <div className="stat-value amber">
          {formatCurrency(analytics.total_cost)}
        </div>
        <div className="stat-sub">Cumulative API spend (30d)</div>
      </div>

      <div className="glass-card stat-card green animate-in">
        <div className="stat-label">Total Value</div>
        <div className="stat-value green">
          {formatCurrency(analytics.total_value)}
        </div>
        <div className="stat-sub">Estimated user impact value</div>
      </div>

      <div className="glass-card stat-card purple animate-in">
        <div className="stat-label">Overall ROI</div>
        <div
          className={`stat-value ${
            analytics.overall_roi >= 0.5
              ? "green"
              : analytics.overall_roi >= 0
              ? "amber"
              : "rose"
          }`}
        >
          {formatROI(analytics.overall_roi)}
        </div>
        <div className="stat-sub">
          {analytics.overall_roi >= 0.5
            ? "✓ Healthy returns"
            : analytics.overall_roi >= 0
            ? "⚠ Needs improvement"
            : "✕ Negative returns"}
        </div>
      </div>
    </div>
  );
}
