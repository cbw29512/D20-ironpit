from __future__ import annotations

import re

from app.content.monster_combat_scope import feature_blocks
from app.content.monster_trait_source_audit import parse_trait_names

_NUMBER = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
_ATTACK = re.compile(
    r"\b(Melee|Ranged) Attack Roll:\s*([+-]?\d+),\s*"
    r"(?:(?:reach\s+(\d+)\s*ft\.)|(?:range\s+(\d+)\s*/\s*(\d+)\s*ft\.))\s*"
    r"Hit:\s*\d+\s*\(\s*(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\s*\)\s*([A-Za-z]+)\s+damage",
    re.I,
)
_EXTRA_DICE = re.compile(
    r"\bplus\s+\d+\s*\(\s*(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\s*\)\s*([A-Za-z]+)\s+damage",
    re.I,
)
_EXTRA_FIXED = re.compile(r"\bplus\s+(\d+)\s+([A-Za-z]+)\s+damage\b", re.I)
_NEXT_ATTACK_DISADVANTAGE = re.compile(
    r"(?:has|gains?)\s+Disadvantage\s+on\s+(?:the|its)\s+next\s+attack\s+roll"
    r"(?:\s+it\s+makes)?\s+before\s+the\s+end\s+of\s+its\s+next\s+turn",
    re.I,
)
_COUNT = r"one|two|three|four|five|six|\d+"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _number(value: str) -> int:
    return _NUMBER.get(value.lower(), int(value) if value.isdigit() else 0)


def _dice(count: str, size: str, sign: str | None, bonus: str | None) -> dict[str, int]:
    amount = int(bonus or 0) * (-1 if sign == "-" else 1)
    return {"count": int(count), "size": int(size), "bonus": amount}


def parse_simple_attacks(row: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object] | None]:
    """Parse ordinary attack-roll stat blocks; reject any unrecognized attack shape."""
    source = str(row.get("actions", ""))
    headings = parse_trait_names(source, preserve_annotations=True)
    blocks = feature_blocks(source, headings)
    monster_slug = _slug(str(row["name"]))
    attacks: list[dict[str, object]] = []
    by_name: dict[str, str] = {}
    for heading, block in blocks.items():
        if "Attack Roll:" not in block:
            continue
        match = _ATTACK.search(block)
        if match is None or "Melee or Ranged Attack Roll:" in block:
            raise ValueError(f"Simple attack parser cannot prove {row['name']} {heading!r}: {block!r}")
        kind, bonus, reach, normal, long, count, size, sign, damage_bonus, damage_type = match.groups()
        attack_id = f"srd-{monster_slug}-{_slug(heading)}"
        effects: list[dict[str, object]] = []
        for extra in _EXTRA_DICE.finditer(block):
            e_count, e_size, e_sign, e_bonus, e_type = extra.groups()
            effects.append({"kind": "damage", "source": heading, "dice": _dice(e_count, e_size, e_sign, e_bonus), "damage_type": e_type.lower()})
        dice_spans = [match.span(), *[item.span() for item in _EXTRA_DICE.finditer(block)]]
        for extra in _EXTRA_FIXED.finditer(block):
            if any(start <= extra.start() < end for start, end in dice_spans):
                continue
            amount, e_type = extra.groups()
            effects.append({"kind": "damage", "source": heading, "dice": {"count": 0, "size": 6, "bonus": int(amount)}, "damage_type": e_type.lower()})
        if _NEXT_ATTACK_DISADVANTAGE.search(block):
            effects.append({"kind": "next-attack-disadvantage", "expires_at_end_of_target_turn": True})
        attack = {
            "id": attack_id, "name": heading, "weapon_id": f"{attack_id}-weapon",
            "attack_kind": kind.lower(), "attack_bonus": int(bonus),
            "damage": _dice(count, size, sign, damage_bonus), "damage_type": damage_type.lower(),
            "animation": "projectile" if kind.lower() == "ranged" else "strike",
            "reach_ft": int(reach or 5), "effects": effects,
        }
        if normal:
            attack.update({"normal_range_ft": int(normal), "long_range_ft": int(long), "projectile": _slug(heading)})
        attacks.append(attack)
        by_name[heading] = attack_id
    if not attacks:
        raise ValueError(f"No ordinary attacks parsed for {row['name']!r}.")
    return attacks, _parse_multiattack(row, blocks.get("Multiattack"), by_name)


def _parse_multiattack(row: dict[str, object], source: str | None, by_name: dict[str, str]) -> dict[str, object] | None:
    if source is None:
        return None
    declared = re.search(rf"\bmakes\s+({_COUNT})\s+attacks?\b", source, re.I)
    choice = re.search(r"\busing\s+(.+?)\s+in\s+any\s+combination\b", source, re.I)
    slots: list[dict[str, list[str]]] = []
    if choice:
        if declared is None:
            raise ValueError(f"Unrecognized Multiattack count for {row['name']!r}: {source!r}")
        total = _number(declared.group(1))
        names = [item.strip() for item in re.split(r"\s+or\s+|,", choice.group(1)) if item.strip()]
        ids = [by_name[name] for name in names if name in by_name]
        if len(ids) != len(names):
            raise ValueError(f"Multiattack references an unknown attack for {row['name']!r}.")
        slots = [{"attack_ids": ids} for _ in range(total)]
    else:
        parts = re.findall(rf"\b({_COUNT})\s+([A-Z][A-Za-z’'\-]*(?:\s+[A-Z][A-Za-z’'\-]*)?)(?=\s+(?:attacks?\b|and\b|,|$))", source)
        for count, name in parts:
            if name not in by_name:
                continue
            slots.extend({"attack_ids": [by_name[name]]} for _ in range(_number(count)))
        total = _number(declared.group(1)) if declared is not None else sum(_number(count) for count, name in parts if name in by_name)
        if not total or len(slots) != total:
            raise ValueError(f"Unrecognized fixed Multiattack sequence for {row['name']!r}: {source!r}")
    return {"id": f"srd-{_slug(str(row['name']))}-multiattack", "name": "Multiattack", "is_attack_action": False, "slots": slots}
