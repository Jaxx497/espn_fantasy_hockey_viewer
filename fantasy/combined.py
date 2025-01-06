# File: api.py

from dataclasses import dataclass
import os
import requests
from dotenv import load_dotenv


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
        url = f"{self.BASE_URL}{self.season}{self.MID_URL}{self.league_id}{endpoint}"
        response = requests.get(url)
        return response.json()


# File: matchup.py

from dataclasses import dataclass
from fantasy.team import FantasyTeam


@dataclass
class MatchUp:
    home: FantasyTeam
    away: FantasyTeam

    @classmethod
    def new_matchup(cls, home: FantasyTeam, away: FantasyTeam) -> "MatchUp":
        return MatchUp(home, away).__dict__


# File: meta.py

from dataclasses import dataclass


@dataclass
class LeagueMeta:
    day: int
    week: int
    season: int
    total_days: int

    @classmethod
    def create_meta(cls, raw_data) -> dict:
        lm = LeagueMeta(
            day=int(raw_data.get("scoringPeriodId")),
            week=int(raw_data.get("status").get("currentMatchupPeriod")),
            season=int(raw_data.get("seasonId")),
            total_days=int(raw_data.get("status").get("finalScoringPeriod")),
        )

        return {"meta": lm.__dict__}


# File: service.py

from dataclasses import dataclass

from fantasy.api import FantasyAPI
from fantasy.team import FantasyTeam
from fantasy.meta import LeagueMeta
from fantasy.matchup import MatchUp


@dataclass
class FantasyService:
    api: FantasyAPI
    metadata: dict
    fantasy_teams: dict[int, FantasyTeam]

    @classmethod
    def create(cls, season: int, league_id: str | None = None) -> "FantasyService":
        """Factory method to create FantasyService instance with initial data"""
        api = FantasyAPI(season=season, league_id=league_id)

        # Load initial static data
        team_data = api.fetch_team_data(api.TEAM_ENDPOINT)
        metadata = LeagueMeta.create_meta(team_data)
        fantasy_teams = FantasyTeam.build_teams(team_data)

        return cls(api=api, metadata=metadata, fantasy_teams=fantasy_teams)

    def get_current_state(self) -> dict:
        """Get current state with latest matchup data"""
        matchups = self._update_matchups()
        return self.metadata | matchups

    def _update_matchups(self) -> dict:
        """Update and return current matchup data"""
        matchup_data = self.api.fetch_team_data(self.api.MATCHUP_ENDPOINT)
        return self._process_matchups(matchup_data)

    def refresh_static_data(self) -> None:
        """Force refresh of static team and league data"""
        team_data = self.api.fetch_team_data(self.api.TEAM_ENDPOINT)
        self.metadata = LeagueMeta.create_meta(team_data)
        self.fantasy_teams = FantasyTeam.build_teams(team_data)

    def _process_matchups(self, matchup_data: dict) -> dict:
        """Process matchup data and update team scores"""
        matchups = []
        schedule = matchup_data.get("schedule", [])

        for matchup in schedule:
            if matchup.get("home").get("rosterForCurrentScoringPeriod"):
                home_id = int(matchup.get("home").get("teamId"))
                away_id = int(matchup.get("away").get("teamId"))

                home = self.fantasy_teams.get(home_id)
                away = self.fantasy_teams.get(away_id)

                if home and away:
                    self._update_team_points(home, matchup.get("home"))
                    self._update_team_points(away, matchup.get("away"))

                    this_mu = MatchUp.new_matchup(home.__dict__, away.__dict__)
                    matchups.append(this_mu)

        return {"matchups": matchups}

    @staticmethod
    def _update_team_points(team: FantasyTeam, data: dict) -> None:
        def formatter(x: float):
            return round(float(x), 1)

        team.pts_old = formatter(data.get("totalPoints", 0))
        team.pts_live = formatter(data.get("totalPointsLive", 0))
        team.pts_today = round(team.pts_live - team.pts_old, 1)


# File: team.py

from dataclasses import dataclass
from enum import Enum


@dataclass
class FantasyTeam:
    # Metadata
    id: int
    name: str
    abbr: str

    # Record
    rank: int
    wins: int
    losses: int
    ties: int
    streak_len: int
    streak_type: str

    # Season Stats
    points_for: float
    points_against: float
    acquisitions: int
    drops: int
    move_to_ir: int

    # Matchup Stats
    pts_old: float
    pts_live: float
    pts_today: float

    @property
    def record(self) -> str:
        """Returns formatted record string"""
        return f"{self.wins}-{self.losses}-{self.ties}"

    @classmethod
    def from_api_data(cls, team_data) -> "FantasyTeam":
        record = team_data.get("record").get("overall")
        transactions = team_data.get("transactionCounter")

        try:
            return FantasyTeam(
                id=int(team_data["id"]),
                name=team_data["name"],
                abbr=team_data["abbrev"],
                rank=int(team_data["playoffSeed"]),
                wins=int(record["wins"]),
                losses=int(record["losses"]),
                ties=int(record["ties"]),
                streak_len=int(record["streakLength"]),
                streak_type=record["streakType"],
                points_for=round(float(record["pointsFor"]), 1),
                points_against=round(float(record["pointsAgainst"]), 1),
                acquisitions=int(transactions["acquisitions"]),
                drops=int(transactions["drops"]),
                move_to_ir=int(transactions["moveToIR"]),
                pts_old=0.0,
                pts_live=0.0,
                pts_today=0.0,
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Error creating FantasyTeam data from API.\nError: {e}")

    @classmethod
    def build_teams(cls, raw_data) -> dict[int, "FantasyTeam"]:
        """Creates a list of FantasyTeam instances"""
        teams = raw_data.get("teams")

        return {
            team_data.id: team_data
            for team in teams
            if (team_data := cls.from_api_data(team))
        }
