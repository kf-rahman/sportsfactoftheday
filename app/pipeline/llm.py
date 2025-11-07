# app/pipeline/llm.py
import os
import json
import requests
from typing import Dict, Optional
# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/polaris-alpha")
SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8000")
APP_TITLE = os.getenv("OPENROUTER_APP_NAME", "newtest")

_cache: Dict[str, str] = {}

# ------------------------------------------------------------
# BUILD PROMPT
# ------------------------------------------------------------
def _prompt_from_fields(fields: Dict) -> str:
    team_city = (fields.get("team_city") or "").strip()
    team_name = (fields.get("team_name") or "").strip()
    venue = (fields.get("venue") or "").strip()
    division = (fields.get("division") or "").strip()
    league = (fields.get("league") or "").strip()
    first_year = (fields.get("first_year") or "").strip()
    abbr = (fields.get("abbrev") or "").strip()

    context = (
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
        "Do NOT output anything except the sentence. WRITE EVERYTHING IN CAPS\n\n"
        f"{context}"
    )

# ------------------------------------------------------------
# CALL OPENROUTER
# ------------------------------------------------------------
def compose_fact(fields: Dict) -> Optional[str]:
    """Compose a one-sentence MLB fact using OpenRouter's chat completions API."""
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
                "content": [
                    {"type": "text", "text": prompt}
                ],
            }
        ],
        "temperature": 0.4,
        "max_tokens": 64,
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
