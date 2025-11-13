from fastapi import APIRouter, Query
from datetime import date
from sqlalchemy import select
from app.core.db import SessionLocal
from app.models import DailyAggregate, DailySummary

router = APIRouter()

@router.get("")
def get_daily(day: date | None = Query(None)):
    db = SessionLocal()
    try:
        if day:
            agg = db.execute(select(DailyAggregate).where(DailyAggregate.day == day)).scalars().first()
        else:
            agg = db.execute(select(DailyAggregate).order_by(DailyAggregate.day.desc())).scalars().first()
        if not agg:
            return {"day": str(day) if day else None, "data": None}
        summary = db.execute(select(DailySummary).where(DailySummary.day == agg.day)).scalars().first()
        return {
            "day": str(agg.day),
            "summary_text": summary.summary_text if summary else None,
            "top_entities": agg.top_entities,
            "top_topics": agg.top_topics,
            "sentiment_overall": agg.sentiment_overall,
            "top_posts": agg.top_posts
        }
    finally:
        db.close()
