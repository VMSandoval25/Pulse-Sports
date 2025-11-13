from sqlalchemy import select
from app.core.db import SessionLocal
from app.models import *

def main():
    db = SessionLocal()
    try:
        for n in ("reddit","espn"):
            exists = db.execute(select(Source).where(Source.name==n)).scalars().first()
            if not exists:
                db.add(Source(name=n))
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    main()
