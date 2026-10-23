from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

_FORCED_DISPLACEMENT = re.compile(
    r"\b(?:is|be|are)\s+(?:flung|pushed|pulled|thrown)\b"
    r"|\bcan choose to be pushed\b"
    r"|\b(?:pulls|throws)\s+(?:each|one|a|the)\b"
    r"|\bcreatures restrained by the whirlwind move with it\b",
    re.IGNORECASE,
)


def _mapping(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    dump = getattr(value, "model_dump", None)
    return dump() if callable(dump) else {}


def _structured_bindings(monster: SourceMonster2014) -> list[dict[str, object]]:
    bindings: list[dict[str, object]] = []
    for action_value in monster.saving_throw_actions:
        action = _mapping(action_value)
        distance = int(action.get("failure_push_ft", 0) or 0)
        if distance:
            bindings.append({
                "source_kind": "saving_throw_action",
                "source_id": str(action.get("id", "")),
                "distance_ft": distance,
                "direction": "away_from_source",
            })
    for attack in monster.attacks:
        save = _mapping(attack.on_hit_save_effect)
        distance = int(save.get("failure_push_ft", 0) or 0)
        if distance:
            bindings.append({
                "source_kind": "on_hit_save",
                "source_id": attack.id,
                "distance_ft": distance,
                "direction": "away_from_source",
            })
        contest = _mapping(attack.on_hit_contested_movement)
        distance = int(contest.get("distance_ft", 0) or 0)
        if distance:
            bindings.append({
                "source_kind": "on_hit_contested_movement",
                "source_id": attack.id,
                "distance_ft": distance,
                "direction": str(contest.get("direction", "")),
            })
    return bindings


def _has_printed_clause(monster: SourceMonster2014) -> bool:
    text = " ".join(filter(None, (
        monster.source_traits,
        monster.source_actions,
        monster.source_reactions,
    )))
    return bool(_FORCED_DISPLACEMENT.search(text))


def forced_displacement_inventory_2014(
    monsters: tuple[SourceMonster2014, ...] | list[SourceMonster2014],
) -> dict[str, object]:
    """Scan every immutable 2014 card for involuntary positional displacement."""
    try:
        applicable: list[dict[str, object]] = []
        exceptions: list[dict[str, object]] = []
        for monster in monsters:
            bindings = _structured_bindings(monster)
            if not bindings and not _has_printed_clause(monster):
                continue
            row = {
                "monster_id": monster.id,
                "monster_name": monster.name,
                "bindings": bindings,
            }
            applicable.append(row)
            if not bindings:
                exceptions.append({
                    "monster_id": monster.id,
                    "monster_name": monster.name,
                    "reason": (
                        "Printed forced-displacement clause lacks complete structured "
                        "source parameters; no approximation was admitted."
                    ),
                })
        wired = [row for row in applicable if row["bindings"]]
        return {
            "schema_version": 1,
            "mechanic": "forced-displacement-arena-exclusion",
            "source_card_count": len(monsters),
            "applicable_card_count": len(applicable),
            "python_wired_card_count": len(wired),
            "browser_wired_card_count": len(wired),
            "remaining_card_count": len(exceptions),
            "wired": wired,
            "exceptions": exceptions,
        }
    except Exception:
        logger.exception("Failed to inventory 2014 forced-displacement cards.")
        raise
