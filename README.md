# 📊 Sports Pulse — Real-Time Community Sentiment & Trend Tracker

**Sports Pulse** is a full-stack analytics platform that collects, processes, summarizes, and visualizes real-time Sports community discussions across social platforms (starting with Reddit).  
It transforms unstructured fan conversations into **actionable insights**, such as:

- Trending players & teams  
- Sentiment of discussions  
- Narrative summaries of the day  
- Heatmaps, leaderboards, and searchable feeds  

Designed as both a personal project and a portfolio piece, Sports Pulse demonstrates skills across backend engineering, NLP, data engineering, ETL pipelines, and frontend visualization.

---

## 🚀 Purpose of the Project

The goal of **Sports Pulse** is to answer a simple question:

> **“What is the Sports community talking about today, and how do they feel about it?”**

Basketball discussion online is fast, chaotic, and emotional. This project turns that unstructured noise into structured, queryable data:

- What players are being discussed the most?  
- What teams are trending upward or downward?  
- What posts sparked controversy or disagreement?  
- How does sentiment shift over time?  
- What are the top narratives of the day?  

Sports Pulse provides the foundation for a dashboard or Chrome extension that fans can use to get **instant insight** into the daily Sports conversation.

---

## 🧠 High-Level Architecture

- **PostgreSQL** for structured data storage  
- **SQLAlchemy + Alembic** for ORM and migrations  
- **FastAPI** backend for REST API  
- **NLP pipelines** (sentiment, entity tagging, NER)  
- **ETL ingestion jobs** for Reddit posts + comments  
- **Scheduled daily aggregation + LLM summary generation**  
- **Next.js frontend** (Phase 3) for visuals & UI widgets  

Everything is modular, scalable, and built exactly like a production analytics system.

---

# ✨ Features (Current & In-Progress)

## ✅ **Phase 1: Core Infrastructure (COMPLETED)**  
- Local Postgres DB with persistent Docker volume  
- Reddit API integration (PRAW)  
- ETL ingestion pipeline for:
  - Hot posts  
  - Comments (full comment tree)
- Clean ORM models split by domain (`app/models/`)  
- Database migrations via Alembic  
- Fully functioning backend environment  
- Visual DB exploration with PostgreSQL extension in VSCode  

---

## 🚧 **Phase 2: Data Analysis & NLP Pipeline (IN PROGRESS)**  

### 🔎 Entity Tagging (Teams + Players)
- Structured `entities` table  
- Sports seed via `entities.json`  
- Tagging system that maps mentions like “Bron”, “AD”, “Lakers” → canonical entities  
- NLP-assisted matching using:
  - spaCy NER  
  - fuzzy matching  
  - alias dictionary  
- Link tables:  
  - `post_entities`  
  - `comment_entities`

### 💬 Sentiment Analysis
- Per-comment sentiment  
- Aggregated per post  
- Aggregated per entity  
- Disagreement / controversy metrics

### 📅 Daily Aggregations
- Top entities  
- Top posts  
- Community mood  
- Day-level sentiment graphs  
- New narratives emerging

### 📝 LLM Daily Summary
- Generates a “Daily Sports Pulse Summary”  
- Captures top narratives, player performances, fan arguments, controversies  
- Stored in `daily_summaries` table  

---

## 🎨 **Phase 3: Frontend Web Dashboard (Upcoming)**  
- Next.js + Tailwind UI  
- Trending players module  
- Team sentiment heatmap  
- “Pulse score” per entity  
- Daily summaries viewer  
- Searchable feed of posts/comments  
- Filters (entity, sentiment, timeframe, source)  
- Real-time auto-refresh scoreboard  

---

## 🧩 **Phase 4: Chrome Extension (Optional)**  
- Injects context into Reddit/Twitter/YouTube  
- Shows:
  - Sentiment chevron near usernames  
  - Heat meter on posts (“Highly Controversial”)  
  - Player mentions highlight  
- Popup dashboard view with trending players  
- Loginless experience (stats fetched from your API)  

---

## 🛠 Tech Stack

**Backend**
- Python 3.12  
- FastAPI  
- SQLAlchemy  
- Alembic  
- PostgreSQL (Docker)  
- Redis (for future caching)  
- PRAW (Reddit)  

**NLP**
- spaCy  
- HuggingFace Sentiment model (or VADER)  
- RapidFuzz for alias fuzzy-matching  
- LLMs for daily summaries  

**Frontend**
- Next.js  
- TypeScript  
- Tailwind CSS  

**Dev Tools**
- Docker & Docker Compose  
- VSCode PostgreSQL extension  
- Makefile (optional)  
- Pre-commit hooks (optional)  

---

# 🏗 Folder Structure (Simplified)

```text
wnba-pulse-api/
  app/
    api/
    core/
    etl/
    models/
  infra/
  migrations/
  seed/
    entities_nba.json
  scripts/
  main.py

wnba-pulse-web/
  app/
  public/
  next.config.js
  package.json
```

# Early Database Design
![Database, Pulse Database](/assets/database.png)


# How to Run 
```text
docker compose -f wnba-pulse-api/infra/docker-compose.yml up -d
python -m app.etl.reddit_ingest
python -m app.etl.reddit_comments
python -m app.etl.aggregate
```