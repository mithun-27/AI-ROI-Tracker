"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Feature ─────────────────────────────────────────────────────
class FeatureCreate(BaseModel):
    name: str
    description: str = ""
    model_provider: str = "openai"
    model_name: str = "gpt-4"
    cost_per_1k_input_tokens: float = 0.03
    cost_per_1k_output_tokens: float = 0.06


class FeatureResponse(BaseModel):
    id: int
    name: str
    description: str
    model_provider: str
    model_name: str
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Usage Log ───────────────────────────────────────────────────
class UsageLogCreate(BaseModel):
    feature_id: int
    user_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    latency_ms: int = 0
    model_used: str = "gpt-4"


class UsageLogResponse(BaseModel):
    id: int
    feature_id: int
    user_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    latency_ms: int
    model_used: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ─── User Metric ─────────────────────────────────────────────────
class UserMetricCreate(BaseModel):
    user_id: str
    feature_id: int
    engagement_score: float = Field(0.0, ge=0.0, le=1.0)
    retention_flag: bool = False
    conversion_flag: bool = False
    session_duration_sec: int = 0


class UserMetricResponse(BaseModel):
    id: int
    user_id: str
    feature_id: int
    engagement_score: float
    retention_flag: bool
    conversion_flag: bool
    session_duration_sec: int
    timestamp: datetime

    class Config:
        from_attributes = True


# ─── ROI Summary ─────────────────────────────────────────────────
class ROISummaryResponse(BaseModel):
    feature_id: int
    feature_name: str = ""
    total_calls: int
    total_tokens: int
    total_cost: float
    total_value: float
    roi_score: float
    avg_engagement: float
    retention_rate: float
    conversion_rate: float
    recommendation: str
    last_updated: datetime

    class Config:
        from_attributes = True


# ─── Analytics ───────────────────────────────────────────────────
class DailyUsage(BaseModel):
    date: str
    total_cost: float
    total_calls: int
    total_tokens: int


class FeatureComparison(BaseModel):
    feature_name: str
    total_cost: float
    total_value: float
    roi_score: float
    recommendation: str


class AnalyticsDashboard(BaseModel):
    total_features: int
    total_cost: float
    total_value: float
    overall_roi: float
    daily_usage: List[DailyUsage]
    feature_comparisons: List[FeatureComparison]
    alerts: List[str]


# ─── Decision Engine ─────────────────────────────────────────────
class OptimizationResult(BaseModel):
    feature_id: int
    feature_name: str
    current_model: str
    recommended_model: str
    current_roi: float
    projected_roi: float
    action: str          # "downgrade", "keep", "disable", "monitor"
    reason: str
    estimated_savings: float
