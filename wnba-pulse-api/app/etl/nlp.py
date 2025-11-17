from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import select
from app.core.db import SessionLocal
from app.models import *

"""
nlp.py — Comment Sentiment Analysis Pipeline
NEEDS FUTURE IMPORVEMENTS
-------------------------------------------

Purpose:
    Runs sentiment analysis on user comments and stores the results in the
    `comment_nlp` table. This module processes comments that have not yet
    been analyzed and assigns each a sentiment label (`pos`, `neu`, `neg`)
    along with a compound sentiment score.

How it works:
    1. Fetch all comments that do NOT yet have a sentiment record.
       (Uses an ORM query joining `Comment` → `CommentNLP`.)
    2. For each comment, compute a sentiment score using VADER.
    3. Convert the compound score to a label.
    4. Insert or update (`merge`) the sentiment record in the database.

Why this file exists:
    • It keeps NLP logic separate from ingestion.
    • It allows NLP to be re-run independently of data collection.
    • It ensures comments are enriched with sentiment metadata that powers
      downstream analytics such as controversy, disagreement, daily aggregates,
      and summaries.

Used by:
    • aggregate.py (for computing per-post metrics)
    • summarize.py (to summarize daily trends)
    • Any analytics that depend on per-comment sentiment

Key responsibilities:
    • Identify unprocessed comments
    • Compute sentiment
    • Persist results efficiently in batches

Run manually:
    python -m app.etl.nlp

Recommended schedule:
    Runs periodically (every few minutes) via APScheduler.
"""



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
        stmt = (
            select(Comment.id, Comment.body)
            .outerjoin(CommentNLP, CommentNLP.comment_id == Comment.id)
            .where(CommentNLP.comment_id.is_(None))
            .order_by(Comment.created_at.desc())
            .limit(batch)
        )

        rows = db.execute(stmt).all()

        for cid, body in rows:
            vs = analyzer.polarity_scores(body or "")
            comp = vs.get("compound", 0.0)
            db.merge(
                CommentNLP(
                    comment_id=cid,
                    sentiment_label=label(comp),
                    sentiment_score=comp,
                )
            )

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run_comment_sentiment()
