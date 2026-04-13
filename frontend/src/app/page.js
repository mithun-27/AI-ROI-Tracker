"use client";

import { useState, useEffect } from "react";
import StatsCards from "@/components/dashboard/StatsCards";
import CostTrendChart from "@/components/dashboard/CostTrendChart";
import FeatureROIChart from "@/components/dashboard/FeatureROIChart";
import FeatureTable from "@/components/dashboard/FeatureTable";
import AlertsPanel from "@/components/dashboard/AlertsPanel";
import OptimizationCards from "@/components/dashboard/OptimizationCards";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState(null);
  const [optimizations, setOptimizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [analyticsRes, optimizeRes] = await Promise.all([
        fetch(`${API_BASE}/analytics`),
        fetch(`${API_BASE}/optimize`),
      ]);

      if (!analyticsRes.ok || !optimizeRes.ok) {
        throw new Error("Failed to fetch data from API");
      }

      const analyticsData = await analyticsRes.json();
      const optimizeData = await optimizeRes.json();

      setAnalytics(analyticsData);
      setOptimizations(optimizeData);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error("API Error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="app-layout">
        <Header />
        <main className="app-main">
          <div className="loading-container">
            <div className="loading-spinner" />
            <span className="loading-text">Loading analytics...</span>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-layout">
        <Header />
        <main className="app-main">
          <div className="loading-container">
            <div style={{ fontSize: 48 }}>⚠️</div>
            <span className="loading-text">
              Cannot connect to API at {API_BASE}
            </span>
            <p style={{ color: "var(--text-muted)", fontSize: 13 }}>
              Make sure the backend is running: <code>cd backend && uvicorn main:app --reload --port 8000</code>
            </p>
            <button className="btn-primary" onClick={fetchData}>
              Retry Connection
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Header />
      <main className="app-main">
        {/* ── Top-level KPIs ───────────────────────────────────── */}
        <StatsCards analytics={analytics} />

        {/* ── Charts Row ──────────────────────────────────────── */}
        <div className="charts-row">
          <CostTrendChart dailyUsage={analytics.daily_usage} />
          <FeatureROIChart features={analytics.feature_comparisons} />
        </div>

        {/* ── Alerts ──────────────────────────────────────────── */}
        {analytics.alerts && analytics.alerts.length > 0 && (
          <AlertsPanel alerts={analytics.alerts} />
        )}

        {/* ── Optimization Recommendations ────────────────────── */}
        <div className="section-header">
          <div>
            <h2 className="section-title">🤖 Optimization Engine</h2>
            <p className="section-subtitle">
              AI-powered recommendations to reduce costs & maximize ROI
            </p>
          </div>
          <button className="btn-primary" onClick={fetchData}>
            ↻ Recalculate
          </button>
        </div>
        <OptimizationCards optimizations={optimizations} />

        {/* ── Feature Comparison Table ────────────────────────── */}
        <div className="features-section" style={{ marginTop: 24 }}>
          <div className="section-header">
            <div>
              <h2 className="section-title">📊 Feature Performance</h2>
              <p className="section-subtitle">
                Side-by-side comparison of all tracked AI features
              </p>
            </div>
          </div>
          <FeatureTable features={analytics.feature_comparisons} />
        </div>
      </main>
    </div>
  );
}

function Header() {
  return (
    <header className="app-header">
      <div className="app-logo">
        <div className="app-logo-icon">⚡</div>
        <span className="app-logo-text">AI ROI Tracker</span>
        <span className="app-logo-badge">v1.0</span>
      </div>
      <div className="app-header-actions">
        <div className="header-status">
          <span className="dot" />
          Live Tracking
        </div>
      </div>
    </header>
  );
}
