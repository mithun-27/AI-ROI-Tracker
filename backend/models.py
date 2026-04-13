"""
SQLAlchemy ORM models for feature tracking, usage logs, user metrics, and ROI.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


class Feature(Base):
    """Represents an AI-powered feature being tracked."""
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    model_provider = Column(String(50), default="openai")       # openai, anthropic, etc.
    model_name = Column(String(50), default="gpt-4")            # gpt-4, gpt-3.5-turbo, etc.
    cost_per_1k_input_tokens = Column(Float, default=0.03)      # USD
    cost_per_1k_output_tokens = Column(Float, default=0.06)     # USD
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    usage_logs = relationship("UsageLog", back_populates="feature")
    user_metrics = relationship("UserMetric", back_populates="feature")
    roi_summary = relationship("ROISummary", back_populates="feature", uselist=False)


class UsageLog(Base):
    """Logs each individual AI API call for a feature."""
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)                           # USD
    latency_ms = Column(Integer, default=0)                     # response time
    model_used = Column(String(50), default="gpt-4")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    feature = relationship("Feature", back_populates="usage_logs")


class UserMetric(Base):
    """Tracks user behavior correlated with AI feature usage."""
    __tablename__ = "user_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False, index=True)
    engagement_score = Column(Float, default=0.0)               # 0.0 - 1.0
    retention_flag = Column(Boolean, default=False)              # did user return?
    conversion_flag = Column(Boolean, default=False)             # did user convert?
    session_duration_sec = Column(Integer, default=0)            # time spent in feature
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    feature = relationship("Feature", back_populates="user_metrics")


class ROISummary(Base):
    """Aggregated ROI metrics per feature — updated periodically."""
    __tablename__ = "roi_summary"

    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"), unique=True, nullable=False)
    total_calls = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)                     # USD
    total_value = Column(Float, default=0.0)                    # estimated USD value
    roi_score = Column(Float, default=0.0)                      # (value - cost) / cost
    avg_engagement = Column(Float, default=0.0)
    retention_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    recommendation = Column(String(200), default="")            # decision engine output
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    feature = relationship("Feature", back_populates="roi_summary")
