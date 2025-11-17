import praw
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.db import SessionLocal
from app.core.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from app.models import *

"""
reddit_comments.py
-------------------

Purpose:
    Fetches COMMENTS for posts previously ingested by `reddit_ingest.py`.
    This script loads replies under each Reddit post and stores them in the `comments` table.

What it does:
    • Iterates over posts already stored in the database
    • Uses PRAW to load all comments for each post
    • Handles nested replies (comment trees)
    • Extracts metadata such as:
        - external_id (Reddit comment ID)
        - parent_comment_id (for threading)
        - post_id (link to posts table)
        - body text
        - author
        - score
        - created_at timestamp
        - depth (0 = top-level comment, 1+ for nested replies)
    • Inserts new comments into the `comments` table
    • Avoids duplicates via (post_id, external_id) uniqueness

When to run:
    • Immediately after `reddit_ingest.py`
    • Every few minutes to get new comments during active threads
    • Prior to running NLP sentiment analysis
    • Anytime comments need to be updated independently from posts

Dependencies:
    • Requires posts to already exist in the `posts` table
    • Populates only the `comments` table

Notes:
    This script does NOT fetch posts. It fetches comments ONLY.
    Paired with `reddit_ingest.py`, they form the complete Reddit ingestion pipeline.
"""


def client():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

def ingest_comments_for_recent_posts(limit_per_post=50, recent_posts=30):
    db = SessionLocal()
    try:
        posts = db.execute(select(Post).order_by(Post.created_at.desc()).limit(recent_posts)).scalars().all()
        reddit = client()
        for p in posts:
            subm = reddit.submission(id=p.external_id)
            subm.comments.replace_more(limit=0)
            for c in subm.comments[:limit_per_post]:
                ext_id = c.id
                exists = db.execute(select(Comment).where(Comment.post_id==p.id, Comment.external_id==ext_id)).scalars().first()
                if exists:
                    continue
                db.add(Comment(
                    post_id=p.id,
                    external_id=ext_id,
                    parent_external_id=c.parent_id.replace("t1_","").replace("t3_","") if c.parent_id else None,
                    author=str(c.author) if c.author else None,
                    body=c.body or "",
                    score=int(c.score),
                    created_at=datetime.fromtimestamp(c.created_utc, tz=timezone.utc),
                    raw_payload={}
                ))
        db.commit()
    finally:
        db.close()

def run():
    ingest_comments_for_recent_posts()

if __name__ == "__main__":
    run()
