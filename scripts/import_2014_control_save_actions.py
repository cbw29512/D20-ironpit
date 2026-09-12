from __future__ import annotations

import re


def _sleep_breath(name: str, text: str, area: dict, save: tuple[str, int], resource_id: str) -> dict | None:
    if name.lower() != "sleep breath":
        return None
    if not re.search(r"unconscious for 1 minute", text, re.I):
        return None
    if not re.search(r"takes damage", text, re.I) or not re.search(r"uses an action to wake", text, re.I):
        return None
    ability, dc = save
    return {
        "id": "sleep-breath", "name": name,
        "save_ability": ability, "dc": dc, "range_ft": area.get("length_ft", 0),
        "area": area,
        "failure_control_effect": {
            "condition_id": "unconscious",
            "expiry_timing": "source_turn_start",
            "duration_rounds": 10,
            "allowed_removal_action_ids": ["wake-sleeper"],
            "ends_on_damage": True,
        },
        "resource_id": resource_id, "resource_cost": 1, "animation": "unconscious",
    }


def _paralyzing_breath(name: str, text: str, area: dict, save: tuple[str, int], resource_id: str) -> dict | None:
    if name.lower() != "paralyzing breath":
        return None
    if not re.search(r"paralyzed for 1 minute", text, re.I):
        return None
    if not re.search(r"repeat the saving throw at the end of each of its turns", text, re.I):
        return None
    ability, dc = save
    return {
        "id": "paralyzing-breath", "name": name,
        "save_ability": ability, "dc": dc, "range_ft": area.get("length_ft", 0),
        "area": area,
        "failure_control_effect": {
            "condition_id": "paralyzed", "expiry_timing": "target_turn_end",
            "duration_rounds": 10, "repeat_save_ability": ability,
            "repeat_save_dc": dc, "repeat_save_timing": "target_turn_end",
        },
        "resource_id": resource_id, "resource_cost": 1, "animation": "paralyzed",
    }


def parse_control_save_action(
    heading: str,
    text: str,
    area: dict | None,
    save: tuple[str, int] | None,
    resource_id: str | None,
) -> dict | None:
    """Normalize control save actions already representable by universal timed conditions."""
    name = heading.split("(Recharge", 1)[0].strip()
    if area is None or save is None or resource_id is None:
        return None
    return (
        _sleep_breath(name, text, area, save, resource_id)
        or _paralyzing_breath(name, text, area, save, resource_id)
    )
