import random

_TEMPLATES = {
    "nba": [
        "{player} once had {stat} in a single game for the {team}.",
        "The {team} recorded a {streak}-game win streak in {year}.",
        "{player} averaged {avg} {stat_type} per game in {year}."
    ],
    "mlb": [
        "{player} hit {stat} in {year} for the {team}.",
        "The {team} posted a team ERA of {avg} in {year}.",
        "{player} recorded {stat} strikeouts in a season for the {team}."
    ],
    "nhl": [
        "{player} scored {stat} points in {year} with the {team}.",
        "The {team} had a {streak}-game point streak in {year}.",
        "{player} posted a save percentage of {avg} in {year}."
    ],
}

# Silly placeholder values so the pipeline shape works before real data
_PLACEHOLDERS = {
    "player": ["Nikola Jokić", "Shohei Ohtani", "Connor McDavid", "Auston Matthews", "Mookie Betts", "Luka Dončić"],
    "team": ["Nuggets", "Yankees", "Oilers", "Maple Leafs", "Dodgers", "Celtics", "Rangers"],
    "stat": ["15 assists", "3 home runs", "4 points", "12 strikeouts", "50 saves"],
    "streak": ["5", "8", "10", "12"],
    "year": ["2019", "2021", "2022", "2023", "2024"],
    "avg": ["2.3", "3.7", "0.932", "1.8", "4.5"],
    "stat_type": ["assists", "rebounds", "steals", "blocks", "points"],
}

def mock_fact(sport: str) -> str:
    sport = (sport or "").lower()
    if sport not in _TEMPLATES:
        sport = "nba"
    template = random.choice(_TEMPLATES[sport])
    values = {k: random.choice(v) for k, v in _PLACEHOLDERS.items()}
    return template.format(**values)
