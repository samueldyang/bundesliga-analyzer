import requests
from typing import List, Dict

def fetch_season_matches(league_shortcut: str, season: int) -> list:
    url = f"https://api.openligadb.de/getmatchdata/{league_shortcut}/{season}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {league_shortcut} season {season}: {e}")
        return []

def fetch_matchday_fixtures(league_shortcut: str, season: int, matchday: int) -> List[Dict]:
    """Fetches all fixtures for a specific matchday (Spieltag)."""
    url = f"https://api.openligadb.de/getmatchdata/{league_shortcut}/{season}/{matchday}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        fixtures = []
        for m in data:
            fixtures.append({
                "match_id": m.get("matchID"),
                "home_team": m.get("team1", {}).get("teamName"),
                "away_team": m.get("team2", {}).get("teamName"),
                "match_date": m.get("matchDateTime"),
                "is_finished": m.get("matchIsFinished", False)
            })
        return fixtures
    except Exception as e:
        print(f"Error fetching matchday fixtures: {e}")
        return []

def parse_match(raw: dict) -> dict:
    if not raw.get("matchIsFinished"):
        return None

    results = {r["resultName"]: r for r in raw.get("matchResults", [])}
    ft = results.get("Endergebnis") or results.get("Endresultat")
    ht = results.get("Halbzeitergebnis")

    if not ft or not ht:
        return None

    return {
        "match_id": raw["matchID"],
        "league_shortcut": raw["leagueShortcut"],
        "season": raw["leagueSeason"],
        "match_date": raw["matchDateTime"],
        "home_team": raw["team1"]["teamName"],
        "away_team": raw["team2"]["teamName"],
        "ft_home_goals": ft["pointsTeam1"],
        "ft_away_goals": ft["pointsTeam2"],
        "ht_home_goals": ht["pointsTeam1"],
        "ht_away_goals": ht["pointsTeam2"],
    }