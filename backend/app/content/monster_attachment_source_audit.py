from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def attachment_issues(attack: WeaponAttack, actions: str) -> list[str]:
    rule = attack.attachment_on_hit
    if rule is None:
        return []
    issues: list[str] = []
    if not re.search(r"attaches\s+to\s+the\s+target", actions, re.IGNORECASE):
        issues.append(f"attachment-rider-mismatch:{attack.id}")
    if attack.id in rule.forbids_source_attack_ids:
        pattern = rf"can(?:not|'t|’t)\s+make\s+{re.escape(attack.weapon.name)}\s+attacks"
        if not re.search(pattern, actions, re.IGNORECASE):
            issues.append(f"attachment-attack-lockout-mismatch:{attack.id}")
    dice = rf"{rule.periodic_damage_count}\s*d\s*{rule.periodic_damage_size}"
    periodic = (
        rf"\(\s*{dice}\s*\)\s+{re.escape(rule.periodic_damage_type.value)}\s+damage\s+"
        r"at\s+the\s+start\s+of\s+each\s+of\s+the\s+[^.]+?[’']s\s+turns"
    )
    if not re.search(periodic, actions, re.IGNORECASE):
        issues.append(f"attachment-periodic-damage-mismatch:{attack.id}")
    movement = rule.detachable_by_source_movement_ft
    if movement is not None:
        pattern = rf"detach\s+itself\s+by\s+spending\s+{movement}\s+(?:feet|ft\.?)\s+of\s+its\s+movement"
        if not re.search(pattern, actions, re.IGNORECASE):
            issues.append(f"attachment-source-detach-mismatch:{attack.id}")
    if rule.detachable_by_target_action:
        if not re.search(r"target[^.]+can\s+detach[^.]+as\s+an\s+action", actions, re.IGNORECASE):
            issues.append(f"attachment-target-detach-mismatch:{attack.id}")
    if rule.detachable_by_adjacent_action:
        if not re.search(r"creature\s+within\s+5\s+(?:feet|ft\.?)\s+of\s+it\s+can\s+detach[^.]+as\s+an\s+action", actions, re.IGNORECASE):
            issues.append(f"attachment-adjacent-detach-mismatch:{attack.id}")
    return issues
