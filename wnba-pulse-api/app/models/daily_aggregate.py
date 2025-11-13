"""
Defines DailyAggregate: per-day JSON summaries (top entities/topics, sentiment, top posts).
Populated by ETL after NLP and tagging steps; feeds the /daily endpoint and UI.
"""
from sqlalchemy import Column, BigInteger, Date, DateTime, JSON
from app.core.db import Base

class DailyAggregate(Base):
    __tablename__ = "daily_aggregates"
    id = Column(BigInteger, primary_key=True)
    day = Column(Date, unique=True)
    top_entities = Column(JSON)        # [{id, name, type, count, avg_sentiment}, ...]
    top_topics = Column(JSON)          # [{topic, count}, ...]
    sentiment_overall = Column(JSON)   # {pos, neu, neg, avg_score}
    top_posts = Column(JSON)           # [{post_id, score, comment_count, ...}, ...]
    created_at = Column(DateTime(timezone=True))
