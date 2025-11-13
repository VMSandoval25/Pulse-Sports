from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import text
from app.core.db import SessionLocal
from app.models import *

analyzer = SentimentIntensityAnalyzer()

def label(score: float) -> str:
    if score >= 0.05:
        return "pos"
    if score <= -0.05:
        return "neg"
    return "neu"

def run_comment_sentiment(batch: int = 500):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT c.id, c.body
            FROM comments c
            LEFT JOIN comment_nlp n ON n.comment_id = c.id
            WHERE n.comment_id IS NULL
            ORDER BY c.created_at DESC
            LIMIT :batch
        """), {"batch": batch}).all()
        for cid, body in rows:
            vs = analyzer.polarity_scores(body or "")
            comp = vs.get("compound", 0.0)
            db.merge(CommentNLP(comment_id=cid, sentiment_label=label(comp), sentiment_score=comp))
        db.commit()
    finally:
        db.close()
