import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.etl.reddit_ingest import run as ingest_posts
from app.etl.reddit_comments import run as ingest_comments
from app.etl.nlp import run_comment_sentiment
from app.etl.aggregate import compute_daily
from app.etl.summarize import summarize_day

PT = pytz.timezone("America/Los_Angeles")
scheduler = BackgroundScheduler(timezone=PT)

def daily_job():
    ingest_posts()
    ingest_comments()
    run_comment_sentiment()
    compute_daily()
    summarize_day(datetime.now(tz=PT).date())

def start_scheduler():
    scheduler.add_job(daily_job, "cron", hour=7, minute=30)
    scheduler.start()
