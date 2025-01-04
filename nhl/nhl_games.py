from dataclasses import dataclass
from pprint import pprint
import requests


@dataclass
class NHLGames:
    status_abstract: str
    status_detailed: str

    @classmethod
    def temp(cls):
        bleh = "https://api-web.nhle.com/v1/score/now"
        res = requests.get(bleh)

        x = res.json()

        pprint(x["games"])
