"""
Defines PostDiscussionMetrics: rollup stats computed from a post's comments.
Includes counts, average/variance, and custom disagreement/controversy signals.
"""
from sqlalchemy import Column, BigInteger, Integer, Float, ForeignKey
from app.core.db import Base

class PostDiscussionMetrics(Base):
    __tablename__ = "post_discussion_metrics"
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    pos_count = Column(Integer)
    neu_count = Column(Integer)
    neg_count = Column(Integer)
    avg_sentiment = Column(Float)
    sentiment_std = Column(Float)
    disagreement = Column(Float)
    controversy = Column(Float)
