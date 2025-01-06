import os
from dataclasses import dataclass

import requests
from dotenv import load_dotenv
from requests.models import Response


@dataclass
class FantasyAPI:
    BASE_URL: str = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/fhl/seasons/"
    MID_URL: str = "/segments/0/leagues/"
    TEAM_ENDPOINT: str = "?view=mTeam"
    MATCHUP_ENDPOINT: str = "?view=mMatchupScore"

    def __init__(self, season: int, league_id: str | None = None) -> None:
        self.season: int = season
        self.league_id: str = (
            league_id or os.getenv("FANTASY_LEAGUE_ID", "") if load_dotenv() else ""
        )

    def fetch_team_data(self, endpoint: str) -> dict:
        """Fetch data from ESPN Fantasy API"""
        url: str = (
            f"{self.BASE_URL}{self.season}{self.MID_URL}{self.league_id}{endpoint}"
        )
        response: Response = requests.get(url)
        return response.json()
