import requests


def fetch_season_matches(league_shortcut: str, season: int) -> list:
  url = f"https://api.openligadb.de/getmatchdata/{league_shortcut}/{season}"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
      )
  }
  try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()
  except Exception as e:
    print(f"Error fetching {league_shortcut} season {season}: {e}")
    return []


def fetch_matchday_fixtures(
    league_shortcut: str, season: int, matchday: int
) -> list:
  url = f"https://api.openligadb.de/getmatchdata/{league_shortcut}/{season}/{matchday}"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
      )
  }
  try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    raw_data = response.json()
    fixtures = []
    for m in raw_data:
      fixtures.append({
          "match_id": m["matchID"],
          "home_team": m["team1"]["teamName"],
          "away_team": m["team2"]["teamName"],
          "match_date": m["matchDateTime"],
          "is_finished": m.get("matchIsFinished", False),
      })
    return fixtures
  except Exception as e:
    print(f"Error fetching fixtures for matchday {matchday}: {e}")
    return []


def parse_match(raw: dict) -> dict:
  if not raw.get("matchIsFinished"):
    return None

  match_results = raw.get("matchResults", [])
  if not match_results:
    return None

  ft, ht = None, None

  for r in match_results:
    order_id = r.get("resultOrderID")
    name = str(r.get("resultName", "")).lower()

    # OpenLigaDB uses orderID 2 or "Endergebnis" for Full-Time
    if order_id == 2 or "endergebnis" in name or "endresultat" in name:
      ft = r
    # OpenLigaDB uses orderID 1 or "Halbzeitergebnis" for Half-Time
    elif order_id == 1 or "halbzeit" in name:
      ht = r

  if not ft:
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
      "ht_home_goals": ht["pointsTeam1"] if ht else 0,
      "ht_away_goals": ht["pointsTeam2"] if ht else 0,
  }