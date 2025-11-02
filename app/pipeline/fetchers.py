# app/pipeline/fetchers.py
import random
import httpx

TIMEOUT = httpx.Timeout(10.0, connect=6.0)
HEADERS = {"User-Agent": "sports-facts-mvp/0.1"}

async def _get_json(url: str):
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS, http2=False) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()

# ---------- MLB (StatsAPI, no key) ----------
async def fetch_mlb_sample():
    data = await _get_json("https://statsapi.mlb.com/api/v1/teams?sportId=1")
    teams = data.get("teams", []) or []
    team = random.choice(teams)

    venue = (team.get("venue") or {}).get("name")

    return {
        "sport": "mlb",
        "team_city": team.get("locationName"),
        "team_name": team.get("teamName"),
        "abbrev": team.get("abbreviation"),
        "first_year": team.get("firstYearOfPlay"),
        "league": (team.get("league") or {}).get("name"),
        "division": (team.get("division") or {}).get("name"),
        "venue": venue,
    }
