from __future__ import annotations

import re


def _duration_rounds(text: str) -> int | None:
    patterns = (
        r"(?:unconscious|paralyzed)\s+for\s+(\d+)\s+(minute|minutes|round|rounds)",
        r"effects last for\s+(\d+)\s+(minute|minutes|round|rounds)",
        r"disadvantage .*? for\s+(\d+)\s+(minute|minutes|round|rounds)",
    )
    match = next((found for pattern in patterns if (found := re.search(pattern, text, re.I))), None)
    if match is None:
        return None
    amount, unit = match.groups()
    count = int(amount)
    return count * 10 if unit.lower().startswith("minute") else count


def _range(area: dict) -> int:
    return int(area.get("length_ft", area.get("radius_ft", 0)))


def _sleep_breath(name: str, text: str, area: dict, save: tuple[str, int], resource_id: str) -> dict | None:
    if name.lower() != "sleep breath":
        return None
    duration = _duration_rounds(text)
    if duration is None or not re.search(r"fall unconscious", text, re.I):
        return None
    if not re.search(r"takes damage", text, re.I) or not re.search(r"uses an action to wake", text, re.I):
        return None
    ability, dc = save
    return {
        "id": "sleep-breath", "name": name,
        "save_ability": ability, "dc": dc, "range_ft": _range(area),
        "area": area,
        "failure_control_effect": {
            "condition_id": "unconscious",
            "expiry_timing": "source_turn_start",
            "duration_rounds": duration,
            "allowed_removal_action_ids": ["wake-sleeper"],
            "ends_on_damage": True,
        },
        "resource_id": resource_id, "resource_cost": 1, "animation": "unconscious",
    }


def _paralyzing_breath(name: str, text: str, area: dict, save: tuple[str, int], resource_id: str) -> dict | None:
    if name.lower() != "paralyzing breath":
        return None
    duration = _duration_rounds(text)
    if duration is None or not re.search(r"paralyzed", text, re.I):
        return None
    if not re.search(r"repeat the saving throw at the end of each of its turns", text, re.I):
        return None
    ability, dc = save
    return {
        "id": "paralyzing-breath", "name": name,
        "save_ability": ability, "dc": dc, "range_ft": _range(area),
        "area": area,
        "failure_control_effect": {
            "condition_id": "paralyzed", "expiry_timing": "target_turn_end",
            "duration_rounds": duration, "repeat_save_ability": ability,
            "repeat_save_dc": dc, "repeat_save_timing": "target_turn_end",
        },
        "resource_id": resource_id, "resource_cost": 1, "animation": "paralyzed",
    }


def _slowing_effect(name: str, text: str, area: dict, save: tuple[str, int], resource_id: str) -> dict | None:
    lower_name = name.lower()
    if lower_name not in {"slowing breath", "slow"}:
        return None
    required = (
        r"can't use reactions", r"speed is halved", r"can't make more than one attack",
        r"either an action or a bonus action", r"repeat the saving throw at the end of each of its turns",
    )
    duration = _duration_rounds(text)
    if duration is None or not all(re.search(pattern, text, re.I) for pattern in required):
        return None
    ability, dc = save
    action_id = "slowing-breath" if lower_name == "slowing breath" else "slow"
    return {
        "id": action_id, "name": name,
        "save_ability": ability, "dc": dc, "range_ft": _range(area),
        "area": area,
        "failure_control_effect": {
            "effect_id": "slowed",
            "expiry_timing": "target_turn_end", "duration_rounds": duration,
            "repeat_save_ability": ability, "repeat_save_dc": dc,
            "repeat_save_timing": "target_turn_end",
            "speed_multiplier": 0.5, "blocks_reactions": True,
            "action_bonus_exclusive": True, "max_attacks_per_turn": 1,
        },
        "resource_id": resource_id, "resource_cost": 1, "animation": "slowed",
    }


def _weakening_breath(name: str, text: str, area: dict, save: tuple[str, int], resource_id: str) -> dict | None:
    if name.lower() != "weakening breath":
        return None
    required = (
        r"disadvantage on Strength-based attack rolls",
        r"Strength checks",
        r"Strength saving throws",
        r"repeat the saving throw at the end of each of its turns",
    )
    duration = _duration_rounds(text)
    if duration is None or not all(re.search(pattern, text, re.I) for pattern in required):
        return None
    ability, dc = save
    return {
        "id": "weakening-breath", "name": name,
        "save_ability": ability, "dc": dc, "range_ft": _range(area),
        "area": area,
        "failure_control_effect": {
            "effect_id": "weakened-strength",
            "expiry_timing": "target_turn_end", "duration_rounds": duration,
            "repeat_save_ability": ability, "repeat_save_dc": dc,
            "repeat_save_timing": "target_turn_end",
            "disadvantage_strength_d20_tests": True,
        },
        "resource_id": resource_id, "resource_cost": 1, "animation": "weakened-strength",
    }


def _repulsion(name: str, text: str, area: dict, save: tuple[str, int], resource_id: str) -> dict | None:
    push = re.search(r"pushed\s+(\d+)\s+feet\s+away", text, re.I)
    if name.lower() != "repulsion breath" or push is None:
        return None
    ability, dc = save
    return {
        "id": "repulsion-breath", "name": name,
        "save_ability": ability, "dc": dc, "range_ft": _range(area),
        "area": area, "failure_push_ft": int(push.group(1)),
        "resource_id": resource_id, "resource_cost": 1, "animation": "forced-movement",
    }


def parse_control_save_action(
    heading: str,
    text: str,
    area: dict | None,
    save: tuple[str, int] | None,
    resource_id: str | None,
) -> dict | None:
    """Normalize control save actions represented by universal timed effects or forced movement."""
    name = heading.split("(Recharge", 1)[0].strip()
    if area is None or save is None or resource_id is None:
        return None
    return (
        _sleep_breath(name, text, area, save, resource_id)
        or _paralyzing_breath(name, text, area, save, resource_id)
        or _slowing_effect(name, text, area, save, resource_id)
        or _weakening_breath(name, text, area, save, resource_id)
        or _repulsion(name, text, area, save, resource_id)
    )
