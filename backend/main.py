"""
AI ROI Tracker — FastAPI Backend
Main application with all API routes.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List
from datetime import datetime, timezone

from database import engine, get_db, Base
from models import Feature, UsageLog, UserMetric, ROISummary
from schemas import (
    FeatureCreate, FeatureResponse,
    UsageLogCreate, UsageLogResponse,
    UserMetricCreate, UserMetricResponse,
    ROISummaryResponse,
    AnalyticsDashboard, DailyUsage, FeatureComparison,
    OptimizationResult,
)
from services.roi_engine import calculate_feature_roi, calculate_all_roi
from services.decision_engine import analyze_feature, analyze_all_features, get_alerts

# ─── Create tables ───────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── App ─────────────────────────────────────────────────────────
app = FastAPI(
    title="AI ROI Tracker",
    description="Feature-level AI cost tracking, ROI calculation, and optimization engine.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════
#  FEATURES
# ═══════════════════════════════════════════════════════════════════

@app.get("/features", response_model=List[FeatureResponse], tags=["Features"])
def list_features(db: Session = Depends(get_db)):
    """List all tracked AI features."""
    return db.query(Feature).all()


@app.post("/features", response_model=FeatureResponse, tags=["Features"])
def create_feature(data: FeatureCreate, db: Session = Depends(get_db)):
    """Register a new AI feature for tracking."""
    existing = db.query(Feature).filter(Feature.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feature with this name already exists")
    feature = Feature(**data.model_dump())
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature


@app.get("/features/{feature_id}", response_model=FeatureResponse, tags=["Features"])
def get_feature(feature_id: int, db: Session = Depends(get_db)):
    """Get details of a specific feature."""
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature


# ═══════════════════════════════════════════════════════════════════
#  USAGE LOGGING
# ═══════════════════════════════════════════════════════════════════

@app.post("/usage", response_model=UsageLogResponse, tags=["Usage"])
def log_usage(data: UsageLogCreate, db: Session = Depends(get_db)):
    """Log an AI API call for a feature."""
    feature = db.query(Feature).filter(Feature.id == data.feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    # Auto-calculate cost if not provided
    if data.cost == 0 and data.total_tokens > 0:
        input_cost = (data.input_tokens / 1000) * feature.cost_per_1k_input_tokens
        output_cost = (data.output_tokens / 1000) * feature.cost_per_1k_output_tokens
        data.cost = round(input_cost + output_cost, 6)

    log = UsageLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@app.get("/usage", response_model=List[UsageLogResponse], tags=["Usage"])
def list_usage(
    feature_id: int = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List recent usage logs, optionally filtered by feature."""
    query = db.query(UsageLog)
    if feature_id:
        query = query.filter(UsageLog.feature_id == feature_id)
    return query.order_by(UsageLog.timestamp.desc()).limit(limit).all()


# ═══════════════════════════════════════════════════════════════════
#  USER METRICS
# ═══════════════════════════════════════════════════════════════════

