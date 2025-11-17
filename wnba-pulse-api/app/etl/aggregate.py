"""
aggregate.py — Daily Discussion Metrics & Aggregates
---------------------------------------------------

Purpose:
    Compute per-post discussion metrics (sentiment counts, disagreement,
    controversy) for a given day, and store a daily snapshot in the
    `daily_aggregates` table.

How it works:
    1. Convert "now" in UTC to a Pacific Time day window [start_utc, end_utc).
    2. Aggregate comment sentiment per post (using Comment + CommentNLP).
    3. Compute per-post metrics and upsert into PostDiscussionMetrics.
    4. Select the top controversial posts for the day and store them,
       along with placeholder entity/topic/sentiment-overall fields,
       into DailyAggregate.

Used by:
    • Scheduler (APScheduler) to run once per day.
    • Frontend/API to show “top controversy posts” and daily trends.

Run manually:
    python -m app.etl.aggregate
"""

import math
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select, func, case

from app.core.db import SessionLocal
from app.models.post import Post
from app.models.comment import Comment
from app.models.comment_nlp import CommentNLP
from app.models.post_discussion_metrics import PostDiscussionMetrics
from app.models.daily_aggregate import DailyAggregate


def pt_bounds(dt_utc: datetime):
    """
    Given an aware UTC datetime, return (start_utc, end_utc, pt_date).

    - Converts the given UTC datetime to America/Los_Angeles.
    - Computes the start and end of that local day (midnight → +1 day).
    - Returns those bounds converted back to UTC plus the PT calendar date.
    """
    pt = ZoneInfo("America/Los_Angeles")
    dt_pt = dt_utc.astimezone(pt)

    start_pt = dt_pt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_pt = start_pt + timedelta(days=1)

    start_utc = start_pt.astimezone(timezone.utc)
    end_utc = end_pt.astimezone(timezone.utc)

    return start_utc, end_utc, start_pt.date()


def compute_post_discussion_metrics(day_start_utc, day_end_utc):
    """
    Compute per-post discussion metrics for comments in [day_start_utc, day_end_utc).

    For each post that has comments in this window:
        - pos_count / neu_count / neg_count  (from CommentNLP.sentiment_label)
        - avg_sentiment                      (average of sentiment_score)
        - sentiment_std                      (stddev of sentiment_score)
        - disagreement                       (how balanced pos vs neg are)
        - controversy                        (volume * disagreement)

    Results are upserted into post_discussion_metrics.
    """
    db = SessionLocal()
    try:
        # CASE expressions for counting sentiment types
        pos_case = case((CommentNLP.sentiment_label == "pos", 1), else_=0)
        neu_case = case((CommentNLP.sentiment_label == "neu", 1), else_=0)
        neg_case = case((CommentNLP.sentiment_label == "neg", 1), else_=0)

        stmt = (
            select(
                Comment.post_id.label("post_id"),
                func.count().label("total"),
                func.sum(pos_case).label("pos_count"),
                func.sum(neu_case).label("neu_count"),
                func.sum(neg_case).label("neg_count"),
                func.avg(CommentNLP.sentiment_score).label("avg_sentiment"),
                func.stddev_pop(CommentNLP.sentiment_score).label("sentiment_std"),
            )
            .join(CommentNLP, CommentNLP.comment_id == Comment.id)
            .where(
                Comment.created_at >= day_start_utc,
                Comment.created_at < day_end_utc,
            )
            .group_by(Comment.post_id)
        )

        rows = db.execute(stmt).all()

        for row in rows:
            post_id = row.post_id
            pos_count = int(row.pos_count or 0)
            neu_count = int(row.neu_count or 0)
            neg_count = int(row.neg_count or 0)
            avg_sentiment = float(row.avg_sentiment or 0.0)
            sentiment_std = float(row.sentiment_std or 0.0)

            # Disagreement: how split positive vs negative are
            pos_neg_total = pos_count + neg_count
            if pos_neg_total > 0:
                pos_ratio = pos_count / pos_neg_total
                neg_ratio = neg_count / pos_neg_total
                disagreement = 1.0 - abs(pos_ratio - neg_ratio)
            else:
                disagreement = 0.0

            # Controversy: log(1 + total comments) * disagreement
            total_comments = pos_count + neu_count + neg_count
            if total_comments > 0:
                controversy = math.log1p(total_comments) * disagreement
            else:
                controversy = 0.0

            existing = db.get(PostDiscussionMetrics, post_id)
            if existing:
                existing.pos_count = pos_count
                existing.neu_count = neu_count
                existing.neg_count = neg_count
                existing.avg_sentiment = avg_sentiment
                existing.sentiment_std = sentiment_std
                existing.disagreement = disagreement
                existing.controversy = controversy
            else:
                db.add(
                    PostDiscussionMetrics(
                        post_id=post_id,
                        pos_count=pos_count,
                        neu_count=neu_count,
                        neg_count=neg_count,
                        avg_sentiment=avg_sentiment,
                        sentiment_std=sentiment_std,
                        disagreement=disagreement,
                        controversy=controversy,
                    )
                )

        db.commit()
    finally:
        db.close()


def compute_daily():
    """
    Compute daily aggregates for "today" in Pacific Time:

        1. Determine today's PT window in UTC.
        2. Compute per-post discussion metrics for that window.
        3. Select top controversial posts and store them in DailyAggregate.
    """
    db = SessionLocal()
    try:
        # Now in UTC → PT date window → back to UTC bounds
        start_utc, end_utc, day = pt_bounds(datetime.now(timezone.utc))

        # Step 1: per-post metrics based on today's comments
        compute_post_discussion_metrics(start_utc, end_utc)

        # Step 2: fetch top controversial posts for this day
        rows = (
            db.execute(
                select(Post, PostDiscussionMetrics)
                .join(
                    PostDiscussionMetrics,
                    PostDiscussionMetrics.post_id == Post.id,
                )
                .where(Post.created_at >= start_utc, Post.created_at < end_utc)
                .order_by(PostDiscussionMetrics.controversy.desc())
                .limit(10)
            )
            .all()
        )

        top_posts = [
            {
                "title": p.title,
                "canonical_url": p.canonical_url,
                "score": p.score,
                "disagreement": m.disagreement,
                "controversy": m.controversy,
            }
            for (p, m) in rows
        ]

        # TODO: once entity tagging + topic modeling exists, populate these.
        sentiment_overall = {"pos": 0, "neu": 1, "neg": 0}
        top_entities, top_topics = [], []

        existing = (
            db.execute(
                select(DailyAggregate).where(DailyAggregate.day == day)
            )
            .scalars()
            .first()
        )

        if existing:
            existing.top_posts = top_posts
            existing.top_entities = top_entities
            existing.top_topics = top_topics
            existing.sentiment_overall = sentiment_overall
        else:
            db.add(
                DailyAggregate(
                    day=day,
                    top_posts=top_posts,
                    top_entities=top_entities,
                    top_topics=top_topics,
                    sentiment_overall=sentiment_overall,
                )
            )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    compute_daily()
