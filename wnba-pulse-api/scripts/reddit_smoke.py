import os, praw
from dotenv import load_dotenv
load_dotenv()

cid = os.getenv("REDDIT_CLIENT_ID")
csec = os.getenv("REDDIT_CLIENT_SECRET")
ua = os.getenv("REDDIT_USER_AGENT")

r = praw.Reddit(client_id=cid, client_secret=csec, user_agent=ua)
r.read_only = True
print("read_only:", r.read_only)
post = next(r.subreddit("WNBA").hot(limit=1))
print("OK. Example title:", post.title)
