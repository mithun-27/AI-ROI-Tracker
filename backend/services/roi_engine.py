"""
ROI Calculation Engine.

Calculates the return on investment for each AI feature by combining
cost data with user impact metrics (engagement, retention, conversion).

Formula:
    Value = (Retention Rate * RETENTION_VALUE)
          + (Conversion Rate * CONVERSION_VALUE)
          + (Avg Engagement * ENGAGEMENT_VALUE)
          * Unique Users (scale factor)

    ROI = (Value - Cost) / Cost
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Feature, UsageLog, UserMetric, ROISummary

# ─── Configurable Value Weights ──────────────────────────────────
RETENTION_VALUE = float(os.getenv("RETENTION_VALUE", "10.0"))
CONVERSION_VALUE = float(os.getenv("CONVERSION_VALUE", "50.0"))
ENGAGEMENT_VALUE = float(os.getenv("ENGAGEMENT_VALUE", "5.0"))


def calculate_feature_roi(db: Session, feature_id: int) -> dict:
    """
    Calculate ROI for a single feature and update the roi_summary table.
    """
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        return None

    # ── Aggregate usage stats ────────────────────────────────────
    total_calls = db.query(func.count(UsageLog.id)).filter(
        UsageLog.feature_id == feature_id
    ).scalar() or 0

    total_tokens = db.query(func.sum(UsageLog.total_tokens)).filter(
        UsageLog.feature_id == feature_id
    ).scalar() or 0

    total_cost = float(db.query(func.sum(UsageLog.cost)).filter(
        UsageLog.feature_id == feature_id
    ).scalar() or 0)

    # ── Aggregate user impact metrics ────────────────────────────
    total_metric_records = db.query(func.count(UserMetric.id)).filter(
        UserMetric.feature_id == feature_id
    ).scalar() or 0

    avg_engagement = float(db.query(func.avg(UserMetric.engagement_score)).filter(
        UserMetric.feature_id == feature_id
    ).scalar() or 0)

    retained_count = db.query(func.count(UserMetric.id)).filter(
        UserMetric.feature_id == feature_id,
        UserMetric.retention_flag == True
    ).scalar() or 0

    converted_count = db.query(func.count(UserMetric.id)).filter(
        UserMetric.feature_id == feature_id,
        UserMetric.conversion_flag == True
    ).scalar() or 0

    retention_rate = (retained_count / total_metric_records) if total_metric_records > 0 else 0
    conversion_rate = (converted_count / total_metric_records) if total_metric_records > 0 else 0

    # ── Calculate Value ──────────────────────────────────────────
    unique_users = db.query(func.count(func.distinct(UserMetric.user_id))).filter(
        UserMetric.feature_id == feature_id
    ).scalar() or 0

    total_value = (
        (retention_rate * RETENTION_VALUE * unique_users)
        + (conversion_rate * CONVERSION_VALUE * unique_users)
        + (avg_engagement * ENGAGEMENT_VALUE * unique_users)
    )

    # ── Calculate ROI ────────────────────────────────────────────
    roi_score = ((total_value - total_cost) / total_cost) if total_cost > 0 else 0

    # ── Update or create ROI Summary ─────────────────────────────
    try:
        roi_summary = db.query(ROISummary).filter(ROISummary.feature_id == feature_id).first()
        if not roi_summary:
            roi_summary = ROISummary(feature_id=feature_id)
            db.add(roi_summary)

        roi_summary.total_calls = total_calls
        roi_summary.total_tokens = total_tokens
        roi_summary.total_cost = round(total_cost, 2)
        roi_summary.total_value = round(total_value, 2)
        roi_summary.roi_score = round(roi_score, 2)
        roi_summary.avg_engagement = round(avg_engagement, 2)
        roi_summary.retention_rate = round(retention_rate, 4)
        roi_summary.conversion_rate = round(conversion_rate, 4)
        roi_summary.last_updated = datetime.now(timezone.utc)

        db.commit()
        db.refresh(roi_summary)
    except Exception as e:
        db.rollback()
        # Fallback: if it was a race condition, try to get the existing one again
        roi_summary = db.query(ROISummary).filter(ROISummary.feature_id == feature_id).first()
        if roi_summary:
            roi_summary.total_calls = total_calls
            roi_summary.total_tokens = total_tokens
            roi_summary.total_cost = round(total_cost, 2)
            roi_summary.total_value = round(total_value, 2)
            roi_summary.roi_score = round(roi_score, 2)
            roi_summary.avg_engagement = round(avg_engagement, 2)
            roi_summary.retention_rate = round(retention_rate, 4)
            roi_summary.conversion_rate = round(conversion_rate, 4)
            roi_summary.last_updated = datetime.now(timezone.utc)
            db.commit()
            db.refresh(roi_summary)
        else:
            raise e

    return {
        "feature_id": feature_id,
        "feature_name": feature.name,
        "total_calls": total_calls,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 2),
        "total_value": round(total_value, 2),
        "roi_score": round(roi_score, 2),
        "avg_engagement": round(avg_engagement, 2),
        "retention_rate": round(retention_rate, 4),
        "conversion_rate": round(conversion_rate, 4),
    }


def calculate_all_roi(db: Session) -> list:
    """Calculate ROI for all active features."""
    features = db.query(Feature).filter(Feature.is_active == True).all()
    results = []
    for feature in features:
        result = calculate_feature_roi(db, feature.id)
        if result:
            results.append(result)
    return results
