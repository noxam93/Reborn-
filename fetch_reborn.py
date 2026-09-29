#!/usr/bin/env python3
"""ReBorN tracker — snapshot + historia (do 31 dni)."""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ZONE = "EmpirefourkingdomsExGG2_3"
AID = 115
API = f"https://empire-api.fly.dev/{ZONE}/ain/%22AID%22:{AID}"

ROOT = Path(__file__).resolve().parent
LATEST = ROOT / "latest.json"
HISTORY = ROOT / "history.json"

# trzymamy max ~31 dni; przy cronie co 5 min to ~9000 wpisów — kompaktowo
KEEP_DAYS = 31
MAX_POINTS = 9000


def fetch() -> dict:
    req = urllib.request.Request(API, headers={"User-Agent": "reborn-tracker/2.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> None:
    raw = fetch()
    A = raw["content"]["A"]
    members = sorted(A["M"], key=lambda m: m.get("MP", 0), reverse=True)
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    players = []
    compact = {}  # oid -> [honor, might, loot]
    for m in members:
        oid = m.get("OID")
        h = int(m.get("H", 0) or 0)
        mp = int(m.get("MP", 0) or 0)
        cf = int(m.get("CF", 0) or 0)
        players.append(
            {
                "oid": oid,
                "name": m.get("N"),
                "honor": h,
                "might": mp,
                "loot_current": cf,
                "loot_highest": int(m.get("HF", 0) or 0),
                "level": m.get("L", 0),
                "legend": m.get("LL", 0),
            }
        )
        compact[str(oid)] = [h, mp, cf]

    hist = load_json(HISTORY, {"alliance": "- ReBorN -", "aid": AID, "points": []})
    points = hist.get("points") or []

    # nie zapisuj duplikatu jeśli te same wartości co ostatni punkt (API bez zmian)
    if points:
        last = points[-1]
        if last.get("p") == compact:
            # i tak odśwież latest (timestamp), ale nie doklejaj historii
            pass
        else:
            points.append({"t": now_iso, "p": compact})
    else:
        points.append({"t": now_iso, "p": compact})

    # przytnij do 31 dni / MAX_POINTS
    cutoff = (now - timedelta(days=KEEP_DAYS)).isoformat()
    points = [x for x in points if x.get("t", "") >= cutoff]
    if len(points) > MAX_POINTS:
        points = points[-MAX_POINTS:]

    hist = {
        "alliance": A.get("N") or "- ReBorN -",
        "aid": AID,
        "server": ZONE,
        "updated_at": now_iso,
        "points": points,
    }
    HISTORY.write_text(json.dumps(hist, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # prev = poprzedni punkt historii (do szybkiego Δ)
    prev_players = {}
    if len(points) >= 2:
        for oid, vals in (points[-2].get("p") or {}).items():
            prev_players[oid] = {
                "honor": vals[0],
                "might": vals[1],
                "loot_current": vals[2],
            }

    snap = {
        "alliance": A.get("N"),
        "aid": AID,
        "server": ZONE,
        "server_label": "E4K Polska 1",
        "fetched_at": now_iso,
        "player_count": len(players),
        "total_might": sum(p["might"] for p in players),
        "players": players,
        "prev_players": prev_players,
        "history_points": len(points),
        "activity_rule": (
            "Aktywny w oknie = zmiana honoru LUB mocy LUB łupów (CF) "
            "między dwiema kolejnymi próbkami w tym oknie. "
            "Źródło: empire-api ain (skład sojuszu), nie ranking grabieży lt2."
        ),
    }
    LATEST.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK players={len(players)} history={len(points)} might={snap['total_might']}")


if __name__ == "__main__":
    main()
    
