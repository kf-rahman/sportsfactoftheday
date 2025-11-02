from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import datetime

from app.pipeline.prompts import mock_fact
from app.db import create_db_and_tables, engine
from app.models import Subscriber
from app.schemas import SubscribeIn, SubscribeOut

# ...
from app.deps import RateLimiter, RecentFactsCache

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# singletons (in-memory; fine for MVP / single-process)
limiter = RateLimiter(rate=8, per=60)          # 8 requests per minute per IP
recent_cache = RecentFactsCache(maxlen=15)     # remember last 15 per sport


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/healthz")
def healthcheck():
    return {"ok": True}

@app.get("/api/generate", response_class=JSONResponse)
def generate_fact(request: Request, sport: str = Query("nba", pattern="^(nba|mlb|nhl)$")):
    # rate limit
    ip = request.client.host if request.client else "unknown"
    limiter.check(ip)

    # no-repeat cache
    fact = recent_cache.unique_generate(sport, lambda: mock_fact(sport), attempts=6)
    return {"fact": fact}


@app.post("/api/subscribe", response_model=SubscribeOut)
def subscribe(body: SubscribeIn):
    if not body.sports:
        raise HTTPException(status_code=400, detail="Choose at least one sport (nba, mlb, nhl).")

    # Normalize flags
    flags = {"nba": False, "mlb": False, "nhl": False}
    for s in body.sports:
        flags[s] = True

    with Session(engine) as session:
        # upsert by email
        existing = session.exec(select(Subscriber).where(Subscriber.email == body.email)).first()
        if existing:
            existing.nba = flags["nba"]
            existing.mlb = flags["mlb"]
            existing.nhl = flags["nhl"]
            existing.updated_at = datetime.utcnow()
            session.add(existing)
            session.commit()
            return SubscribeOut(ok=True, message="Preferences updated. You're on the list!")
        else:
            sub = Subscriber(
                email=body.email,
                nba=flags["nba"],
                mlb=flags["mlb"],
                nhl=flags["nhl"],
            )
            session.add(sub)
            session.commit()
            return SubscribeOut(ok=True, message="Signed up! Welcome to Sports Facts.")
