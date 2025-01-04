from dataclasses import dataclass

from fantasy.teams import FantasyTeam


@dataclass
class MatchUp:
    home: FantasyTeam
    away: FantasyTeam

    @classmethod
    def new_matchup(cls, home: FantasyTeam, away: FantasyTeam) -> "MatchUp":
        return MatchUp(home, away)

    def to_dict(self):
        return self.__dict__
