# app/main.py
import os
import random
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import create_db_and_tables, engine
from app.models import Subscriber
from app.schemas import SubscribeIn, SubscribeOut

from app.deps import RateLimiter, RecentFactsCache
from app.pipeline.fetchers import fetch_sport_sample
from app.pipeline.agents import render_blurb
from app.pipeline.llm import compose_fact  # OpenRouter-backed compose
from app.services.email_service import email_service

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# In-memory singletons (fine for MVP / single-process)
limiter = RateLimiter(rate=8, per=60)       # 8 requests/min/IP
recent_cache = RecentFactsCache(maxlen=15)  # remember last 15 facts per sport


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
    sport: Optional[str] = Query(None, description="Sport type: mlb, nba, or random"),
    debug: Optional[int] = 0,
):
    # Rate limit per client IP
    ip = request.client.host if request.client else "unknown"
    limiter.check(ip)

    try:
        # 1) Fetch live data (MLB or NBA based on sport param or random)
        fields = await fetch_sport_sample(sport)
        
        # Get sport name for caching
        sport_key = fields.get("sport", "unknown")

        # 2) Ask OpenRouter LLM to compose a one-liner (returns None on failure)
        llm_sentence = compose_fact(fields)

        # 3) Fallback to deterministic blurb if LLM didn't return content
        sentence = llm_sentence if llm_sentence else render_blurb(fields)

        # 4) Avoid immediate duplicates
        if sentence in recent_cache._set.get(sport_key, set()):
            sentence = sentence + " "
        recent_cache.remember(sport_key, sentence)

        # 5) Build response
        payload = {
            "text": sentence,
            "source": "api",
            "sport": sport_key,
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
                content={"detail": "Failed to fetch sports data", "error": str(e)},
            )
        raise HTTPException(status_code=502, detail="Failed to fetch sports data")


@app.post("/api/subscribe", response_model=SubscribeOut)
def subscribe(body: SubscribeIn):
    if not body.sports:
        raise HTTPException(status_code=400, detail="Choose at least one sport (nba, mlb).")

    # Normalize selection flags
    flags = {"nba": False, "mlb": False}
    for s in body.sports:
        if s in flags:
            flags[s] = True

    with Session(engine) as session:
        # Upsert by email
        existing = session.exec(select(Subscriber).where(Subscriber.email == body.email)).first()
        if existing:
            existing.nba = flags["nba"]
            existing.mlb = flags["mlb"]
            existing.updated_at = datetime.utcnow()
            session.add(existing)
            session.commit()
            return SubscribeOut(ok=True, message="Preferences updated. You're on the list!")
        else:
            sub = Subscriber(
                email=body.email,
                nba=flags["nba"],
                mlb=flags["mlb"],
            )
            session.add(sub)
            session.commit()
            return SubscribeOut(ok=True, message="Signed up! Welcome to Sports Facts.")


@app.get("/api/sports")
def list_sports():
    """Return available sports and fact types."""
    return {
        "sports": [
            {
                "key": "mlb",
                "name": "Major League Baseball",
                "fact_types": ["team_info", "career_leaders", "season_stats"]
            },
            {
                "key": "nba", 
                "name": "National Basketball Association",
                "fact_types": ["career_leader", "season_leader", "milestone"]
            }
        ]
    }


# ------------------------------------------------------------
# EMAIL ENDPOINTS
# ------------------------------------------------------------

@app.get("/api/email/status")
def email_status():
    """Check if email service is configured."""
    return {
        "configured": email_service.is_configured(),
        "from_email": os.getenv("FROM_EMAIL", "not set"),
        "has_resend_key": bool(os.getenv("RESEND_API_KEY", ""))
    }


@app.post("/api/email/send-test")
async def send_test_email(email: str, sport: str = "random"):
    """Send a test email to a specific address."""
    if not email_service.is_configured():
        raise HTTPException(
            status_code=503, 
            detail="Email service not configured. Set RESEND_API_KEY env variable."
        )
    
    # Generate fact
    fact = await email_service.generate_daily_fact(sport)
    
    # Send email
    success = await email_service.send_email(email, fact)
    
    if success:
        return {
            "success": True,
            "message": f"Test email sent to {email}",
            "fact": fact
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")


@app.post("/api/email/send-daily")
async def send_daily_emails(
    sport: str = "random",
    secret: Optional[str] = Query(None, description="Secret key for admin access")
):
    """Send daily emails to all subscribers. Protected by secret key."""
    # Simple protection - in production use proper auth
    admin_secret = os.getenv("ADMIN_SECRET", "dev-secret-123")
    if secret != admin_secret:
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    if not email_service.is_configured():
        raise HTTPException(
            status_code=503, 
            detail="Email service not configured. Set RESEND_API_KEY env variable."
        )
    
    # Send emails
    result = await email_service.send_daily_emails(sport)
    
    return {
        "success": True,
        "total_subscribers": result["total"],
        "sent": result["sent"],
        "failed": result["failed"],
        "fact_sent": result["fact"]
    }


@app.get("/unsubscribe")
def unsubscribe_page(request: Request, email: Optional[str] = None):
    """Show unsubscribe page."""
    return templates.TemplateResponse("unsubscribe.html", {
        "request": request, 
        "email": email or ""
    })


@app.post("/api/unsubscribe")
def unsubscribe(email: str):
    """Unsubscribe an email from daily facts."""
    with Session(engine) as session:
        subscriber = session.exec(
            select(Subscriber).where(Subscriber.email == email)
        ).first()
        
        if subscriber:
            session.delete(subscriber)
            session.commit()
            return {"success": True, "message": "You've been unsubscribed. Sorry to see you go!"}
        else:
            return {"success": False, "message": "Email not found in our list."}
