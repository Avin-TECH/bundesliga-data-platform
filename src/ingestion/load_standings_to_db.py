"""
Fetch Bundesliga standings from football-data and save to Postgres.
Tables populated: teams, standings.
"""
import os
import sys
import requests
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.utils.db import get_connection

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"


def fetch_standings():
    url = f"{BASE_URL}/competitions/BL1/standings"
    headers = {"X-Auth-Token": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def upsert_team(cursor, team):
    cursor.execute(
        """
        INSERT INTO teams (team_id, name, short_name, tla, crest_url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (team_id) DO UPDATE SET
            name = EXCLUDED.name,
            short_name = EXCLUDED.short_name,
            tla = EXCLUDED.tla,
            crest_url = EXCLUDED.crest_url;
        """,
        (
            team["id"],
            team["name"],
            team.get("shortName"),
            team.get("tla"),
            team.get("crest"),
        ),
    )


def insert_standing(cursor, season, entry):
    cursor.execute(
        """
        INSERT INTO standings (
            team_id, season, position, played_games,
            won, draw, lost, points,
            goals_for, goals_against, goal_difference
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """,
        (
            entry["team"]["id"],
            season,
            entry["position"],
            entry["playedGames"],
            entry["won"],
            entry["draw"],
            entry["lost"],
            entry["points"],
            entry["goalsFor"],
            entry["goalsAgainst"],
            entry["goalDifference"],
        ),
    )


def load_to_db(api_data):
    season = api_data["season"]["startDate"][:4]
    table = api_data["standings"][0]["table"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        for entry in table:
            upsert_team(cursor, entry["team"])
            insert_standing(cursor, int(season), entry)

        conn.commit()
        print(f"Saved {len(table)} teams and standings to Postgres")
    except Exception as e:
        conn.rollback()
        print(f"Error saving to DB: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("Fetching Bundesliga standings...")
    data = fetch_standings()
    print(f"Got {len(data['standings'][0]['table'])} teams")
    load_to_db(data)
