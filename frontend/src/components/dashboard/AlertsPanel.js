"use client";

export default function AlertsPanel({ alerts }) {
  const getAlertClass = (alert) => {
    if (alert.includes("CRITICAL")) return "alert-critical";
    if (alert.includes("WARNING")) return "alert-warning";
    return "alert-info";
  };

  return (
    <div className="alerts-section animate-in">
      <div className="section-header">
        <div>
          <h2 className="section-title">🔔 Active Alerts</h2>
          <p className="section-subtitle">
            {alerts.length} alert{alerts.length !== 1 ? "s" : ""} requiring
            attention
          </p>
        </div>
      </div>
      <div className="glass-card-static">
        {alerts.map((alert, i) => (
          <div key={i} className={`alert-item ${getAlertClass(alert)}`}>
            {alert}
          </div>
        ))}
      </div>
    </div>
  );
}
