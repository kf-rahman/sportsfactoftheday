# app/pipeline/agents.py
from typing import Optional
from datetime import datetime

def normalize_name(city: Optional[str], name: Optional[str]) -> str:
    city = (city or "").strip()
    name = (name or "").strip()
    if city and name:
        return f"{city} {name}"
    return city or name or "Unknown Team"

def clean_division(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    return name.replace("Division", "").strip()

def pretty_year(y: Optional[str]) -> Optional[str]:
    # MLB/NHL return strings like "1969"
    if not y:
        return None
    try:
        int(y)
        return y
    except ValueError:
        return None

def render_mlb_fact(fields: dict) -> str:
    """
    Build a short, readable MLB fact from fields.
    Tries to include venue/division/year/league when present.
    """
    team = normalize_name(fields.get("team_city"), fields.get("team_name"))
    sport = (fields.get("sport") or "").upper()

    venue = fields.get("venue")
    if venue:
        return f"⚾ The {team} have played at {venue} since their founding ({sport})."

    first_year = pretty_year(fields.get("first_year"))
    if first_year:
        return f"⚾ The {team} were founded in {first_year} and are one of MLB's historic franchises."

    division = clean_division(fields.get("division"))
    if division:
        return f"⚾ The {team} compete in the {division} Division ({sport})."

    league = fields.get("league")
    if league:
        return f"⚾ The {team} compete in {league} ({sport})."

    return f"⚾ The {team} ({sport})."


def render_nba_fact(fields: dict) -> str:
    """
    Build a short, readable NBA fact from fields.
    Handles career leaders from real NBA API data.
    """
    fact_type = fields.get("fact_type")
    player_name = fields.get("player_name", "an NBA player")
    
    if fact_type == "career_leader":
        category = fields.get("category", "stats")
        rank = fields.get("rank", 0)
        value = fields.get("value", "")
        active = fields.get("active", False)
        
        stat_names = {
            "PTS": "points",
            "REB": "rebounds", 
            "AST": "assists",
            "STL": "steals",
            "BLK": "blocks",
        }
        stat_name = stat_names.get(category, category)
        
        active_text = " (still active)" if active else ""
        
        if rank == 1:
            return f"🏀 {player_name} is the NBA's all-time leader in {stat_name} with {value} career {stat_name}{active_text}."
        else:
            return f"🏀 {player_name} ranks #{rank} in NBA history for career {stat_name} with {value} {stat_name}{active_text}."
    
    elif fact_type == "error":
        return f"🏀 Unable to fetch NBA data at this moment. Please try again!"
    
    else:
        return f"🏀 NBA - where amazing happens! Home to the world's greatest basketball players."


def render_blurb(fields: dict) -> str:
    """
    Build a fact based on sport type.
    """
    sport = fields.get("sport", "").lower()
    
    if sport == "nba":
        return render_nba_fact(fields)
    elif sport == "mlb":
        return render_mlb_fact(fields)
    else:
        return "Sports fact coming soon!"
