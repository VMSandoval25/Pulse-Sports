from sqlalchemy import select
from app.core.db import SessionLocal
from app.models import *
from datetime import date

def build_prompt(agg):
    # Stub prompt kept for future use; summarizer returns placeholder text
    return f"Summarize {agg.day} with top posts: {agg.top_posts}"

def call_stub(_: str) -> str:
    return "Fans debated multiple topics across r/WNBA today. (Stubbed summary for Phase 1 local setup.)"

def summarize_day(day: date):
    db = SessionLocal()
    try:
        agg = db.execute(select(DailyAggregate).where(DailyAggregate.day==day)).scalars().first()
        if not agg:
            return
        text = call_stub(build_prompt(agg))
        existing = db.execute(select(DailySummary).where(DailySummary.day==day)).scalars().first()
        if existing:
            existing.summary_text = text
        else:
            db.add(DailySummary(day=day, summary_text=text, model="stub", prompt_used="stub"))
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import date as _d
    summarize_day(_d.today())
