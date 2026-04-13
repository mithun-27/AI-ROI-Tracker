"""
Data Simulation Script for AI ROI Tracker.

Populates the database with realistic AI feature usage data
to demonstrate the dashboard, ROI calculations, and decision engine.

Run: python scripts/simulate_data.py
"""
import sys
import os

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')
import random
from datetime import datetime, timedelta, timezone

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from database import engine, SessionLocal, Base
from models import Feature, UsageLog, UserMetric

# ─── Reset & create tables ───────────────────────────────────────
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ═══════════════════════════════════════════════════════════════════
#  1. CREATE FEATURES
# ═══════════════════════════════════════════════════════════════════
features_data = [
    {
        "name": "AI Chatbot",
        "description": "Customer support chatbot powered by GPT-4",
        "model_provider": "openai",
        "model_name": "gpt-4",
        "cost_per_1k_input_tokens": 0.03,
        "cost_per_1k_output_tokens": 0.06,
    },
    {
        "name": "Smart Search",
        "description": "Semantic search using embeddings + LLM reranking",
        "model_provider": "openai",
        "model_name": "gpt-4o-mini",
        "cost_per_1k_input_tokens": 0.00015,
        "cost_per_1k_output_tokens": 0.0006,
    },
    {
        "name": "Content Recommendations",
        "description": "AI-powered content recommendation engine",
        "model_provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "cost_per_1k_input_tokens": 0.0015,
        "cost_per_1k_output_tokens": 0.002,
    },
    {
        "name": "Auto Summarizer",
        "description": "Document and article summarization",
        "model_provider": "anthropic",
        "model_name": "claude-3.5-sonnet",
        "cost_per_1k_input_tokens": 0.003,
        "cost_per_1k_output_tokens": 0.015,
    },
    {
        "name": "Code Assistant",
        "description": "In-app coding assistant for developers",
        "model_provider": "openai",
        "model_name": "gpt-4",
        "cost_per_1k_input_tokens": 0.03,
        "cost_per_1k_output_tokens": 0.06,
    },
    {
        "name": "Email Writer",
        "description": "AI email drafting and reply suggestions",
        "model_provider": "openai",
        "model_name": "gpt-4",
        "cost_per_1k_input_tokens": 0.03,
        "cost_per_1k_output_tokens": 0.06,
    },
]

print("🔧 Creating features...")
features = []
for fd in features_data:
    f = Feature(**fd)
    db.add(f)
    features.append(f)

db.commit()
for f in features:
    db.refresh(f)
    print(f"   ✅ {f.name} (id={f.id})")

# ═══════════════════════════════════════════════════════════════════
#  2. SIMULATE USAGE LOGS (30 days of data)
# ═══════════════════════════════════════════════════════════════════

# Feature profiles: (avg_daily_calls, avg_input_tokens, avg_output_tokens)
feature_profiles = {
    "AI Chatbot": (150, 800, 400),          # High usage, high cost
    "Smart Search": (500, 200, 50),          # Very high usage, low cost
    "Content Recommendations": (300, 150, 100), # Medium usage, low cost
    "Auto Summarizer": (80, 2000, 500),      # Lower usage, higher tokens
    "Code Assistant": (60, 1500, 800),       # Lower usage, high cost
    "Email Writer": (40, 300, 200),          # Low usage, moderate cost
}

user_ids = [f"user_{i:04d}" for i in range(1, 201)]  # 200 users

print("\n📊 Simulating 30 days of usage logs...")
total_logs = 0
now = datetime.now(timezone.utc)

for day_offset in range(30, 0, -1):
    day = now - timedelta(days=day_offset)

    for feature in features:
        profile = feature_profiles.get(feature.name, (100, 500, 200))
        avg_calls, avg_input, avg_output = profile

        # Add some daily variance
        daily_calls = max(1, int(avg_calls * random.uniform(0.6, 1.4)))

        for _ in range(daily_calls):
            user = random.choice(user_ids)
            input_tokens = max(10, int(avg_input * random.uniform(0.5, 2.0)))
            output_tokens = max(5, int(avg_output * random.uniform(0.5, 2.0)))
            total_tokens = input_tokens + output_tokens

            cost = (
                (input_tokens / 1000) * feature.cost_per_1k_input_tokens
                + (output_tokens / 1000) * feature.cost_per_1k_output_tokens
            )

            latency = random.randint(200, 3000)
            timestamp = day + timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )

            log = UsageLog(
                feature_id=feature.id,
                user_id=user,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost=round(cost, 6),
                latency_ms=latency,
                model_used=feature.model_name,
                timestamp=timestamp,
            )
            db.add(log)
            total_logs += 1

    # Commit daily to avoid memory issues
    db.commit()
    print(f"   Day -{day_offset}: committed")

print(f"   ✅ Total usage logs: {total_logs}")

# ═══════════════════════════════════════════════════════════════════
#  3. SIMULATE USER METRICS
# ═══════════════════════════════════════════════════════════════════

# Feature impact profiles: (retention_prob, conversion_prob, engagement_mean)
impact_profiles = {
    "AI Chatbot": (0.35, 0.05, 0.45),         # Low: costly but weak retention
    "Smart Search": (0.85, 0.25, 0.82),        # ★ Excellent: high value, low cost
    "Content Recommendations": (0.70, 0.18, 0.72), # Good: decent returns
    "Auto Summarizer": (0.40, 0.08, 0.50),     # Meh: moderate
    "Code Assistant": (0.90, 0.30, 0.88),       # ★ Excellent: high retention & conversion
    "Email Writer": (0.20, 0.02, 0.30),         # Poor: low impact
}

print("\n👥 Simulating user metrics...")
total_metrics = 0

for feature in features:
    profile = impact_profiles.get(feature.name, (0.5, 0.1, 0.5))
    retention_prob, conversion_prob, engagement_mean = profile

    for user_id in user_ids:
        # Each user gets a metric record per feature (if they used it)
        if random.random() < 0.7:  # 70% of users have metrics
            metric = UserMetric(
                user_id=user_id,
                feature_id=feature.id,
                engagement_score=round(
                    min(1.0, max(0.0, random.gauss(engagement_mean, 0.15))), 2
                ),
                retention_flag=random.random() < retention_prob,
                conversion_flag=random.random() < conversion_prob,
                session_duration_sec=random.randint(10, 600),
                timestamp=now - timedelta(days=random.randint(0, 30)),
            )
            db.add(metric)
            total_metrics += 1

db.commit()
print(f"   ✅ Total user metrics: {total_metrics}")

db.close()
print("\n🎉 Data simulation complete! Start the backend to see it in action.")
print("   cd backend && uvicorn main:app --reload --port 8000")
