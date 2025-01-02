from dataclasses import dataclass


@dataclass
class LeagueMeta:
    day: int
    week: int
    season: int
    total_days: int

    @classmethod
    def create_meta(cls, raw_data) -> "LeagueMeta":
        return LeagueMeta(
            day=int(raw_data.get("scoringPeriodId")),
            week=int(raw_data.get("status").get("currentMatchupPeriod")),
            season=int(raw_data.get("seasonId")),
            total_days=int(raw_data.get("status").get("finalScoringPeriod")),
        )
