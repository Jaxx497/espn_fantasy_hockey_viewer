from dataclasses import dataclass
from pprint import pprint


@dataclass
class NHLTeam:
    id: int
    abbr: str
    score: int
    sog: int
    name: str

    @classmethod
    def from_api_data(cls, team_data: dict):
        return cls(
            id=int(team_data.get("id", 0)),
            abbr=team_data.get("abbrev", {}),
            name=team_data.get("name", {}).get("default"),
            score=int(team_data.get("score", 0)),
            sog=int(team_data.get("sog", 0)),
        )
