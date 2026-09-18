import os
import sys
from typing import Dict, List

# Add project root directory to Python path for direct script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import get_team_last_matches


def calculate_team_stats(team_name: str, limit: int = 10) -> Dict:
    """Calculates Over 0.5 1H and Over 2.5 FT hit rates for a team's last N matches."""
    matches = get_team_last_matches(team_name, limit=limit)

    if not matches:
        return {
            "team_name": team_name,
            "sample_size": 0,
            "over_05_ht_count": 0,
            "over_05_ht_rate": 0.0,
            "over_25_ft_count": 0,
            "over_25_ft_rate": 0.0,
        }

    sample_size = len(matches)

    # First Half Over 0.5 (At least 1 goal scored in 1H)
    over_05_ht_count = sum(
        1 for m in matches if (m["ht_home_goals"] + m["ht_away_goals"]) >= 1
    )

    # Full Time Over 2.5 (At least 3 goals scored in FT)
    over_25_ft_count = sum(
        1 for m in matches if (m["ft_home_goals"] + m["ft_away_goals"]) >= 3
    )

    return {
        "team_name": team_name,
        "sample_size": sample_size,
        "over_05_ht_count": over_05_ht_count,
        "over_05_ht_rate": round(over_05_ht_count / sample_size, 2),
        "over_25_ft_count": over_25_ft_count,
        "over_25_ft_rate": round(over_25_ft_count / sample_size, 2),
    }


def compare_matchup(team_a: str, team_b: str, limit: int = 10) -> Dict:
    """Combines rolling statistics for two teams to calculate joint expectations."""
    stats_a = calculate_team_stats(team_a, limit=limit)
    stats_b = calculate_team_stats(team_b, limit=limit)

    avg_05_ht = round(
        (stats_a["over_05_ht_rate"] + stats_b["over_05_ht_rate"]) / 2, 2
    )
    avg_25_ft = round(
        (stats_a["over_25_ft_rate"] + stats_b["over_25_ft_rate"]) / 2, 2
    )

    return {
        "team_a": stats_a,
        "team_b": stats_b,
        "matchup_summary": {
            "sample_limit": limit,
            "combined_over_05_ht_expectation": avg_05_ht,
            "combined_over_25_ft_expectation": avg_25_ft,
        },
    }


if __name__ == "__main__":
    team_1 = "FC Bayern München"
    team_2 = "Borussia Dortmund"

    print(f"Analyzing matchup: {team_1} vs {team_2}...\n")
    analysis = compare_matchup(team_1, team_2, limit=10)

    print(f"--- {team_1} (Last {analysis['team_a']['sample_size']} Matches) ---")
    print(
        f"1H Over 0.5 Rate: {analysis['team_a']['over_05_ht_rate'] * 100}% ({analysis['team_a']['over_05_ht_count']}/{analysis['team_a']['sample_size']})"
    )
    print(
        f"FT Over 2.5 Rate: {analysis['team_a']['over_25_ft_rate'] * 100}% ({analysis['team_a']['over_25_ft_count']}/{analysis['team_a']['sample_size']})\n"
    )

    print(f"--- {team_2} (Last {analysis['team_b']['sample_size']} Matches) ---")
    print(
        f"1H Over 0.5 Rate: {analysis['team_b']['over_05_ht_rate'] * 100}% ({analysis['team_b']['over_05_ht_count']}/{analysis['team_b']['sample_size']})"
    )
    print(
        f"FT Over 2.5 Rate: {analysis['team_b']['over_25_ft_rate'] * 100}% ({analysis['team_b']['over_25_ft_count']}/{analysis['team_b']['sample_size']})\n"
    )

    print("--- Combined Matchup Expectation ---")
    print(
        f"1H Over 0.5 Probability Expectation: {analysis['matchup_summary']['combined_over_05_ht_expectation'] * 100}%"
    )
    print(
        f"FT Over 2.5 Probability Expectation: {analysis['matchup_summary']['combined_over_25_ft_expectation'] * 100}%"
    )