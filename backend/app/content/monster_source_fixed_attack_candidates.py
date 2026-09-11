from __future__ import annotations

import re

from app.content.monster_source_attack_riders import parse_attack_riders
from app.content.monster_source_charge_riders import parse_charge_replacement
from app.domain.capability_attacks import AttackCapabilityDefinition
from app.domain.weapons import DamageType, WeaponAttackKind

_FIXED_ATTACK = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+(?P<kind>Melee|Ranged|Melee or Ranged) Attack Roll:\s*"
    r"(?P<bonus>[+-]?\d+),\s*(?P<range>reach\s+\d+\s*ft\.|range\s+\d+(?:/\d+)?\s*ft\.)\s*"
    r"Hit:\s*(?P<fixed>\d+)\s+(?P<dtype>[A-Za-z]+) damage(?P<tail>[^.]*)\.", re.I,
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def source_fixed_attack_candidates(row: dict[str, object], actions: str) -> list[AttackCapabilityDefinition]:
    attacks: list[AttackCapabilityDefinition] = []
    for match in _FIXED_ATTACK.finditer(actions):
        name = match.group("name").strip()
        reach = re.search(r"reach\s+(\d+)", match.group("range"), re.I)
        ranged = re.search(r"range\s+(\d+)(?:/(\d+))?", match.group("range"), re.I)
        attack_id = f"srd-{_slug(str(row['name']))}-{_slug(name)}"
        rider_text = match.group("tail") or ""
        attacks.append(AttackCapabilityDefinition(
            id=attack_id, name=name, weapon_id=f"{attack_id}-weapon",
            attack_kind=WeaponAttackKind(match.group("kind").lower().replace(" ", "_")),
            attack_bonus=int(match.group("bonus")), fixed_damage=int(match.group("fixed")),
            damage_type=DamageType(match.group("dtype").lower()), animation="strike",
            reach_ft=int(reach.group(1)) if reach else 5,
            normal_range_ft=int(ranged.group(1)) if ranged else None,
            long_range_ft=int(ranged.group(2) or ranged.group(1)) if ranged else None,
            effects=parse_attack_riders(rider_text), charge_profile=parse_charge_replacement(rider_text),
        ))
    return attacks


__all__ = ["source_fixed_attack_candidates"]