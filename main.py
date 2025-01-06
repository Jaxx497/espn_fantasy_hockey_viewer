from pprint import pprint
from time import sleep
from fantasy.service import FantasyService
from nhl.nhl_games import NHLGame

SEASON = 2025
TEAM_ENDPOINT = "?view=mTeam"
MATCHUP_ENDPOINT = "?view=mMatchupScore"


def main():
    fantasy_data = FantasyService.create(2025)

    while True:
        x = update_routine(fantasy_data)
        sleep(5)
        print("yeye")
        sleep(1)


def update_routine(a):
    """Get combined current state of fantasy league and NHL games"""
    fantasy_data = a.get_current_state()
    nhl_state = NHLGame.get_current_state()

    pprint(fantasy_data | nhl_state)


if __name__ == "__main__":
    main()
