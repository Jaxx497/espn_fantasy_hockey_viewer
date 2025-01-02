from pprint import pprint

import os
import requests
from dotenv import load_dotenv

from fantasy.fantasy_teams import FantasyTeam
from fantasy.league_meta import LeagueMeta
from fantasy.matchup import MatchUp

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
    load_dotenv()

    api = FantasyAPI(SEASON, os.getenv("FANTASY_LEAGUE_ID"))
    mTeam_data = api.fetch_fantasy_team_data(TEAM_ENDPOINT)
    mMatchup_data = api.fetch_fantasy_team_data(MATCHUP_ENDPOINT)

    metadata = LeagueMeta.create_meta(mTeam_data)
    fantasy_teams: dict[int, FantasyTeam] = FantasyTeam.build_teams(mTeam_data)

    # Update function uses mMatchup to pull new point totals
    output_data = update_fantasy_totals(mMatchup_data, fantasy_teams)

    pprint(output_data)


def update_fantasy_totals(mMatchup_data, fantasy_teams):
    schedule = mMatchup_data.get("schedule")
    matchups = []
    for i in schedule:
        if i.get("home").get("rosterForCurrentScoringPeriod"):
            home_id = int(i.get("home").get("teamId"))
            away_id = int(i.get("away").get("teamId"))

            home = fantasy_teams.get(home_id)
            away = fantasy_teams.get(away_id)

            home.pts_old = round(float(i.get("home").get("totalPoints")), 1)
            home.pts_live = round(float(i.get("home").get("totalPointsLive")), 1)
            home.pts_today = round(home.pts_live - home.pts_old, 1)

            away.pts_old = round(float(i.get("away").get("totalPoints")), 1)
            away.pts_live = round(float(i.get("away").get("totalPointsLive")), 1)
            away.pts_today = round(away.pts_live - away.pts_old, 1)

            this_mu = MatchUp.new_matchup(home, away)
            matchups.append(this_mu)

    return matchups


if __name__ == "__main__":
    main()
