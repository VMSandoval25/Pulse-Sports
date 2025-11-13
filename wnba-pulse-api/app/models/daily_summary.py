"""
Defines DailySummary: per-day LLM-generated recap text plus prompt/model metadata.
Cached daily to avoid repeated LLM calls; read by /daily for the recap card.
"""
from sqlalchemy import Column, BigInteger, Date, DateTime, Text
from app.core.db import Base

class DailySummary(Base):
    __tablename__ = "daily_summaries"
    id = Column(BigInteger, primary_key=True)
    day = Column(Date, unique=True)
    summary_text = Column(Text)
    prompt_used = Column(Text)
    model = Column(Text)
    created_at = Column(DateTime(timezone=True))
