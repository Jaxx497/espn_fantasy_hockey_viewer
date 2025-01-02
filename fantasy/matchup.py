from dataclasses import dataclass

from fantasy.fantasy_teams import FantasyTeam


@dataclass
class MatchUp:
    home: FantasyTeam
    away: FantasyTeam

    @classmethod
    def new_matchup(cls, home: FantasyTeam, away: FantasyTeam) -> "MatchUp":
        return MatchUp(home, away)
