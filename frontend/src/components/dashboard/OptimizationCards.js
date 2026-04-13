"use client";

export default function OptimizationCards({ optimizations }) {
  const getROIColor = (roi) => {
    if (roi >= 0.5) return "var(--accent-emerald)";
    if (roi >= 0) return "var(--accent-amber)";
    return "var(--accent-rose)";
  };

  return (
    <div className="optimizations-grid">
      {optimizations.map((opt, i) => (
        <div
          key={i}
          className={`glass-card optimization-card action-${opt.action} animate-in`}
        >
          <div className="action-strip" />

          <div className="opt-header">
            <span className="opt-feature-name">{opt.feature_name}</span>
            <span className={`badge badge-${opt.action}`}>
              {opt.action.toUpperCase()}
            </span>
          </div>

          <div className="opt-metrics">
            <div>
              <div className="opt-metric-label">Current Model</div>
              <div className="feature-model" style={{ marginTop: 4 }}>
                {opt.current_model}
              </div>
            </div>
            <div>
              <div className="opt-metric-label">Recommended</div>
              <div
                className="feature-model"
                style={{
                  marginTop: 4,
                  borderColor:
                    opt.recommended_model !== opt.current_model
                      ? "rgba(16, 185, 129, 0.3)"
                      : undefined,
                  color:
                    opt.recommended_model !== opt.current_model
                      ? "var(--accent-emerald)"
                      : undefined,
                  background:
                    opt.recommended_model !== opt.current_model
                      ? "rgba(16, 185, 129, 0.1)"
                      : undefined,
                }}
              >
                {opt.recommended_model}
              </div>
            </div>
            <div>
              <div className="opt-metric-label">Current ROI</div>
              <div
                className="opt-metric-value"
                style={{ color: getROIColor(opt.current_roi) }}
              >
                {(opt.current_roi * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="opt-metric-label">
                {opt.action === "keep" ? "ROI" : "Projected ROI"}
              </div>
              <div
                className="opt-metric-value"
                style={{ color: getROIColor(opt.projected_roi) }}
              >
                {(opt.projected_roi * 100).toFixed(0)}%
              </div>
            </div>
          </div>

          {opt.estimated_savings > 0 && (
            <div
              style={{
                padding: "8px 12px",
                borderRadius: 8,
                background: "rgba(16, 185, 129, 0.08)",
                border: "1px solid rgba(16, 185, 129, 0.15)",
                marginBottom: 12,
                fontSize: 13,
                fontWeight: 600,
                color: "var(--accent-emerald)",
              }}
            >
              💰 Est. savings: ${opt.estimated_savings.toFixed(2)}
            </div>
          )}

          <div className="opt-reason">{opt.reason}</div>
        </div>
      ))}
    </div>
  );
}
