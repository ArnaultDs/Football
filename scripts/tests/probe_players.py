"""Compare fixtures/players et fixtures?ids= (clé players) sur le même match : 1 appel."""

import json
import logging
import os
from pathlib import Path
from typing import Any

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

BASE_URL = os.environ.get("FOOTBALL_API_BASE_URL", "https://v3.football.api-sports.io")
HEADERS = {"x-apisports-key": "bd908da75091262dc44e11b81d9609a2"}
OUT = Path("tests/fixtures/api")


def fields(node: Any, prefix: str = "") -> set[str]:
    """Chemins de tous les champs (les index de liste sont remplacés par [])."""
    if isinstance(node, dict):
        return {p for k, v in node.items() for p in fields(v, f"{prefix}.{k}" if prefix else k)}
    if isinstance(node, list):
        return {p for v in node for p in fields(v, f"{prefix}[]")}
    return {prefix}


by_ids = json.loads((OUT / "fixtures_by_ids.json").read_text())
fixture_id = by_ids["response"][0]["fixture"]["id"]

r = requests.get(f"{BASE_URL}/fixtures/players", headers=HEADERS,
                 params={"fixture": fixture_id}, timeout=30)
players = r.json()
(OUT / "fixtures_players.json").write_text(json.dumps(players, indent=2, ensure_ascii=False))
log.info("fixtures/players fixture=%s → HTTP %s, results=%s, errors=%s",
         fixture_id, r.status_code, players.get("results"), players.get("errors"))

from_ids = fields(by_ids["response"][0]["players"])
from_endpoint = fields(players["response"])

log.info("champs communs : %s", len(from_ids & from_endpoint))
log.info("seulement dans fixtures/players : %s", sorted(from_endpoint - from_ids) or "aucun")
log.info("seulement dans ids : %s", sorted(from_ids - from_endpoint) or "aucun")
log.info("contenu strictement identique : %s", by_ids["response"][0]["players"] == players["response"])