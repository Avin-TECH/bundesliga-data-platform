"""
Fetch current Bundesliga standings from football-data.org API.
"""
import os #lets us read environment variables
import requests
from dotenv import load_dotenv

"""→ a docstring describing what the file does (good practice)
import os → lets us read environment variables
import requests → the library for making HTTP requests
from dotenv import load_dotenv → reads variables from .env file
load_dotenv() → loads the environment variables from the .env file"""


load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")  # Get API key from environment variable
API_URL = "https://api.football-data.org/v4"


def fetch_bundesliga_standings():
    """Fetch current Bundesliga standings from football-data.org API."""
    url=f"{API_URL}/competitions/BL1/standings"
    headers = {"X-Auth-Token": API_KEY}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def print_standings(data):
    """Print the standings in a readable format."""
    standings = data["standings"][0]["table"]

    print("\n=== Bundesliga Standings ===\n")
    for entry in standings:
        position = entry["position"]
        team = entry["team"]["name"]
        points = entry["points"]
        played = entry["playedGames"]
        print(f"{position:>2}. {team:<25} {points:>3} pts ({played} games)")
    print()


if __name__ == "__main__":
    standings_data = fetch_bundesliga_standings()
    print_standings(standings_data)