import sqlite3
import pandas as pd
import streamlit as st
from src.analyzer import compare_matchup
from src.api_client import fetch_season_matches, parse_match
from src.database import DB_PATH, get_team_last_matches, init_db, upsert_matches

st.set_page_config(
    page_title="Bundesliga Goal Analytics", page_icon="⚽", layout="wide"
)

init_db()


def get_available_teams() -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT home_team FROM matches UNION SELECT DISTINCT away_team FROM matches ORDER BY home_team"
    )
    teams = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return teams


# Custom Styling
st.markdown(
    """
    <style>
        div[data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #0E1117; }
        .stProgress > div > div > div > div { background-color: #FF4B4B; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚽ FCSamurai's Bundesliga Goal Trend Dashboard")
st.caption(
    "Venue-filtered, exponentially weighted Poisson model for 1H Over 0.5 and FT Over 2.5 goal expectations."
)

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Configuration")
    match_limit = st.slider(
        "Rolling Match Window", min_value=5, max_value=20, value=10
    )

    st.divider()
    if st.button("🔄 Sync OpenLigaDB Data", use_container_width=True):
        with st.spinner("Fetching latest results..."):
            for league in ["bl1", "bl2", "bl3"]:
                raw = fetch_season_matches(league, 2025)
                parsed = [parse_match(m) for m in raw if parse_match(m)]
                upsert_matches(parsed)
            st.success("Database synced!")
            st.rerun()

teams = get_available_teams()

if not teams:
    st.info(
        "👈 Click **Sync OpenLigaDB Data** in the sidebar to populate the database."
    )
else:
    # Team Selection Bar
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Select Home Team", teams, index=0)
    with col2:
        team_b = st.selectbox(
            "Select Away Team", teams, index=1 if len(teams) > 1 else 0
        )

    if team_a and team_b:
        analysis = compare_matchup(team_a, team_b, limit=match_limit)
        summary = analysis["matchup_summary"]
        xg = analysis["expected_goals"]

        st.markdown("### 📊 Poisson Goal Model Expectation")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="Expected Goals (xG)", value=f"{xg['total_ft']}")
        with m2:
            val_1h = summary["combined_over_05_ht_expectation"]
            st.metric(label="1H Over 0.5 Probability", value=f"{int(val_1h * 100)}%")
            st.progress(val_1h)
        with m3:
            val_ft = summary["combined_over_25_ft_expectation"]
            st.metric(label="FT Over 2.5 Probability", value=f"{int(val_ft * 100)}%")
            st.progress(val_ft)

        st.divider()

        # Detailed Side-by-Side Breakdown
        t1, t2 = st.columns(2)

        def display_team_card(team_name, is_home):
            role = "Home" if is_home else "Away"
            st.markdown(f"### {team_name} ({role})")

            raw_matches = get_team_last_matches(team_name, limit=match_limit)
            if raw_matches:
                df = pd.DataFrame(raw_matches)
                df["Date"] = pd.to_datetime(df["match_date"]).dt.strftime(
                    "%Y-%m-%d"
                )
                df["Score (HT)"] = (
                    df["ft_home_goals"].astype(str)
                    + "-"
                    + df["ft_away_goals"].astype(str)
                    + " ("
                    + df["ht_home_goals"].astype(str)
                    + "-"
                    + df["ht_away_goals"].astype(str)
                    + ")"
                )
                df["Match"] = df["home_team"] + " vs " + df["away_team"]

                st.markdown("**Recent Fixtures**")
                st.dataframe(
                    df[["Date", "Match", "Score (HT)"]],
                    hide_index=True,
                    use_container_width=True,
                )

        with t1:
            display_team_card(team_a, is_home=True)
        with t2:
            display_team_card(team_b, is_home=False)