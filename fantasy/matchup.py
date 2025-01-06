from dataclasses import dataclass
from fantasy.team import FantasyTeam


@dataclass
class MatchUp:
    home: FantasyTeam
    away: FantasyTeam

    @classmethod
    def new_matchup(cls, home: FantasyTeam, away: FantasyTeam) -> "MatchUp":
        return MatchUp(home, away)
