from fastapi import FastAPI
from app.api.daily import router as daily_router

app = FastAPI(title="WNBA Pulse API (Local)")
app.include_router(daily_router, prefix="/daily", tags=["daily"])

@app.get("/health")
def health():
    return {"ok": True}