@app.post("/metrics", response_model=UserMetricResponse, tags=["Metrics"])
def log_metric(data: UserMetricCreate, db: Session = Depends(get_db)):
    """Log user impact metrics for a feature."""
    feature = db.query(Feature).filter(Feature.id == data.feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    metric = UserMetric(**data.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


@app.get("/metrics", response_model=List[UserMetricResponse], tags=["Metrics"])
def list_metrics(
    feature_id: int = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List user metrics, optionally filtered by feature."""
    query = db.query(UserMetric)
    if feature_id:
        query = query.filter(UserMetric.feature_id == feature_id)
    return query.order_by(UserMetric.timestamp.desc()).limit(limit).all()


# ═══════════════════════════════════════════════════════════════════
#  ROI
# ═══════════════════════════════════════════════════════════════════

@app.get("/roi/{feature_id}", response_model=ROISummaryResponse, tags=["ROI"])
def get_feature_roi(feature_id: int, db: Session = Depends(get_db)):
    """Calculate and return ROI for a specific feature."""
    result = calculate_feature_roi(db, feature_id)
    if not result:
        raise HTTPException(status_code=404, detail="Feature not found")

    roi_summary = db.query(ROISummary).filter(ROISummary.feature_id == feature_id).first()
    return ROISummaryResponse(
        **result,
        recommendation=roi_summary.recommendation if roi_summary else "",
        last_updated=roi_summary.last_updated if roi_summary else datetime.now(timezone.utc),
    )


@app.post("/roi/calculate-all", tags=["ROI"])
def recalculate_all_roi(db: Session = Depends(get_db)):
    """Recalculate ROI for all active features."""
    results = calculate_all_roi(db)
    return {"message": f"ROI recalculated for {len(results)} features", "results": results}


# ═══════════════════════════════════════════════════════════════════
#  ANALYTICS DASHBOARD
# ═══════════════════════════════════════════════════════════════════

@app.get("/analytics", response_model=AnalyticsDashboard, tags=["Analytics"])
def get_analytics(db: Session = Depends(get_db)):
    """Get full analytics dashboard data."""

    # Recalculate all ROI first
    calculate_all_roi(db)

    # Run decision engine
    recommendations = analyze_all_features(db)

    # ── Totals ────────────────────────────────────────────────────
    total_features = db.query(func.count(Feature.id)).scalar() or 0
    total_cost = float(db.query(func.sum(ROISummary.total_cost)).scalar() or 0)
    total_value = float(db.query(func.sum(ROISummary.total_value)).scalar() or 0)
    overall_roi = ((total_value - total_cost) / total_cost) if total_cost > 0 else 0

    # ── Daily usage (last 30 days) ────────────────────────────────
    daily_rows = (
        db.query(
            func.date(UsageLog.timestamp).label("date"),
            func.sum(UsageLog.cost).label("total_cost"),
            func.count(UsageLog.id).label("total_calls"),
            func.sum(UsageLog.total_tokens).label("total_tokens"),
        )
        .group_by(func.date(UsageLog.timestamp))
        .order_by(func.date(UsageLog.timestamp))
        .limit(30)
        .all()
    )

    daily_usage = [
        DailyUsage(
            date=str(row.date),
            total_cost=round(float(row.total_cost or 0), 2),
            total_calls=int(row.total_calls or 0),
            total_tokens=int(row.total_tokens or 0),
        )
        for row in daily_rows
    ]

    # ── Feature comparisons ──────────────────────────────────────
    feature_comparisons = []
    summaries = db.query(ROISummary).all()
    for s in summaries:
        feature = db.query(Feature).filter(Feature.id == s.feature_id).first()
        if feature:
            feature_comparisons.append(
                FeatureComparison(
                    feature_name=feature.name,
                    total_cost=round(s.total_cost, 2),
                    total_value=round(s.total_value, 2),
                    roi_score=round(s.roi_score, 2),
                    recommendation=s.recommendation or "",
                )
            )

    # ── Alerts ───────────────────────────────────────────────────
    alerts = get_alerts(db)

    return AnalyticsDashboard(
        total_features=total_features,
        total_cost=round(total_cost, 2),
        total_value=round(total_value, 2),
        overall_roi=round(overall_roi, 2),
        daily_usage=daily_usage,
        feature_comparisons=feature_comparisons,
        alerts=alerts,
    )


# ═══════════════════════════════════════════════════════════════════
#  OPTIMIZATION / DECISION ENGINE
# ═══════════════════════════════════════════════════════════════════

@app.post("/optimize/{feature_id}", response_model=OptimizationResult, tags=["Optimization"])
def optimize_feature(feature_id: int, db: Session = Depends(get_db)):
    """Run decision engine on a specific feature and return recommendation."""
    # First recalculate ROI
    calculate_feature_roi(db, feature_id)
    result = analyze_feature(db, feature_id)
    if not result:
        raise HTTPException(status_code=404, detail="Feature not found")
    return result


@app.get("/optimize", response_model=List[OptimizationResult], tags=["Optimization"])
def optimize_all(db: Session = Depends(get_db)):
    """Run decision engine on all features."""
    calculate_all_roi(db)
    return analyze_all_features(db)


# ═══════════════════════════════════════════════════════════════════
#  HEALTH
# ═══════════════════════════════════════════════════════════════════

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI ROI Tracker",
        "version": "1.0.0",
    }
