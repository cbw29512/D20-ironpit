from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def hit_modifier_issues(attack: WeaponAttack, actions: str) -> list[str]:
    issues: list[str] = []
    for effect in attack.on_hit_modifier_effects:
        if effect.kind != "attacks-against-advantage" or not effect.consume_on_attack_against or not effect.expires_at_start_of_source_turn:
            issues.append(f"unsupported-hit-modifier:{attack.id}:{effect.kind}")
            continue
        pattern = r"next\s+attack\s+roll\s+made\s+against\s+the\s+target\s+before\s+the\s+start\s+of\s+the\s+[^.]+?[’']s\s+next\s+turn\s+has\s+advantage"
        if not re.search(pattern, actions, re.IGNORECASE):
            issues.append(f"hit-modifier-mismatch:{attack.id}:{effect.kind}")
    return issues
