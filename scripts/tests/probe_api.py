
"""Sonde ponctuelle API-Football : 5 appels, réponses sauvegardées dans tests/fixtures/api/."""

import json
import logging
import os
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

BASE_URL = os.environ.get("FOOTBALL_API_BASE_URL", "https://v3.football.api-sports.io")
HEADERS = {"x-apisports-key": os.environ["X_APISPORTS_KEY"]}
OUT = Path("tests/fixtures/api")
OUT.mkdir(parents=True, exist_ok=True)


def call(name: str, endpoint: str, params: dict[str, str | int]) -> dict:
    r = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params, timeout=30)
    body = r.json()
    (OUT / f"{name}.json").write_text(json.dumps(body, indent=2, ensure_ascii=False))
    quota = {k: v for k, v in r.headers.items() if k.lower().startswith("x-ratelimit")}
    log.info("%s → HTTP %s, results=%s, errors=%s, paging=%s, quota=%s",
             name, r.status_code, body.get("results"), body.get("errors"), body.get("paging"), quota)
    return body


season = call("fixtures_by_season", "fixtures", {"league": 61, "season": 2025})
call("fixtures_by_season_2023", "fixtures", {"league": 61, "season": 2023})

matches = season["response"]
finished = [m["fixture"]["id"] for m in matches if m["fixture"]["status"]["short"] == "FT"][:2]
by_ids = call("fixtures_by_ids", "fixtures", {"ids": "-".join(map(str, finished))})
log.info("clés d'un match via ids : %s", sorted(by_ids["response"][0]))

call("players_page1", "players", {"team": matches[0]["teams"]["home"]["id"], "season": 2025})
call("standings", "standings", {"league": 61, "season": 2025})