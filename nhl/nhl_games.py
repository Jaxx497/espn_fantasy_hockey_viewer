from dataclasses import dataclass
from datetime import datetime
from pprint import pprint
from zoneinfo import ZoneInfo

import requests

from nhl.nhl_team import NHLTeam


@dataclass
class NHLGame:
    status: str
    start_time: str
    period: int
    time_rem: str
    intermission: bool
    home: NHLTeam
    away: NHLTeam

    @classmethod
    def get_current_state(cls):
        base_URL = "https://api-web.nhle.com/v1/score/now"
        res = requests.get(base_URL)

        raw_data = res.json()
        games = raw_data.get("games")

        return {"nhl": [cls.from_api_data(g) for g in games]}

    @classmethod
    def from_api_data(cls, game_data: dict) -> dict:
        return cls(
            status=game_data.get("gameState"),
            start_time=time_conversion(game_data.get("startTimeUTC")),
            period=int(game_data.get("period", 0)),
            time_rem=game_data.get("clock", {}).get("timeRemaining", "NA"),
            intermission=game_data.get("clock", {}).get("inIntermission", "NA"),
            home=NHLTeam.from_api_data(game_data.get("homeTeam")).__dict__,
            away=NHLTeam.from_api_data(game_data.get("awayTeam")).__dict__,
        ).__dict__


def time_conversion(utc_str: str):
    utc_time = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=ZoneInfo("UTC"))
    mountain = utc_time.astimezone(ZoneInfo("America/Denver"))

    return mountain.strftime("%I:%M %p")
