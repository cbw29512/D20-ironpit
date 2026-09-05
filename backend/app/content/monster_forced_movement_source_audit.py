from __future__ import annotations

import re

from app.domain.models import WeaponAttack
from app.domain.size import CreatureSize

_SIZE = {item.value: item for item in CreatureSize}


def _attack_segment(attack: WeaponAttack, actions: str) -> str:
    name = re.escape(attack.weapon.name.lower())
    match = re.search(
        rf"\b{name}\.\s+(.*?)(?=\b[a-z][a-z ’'\-]{{1,40}}\.\s+(?:(?:melee|ranged|melee or ranged)\s+attack roll:|(?:strength|dexterity|constitution|intelligence|wisdom|charisma)\s+saving throw:)|$)",
        actions,
        re.IGNORECASE | re.DOTALL,
    )
    return match.group(1) if match else ""


def _source_effect(attack: WeaponAttack, actions: str) -> tuple[str, int, CreatureSize | None] | None:
    segment = _attack_segment(attack, actions)
    conditional = re.search(
        r"if the target is a?\s*(tiny|small|medium|large|huge|gargantuan) or smaller creature,\s+"
        r"the [a-z][a-z -]* (pushes|pulls) the target up to (\d+) feet straight (away from|toward) itself",
        segment,
        re.IGNORECASE,
    )
    if conditional:
        direction = "push" if conditional.group(2).lower().startswith("push") else "pull"
        relation = conditional.group(4).lower()
        if (direction == "push") != relation.startswith("away"):
            raise ValueError(f"Forced movement direction grammar disagrees for {attack.id}.")
        return direction, int(conditional.group(3)), _SIZE[conditional.group(1).lower()]
    passive = re.search(
        r"\bthe target is (pushed|pulled) up to (\d+) feet straight (away from|toward) the [a-z][a-z -]*",
        segment,
        re.IGNORECASE,
    )
    if not passive:
        return None
    direction = "push" if passive.group(1).lower().startswith("push") else "pull"
    relation = passive.group(3).lower()
    if (direction == "push") != relation.startswith("away"):
        raise ValueError(f"Forced movement direction grammar disagrees for {attack.id}.")
    return direction, int(passive.group(2)), None


def forced_movement_issues(attack: WeaponAttack, actions: str) -> list[str]:
    expected = _source_effect(attack, actions)
    actual = attack.forced_movement
    if expected is None and actual is None:
        return []
    if expected is None:
        return [f"forced-movement-source-missing:{attack.id}"]
    if actual is None:
        return [f"forced-movement-runtime-missing:{attack.id}"]
    if (actual.direction, actual.distance_ft, actual.max_target_size) != expected:
        return [f"forced-movement-mismatch:{attack.id}"]
    return []
