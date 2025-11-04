# app/main.py
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import create_db_and_tables, engine
from app.models import Subscriber
from app.schemas import SubscribeIn, SubscribeOut

from app.deps import RateLimiter, RecentFactsCache
from app.pipeline.fetchers import fetch_mlb_sample
from app.pipeline.agents import render_blurb
from app.pipeline.llm import compose_fact  # OpenRouter-backed compose

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# In-memory singletons (fine for MVP / single-process)
limiter = RateLimiter(rate=8, per=60)       # 8 requests/min/IP
recent_cache = RecentFactsCache(maxlen=15)  # remember last 15 MLB sentences


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
async def generate_fact(
    request: Request,
    debug: Optional[int] = 0,
):
    # Rate limit per client IP
    ip = request.client.host if request.client else "unknown"
    limiter.check(ip)

    try:
        # 1) Fetch live MLB fields (free MLB Stats API)
        fields = await fetch_mlb_sample()

        # 2) Ask OpenRouter LLM to compose a one-liner (returns None on failure)
        llm_sentence = compose_fact(fields)

        # 3) Fallback to deterministic blurb if LLM didn't return content
        sentence = llm_sentence if llm_sentence else render_blurb(fields)

        # 4) Avoid immediate duplicates
        if sentence in recent_cache._set["mlb"]:
            sentence = sentence + " "
        recent_cache.remember("mlb", sentence)

        # 5) Build response
        payload = {
            "text": sentence,
            "source": "api",
            "llm": bool(llm_sentence),  # True if OpenRouter produced the sentence
        }
        if debug:
            payload["fields"] = fields
            payload["llm_provider"] = "openrouter"
            payload["model"] = os.getenv("OPENROUTER_MODEL", "")
        return payload

    except Exception as e:
        if debug:
            return JSONResponse(
                status_code=502,
                content={"detail": "Failed to fetch MLB data", "error": str(e)},
            )
        raise HTTPException(status_code=502, detail="Failed to fetch MLB data")


@app.post("/api/subscribe", response_model=SubscribeOut)
def subscribe(body: SubscribeIn):
    if not body.sports:
        raise HTTPException(status_code=400, detail="Choose at least one sport (nba, mlb, nhl).")

    # Normalize selection flags
    flags = {"nba": False, "mlb": False, "nhl": False}
    for s in body.sports:
        flags[s] = True

    with Session(engine) as session:
        # Upsert by email
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
