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


def _source_profile_issues(attack_id: str, profile: object, actions: str) -> list[str]:
    if not attack_id.startswith("srd-"): return []
    issues: list[str] = []
    minimum = getattr(profile, "minimum_move_ft")
    if not re.search(rf"\bmoved\s+{minimum}\+\s*feet\s+straight\s+toward\b", actions, re.I):
        issues.append(f"charge-movement-mismatch:{attack_id}")
    maximum = getattr(profile, "max_target_size")
    if maximum is not None and not re.search(rf"\b{maximum.value}\s+or\s+smaller\b", actions, re.I):
        issues.append(f"charge-size-mismatch:{attack_id}")
    bonus = getattr(profile, "bonus_damage")
    if bonus is not None:
        dice = _dice_text(bonus.dice_count, bonus.dice_size, bonus.damage_bonus)
        if not re.search(rf"\bextra\s+\d+\s*\(\s*{dice}\s*\)\s+{bonus.damage_type.value}\s+damage\b", actions, re.I):
            issues.append(f"charge-bonus-damage-mismatch:{attack_id}")
    prone = getattr(profile, "prone_max_target_size")
    if prone is not None and not re.search(r"\bProne\s+condition\b", actions, re.I):
        issues.append(f"charge-prone-mismatch:{attack_id}")
    return issues


def charge_replacement_issues(template: CombatantTemplate, actions: str) -> list[str]:
    issues: list[str] = []
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    for attack in attacks:
        profile = attack.charge or charge_profile_for_attack_id(attack.id)
        if profile is None: continue
        issues.extend(_source_profile_issues(attack.id, profile, actions))
        replacement = profile.replacement_damage
        if replacement is None: continue
        dice = _dice_text(replacement.dice_count, replacement.dice_size, replacement.damage_bonus)
        pattern = re.compile(
            rf"\bor\s+\d+\s*\(\s*{dice}\s*\)\s+{replacement.damage_type.value}\s+damage\s+"
            rf"if\s+the\s+[^.]+?\s+moved\s+{profile.minimum_move_ft}\+\s*feet\s+straight\s+toward\s+the\s+target\s+"
            r"immediately\s+before\s+the\s+hit",
            re.IGNORECASE,
        )
        if not pattern.search(actions): issues.append(f"charge-replacement-mismatch:{attack.id}")
    return issues
