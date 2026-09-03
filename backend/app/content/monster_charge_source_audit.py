from __future__ import annotations

import re

from app.combat.charge import charge_profile_for_attack_id
from app.domain.models import CombatantTemplate


def _dice_text(count: int, size: int, bonus: int) -> str:
    base = rf"{count}\s*d\s*{size}"
    if bonus == 0:
        return base + r"(?:\s*\+\s*0)?"
    sign = r"\+" if bonus > 0 else "-"
    return base + rf"\s*{sign}\s*{abs(bonus)}"


def charge_replacement_issues(template: CombatantTemplate, actions: str) -> list[str]:
    issues: list[str] = []
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    for attack in attacks:
        profile = charge_profile_for_attack_id(attack.id)
        replacement = profile.replacement_damage if profile else None
        if profile is None or replacement is None:
            continue
        dice = _dice_text(replacement.dice_count, replacement.dice_size, replacement.damage_bonus)
        pattern = re.compile(
            rf"\bor\s+\d+\s*\(\s*{dice}\s*\)\s+{replacement.damage_type.value}\s+damage\s+"
            rf"if\s+the\s+[^.]+?\s+moved\s+{profile.minimum_move_ft}\+\s*feet\s+straight\s+toward\s+the\s+target\s+"
            r"immediately\s+before\s+the\s+hit",
            re.IGNORECASE,
        )
        if not pattern.search(actions):
            issues.append(f"charge-replacement-mismatch:{attack.id}")
    return issues
