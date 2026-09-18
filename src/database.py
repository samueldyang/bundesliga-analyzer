import os
import sqlite3
import sys
from typing import Dict, List

# 1. Add project root to sys.path for direct execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2. Define global variables BEFORE function signatures
DB_PATH = os.path.join("data", "matches.db")

from src.api_client import fetch_season_matches, parse_match


def init_db(db_path: str = DB_PATH) -> None:
    """Creates the data directory and initializes the matches table if it doesn't exist."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY,
            league TEXT,
            match_date TEXT,
            home_team TEXT,
            away_team TEXT,
            ht_home_goals INTEGER,
            ht_away_goals INTEGER,
            ft_home_goals INTEGER,
            ft_away_goals INTEGER
        )
    """
    )

    conn.commit()
    conn.close()


def upsert_matches(matches: List[Dict], db_path: str = DB_PATH) -> None:
    """Inserts new matches or updates existing ones to avoid duplicates."""
    if not matches:
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT INTO matches (
            match_id, league, match_date, home_team, away_team,
            ht_home_goals, ht_away_goals, ft_home_goals, ft_away_goals
        ) VALUES (
            :match_id, :league, :match_date, :home_team, :away_team,
            :ht_home_goals, :ht_away_goals, :ft_home_goals, :ft_away_goals
        )
        ON CONFLICT(match_id) DO UPDATE SET
            league=excluded.league,
            match_date=excluded.match_date,
            home_team=excluded.home_team,
            away_team=excluded.away_team,
            ht_home_goals=excluded.ht_home_goals,
            ht_away_goals=excluded.ht_away_goals,
            ft_home_goals=excluded.ft_home_goals,
            ft_away_goals=excluded.ft_away_goals
    """,
        matches,
    )

    conn.commit()
    conn.close()


def get_team_last_matches(
    team_name: str, limit: int = 10, db_path: str = DB_PATH
) -> List[Dict]:
    """Fetches the last N finished matches for a team ordered by date descending."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM matches
        WHERE home_team = ? OR away_team = ?
        ORDER BY match_date DESC
        LIMIT ?
    """,
        (team_name, team_name, limit),
    )

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    print("Initializing Database...")
    init_db()

    print("Fetching and caching 1. Bundesliga 2025 matches...")
    raw_data = fetch_season_matches("bl1", 2025)
    parsed = [m for m in (parse_match(match) for match in raw_data) if m]

    upsert_matches(parsed)
    print(f"Stored {len(parsed)} matches in database.")

    sample_team = "FC Bayern München"
    history = get_team_last_matches(sample_team, limit=10)
    print(f"\nFetched last {len(history)} matches for {sample_team}:")
    for m in history[:3]:
        print(
            f"  {m['match_date'][:10]} | {m['home_team']} {m['ft_home_goals']}-{m['ft_away_goals']} {m['away_team']} (HT: {m['ht_home_goals']}-{m['ht_away_goals']})"
        )