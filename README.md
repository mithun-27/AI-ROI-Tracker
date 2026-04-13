# ⚡ AI ROI Tracker

A feature-level analytics system focused on tracking AI costs, user impact, and Return on Investment (ROI). 

Think of it as **"Google Analytics + Cost Monitor"** for your AI infrastructure.

## 🚀 Overview
Companies often struggle to understand if their expensive LLM features are actually driving business value. This project solves that by:
- **Tracking Costs**: Granular monitoring of token usage and API spend per feature.
- **Measuring Impact**: Correlating AI interactions with user engagement, retention, and conversion.
- **ROI Engine**: Calculating real ROI scores using weighted business value metrics.
- **Optimization**: Recommending model downgrades or feature deprecations when ROI is low.

## 🛠️ Tech Stack
- **Frontend**: Next.js (App Router), Recharts, Vanilla CSS.
- **Backend**: FastAPI, SQLAlchemy, SQLite (Default).
- **Core Logic**: ROI Engine & Decision Engine services.

## 📂 Project Structure
- `/backend`: FastAPI service for logging and analytics.
- `/frontend`: Next.js dashboard for visualization.
- `/scripts`: Data simulation and diagnostic tools.

## 🏁 Getting Started
1. **Install Backend**: `pip install -r backend/requirements.txt`
2. **Install Frontend**: `cd frontend && npm install`
3. **Simulate Data**: `python scripts/simulate_data.py`
4. **Run Servers**:
   - Backend: `uvicorn main:app --reload` (in /backend)
   - Frontend: `npm run dev` (in /frontend)

---
*Created with focus on AI Business Value & Cost Optimization.*
