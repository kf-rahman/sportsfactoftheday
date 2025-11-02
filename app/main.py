from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from datetime import datetime

from app.pipeline.prompts import mock_fact
from app.db import create_db_and_tables, engine
from app.models import Subscriber
from app.schemas import SubscribeIn, SubscribeOut
# add these
from app.pipeline.fetchers import fetch_mlb_sample
from app.pipeline.agents import render_blurb


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

# app/main.py (only the /api/generate route needs to change)
from typing import Optional

from typing import Optional
# add to imports:
# from app.pipeline.agents import render_one_sentence, render_blurb
# from app.pipeline.fetchers import fetch_nba_sample, fetch_mlb_sample, fetch_nhl_sample
# from app.pipeline.prompts import mock_fact
# (and keep limiter, recent_cache, etc.)

from typing import Optional
from fastapi import HTTPException


@app.get("/api/generate", response_class=JSONResponse)
async def generate_fact(
    request: Request,
    debug: Optional[int] = 0,
):
    ip = request.client.host if request.client else "unknown"
    limiter.check(ip)

    try:
        fields = await fetch_mlb_sample()
        blurb = render_blurb(fields)

        # avoid immediate duplicates
        if blurb in recent_cache._set["mlb"]:
            blurb = blurb + " "
        recent_cache.remember("mlb", blurb)

        payload = {"text": blurb, "source": "api"}
        if debug:
            payload["fields"] = fields
        return payload

    except Exception as e:
        if debug:
            return JSONResponse(status_code=502, content={"detail": "Failed to fetch MLB data", "error": str(e)})
        raise HTTPException(status_code=502, detail="Failed to fetch MLB data")




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
