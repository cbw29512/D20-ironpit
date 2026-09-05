from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def _attack_segment(attack: WeaponAttack, actions: str) -> str:
    name = re.escape(attack.weapon.name.lower())
    match = re.search(
        rf"\b{name}\.\s+(.*?)(?=\b[a-z][a-z ’'\-]{{1,40}}\.\s+(?:(?:melee|ranged|melee or ranged)\s+attack roll:|(?:strength|dexterity|constitution|intelligence|wisdom|charisma)\s+saving throw:)|$)",
        actions,
        re.IGNORECASE | re.DOTALL,
    )
    return match.group(1) if match else ""


def _advantage_modifier_matches(effect, segment: str) -> bool:
    if effect.consume_on_attack_against is not True or effect.expires_at_start_of_source_turn is not True:
        return False
    if effect.flat_bonus or effect.expires_at_end_of_target_turn:
        return False
    pattern = r"next\s+attack\s+roll\s+made\s+against\s+the\s+target\s+before\s+the\s+start\s+of\s+the\s+[^.]+?[’']s\s+next\s+turn\s+has\s+advantage"
    return bool(re.search(pattern, segment, re.IGNORECASE))


def _next_attack_disadvantage_matches(effect, segment: str) -> bool:
    if effect.flat_bonus or effect.consume_on_attack_against or effect.expires_at_start_of_source_turn:
        return False
    if effect.expires_at_end_of_target_turn is not True:
        return False
    return bool(re.search(
        r"target\s+has\s+disadvantage\s+on\s+the\s+next\s+attack\s+roll\s+it\s+makes\s+before\s+the\s+end\s+of\s+its\s+next\s+turn",
        segment,
        re.IGNORECASE,
    ))


def _speed_modifier_matches(effect, segment: str) -> bool:
    if effect.flat_bonus >= 0 or effect.consume_on_attack_against or effect.expires_at_start_of_source_turn:
        return False
    if effect.expires_at_end_of_target_turn is not True:
        return False
    amount = abs(effect.flat_bonus)
    pattern = rf"speed\s+decreases\s+by\s+{amount}\s+(?:feet|ft\.?)\s+until\s+the\s+end\s+of\s+its\s+next\s+turn"
    return bool(re.search(pattern, segment, re.IGNORECASE))


def hit_modifier_issues(attack: WeaponAttack, actions: str) -> list[str]:
    issues: list[str] = []
    segment = _attack_segment(attack, actions)
    source_next_disadvantage = bool(re.search(
        r"target\s+has\s+disadvantage\s+on\s+the\s+next\s+attack\s+roll\s+it\s+makes\s+before\s+the\s+end\s+of\s+its\s+next\s+turn",
        segment,
        re.IGNORECASE,
    ))
    runtime_next_disadvantage = any(effect.kind == "next-attack-disadvantage" for effect in attack.on_hit_modifier_effects)
    if source_next_disadvantage and not runtime_next_disadvantage:
        issues.append(f"hit-modifier-runtime-missing:{attack.id}:next-attack-disadvantage")
    for effect in attack.on_hit_modifier_effects:
        if effect.kind == "attacks-against-advantage":
            matched = _advantage_modifier_matches(effect, segment)
        elif effect.kind == "next-attack-disadvantage":
            matched = _next_attack_disadvantage_matches(effect, segment)
        elif effect.kind == "speed":
            matched = _speed_modifier_matches(effect, segment)
        else:
            issues.append(f"unsupported-hit-modifier:{attack.id}:{effect.kind}")
            continue
        if not matched:
            issues.append(f"hit-modifier-mismatch:{attack.id}:{effect.kind}")
    return issues
