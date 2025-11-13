from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select, text
from app.core.db import SessionLocal
from app.models import *

# PT = pytz.timezone("America/Los_Angeles")

# def pt_bounds(dt_utc):
#     now_pt = dt_utc.astimezone(PT)
#     day_start_pt = PT.localize(now_pt.replace(hour=0, minute=0, second=0, microsecond=0))
#     day_end_pt = day_start_pt + timedelta(days=1)
#     return day_start_pt.astimezone(pytz.UTC), day_end_pt.astimezone(pytz.UTC), day_start_pt.date()

def pt_bounds(dt_utc: datetime):
    """Given an aware UTC datetime, return [start_utc, end_utc, PT date]."""
    pt = ZoneInfo("America/Los_Angeles")
    dt_pt = dt_utc.astimezone(pt)
    start_pt = dt_pt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_pt = start_pt + timedelta(days=1)
    start_utc = start_pt.astimezone(timezone.utc)
    end_utc = end_pt.astimezone(timezone.utc)
    return start_utc, end_utc, start_pt.date()


def compute_post_discussion_metrics(day_start_utc, day_end_utc):
    db = SessionLocal()
    try:
        sql = text("""
        WITH base AS (
          SELECT c.post_id,
                 COUNT(*)::float AS total,
                 SUM(CASE WHEN n.sentiment_label='pos' THEN 1 ELSE 0 END)::float AS pos_count,
                 SUM(CASE WHEN n.sentiment_label='neu' THEN 1 ELSE 0 END)::float AS neu_count,
                 SUM(CASE WHEN n.sentiment_label='neg' THEN 1 ELSE 0 END)::float AS neg_count,
                 AVG(n.sentiment_score) AS avg_sentiment,
                 STDDEV_POP(n.sentiment_score) AS sentiment_std
          FROM comments c
          JOIN comment_nlp n ON n.comment_id=c.id
          WHERE c.created_at >= :start AND c.created_at < :end
          GROUP BY c.post_id
        )
        INSERT INTO post_discussion_metrics(post_id,pos_count,neu_count,neg_count,avg_sentiment,sentiment_std,disagreement,controversy)
        SELECT post_id, pos_count::int, neu_count::int, neg_count::int, avg_sentiment, sentiment_std,
               1 - ABS( (pos_count/(NULLIF(pos_count+neg_count,0))) - (neg_count/(NULLIF(pos_count+neg_count,0))) ) AS disagreement,
               LN(1 + (pos_count+neu_count+neg_count)) * 
               (1 - ABS( (pos_count/(NULLIF(pos_count+neg_count,0))) - (neg_count/(NULLIF(pos_count+neg_count,0))) ))
        FROM base
        ON CONFLICT (post_id) DO UPDATE SET
          pos_count=EXCLUDED.pos_count,
          neu_count=EXCLUDED.neu_count,
          neg_count=EXCLUDED.neg_count,
          avg_sentiment=EXCLUDED.avg_sentiment,
          sentiment_std=EXCLUDED.sentiment_std,
          disagreement=EXCLUDED.disagreement,
          controversy=EXCLUDED.controversy;
        """)
        db.execute(sql, {"start": day_start_utc, "end": day_end_utc})
        db.commit()
    finally:
        db.close()

def compute_daily():
    db = SessionLocal()
    try:
        # start_utc, end_utc, day = pt_bounds(datetime.utcnow().replace(tzinfo=pytz.UTC))
        start_utc, end_utc, day = pt_bounds(datetime.now(timezone.utc))

        compute_post_discussion_metrics(start_utc, end_utc)
        rows = db.execute(
            select(Post, PostDiscussionMetrics).join(PostDiscussionMetrics, PostDiscussionMetrics.post_id==Post.id)
            .where(Post.created_at>=start_utc, Post.created_at<end_utc)
            .order_by(PostDiscussionMetrics.controversy.desc()).limit(10)
        ).all()
        top_posts = [{
            "title": p.title, "url": p.url, "score": p.score,
            "disagreement": m.disagreement, "controversy": m.controversy
        } for (p, m) in rows]
        sentiment_overall = {"pos": 0, "neu": 1, "neg": 0}
        top_entities, top_topics = [], []

        existing = db.execute(select(DailyAggregate).where(DailyAggregate.day==day)).scalars().first()
        if existing:
            existing.top_posts = top_posts
            existing.top_entities = top_entities
            existing.top_topics = top_topics
            existing.sentiment_overall = sentiment_overall
        else:
            db.add(DailyAggregate(day=day, top_posts=top_posts, top_entities=top_entities,
                                  top_topics=top_topics, sentiment_overall=sentiment_overall))
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    compute_daily()
