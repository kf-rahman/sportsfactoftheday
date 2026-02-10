# app/pipeline/fetchers.py
import random
import httpx
from typing import Dict, Any, Optional

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
        "fact_type": "team_info",
        "team_city": team.get("locationName"),
        "team_name": team.get("teamName"),
        "abbrev": team.get("abbreviation"),
        "first_year": team.get("firstYearOfPlay"),
        "league": (team.get("league") or {}).get("name"),
        "division": (team.get("division") or {}).get("name"),
        "venue": venue,
    }


# ---------- NBA (nba_api package - REAL DATA ONLY) ----------
def fetch_nba_sample_sync() -> Dict[str, Any]:
    """
    Synchronous NBA data fetcher using nba_api.
    Returns ONLY real data from NBA API - no hardcoded facts.
    """
    try:
        from nba_api.stats.endpoints import alltimeleadersgrids
        
        # Only use real API data - get career leaders from various categories
        stat_mapping = {
            "PTS": 1,   # Points leaders
            "AST": 2,   # Assists leaders  
            "REB": 6,   # Rebounds leaders
            "STL": 3,   # Steals leaders
            "BLK": 7,   # Blocks leaders
        }
        stat_type = random.choice(list(stat_mapping.keys()))
        df_index = stat_mapping[stat_type]
        
        leaders = alltimeleadersgrids.AllTimeLeadersGrids(
            league_id="00",
            season_type="Regular Season",
            per_mode_simple="Totals",
            topx=10
        )
        
        # Get the correct dataframe for this stat type
        all_dfs = leaders.get_data_frames()
        if df_index < len(all_dfs):
            df = all_dfs[df_index]
            if not df.empty:
                # Pick a random leader from top 10
                leader = df.sample(1).iloc[0]
                rank_col = f"{stat_type}_RANK"
                return {
                    "sport": "nba",
                    "fact_type": "career_leader",
                    "category": stat_type,
                    "player_name": leader.get('PLAYER_NAME'),
                    "rank": int(leader.get(rank_col, 0)),
                    "value": leader.get(stat_type),
                    "active": leader.get('IS_ACTIVE_FLAG') == 'Y',
                }
        
        # If API fails or returns empty, return None to trigger error handling
        return {
            "sport": "nba",
            "fact_type": "error",
            "error": "No data available",
        }
        
    except Exception as e:
        # Return error - no hardcoded fallback
        return {
            "sport": "nba",
            "fact_type": "error",
            "error": str(e),
        }


async def fetch_nba_sample() -> Dict[str, Any]:
    """
    Async wrapper for NBA data fetching.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_nba_sample_sync)


# ---------- Main Fetch Router ----------
async def fetch_sport_sample(sport: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch sample data for specified sport or random if not specified.
    """
    if sport is None:
        sport = random.choice(["mlb", "nba"])
    
    sport = sport.lower()
    
    if sport == "mlb":
        return await fetch_mlb_sample()
    elif sport == "nba":
        return await fetch_nba_sample()
    else:
        # Default to random
        return await fetch_sport_sample(random.choice(["mlb", "nba"]))
