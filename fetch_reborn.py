#!/usr/bin/env python3
"""Pobiera skład - ReBorN - (AID 115) z empire-api i aktualizuje data/latest.json."""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ZONE = "EmpirefourkingdomsExGG2_3"
AID = 115
API = f"https://empire-api.fly.dev/{ZONE}/ain/%22AID%22:{AID}"

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LATEST = DATA / "latest.json"


def fetch() -> dict:
    req = urllib.request.Request(API, headers={"User-Agent": "reborn-tracker/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    raw = fetch()
    A = raw["content"]["A"]
    members = sorted(A["M"], key=lambda m: m.get("MP", 0), reverse=True)

    players = []
    for m in members:
        players.append(
            {
                "oid": m.get("OID"),
                "name": m.get("N"),
                "honor": m.get("H", 0),
                "might": m.get("MP", 0),
                "loot_current": m.get("CF", 0),
                "loot_highest": m.get("HF", 0),
                "level": m.get("L", 0),
                "legend": m.get("LL", 0),
            }
        )

    prev_players = {}
    if LATEST.exists():
        try:
            old = json.loads(LATEST.read_text(encoding="utf-8"))
            for p in old.get("players", []):
                prev_players[str(p["oid"])] = {
                    "honor": p.get("honor", 0),
                    "might": p.get("might", 0),
                    "loot_current": p.get("loot_current", 0),
                }
        except Exception:
            pass

    snap = {
        "alliance": A.get("N"),
        "aid": AID,
        "server": ZONE,
        "server_label": "E4K Polska 1",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "player_count": len(players),
        "total_might": sum(p["might"] for p in players),
        "players": players,
        "prev_players": prev_players,
    }

    LATEST.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {len(players)} players, might={snap['total_might']:,}, wrote {LATEST}")


if __name__ == "__main__":
    main()
