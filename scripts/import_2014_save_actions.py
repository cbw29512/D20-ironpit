from __future__ import annotations

import html
import re
import unicodedata

DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}
ABILITY_NAMES = {
    "strength": "strength", "dexterity": "dexterity", "constitution": "constitution",
    "intelligence": "intelligence", "wisdom": "wisdom", "charisma": "charisma",
}


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _area(text: str) -> dict | None:
    cone = re.search(r"(\d+)-foot cone", text, re.I)
    if cone:
        return {"shape": "cone", "origin": "self", "length_ft": int(cone.group(1))}
    line = re.search(r"(\d+)-foot line(?: that is)? (\d+) feet wide", text, re.I)
    if line:
        return {
            "shape": "line", "origin": "self",
            "length_ft": int(line.group(1)), "width_ft": int(line.group(2)),
        }
    return None


def _save(text: str) -> tuple[str, int] | None:
    match = re.search(
        r"DC\s+(\d+)\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw",
        text, re.I,
    )
    if match is None:
        return None
    dc, ability = match.groups()
    return ABILITY_NAMES[ability.lower()], int(dc)


def _damage(text: str) -> tuple[int, int, int, str] | None:
    match = re.search(r"(?:taking|takes)\s+\d+\s*\((\d+)d(\d+)(?:\s*([+\-−])\s*(\d+))?\)\s+([A-Za-z]+) damage", text, re.I)
    if match is None:
        return None
    count, size, sign, bonus, damage_type = match.groups()
    dtype = damage_type.lower()
    if dtype not in DAMAGE_TYPES:
        return None
    modifier = int(bonus or 0) * (-1 if sign in {"-", "−"} else 1)
    return int(count), int(size), modifier, dtype


def _heading(paragraph: str) -> str | None:
    match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
    return _plain(match.group(1)).rstrip(".") if match else None


def _recharge_parent(heading: str, recharges: dict[str, int]) -> str | None:
    for resource_id in recharges:
        printed = resource_id.replace("-", " ")
        if heading.lower().startswith(printed):
            return resource_id
    return None


def _frightful_presence(heading: str, text: str) -> dict | None:
    if heading.lower() != "frightful presence":
        return None
    save = _save(text)
    distance = re.search(r"within\s+(\d+)\s+feet", text, re.I)
    if save is None or distance is None or not re.search(r"frightened for 1 minute", text, re.I):
        return None
    ability, dc = save
    radius = int(distance.group(1))
    return {
        "id": "frightful-presence", "name": "Frightful Presence",
        "save_ability": ability, "dc": dc, "range_ft": radius,
        "area": {"shape": "emanation", "origin": "self", "radius_ft": radius},
        "failure_control_effect": {
            "condition_id": "frightened",
            "expiry_timing": "target_turn_end",
            "duration_rounds": 10,
            "repeat_save_ability": ability,
            "repeat_save_dc": dc,
            "repeat_save_timing": "target_turn_end",
            "source_effect_immunity_on_end": True,
        },
        "source_effect_immunity_on_success": True,
        "animation": "fear",
    }


def parse_save_actions(source_actions: str | None, recharges: dict[str, int]) -> list[dict]:
    """Parse exact save actions currently representable by the universal save/control/AoE engine."""
    results: list[dict] = []
    shared_resource: str | None = None
    for paragraph in re.findall(r"<p>(.*?)</p>", source_actions or "", re.I | re.S):
        heading = _heading(paragraph)
        if not heading:
            continue
        text = _plain(paragraph)
        control_action = _frightful_presence(heading, text)
        if control_action is not None:
            results.append(control_action)
            continue
        own_resource = _recharge_parent(heading, recharges)
        if own_resource is not None and "following" in text.lower():
            shared_resource = own_resource
            continue
        area = _area(text); save = _save(text); damage = _damage(text)
        if area is None or save is None or damage is None:
            if own_resource is not None:
                shared_resource = own_resource
            elif shared_resource is not None and "breath" not in heading.lower():
                shared_resource = None
            continue
        ability, dc = save; count, size, bonus, damage_type = damage
        resource_id = own_resource or shared_resource
        action_id = _slug(heading.split("(Recharge", 1)[0].strip())
        success_damage = "half" if re.search(r"half as much damage on a successful", text, re.I) else "none"
        results.append({
            "id": action_id, "name": heading.split("(Recharge", 1)[0].strip(),
            "save_ability": ability, "dc": dc, "range_ft": area.get("length_ft", 0),
            "area": area, "damage_dice_count": count, "damage_dice_size": size,
            "damage_bonus": bonus, "damage_type": damage_type, "success_damage": success_damage,
            "resource_id": resource_id, "resource_cost": 1,
        })
    return results
