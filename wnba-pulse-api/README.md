# wnba-pulse-api (Local Dev)

Phase 1 API for WNBA Pulse — FastAPI + Postgres + Alembic + APScheduler. Summarizer is stubbed.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start Postgres + Redis locally
docker compose -f infra/docker-compose.yml up -d

# Create .env from example
cp .env.example .env

# Initialize Alembic and create tables
alembic init migrations
# edit alembic.ini -> sqlalchemy.url to match DATABASE_URL
# edit migrations/env.py to import app.core.db.Base
alembic revision -m "init schema" --autogenerate
alembic upgrade head

# Seed sources
python -m app.etl.seed_sources

# (Optional) First manual ETL run
python -m app.etl.reddit_ingest
python -m app.etl.reddit_comments
python -m app.etl.nlp
python -m app.etl.aggregate
python -m app.etl.summarize

# Run API
uvicorn main:app --reload
# visit http://127.0.0.1:8000/health and /daily
```

## Notes
- Summarizer is stubbed; no OpenAI key required.
- Reddit ingestion uses PRAW; provide credentials in `.env`. You can switch to HTML fallback if needed.
