from __future__ import annotations

import re

from import_2014_save_actions import _area, _damage, _heading, _plain, _save


def parse_death_trigger(paragraph: str) -> dict | None:
    """Parse Death Burst into the existing universal saving-throw action shape."""
    heading = _heading(paragraph)
    if heading is None or heading.lower() != "death burst":
        return None
    text = _plain(paragraph)
    if not re.search(r"when (?:the|a) [A-Za-z' -]+ dies", text, re.I):
        return None
    area = _area(text); save = _save(text)
    if area is None or save is None:
        return None
    ability, dc = save
    base = {
        "id": "death-burst", "name": "Death Burst", "save_ability": ability, "dc": dc,
        "range_ft": area.get("radius_ft", area.get("length_ft", 0)), "area": area,
        "animation": "death-burst",
    }
    damage = _damage(text)
    if damage is not None:
        count, size, bonus, damage_type = damage
        if not re.search(r"half as much damage on a successful", text, re.I):
            return None
        return {
            **base, "damage_dice_count": count, "damage_dice_size": size,
            "damage_bonus": bonus, "damage_type": damage_type, "success_damage": "half",
        }
    blinded = re.search(r"blinded for 1 minute", text, re.I)
    repeat = re.search(r"repeat the saving throw at the end of each of its turns", text, re.I)
    if blinded and repeat:
        return {
            **base,
            "failure_control_effect": {
                "condition_id": "blinded", "expiry_timing": "target_turn_end", "duration_rounds": 10,
                "repeat_save_ability": ability, "repeat_save_dc": dc,
                "repeat_save_timing": "target_turn_end",
            },
        }
    return None
