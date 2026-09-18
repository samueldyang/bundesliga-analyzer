import os
import sqlite3
import sys

# Force Streamlit Cloud to search root directory first
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
import streamlit as st
from src.analyzer import compare_matchup
from src.api_client import fetch_matchday_fixtures, fetch_season_matches, parse_match
from src.database import DB_PATH, get_team_last_matches, init_db, upsert_matches

# Configuration Constants
CURRENT_SEASON = 2026

st.set_page_config(
    page_title="FCSamurai's Bundesliga Matchday Goal Analytics",
    page_icon="⚽",
    layout="wide",
)
init_db()


def auto_seed_if_empty(league_code):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT COUNT(*) FROM matches WHERE league_shortcut = ?", (league_code,)
  )
  match_count = cursor.fetchone()[0]
  conn.close()

  if match_count == 0:
    with st.spinner(f"Populating database for {league_code}..."):
      total_added = 0
      for season in [CURRENT_SEASON - 1, CURRENT_SEASON]:
        raw = fetch_season_matches(league_code, season)
        parsed = [parse_match(m) for m in raw if parse_match(m)]
        if parsed:
          upsert_matches(parsed)
          total_added += len(parsed)

      if total_added > 0:
        st.success(f"Successfully seeded {total_added} matches for {league_code}!")
        st.rerun()
      else:
        st.error(
            "Failed to retrieve historical match data from OpenLigaDB. Click"
            " 'Sync Database' in the sidebar to try again."
        )


@st.cache_data(ttl=86400)  # Re-checks OpenLigaDB once per day
def sync_latest_season_matches(league_code):
  """Fetches and upserts the current season's latest results on app load."""
  try:
    raw = fetch_season_matches(league_code, CURRENT_SEASON)
    parsed = [parse_match(m) for m in raw if parse_match(m)]
    if parsed:
      upsert_matches(parsed)
  except Exception:
    pass


# Sidebar Configuration
with st.sidebar:
  st.header("⚙️ Settings")
  league_choice = st.selectbox(
      "Select League", ["1. Bundesliga (bl1)", "2. Bundesliga (bl2)"]
  )
  league_code = "bl1" if "bl1" in league_choice else "bl2"

  matchday = st.slider(
      "Select Matchday (Spieltag)", min_value=1, max_value=34, value=1
  )
  match_limit = st.slider(
      "History Sample Window (N matches)", min_value=5, max_value=20, value=10
  )

  st.divider()
  if st.button("🔄 Sync Database from OpenLigaDB", use_container_width=True):
    with st.spinner(
        "Fetching current (2026/27) and previous (2025/26) season data..."
    ):
      for l in ["bl1", "bl2"]:
        for season in [CURRENT_SEASON - 1, CURRENT_SEASON]:
          raw = fetch_season_matches(l, season)
          parsed = [parse_match(m) for m in raw if parse_match(m)]
          upsert_matches(parsed)
      st.success("Database synced successfully with 2026/2027 fixtures!")
      st.rerun()

# Run Auto-Seed Check and Daily Sync for Selected League
auto_seed_if_empty(league_code)
sync_latest_season_matches(league_code)

# Fetch Matchday Fixtures
fixtures = fetch_matchday_fixtures(
    league_code, season=CURRENT_SEASON, matchday=matchday
)

if not fixtures:
  st.info(
      "No fixtures found for this matchday or database needs syncing. Click"
      " **Sync Database** in the sidebar."
  )
else:
  st.subheader(
      f"📅 Fixtures for Matchday {matchday} ({league_choice.split(' ')[0]} -"
      " 2026/27)"
  )

for f in fixtures:
  home, away = f["home_team"], f["away_team"]
  if not home or not away:
    continue

  res = compare_matchup(home, away, limit=match_limit)
  poisson = res["poisson_model"]
  raw = res["raw_model"]

  with st.container(border=True):
    st.markdown(f"#### ⚔️ **{home}** vs **{away}**")

    if poisson["xg"] == 2.4 and raw["prob_1h_over05"] == 0.5:
      st.warning(
          "⚠️ Insufficient historical match data. Displaying league baseline"
          " defaults."
      )

    c1, c2 = st.columns(2)

    with c1:
      st.markdown("**🎯 Poisson Model (Venue & Decay Weighted)**")
      m1, m2, m3 = st.columns(3)
      m1.metric("Expected Goals (xG)", f"{poisson['xg']}")
      m2.metric("1H Over 0.5", f"{int(poisson['prob_1h_over05'] * 100)}%")
      m3.metric("FT Over 2.5", f"{int(poisson['prob_ft_over25'] * 100)}%")

    with c2:
      st.markdown("**📊 Raw Averages (Unweighted Overall)**")
      r1, r2, r3 = st.columns(3)
      r1.metric("Raw xG", f"{raw['xg']}")
      r2.metric("1H Over 0.5 Rate", f"{int(raw['prob_1h_over05'] * 100)}%")
      r3.metric("FT Over 2.5 Rate", f"{int(raw['prob_ft_over25'] * 100)}%")

    with st.expander("Show Recent Fixture History"):
      h_col, a_col = st.columns(2)
      with h_col:
        st.caption(f"{home} Recent Games")
        h_data = pd.DataFrame(get_team_last_matches(home, limit=5))
        if not h_data.empty:
          st.dataframe(
              h_data[[
                  "match_date",
                  "home_team",
                  "away_team",
                  "ft_home_goals",
                  "ft_away_goals",
              ]],
              hide_index=True,
          )
      with a_col:
        st.caption(f"{away} Recent Games")
        a_data = pd.DataFrame(get_team_last_matches(away, limit=5))
        if not a_data.empty:
          st.dataframe(
              a_data[[
                  "match_date",
                  "home_team",
                  "away_team",
                  "ft_home_goals",
                  "ft_away_goals",
              ]],
              hide_index=True,
          )