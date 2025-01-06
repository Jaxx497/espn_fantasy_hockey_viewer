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
    pts_for: float
    pts_against: float
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
                pts_for=round(float(record["pointsFor"]), 1),
                pts_against=round(float(record["pointsAgainst"]), 1),
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
