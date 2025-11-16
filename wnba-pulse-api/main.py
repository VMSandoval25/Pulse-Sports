from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.daily import router as daily_router

app = FastAPI(title="WNBA Pulse API (Local)")

# 👇 allowed frontend origins (Next.js dev)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # in dev you can also use ["*"] if you want
    allow_credentials=False,    # set True only if you're using cookies/auth
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(daily_router, prefix="/daily", tags=["daily"])

@app.get("/health")
def health():
    return {"ok": True}
