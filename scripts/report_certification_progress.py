from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str) -> dict[str, object]:
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def main() -> None:
    hero_manifest = _load("hero_certification_manifest.json")
    monster_manifest = _load("monster_certification_manifest.json")
    heroes = hero_manifest["heroes"]
    monsters = monster_manifest["monsters"]

    print("Heroes:")
    total_ready = 0
    for hero in heroes:
        ready = sum(level["public_ready_status"] == "ready" for level in hero["levels"])
        total_ready += ready
        print(f"{hero['class_name']} {ready}/20 - {hero['hero_name']}")
    print(f"Total certified hero snapshots: {total_ready}/240")

    certified = sum(row["public_ready_status"] == "ready" for row in monsters)
    blocked = len(monsters) - certified
    blocker_counts = Counter(
        blocker
        for row in monsters
        if row["public_ready_status"] == "blocked"
        for blocker in row["blockers"]
        if blocker != "monster-combat-mechanics-not-certified"
    )
    print("\nMonsters:")
    print(f"Certified: {certified}/330")
    print(f"Blocked: {blocked}")
    print("Top blocker families:")
    for blocker, count in blocker_counts.most_common(10):
        print(f"- {blocker}: {count}")


if __name__ == "__main__":
    main()
