from typing import Dict, List, Optional
import requests

BASE_URL = "https://api.openligadb.de"


def fetch_season_matches(league: str, season: int) -> List[Dict]:
    """Fetches all matches for a specified league and season.

    Leagues: 'bl1' (1. BL), 'bl2' (2. BL), 'bl3' (3. Liga) Example season: 2025
    """
    url = f"{BASE_URL}/getmatchdata/{league}/{season}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from OpenLigaDB: {e}")
        return []


def parse_match(match: Dict) -> Optional[Dict]:
    """Parses raw match payload into a standardized dictionary.

    Returns None if the match is not yet finished.
    """
    if not match.get("matchIsFinished", False):
        return None

    ht_home, ht_away = 0, 0
    ft_home, ft_away = 0, 0

    # OpenLigaDB uses resultOrderID 1 for Half-Time and 2 for Full-Time
    for result in match.get("matchResults", []):
        r_name = result.get("resultName", "")
        r_order = result.get("resultOrderID")

        if r_order == 1 or "Halbzeit" in r_name:
            ht_home = result.get("pointsTeam1", 0)
            ht_away = result.get("pointsTeam2", 0)
        elif r_order == 2 or "Endergebnis" in r_name:
            ft_home = result.get("pointsTeam1", 0)
            ft_away = result.get("pointsTeam2", 0)

    return {
        "match_id": match.get("matchID"),
        "league": match.get("leagueShortcut", "").lower(),
        "match_date": match.get("matchDateTime"),
        "home_team": match.get("team1", {}).get("teamName"),
        "away_team": match.get("team2", {}).get("teamName"),
        "ht_home_goals": ht_home,
        "ht_away_goals": ht_away,
        "ft_home_goals": ft_home,
        "ft_away_goals": ft_away,
    }


if __name__ == "__main__":
    print("Testing OpenLigaDB connection...")
    raw_data = fetch_season_matches(league="bl1", season=2025)

    if raw_data:
        parsed_matches = [
            parse_match(m) for m in raw_data if parse_match(m) is not None
        ]
        print(f"Successfully fetched {len(raw_data)} raw matches.")
        print(f"Parsed {len(parsed_matches)} finished matches.\n")
        print("Sample Parsed Match:")
        print(parsed_matches[0])
    else:
        print("Failed to retrieve match data.")