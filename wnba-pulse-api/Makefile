INFRA = docker compose -f infra/docker-compose.yml

.PHONY: \
	infra-up infra-down infra-reset \
	db-revision db-migrate \
	dev-bootstrap dev-etl-sample dev-reset dev-up \
	run-reddit-ingest run-reddit-comments

# -------------------------
# Infra: Postgres + Redis
# -------------------------

infra-up:
	source .venv/bin/activate
	$(INFRA) up -d

infra-down:
	$(INFRA) down
	rm -f 

infra-reset:
	$(INFRA) down -v
	$(INFRA) up -d

# -------------------------
# Database / Alembic
# -------------------------

# Use this ONLY when you change models.
# Example: make db-revision MSG="add entities table"
db-revision:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Please provide a message: make db-revision MSG=\"your message\""; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MSG)"

db-wait:
	@echo "⏳ Waiting 3 seconds for Postgres to boot..."
	@sleep 3


# Safe to run anytime; will just no-op if up-to-date.
db-migrate: db-wait
	alembic upgrade head

# -------------------------
# Seeding / bootstrap
# -------------------------

dev-bootstrap:
	python -m app.etl.seed_sources || true
	python -m app.etl.seed_entities || true

# -------------------------
# ETL runners with auto-migrate retry
# -------------------------

run-reddit-ingest:
	python -m app.etl.reddit_ingest \
	|| (echo "⚠️ reddit_ingest failed, attempting alembic upgrade..." \
	    && alembic upgrade head \
	    && echo "🔁 Retrying reddit_ingest..." \
	    && python -m app.etl.reddit_ingest)

run-reddit-comments:
	python -m app.etl.reddit_comments \
	|| (echo "⚠️ reddit_comments failed, attempting alembic upgrade..." \
	    && alembic upgrade head \
	    && echo "🔁 Retrying reddit_comments..." \
	    && python -m app.etl.reddit_comments)

dev-etl-sample: run-reddit-ingest run-reddit-comments

# -------------------------
# High-level workflows
# -------------------------

# Bring up infra, ensure DB is migrated, seed data.
dev-up: infra-up db-migrate dev-bootstrap

# Nuke everything, recreate infra, migrate, seed, and run sample ETL.
dev-reset: infra-reset db-migrate dev-bootstrap  dev-etl-sample
