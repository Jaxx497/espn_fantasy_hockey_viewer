from pprint import pprint

import os
import requests
from dotenv import load_dotenv

from fantasy.teams import FantasyTeam
from fantasy.league_meta import LeagueMeta
from fantasy.matchup import MatchUp

from nhl.nhl_games import NHLGame

SEASON = 2025
TEAM_ENDPOINT = "?view=mTeam"
MATCHUP_ENDPOINT = "?view=mMatchupScore"


class FantasyAPI:
    BASE_URL: str = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/fhl/seasons/"
    SEC_URL: str = "/segments/0/leagues/"

    def __init__(self, season: int, league_id: int) -> None:
        self.season: int = season
        self.league_id: int = league_id

    def fetch_fantasy_team_data(self, endpoint: str):
        url = f"{self.BASE_URL}{self.season}{self.SEC_URL}{self.league_id}{endpoint}"

        response = requests.get(url)
        return response.json()


def main():
    NHLGame.collect_games()

    # league_id = os.getenv("FANTASY_LEAGUE_ID") if load_dotenv() else ""
    #
    # api = FantasyAPI(SEASON, league_id)
    # mTeam_data = api.fetch_fantasy_team_data(TEAM_ENDPOINT)
    #
    # metadata = LeagueMeta.create_meta(mTeam_data)
    # fantasy_teams: dict[int, FantasyTeam] = FantasyTeam.build_teams(mTeam_data)
    #
    # # Update function uses mMatchup to pull new point totals
    # mMatchup_data = api.fetch_fantasy_team_data(MATCHUP_ENDPOINT)
    # output_data = update_fantasy_totals(mMatchup_data, fantasy_teams)
    #
    # out = metadata | output_data
    # pprint(out)


def update_fantasy_totals(mMatchup_data, fantasy_teams):
    schedule = mMatchup_data.get("schedule")
    matchups = []
    for i in schedule:
        if i.get("home").get("rosterForCurrentScoringPeriod"):
            home_id = int(i.get("home").get("teamId"))
            away_id = int(i.get("away").get("teamId"))

            home = fantasy_teams.get(home_id)
            away = fantasy_teams.get(away_id)

            formatter = lambda x: round(float(x), 1)

            home.pts_old = formatter(i.get("home").get("totalPoints"))
            home.pts_live = formatter(i.get("home").get("totalPointsLive"))
            home.pts_today = round(home.pts_live - home.pts_old, 1)

            away.pts_old = formatter(i.get("away").get("totalPoints"))
            away.pts_live = formatter(i.get("away").get("totalPointsLive"))
            away.pts_today = round(away.pts_live - away.pts_old, 1)

            this_mu = MatchUp.new_matchup(home.__dict__, away.__dict__)
            matchups.append(this_mu.to_dict())

    return {"matchups": matchups}


if __name__ == "__main__":
    main()
