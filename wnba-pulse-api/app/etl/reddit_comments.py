import praw
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.db import SessionLocal
from app.core.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from app.models import *

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
