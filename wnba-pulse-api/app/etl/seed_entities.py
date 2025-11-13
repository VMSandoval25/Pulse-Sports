# app/etl/seed_entities.py
import json
from pathlib import Path
from sqlalchemy import select
from app.core.db import SessionLocal
from app.models.entity import Entity

def run(path: str = "./seed/entities_nba.json"):
    data = json.loads(Path(path).read_text())
    db = SessionLocal()
    try:
        for row in data:
            # Use (league, type, name) as a natural key to avoid dupes
            exists = db.execute(
                select(Entity).where(
                    Entity.league == row["league"],
                    Entity.type == row["type"],
                    Entity.name == row["name"],
                )
            ).scalar_one_or_none()

            if exists:
                # optionally update fields like aliases, team, short_name
                exists.short_name = row.get("short_name")
                exists.team = row.get("team")
                exists.aliases = row["aliases"]
            else:
                db.add(Entity(
                    league=row["league"],
                    type=row["type"],
                    name=row["name"],
                    short_name=row.get("short_name"),
                    team=row.get("team"),
                    aliases=row["aliases"],
                ))
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run()
