# app/pipeline/llm.py
import os
import json
import requests
from typing import Dict, Optional
# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("OPENROUTER_MODEL", "liquid/lfm-2.5-1.2b-thinking:free")
SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8000")
APP_TITLE = os.getenv("OPENROUTER_APP_NAME", "Sports Facts")

_cache: Dict[str, str] = {}

# ------------------------------------------------------------
# BUILD PROMPT
# ------------------------------------------------------------
def _prompt_from_fields(fields: Dict) -> str:
    sport = (fields.get("sport") or "").lower()
    
    if sport == "nba":
        return _prompt_nba(fields)
    elif sport == "mlb":
        return _prompt_mlb(fields)
    else:
        return _prompt_generic(fields)


def _prompt_nba(fields: Dict) -> str:
    """Build prompt for NBA facts."""
    fact_type = fields.get("fact_type", "")
    player_name = fields.get("player_name", "")
    category = fields.get("category", "")
    rank = fields.get("rank", 0)
    value = fields.get("value", "")
    
    stat_names = {
        "PTS": "points",
        "REB": "rebounds", 
        "AST": "assists",
        "STL": "steals",
        "BLK": "blocks",
    }
    stat_name = stat_names.get(category, category)
    
    context = (
        f"Sport: NBA\n"
        f"Player: {player_name}\n"
        f"Statistic: {stat_name}\n"
        f"Rank: #{rank}\n"
        f"Value: {value}\n"
    )
    
    return (
        "You are a concise sports fact writer. "
        "Using ONLY the data below, write ONE short, engaging NBA fact about this player's achievement. "
        "Make it interesting but factual. Keep it under 25 words. "
        "Do NOT output anything except the fact sentence.\n\n"
        f"{context}"
    )


def _prompt_mlb(fields: Dict) -> str:
    """Build prompt for MLB facts."""
    team_city = (fields.get("team_city") or "").strip()
    team_name = (fields.get("team_name") or "").strip()
    venue = (fields.get("venue") or "").strip()
    division = (fields.get("division") or "").strip()
    league = (fields.get("league") or "").strip()
    first_year = (fields.get("first_year") or "").strip()
    abbr = (fields.get("abbrev") or "").strip()

    context = (
        f"Sport: MLB\n"
        f"City: {team_city}\n"
        f"Team: {team_name}\n"
        f"Abbrev: {abbr}\n"
        f"League: {league}\n"
        f"Division: {division}\n"
        f"Venue: {venue}\n"
        f"Founded: {first_year}\n"
    )

    return (
        "You are a concise sports fact writer. "
        "Using ONLY the data below, write ONE short, factual MLB sentence about this team. "
        "Prefer venue, division, or league; include founding year if interesting. "
        "Keep it under 25 words. "
        "Do NOT output anything except the sentence.\n\n"
        f"{context}"
    )


def _prompt_generic(fields: Dict) -> str:
    """Generic prompt for any sport."""
    return (
        "You are a concise sports fact writer. "
        "Write ONE short, interesting sports fact. "
        "Keep it under 25 words. "
        "Do NOT output anything except the sentence.\n"
    )

# ------------------------------------------------------------
# CALL OPENROUTER
# ------------------------------------------------------------
def compose_fact(fields: Dict) -> Optional[str]:
    """Compose a fact using OpenRouter's chat completions API."""
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("PUT_YOUR_KEY"):
        return None

    prompt = _prompt_from_fields(fields)
    if prompt in _cache:
        return _cache[prompt]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,
        "X-Title": APP_TITLE,
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000,  # High limit - model uses many tokens for reasoning before content
    }

    try:
        resp = requests.post(
            url=OPENROUTER_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        text = (
            data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
        )
        if not text:
            return None
        if not text.endswith("."):
            text += "."
        _cache[prompt] = text
        return text
    except Exception as e:
        print("OpenRouter call failed:", e)
        return None
