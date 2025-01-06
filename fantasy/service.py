from dataclasses import asdict, dataclass

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
        api: FantasyAPI = FantasyAPI(season=season, league_id=league_id)

        # Load initial static data
        team_data = api.fetch_team_data(api.TEAM_ENDPOINT)
        metadata: LeagueMeta = LeagueMeta.create_meta(team_data)
        fantasy_teams = FantasyTeam.build_teams(team_data)

        return cls(api, metadata, fantasy_teams)

    def get_current_state(self) -> dict:
        """Get current state with latest matchup data"""
        matchups = self._update_matchups()

        return {
            "meta": asdict(self.metadata),
            "matchups": [asdict(matchup) for matchup in matchups],
        }

    def _update_matchups(self) -> list[MatchUp]:
        """Update and return current matchup data"""
        matchup_data = self.api.fetch_team_data(self.api.MATCHUP_ENDPOINT)
        return self._process_matchups(matchup_data)

    def refresh_static_data(self) -> None:
        """Force refresh of static team and league data"""
        team_data = self.api.fetch_team_data(self.api.TEAM_ENDPOINT)
        self.metadata = LeagueMeta.create_meta(team_data)
        self.fantasy_teams = FantasyTeam.build_teams(team_data)

    def _process_matchups(self, matchup_data: dict) -> list[MatchUp]:
        """Process matchup data and update team scores"""
        matchups = []
        schedule = matchup_data.get("schedule", [])

        for matchup in schedule:
            if matchup.get("home").get("rosterForCurrentScoringPeriod"):
                home_id: int = int(matchup.get("home").get("teamId"))
                away_id: int = int(matchup.get("away").get("teamId"))

                home = self.fantasy_teams.get(home_id)
                away = self.fantasy_teams.get(away_id)

                if home and away:
                    self._update_team_points(home, matchup.get("home"))
                    self._update_team_points(away, matchup.get("away"))

                    this_mu: MatchUp = MatchUp.new_matchup(home, away)
                    matchups.append(this_mu)

        return matchups

    @staticmethod
    def _update_team_points(team: FantasyTeam, data: dict) -> None:
        def formatter(x: float) -> float:
            return round(float(x), 1)

        team.pts_old = formatter(data.get("totalPoints", 0))
        team.pts_live = formatter(data.get("totalPointsLive", 0))
        team.pts_today = round(team.pts_live - team.pts_old, 1)
