from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def _advantage_modifier_matches(effect, actions: str) -> bool:
    if effect.consume_on_attack_against is not True or effect.expires_at_start_of_source_turn is not True:
        return False
    if effect.flat_bonus or effect.expires_at_end_of_target_turn:
        return False
    pattern = r"next\s+attack\s+roll\s+made\s+against\s+the\s+target\s+before\s+the\s+start\s+of\s+the\s+[^.]+?[’']s\s+next\s+turn\s+has\s+advantage"
    return bool(re.search(pattern, actions, re.IGNORECASE))


def _speed_modifier_matches(effect, actions: str) -> bool:
    if effect.flat_bonus >= 0 or effect.consume_on_attack_against or effect.expires_at_start_of_source_turn:
        return False
    if effect.expires_at_end_of_target_turn is not True:
        return False
    amount = abs(effect.flat_bonus)
    pattern = rf"speed\s+decreases\s+by\s+{amount}\s+(?:feet|ft\.?)\s+until\s+the\s+end\s+of\s+its\s+next\s+turn"
    return bool(re.search(pattern, actions, re.IGNORECASE))


def hit_modifier_issues(attack: WeaponAttack, actions: str) -> list[str]:
    issues: list[str] = []
    for effect in attack.on_hit_modifier_effects:
        if effect.kind == "attacks-against-advantage":
            matched = _advantage_modifier_matches(effect, actions)
        elif effect.kind == "speed":
            matched = _speed_modifier_matches(effect, actions)
        else:
            issues.append(f"unsupported-hit-modifier:{attack.id}:{effect.kind}")
            continue
        if not matched:
            issues.append(f"hit-modifier-mismatch:{attack.id}:{effect.kind}")
    return issues
