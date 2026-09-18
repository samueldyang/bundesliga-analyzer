import math
import os
import sys
from typing import Dict, List

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import get_team_last_matches


def poisson_pmf(k: int, lambd: float) -> float:
    """Calculates Poisson probability mass function P(X = k)."""
    if lambd <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.pow(lambd, k) * math.exp(-lambd)) / math.factorial(k)


def calculate_weighted_averages(
    matches: List[Dict], is_home_target: bool
) -> Dict[str, float]:
    """Calculates exponentially weighted average goals for a team (decay factor = 0.85)."""
    if not matches:
        return {"ft_gf": 1.2, "ft_ga": 1.2, "ht_gf": 0.5, "ht_ga": 0.5}

    # Weight decreases exponentially for older matches
    weights = [0.85**i for i in range(len(matches))]
    total_weight = sum(weights)

    ft_gf_sum, ft_ga_sum = 0.0, 0.0
    ht_gf_sum, ht_ga_sum = 0.0, 0.0

    for idx, m in enumerate(matches):
        w = weights[idx]
        if is_home_target:
            ft_gf_sum += m["ft_home_goals"] * w
            ft_ga_sum += m["ft_away_goals"] * w
            ht_gf_sum += m["ht_home_goals"] * w
            ht_ga_sum += m["ht_away_goals"] * w
        else:
            ft_gf_sum += m["ft_away_goals"] * w
            ft_ga_sum += m["ft_home_goals"] * w
            ht_gf_sum += m["ht_away_goals"] * w
            ht_ga_sum += m["ht_home_goals"] * w

    return {
        "ft_gf": ft_gf_sum / total_weight,
        "ft_ga": ft_ga_sum / total_weight,
        "ht_gf": ht_gf_sum / total_weight,
        "ht_ga": ht_ga_sum / total_weight,
    }


def compute_poisson_over_probability(
    lambda_home: float, lambda_away: float, threshold: float
) -> float:
    """Computes P(Total Goals > threshold) using bivariate Poisson independent distribution."""
    prob_under_or_equal = 0.0
    max_goals = int(threshold)

    for h in range(max_goals + 1):
        for a in range(max_goals + 1 - h):
            prob_under_or_equal += poisson_pmf(h, lambda_home) * poisson_pmf(
                a, lambda_away
            )

    return max(0.0, min(1.0, 1.0 - prob_under_or_equal))


def compare_matchup(home_team: str, away_team: str, limit: int = 10) -> Dict:
    """Calculates advanced venue-filtered, exponentially weighted Poisson expectations."""
    all_home = get_team_last_matches(home_team, limit=limit * 2)
    all_away = get_team_last_matches(away_team, limit=limit * 2)

    # 1. Venue-Specific Filtering
    home_matches = [m for m in all_home if m["home_team"] == home_team][:limit]
    away_matches = [m for m in all_away if m["away_team"] == away_team][:limit]

    # Fallback to all matches if venue sample size is too small
    if len(home_matches) < 3:
        home_matches = all_home[:limit]
    if len(away_matches) < 3:
        away_matches = all_away[:limit]

    # 2. Exponential Decay Weighting
    stats_home = calculate_weighted_averages(home_matches, is_home_target=True)
    stats_away = calculate_weighted_averages(away_matches, is_home_target=False)

    # Calculate Expected Goals (λ) by averaging home attack vs away defense
    lambda_home_ft = (stats_home["ft_gf"] + stats_away["ft_ga"]) / 2.0
    lambda_away_ft = (stats_away["ft_gf"] + stats_home["ft_ga"]) / 2.0

    lambda_home_ht = (stats_home["ht_gf"] + stats_away["ht_ga"]) / 2.0
    lambda_away_ht = (stats_away["ht_gf"] + stats_home["ht_ga"]) / 2.0

    # 3. Poisson Probability Modeling
    prob_1h_over05 = compute_poisson_over_probability(
        lambda_home_ht, lambda_away_ht, threshold=0.5
    )
    prob_ft_over25 = compute_poisson_over_probability(
        lambda_home_ft, lambda_away_ft, threshold=2.5
    )

    return {
        "home_team": home_team,
        "away_team": away_team,
        "sample_size_home": len(home_matches),
        "sample_size_away": len(away_matches),
        "expected_goals": {
            "home_ft": round(lambda_home_ft, 2),
            "away_ft": round(lambda_away_ft, 2),
            "total_ft": round(lambda_home_ft + lambda_away_ft, 2),
        },
        "matchup_summary": {
            "combined_over_05_ht_expectation": round(prob_1h_over05, 2),
            "combined_over_25_ft_expectation": round(prob_ft_over25, 2),
        },
    }


if __name__ == "__main__":
    res = compare_matchup(
        "FC Bayern München", "Borussia Dortmund", limit=10
    )
    print("Expected Goals:", res["expected_goals"])
    print("Probabilities:", res["matchup_summary"])