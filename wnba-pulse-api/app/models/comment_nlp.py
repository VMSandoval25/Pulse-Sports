"""
Defines CommentNLP: per-comment sentiment outputs (label/score) produced by NLP pipelines.
FK to comments; cascade delete keeps NL Prows tidy when comments are removed.
"""
from sqlalchemy import Column, BigInteger, Text, Float, ForeignKey
from app.core.db import Base

class CommentNLP(Base):
    __tablename__ = "comment_nlp"
    comment_id = Column(BigInteger, ForeignKey("comments.id", ondelete="CASCADE"), primary_key=True)
    sentiment_label = Column(Text)                         # 'pos'|'neu'|'neg'
    sentiment_score = Column(Float)                        # -1..1
