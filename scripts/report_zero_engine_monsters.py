from __future__ import annotations

import json
import re

from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_classifier import source_blockers
from app.domain.catalog import CoverageStatus

_DETAIL_FIELDS = ("name", "size", "armorClass", "hitPoints", "speed", "challenge", "traits", "actions")
_DETAIL_BLOCKER_LIMIT = 30


def _source_blockers(row: dict[str, object], monster_names: set[str]) -> list[str]:
    """Compatibility wrapper for scripts/tests that imported the old private helper."""
    return source_blockers(row, monster_names)


def main() -> None:
    rows = load_monster_rows()
    monster_names = {str(row["name"]) for row in rows}
    ready_names = {
        card.name for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }
    safe: list[dict[str, object]] = []
    already_ready: list[str] = []
    blocker_counts: dict[str, int] = {}
    blocker_names: dict[str, list[str]] = {}
    blocker_details: dict[str, list[dict[str, object]]] = {"reaction": [], "unsupported-action-rider": []}
    for row in rows:
        name = str(row["name"])
        blockers = source_blockers(row, monster_names)
        for blocker in set(blockers):
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
            blocker_names.setdefault(blocker, []).append(name)
        if "reaction" in blockers:
            blocker_details["reaction"].append({"name": name, "blockers": blockers, "reactions": str(row.get("reactions", ""))})
        if "unsupported-action-rider" in blockers:
            blocker_details["unsupported-action-rider"].append({"name": name, "blockers": blockers, "actions": str(row.get("actions", ""))})
        if blockers:
            continue
        (already_ready if name in ready_names else safe).append(name if name in ready_names else row)
    print(f"ZERO_ENGINE_BASELINE existing={len(already_ready)} missing={len(safe)}")
    for row in safe:
        detail = {field: row.get(field, "") for field in _DETAIL_FIELDS}
        initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row.get("rawText", "")), re.I)
        detail["initiative"] = int(initiative.group(1)) if initiative else None
        print("ZERO_ENGINE_DETAIL\t" + json.dumps(detail, ensure_ascii=False, separators=(",", ":")))
    for detail in blocker_details["reaction"]:
        print("ZERO_ENGINE_REACTION_DETAIL\t" + json.dumps(detail, ensure_ascii=False, separators=(",", ":")))
    for detail in blocker_details["unsupported-action-rider"]:
        print("ZERO_ENGINE_RIDER_DETAIL\t" + json.dumps(detail, ensure_ascii=False, separators=(",", ":")))
    for blocker, count in sorted(blocker_counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"ZERO_ENGINE_BLOCKER\t{blocker}\t{count}")
        if count <= _DETAIL_BLOCKER_LIMIT:
            print(f"ZERO_ENGINE_BLOCKER_NAMES\t{blocker}\t" + " | ".join(sorted(blocker_names[blocker])))


if __name__ == "__main__":
    main()
