from dataclasses import dataclass
from nhl.teams_dict import TEAMS


@dataclass
class NHLTeam:
    # id: int
    abbr: str
    loc: str
    name: str
    score: int
    sog: int

    @classmethod
    def from_api_data(cls, team_data: dict):
        id = int(team_data.get("id"))
        team = TEAMS.get(id)

        return cls(
            abbr=team.get("abbr"),
            loc=team.get("location"),
            name=team.get("short_name"),
            score=int(team_data.get("score", 0)),
            sog=int(team_data.get("sog", 0)),
        )
