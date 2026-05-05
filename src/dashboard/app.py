"""
Bundesliga Data Platform - Streamlit Dashboard
Reads from analytics.fct_team_season (built by dbt)
"""
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Bundesliga Dashboard",
    page_icon="\u26bd",
    layout="wide",
)


@st.cache_resource
def get_engine():
    return create_engine(
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )


@st.cache_data(ttl=300)
def load_standings():
    return pd.read_sql(
        "SELECT * FROM analytics.fct_team_season ORDER BY position",
        get_engine(),
    )


# ============= APP =============

st.title("Bundesliga Dashboard")
st.caption("Live standings powered by football-data.org -> Postgres -> dbt -> Streamlit")

df = load_standings()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

selected_tiers = st.sidebar.multiselect(
    "Show tiers",
    options=df["season_tier"].unique(),
    default=list(df["season_tier"].unique()),
)

position_range = st.sidebar.slider(
    "Position range",
    min_value=1,
    max_value=18,
    value=(1, 18),
)

filtered = df[
    (df["season_tier"].isin(selected_tiers))
    & (df["position"].between(position_range[0], position_range[1]))
]

# ---------- KPI row ----------
col1, col2, col3, col4 = st.columns(4)
with col1:
    leader = df.iloc[0]
    st.metric("League leader", leader["team_name"], f"{leader['points']} pts")
with col2:
    top_scorer = df.loc[df["goals_for"].idxmax()]
    st.metric("Most goals scored", top_scorer["team_name"], f"{top_scorer['goals_for']} goals")
with col3:
    best_defense = df.loc[df["goals_against"].idxmin()]
    st.metric("Best defense", best_defense["team_name"], f"{best_defense['goals_against']} conceded")
with col4:
    st.metric("Total teams", len(df), f"{len(filtered)} shown")

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["Standings table", "Charts", "Team detail"])

with tab1:
    st.subheader("Current standings")
    st.dataframe(
        filtered[
            ["position", "team_name", "played_games", "games_won", "games_drawn",
             "games_lost", "goals_for", "goals_against", "goal_difference",
             "points", "points_per_game", "season_tier"]
        ],
        hide_index=True,
        use_container_width=True,
    )

with tab2:
    st.subheader("Goals scored by team")
    fig_goals = px.bar(
        filtered.sort_values("goals_for", ascending=True),
        x="goals_for",
        y="team_name",
        color="season_tier",
        labels={"goals_for": "Goals scored", "team_name": "Team"},
        height=600,
    )
    st.plotly_chart(fig_goals, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Tier distribution")
        tier_counts = filtered["season_tier"].value_counts().reset_index()
        tier_counts.columns = ["tier", "count"]
        fig_pie = px.pie(tier_counts, names="tier", values="count")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.subheader("Goals scored vs conceded")
        fig_scatter = px.scatter(
            filtered,
            x="goals_against",
            y="goals_for",
            size="points",
            color="season_tier",
            hover_name="team_name",
            labels={"goals_against": "Goals conceded", "goals_for": "Goals scored"},
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Team deep-dive")
    selected_team = st.selectbox("Pick a team", df["team_name"].tolist())
    team_data = df[df["team_name"] == selected_team].iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Position", int(team_data["position"]))
        st.metric("Points", int(team_data["points"]))
        st.metric("Points per game", float(team_data["points_per_game"]))
    with c2:
        st.metric("Games won", int(team_data["games_won"]))
        st.metric("Games drawn", int(team_data["games_drawn"]))
        st.metric("Games lost", int(team_data["games_lost"]))
    with c3:
        st.metric("Goals scored", int(team_data["goals_for"]))
        st.metric("Goals conceded", int(team_data["goals_against"]))
        st.metric("Goal difference", int(team_data["goal_difference"]))

    st.info(f"**{selected_team}** is currently in the **{team_data['season_tier']}** tier.")

st.divider()
st.caption(f"Showing {len(filtered)} of {len(df)} teams - Data refreshes every 5 minutes")
