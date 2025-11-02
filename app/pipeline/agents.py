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

def render_one_sentence(fields: dict) -> str:
    """
    Create a natural one-liner depending on available fields.
    Priority: venue -> division/conference -> founding year -> league
    """
    team = normalize_name(fields.get("team_city"), fields.get("team_name"))
    sport = (fields.get("sport") or "").upper()

    venue = fields.get("venue")
    if venue:
        return f"The {team} play home games at {venue} ({sport})."

    division = clean_division(fields.get("division"))
    conference = fields.get("conference")
    if division and conference:
        return f"The {team} compete in the {division} Division of the {conference} ({sport})."
    if division:
        return f"The {team} compete in the {division} Division ({sport})."
    if conference:
        return f"The {team} are in the {conference} ({sport})."

    first_year = pretty_year(fields.get("first_year"))
    if first_year:
        return f"The {team} were founded in {first_year} ({sport})."

    league = fields.get("league")
    if league:
        return f"The {team} compete in {league} ({sport})."

    # Fallback: just the team name
    return f"{team} ({sport})."
from typing import Optional
# ... (existing functions)

def render_blurb(fields: dict) -> str:
    """
    Build a short, readable blurb straight from fields (no LLM).
    Tries to include venue/division/conference/year/league when present.
    """
    team = normalize_name(fields.get("team_city"), fields.get("team_name"))
    sport = (fields.get("sport") or "").upper()

    bits = [f"{team} — {sport}"]

    # compose from whatever we have
    abbrev = fields.get("abbrev")
    if abbrev:
        bits.append(f"abbr {abbrev}")

    venue = fields.get("venue")
    if venue:
        bits.append(f"venue: {venue}")

    division = clean_division(fields.get("division"))
    if division:
        conf = fields.get("conference")
        if conf:
            bits.append(f"division: {division}, conference: {conf}")
        else:
            bits.append(f"division: {division}")
    else:
        conf = fields.get("conference")
        if conf:
            bits.append(f"conference: {conf}")

    first_year = pretty_year(fields.get("first_year"))
    if first_year:
        bits.append(f"founded: {first_year}")

    league = fields.get("league")
    if league:
        bits.append(f"league: {league}")

    return " • ".join(bits)
