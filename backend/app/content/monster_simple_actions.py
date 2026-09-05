from __future__ import annotations

import re

from app.content.monster_source_definition import slug

_DAMAGE = "acid|bludgeoning|cold|fire|force|lightning|necrotic|piercing|poison|psychic|radiant|slashing|thunder"
_NUMBER = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
_ATTACK = re.compile(
    rf"(?P<name>[A-Z][A-Za-z’' -]{{0,60}})\.\s+(?P<kind>Melee|Ranged) Attack Roll:\s*(?P<bonus>[+-]?\d+),\s*"
    rf"(?:(?:reach\s+(?P<reach>\d+)\s*(?:ft\.?|feet))|(?:range\s+(?P<normal>\d+)\s*/\s*(?P<long>\d+)\s*(?:ft\.?|feet)))\.\s*"
    rf"Hit:\s*\d+\s*\((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<flat>\d+))?\)\s*"
    rf"(?P<type>{_DAMAGE})\s+damage"
    rf"(?:\s+plus\s+\d+\s*\((?P<xcount>\d+)d(?P<xsize>\d+)(?:\s*(?P<xsign>[+-])\s*(?P<xflat>\d+))?\)\s*(?P<xtype>{_DAMAGE})\s+damage)?",
    re.I,
)
_RECHARGE_SAVE = re.compile(
    rf"(?P<name>[A-Z][A-Za-z’' -]{{0,60}})\s*\(Recharge\s+(?P<minimum>\d)(?:\s*[-–]\s*(?P<maximum>\d))?\)\.\s*"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+Saving Throw:\s*DC\s*(?P<dc>\d+),\s*"
    rf"each creature in a\s+(?:(?P<cone>\d+)-foot Cone|(?P<line>\d+)-foot-long,\s*(?P<width>\d+)-foot-wide Line)\.\s*"
    rf"Failure:\s*\d+\s*\((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<flat>\d+))?\)\s*(?P<type>{_DAMAGE})\s+damage\.\s*"
    rf"Success:\s*Half damage",
    re.I,
)


def _bonus(sign: str | None, value: str | None) -> int:
    if value is None:
        return 0
    return int(value) * (-1 if sign == "-" else 1)


def parse_single_attack(row: dict[str, object]) -> dict[str, object]:
    matches = list(_ATTACK.finditer(str(row.get("actions", ""))))
    if len(matches) != 1:
        raise ValueError(f"Simple family requires exactly one attack roll for {row['name']!r}; found {len(matches)}.")
    match = matches[0]; name = match.group("name").strip(); monster_id = f"srd-{slug(str(row['name']))}"
    attack_id = f"{monster_id}-{slug(name)}"; kind = match.group("kind").lower()
    attack: dict[str, object] = {
        "id": attack_id, "name": name, "weapon_id": f"{attack_id}-weapon", "attack_kind": kind,
        "attack_bonus": int(match.group("bonus")),
        "damage": {"count": int(match.group("count")), "size": int(match.group("size")),
                   "bonus": _bonus(match.group("sign"), match.group("flat"))},
        "damage_type": match.group("type").lower(), "animation": "projectile" if kind == "ranged" else ("bite" if name.lower() == "bite" else "slash"),
    }
    if kind == "melee":
        attack["reach_ft"] = int(match.group("reach"))
    else:
        attack.update(normal_range_ft=int(match.group("normal")), long_range_ft=int(match.group("long")))
    if match.group("xtype"):
        attack["effects"] = [{
            "kind": "damage", "source": f"{row['name']} {match.group('xtype').title()}",
            "dice": {"count": int(match.group("xcount")), "size": int(match.group("xsize")),
                     "bonus": _bonus(match.group("xsign"), match.group("xflat"))},
            "damage_type": match.group("xtype").lower(),
        }]
    return attack


def parse_single_recharge_save(row: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    matches = list(_RECHARGE_SAVE.finditer(str(row.get("actions", ""))))
    if len(matches) != 1:
        raise ValueError(f"Recharge family requires exactly one area save for {row['name']!r}; found {len(matches)}.")
    match = matches[0]; name = match.group("name").strip(); monster_id = f"srd-{slug(str(row['name']))}"
    action_id = f"{monster_id}-{slug(name)}"; resource_id = f"{action_id}-recharge"
    length = int(match.group("cone") or match.group("line")); width = int(match.group("width") or length)
    area_slots = max(1, min(6, width // 5))
    action = {
        "id": action_id, "name": name, "save_ability": match.group("ability").lower(), "dc": int(match.group("dc")),
        "range_ft": length, "damage": {"count": int(match.group("count")), "size": int(match.group("size")),
        "bonus": _bonus(match.group("sign"), match.group("flat"))}, "damage_type": match.group("type").lower(),
        "success_damage": "half", "resource_id": resource_id, "area_slots": area_slots, "priority": 100, "animation": "breath",
    }
    resource = {"id": resource_id, "name": name, "max_uses": 1, "recharge_min_d6": int(match.group("minimum"))}
    return action, resource


def parse_uniform_multiattack_count(row: dict[str, object], attack_name: str) -> int:
    actions = str(row.get("actions", ""))
    pattern = re.compile(
        rf"\bMultiattack\.\s+The [^.]+? makes (?P<count>one|two|three|four|five|six|\d+)\s+{re.escape(attack_name)}\s+attacks?\b",
        re.I,
    )
    match = pattern.search(actions)
    if match is None:
        raise ValueError(f"Simple family could not parse Multiattack for {row['name']!r} using {attack_name!r}.")
    value = match.group("count").lower()
    return _NUMBER.get(value, int(value) if value.isdigit() else 0)
