"""
Decision Engine for AI Feature Optimization.

Analyzes ROI data and provides actionable recommendations:
- Downgrade expensive models when ROI is low
- Flag features for review or disabling
- Estimate potential savings from optimizations

Thresholds (configurable via env vars):
    ROI < -0.5  →  DISABLE (losing money badly)
    ROI < 0.0   →  DOWNGRADE model
    ROI < 0.5   →  MONITOR closely
    ROI >= 0.5  →  KEEP as-is
"""
import os
from sqlalchemy.orm import Session

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Feature, ROISummary

# ─── Thresholds ──────────────────────────────────────────────────
DISABLE_THRESHOLD = float(os.getenv("DISABLE_THRESHOLD", "-0.5"))
DOWNGRADE_THRESHOLD = float(os.getenv("DOWNGRADE_THRESHOLD", "0.0"))
MONITOR_THRESHOLD = float(os.getenv("MONITOR_THRESHOLD", "0.5"))

# ─── Model downgrade paths ──────────────────────────────────────
MODEL_DOWNGRADE_MAP = {
    "gpt-4": {"model": "gpt-3.5-turbo", "input_cost": 0.0015, "output_cost": 0.002},
    "gpt-4-turbo": {"model": "gpt-3.5-turbo", "input_cost": 0.0015, "output_cost": 0.002},
    "gpt-4o": {"model": "gpt-4o-mini", "input_cost": 0.00015, "output_cost": 0.0006},
    "claude-3-opus": {"model": "claude-3-haiku", "input_cost": 0.00025, "output_cost": 0.00125},
    "claude-3.5-sonnet": {"model": "claude-3-haiku", "input_cost": 0.00025, "output_cost": 0.00125},
}


def analyze_feature(db: Session, feature_id: int) -> dict:
    """
    Analyze a single feature and return optimization recommendation.
    """
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        return None

    roi_summary = db.query(ROISummary).filter(ROISummary.feature_id == feature_id).first()
    if not roi_summary:
        return {
            "feature_id": feature_id,
            "feature_name": feature.name,
            "current_model": feature.model_name,
            "recommended_model": feature.model_name,
            "current_roi": 0.0,
            "projected_roi": 0.0,
            "action": "monitor",
            "reason": "Insufficient data to make a recommendation. Continue collecting metrics.",
            "estimated_savings": 0.0,
        }

    roi = roi_summary.roi_score
    current_model = feature.model_name
    total_cost = roi_summary.total_cost

    # ── Determine action ─────────────────────────────────────────
    if roi < DISABLE_THRESHOLD:
        action = "disable"
        reason = (
            f"Feature has severely negative ROI ({roi:.1%}). "
            f"Total cost: ${total_cost:.2f} with minimal value generated. "
            f"Recommend disabling or completely redesigning this feature."
        )
        recommended_model = "none"
        estimated_savings = total_cost
        projected_roi = 0.0

    elif roi < DOWNGRADE_THRESHOLD:
        downgrade = MODEL_DOWNGRADE_MAP.get(current_model)
        if downgrade:
            action = "downgrade"
            # Estimate savings: assume same token volume at lower cost
            cost_ratio = (downgrade["input_cost"] + downgrade["output_cost"]) / (
                feature.cost_per_1k_input_tokens + feature.cost_per_1k_output_tokens
            ) if (feature.cost_per_1k_input_tokens + feature.cost_per_1k_output_tokens) > 0 else 1
            estimated_savings = total_cost * (1 - cost_ratio)
            projected_cost = total_cost * cost_ratio
            projected_roi = (
                (roi_summary.total_value - projected_cost) / projected_cost
            ) if projected_cost > 0 else 0

            recommended_model = downgrade["model"]
            reason = (
                f"Negative ROI ({roi:.1%}). Downgrading from {current_model} to "
                f"{recommended_model} could save ~${estimated_savings:.2f} and improve "
                f"ROI to {projected_roi:.1%}."
            )
        else:
            action = "monitor"
            recommended_model = current_model
            estimated_savings = 0
            projected_roi = roi
            reason = (
                f"Negative ROI ({roi:.1%}) but no cheaper model alternative available. "
                f"Consider reducing usage or optimizing prompts."
            )

    elif roi < MONITOR_THRESHOLD:
        action = "monitor"
        recommended_model = current_model
        estimated_savings = 0
        projected_roi = roi
        reason = (
            f"ROI is positive but modest ({roi:.1%}). Monitor for improvement. "
            f"Consider prompt optimization to reduce token usage."
        )

    else:
        action = "keep"
        recommended_model = current_model
        estimated_savings = 0
        projected_roi = roi
        reason = (
            f"Strong ROI ({roi:.1%}). Feature is performing well. "
            f"Consider scaling if budget allows."
        )

    # ── Update recommendation in DB ──────────────────────────────
    roi_summary.recommendation = f"[{action.upper()}] {reason}"
    db.commit()

    return {
        "feature_id": feature_id,
        "feature_name": feature.name,
        "current_model": current_model,
        "recommended_model": recommended_model,
        "current_roi": round(roi, 2),
        "projected_roi": round(projected_roi, 2),
        "action": action,
        "reason": reason,
        "estimated_savings": round(estimated_savings, 2),
    }


def analyze_all_features(db: Session) -> list:
    """Analyze all active features and return recommendations."""
    features = db.query(Feature).filter(Feature.is_active == True).all()
    results = []
    for feature in features:
        result = analyze_feature(db, feature.id)
        if result:
            results.append(result)
    return results


def get_alerts(db: Session) -> list:
    """Get list of alert messages for features needing attention."""
    alerts = []
    summaries = db.query(ROISummary).all()
    for s in summaries:
        feature = db.query(Feature).filter(Feature.id == s.feature_id).first()
        if not feature:
            continue
        if s.roi_score < DISABLE_THRESHOLD:
            alerts.append(
                f"🚨 CRITICAL: '{feature.name}' has ROI of {s.roi_score:.0%} — "
                f"losing ${abs(s.total_cost - s.total_value):.2f}. Consider disabling."
            )
        elif s.roi_score < DOWNGRADE_THRESHOLD:
            alerts.append(
                f"⚠️ WARNING: '{feature.name}' has negative ROI ({s.roi_score:.0%}). "
                f"Model downgrade recommended."
            )
        elif s.roi_score < MONITOR_THRESHOLD:
            alerts.append(
                f"📊 INFO: '{feature.name}' ROI is modest ({s.roi_score:.0%}). Monitoring."
            )
    return alerts
