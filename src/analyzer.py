import math
import os
import sys
from typing import Dict, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.database import get_team_last_matches

def poisson_pmf(k: int, lambd: float) -> float:
    if lambd <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.pow(lambd, k) * math.exp(-lambd)) / math.factorial(k)

def calculate_weighted_averages(matches: List[Dict], is_home_target: bool) -> Dict[str, float]:
    if not matches:
        return {"ft_gf": 1.2, "ft_ga": 1.2, "ht_gf": 0.5, "ht_ga": 0.5}

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

def calculate_raw_stats(matches: List[Dict], team_name: str) -> Dict[str, float]:
    """Calculates raw arithmetic averages without decay weights or venue filtering."""
    if not matches:
        return {"ft_gf": 1.2, "ft_ga": 1.2, "ht_over05_pct": 0.5, "ft_over25_pct": 0.5}

    total = len(matches)
    gf, ga, ht_over05_cnt, ft_over25_cnt = 0, 0, 0, 0

    for m in matches:
        is_home = (m["home_team"] == team_name)
        gf += m["ft_home_goals"] if is_home else m["ft_away_goals"]
        ga += m["ft_away_goals"] if is_home else m["ft_home_goals"]

        if (m["ht_home_goals"] + m["ht_away_goals"]) > 0.5:
            ht_over05_cnt += 1
        if (m["ft_home_goals"] + m["ft_away_goals"]) > 2.5:
            ft_over25_cnt += 1

    return {
        "ft_gf": gf / total,
        "ft_ga": ga / total,
        "ht_over05_pct": ht_over05_cnt / total,
        "ft_over25_pct": ft_over25_cnt / total,
    }

def compute_poisson_over_probability(lambda_home: float, lambda_away: float, threshold: float) -> float:
    prob_under_or_equal = 0.0
    max_goals = int(threshold)

    for h in range(max_goals + 1):
        for a in range(max_goals + 1 - h):
            prob_under_or_equal += poisson_pmf(h, lambda_home) * poisson_pmf(a, lambda_away)

    return max(0.0, min(1.0, 1.0 - prob_under_or_equal))

def compare_matchup(home_team: str, away_team: str, limit: int = 10) -> Dict:
    all_home = get_team_last_matches(home_team, limit=limit * 2)
    all_away = get_team_last_matches(away_team, limit=limit * 2)

    # 1. Poisson Venue-Specific Model
    home_venue = [m for m in all_home if m["home_team"] == home_team][:limit] or all_home[:limit]
    away_venue = [m for m in all_away if m["away_team"] == away_team][:limit] or all_away[:limit]

    stats_home = calculate_weighted_averages(home_venue, is_home_target=True)
    stats_away = calculate_weighted_averages(away_venue, is_home_target=False)

    lambda_home_ft = (stats_home["ft_gf"] + stats_away["ft_ga"]) / 2.0
    lambda_away_ft = (stats_away["ft_gf"] + stats_home["ft_ga"]) / 2.0
    lambda_home_ht = (stats_home["ht_gf"] + stats_away["ht_ga"]) / 2.0
    lambda_away_ht = (stats_away["ht_gf"] + stats_home["ht_ga"]) / 2.0

    prob_1h_over05 = compute_poisson_over_probability(lambda_home_ht, lambda_away_ht, 0.5)
    prob_ft_over25 = compute_poisson_over_probability(lambda_home_ft, lambda_away_ft, 2.5)

    # 2. Raw Unweighted Calculations
    raw_home = calculate_raw_stats(all_home[:limit], home_team)
    raw_away = calculate_raw_stats(all_away[:limit], away_team)

    raw_xg = round((raw_home["ft_gf"] + raw_away["ft_ga"] + raw_away["ft_gf"] + raw_home["ft_ga"]) / 2.0, 2)
    raw_1h_pct = round((raw_home["ht_over05_pct"] + raw_away["ht_over05_pct"]) / 2.0, 2)
    raw_ft_pct = round((raw_home["ft_over25_pct"] + raw_away["ft_over25_pct"]) / 2.0, 2)

    return {
        "home_team": home_team,
        "away_team": away_team,
        "poisson_model": {
            "xg": round(lambda_home_ft + lambda_away_ft, 2),
            "prob_1h_over05": round(prob_1h_over05, 2),
            "prob_ft_over25": round(prob_ft_over25, 2),
        },
        "raw_model": {
            "xg": raw_xg,
            "prob_1h_over05": raw_1h_pct,
            "prob_ft_over25": raw_ft_pct,
        }
    }