# app/etl/reddit_ingest.py
from datetime import datetime, timezone
import praw
from sqlalchemy import select
from app.core.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from app.core.db import SessionLocal
from app.models.source import Source
from app.models.channel import Channel
from app.models.post import Post

"""
reddit_ingest.py
----------------

Purpose:
    Fetches POSTS (threads) from Reddit for a specific subreddit (e.g., NBA, WNBA)
    using the PRAW API. This script ingests only top-level posts — not comments.

What it does:
    • Connects to Reddit using PRAW
    • Pulls posts from subreddit.hot() / .new() / .top()
    • Extracts metadata such as:
        - external_id (Reddit post ID)
        - title
        - selftext/body
        - score
        - number of comments (count only)
        - author
        - permalink / URL
        - created_at timestamp
    • Inserts new posts into the `posts` table
    • Ensures no duplicates (via external_id + source_id unique constraint)

When to run:
    • At the start of each ETL cycle
    • Hourly during the season
    • Before fetching comments
    • Anytime you want fresh subreddit threads

Dependencies:
    • Requires the `sources` table to already contain "reddit"
    • Populates only the `posts` table

Notes:
    This script does NOT fetch comments. Use `reddit_comments.py` afterward.
"""


SUBREDDITS = ["NBA"]  # change to ["nba"] or a list of team subs if you want NBA

def client():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

def get_or_create_source(db, name: str) -> Source:
    src = db.execute(select(Source).where(Source.name == name)).scalars().first()
    if src:
        return src
    src = Source(name=name)
    db.add(src)
    db.flush()  # assigns id
    return src

def get_or_create_channel(db, source_id: int, handle: str, external_id: str, display_name: str | None = None) -> Channel:
    ch = db.execute(
        select(Channel).where(Channel.source_id == source_id, Channel.external_id == external_id)
    ).scalars().first()
    if ch:
        return ch
    ch = Channel(
        source_id=source_id,
        external_id=external_id,   # e.g. "WNBA"
        handle=handle,             # e.g. "r/WNBA"
        display_name=display_name or handle,
        metadata_json={"kind": "subreddit"}
    )
    db.add(ch)
    db.flush()
    return ch

def fetch_posts_from_subreddit(reddit, sub_name: str, limit=50):
    sub = reddit.subreddit(sub_name)
    for s in sub.hot(limit=limit):
        yield {
            "external_id": s.id,
            "title": s.title or "",
            "body": (getattr(s, "selftext", None) or None),
            "canonical_url": f"https://www.reddit.com{s.permalink}",
            "author": str(s.author) if s.author else None,
            "score": int(s.score), #upvotes vs downvoates
            "comment_count": int(getattr(s, "num_comments", 0)),
            "created_at": datetime.fromtimestamp(s.created_utc, tz=timezone.utc),
            "raw_payload": {"permalink": s.permalink, "subreddit": str(s.subreddit)},
        }

def upsert_posts(limit=50):
    db = SessionLocal()
    try:
        reddit = client()
        source = get_or_create_source(db, "reddit")

        for sub_name in SUBREDDITS:
            channel = get_or_create_channel(
                db,
                source_id=source.id,
                handle=f"r/{sub_name}",
                external_id=sub_name,           # store plain subreddit name as the channel external_id
                display_name=f"r/{sub_name}"
            )

            for r in fetch_posts_from_subreddit(reddit, sub_name, limit=limit):
                # already in?
                exists = db.execute(
                    select(Post).where(
                        Post.source_id == source.id,
                        Post.external_id == r["external_id"]
                    )
                ).scalars().first()
                if exists:
                    continue

                db.add(Post(
                    source_id=source.id,
                    channel_id=channel.id,
                    collected_at=datetime.now(timezone.utc),
                    **r
                ))
        db.commit()
    finally:
        db.close()

def run(limit=50):
    upsert_posts(limit=limit)

if __name__ == "__main__":
    run()
