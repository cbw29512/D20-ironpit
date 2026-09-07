from __future__ import annotations

import re
from typing import Any

from app.content.monster_attack_modifier_source_audit import hit_modifier_issues
from app.content.monster_hit_control_source_audit import hit_control_issues
from app.domain.models import WeaponAttack


def normalized(text: object) -> str:
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def _dice_pattern(count: int, size: int, bonus: int) -> re.Pattern[str]:
    base = rf"{count}\s*d\s*{size}"
    if bonus == 0:
        return re.compile(base + r"(?:\s*\+\s*0)?", re.IGNORECASE)
    sign = r"\+" if bonus > 0 else "-"
    return re.compile(base + rf"\s*{sign}\s*{abs(bonus)}", re.IGNORECASE)


def _dice_text(count: int, size: int, bonus: int) -> str:
    base = rf"{count}\s*d\s*{size}"
    if bonus == 0:
        return base + r"(?:\s*\+\s*0)?"
    sign = r"\+" if bonus > 0 else "-"
    return base + rf"\s*{sign}\s*{abs(bonus)}"


def _conditional_clause_pattern(conditional: Any) -> re.Pattern[str]:
    connective = "plus" if conditional.mode == "add" else "or"
    dice = _dice_text(conditional.dice_count, conditional.dice_size, conditional.damage_bonus)
    if conditional.trigger == "attack_advantage":
        trigger = r"if\s+the\s+attack\s+roll\s+had\s+advantage"
    elif conditional.trigger == "target_bloodied":
        trigger = r"if\s+the\s+target\s+is\s+bloodied"
    elif conditional.trigger == "target_grappled_by_self":
        trigger = r"if\s+the\s+target\s+is\s+grappled\s+by\s+the\s+[a-z][a-z'’ -]*"
    else:
        trigger = r"if\s+the\s+(?!target\b)[a-z][a-z -]*\s+is\s+bloodied"
    return re.compile(
        rf"\b{connective}\s+\d+\s*\(\s*{dice}\s*\)\s+{conditional.damage_type.value}\s+damage\s+{trigger}",
        re.IGNORECASE,
    )


def _melee_reach_pattern(reach_ft: int) -> re.Pattern[str]:
    return re.compile(rf"\breach\s+{reach_ft}\s*(?:ft\.?|feet)\b", re.IGNORECASE)


def _max_size_rider_present(actions: str, size: Any, condition: str) -> bool:
    size_name = getattr(size, "value", size)
    return bool(
        re.search(rf"\b{re.escape(str(size_name))}\s+or\s+smaller\b", actions, re.IGNORECASE)
        and condition.lower() in actions
    )


def _save_condition_timing_present(effect: Any, actions: str) -> bool:
    timing = effect.expiry_timing
    if timing is None: return True
    owner, _, edge = timing.partition("_turn_")
    if edge not in {"start", "end"}: return False
    if owner == "source":
        pattern = rf"until\s+the\s+{edge}\s+of\s+(?!its\b)(?:the\s+)?[^.]+?[’']s\s+next\s+turn"
    elif owner == "target":
        pattern = rf"until\s+the\s+{edge}\s+of\s+(?:its|(?:the\s+)?target[’']s)\s+next\s+turn"
    else:
        return False
    return bool(re.search(pattern, actions, re.IGNORECASE))


def _repeat_save_timing_present(effect: Any, actions: str) -> bool:
    timing = effect.repeat_save_timing
    if timing is None: return True
    owner, _, edge = timing.partition("_turn_")
    if owner != "target" or edge not in {"start", "end"}: return False
    return bool(re.search(rf"repeats?\s+the\s+save\s+at\s+the\s+{edge}\s+of\s+each\s+of\s+its\s+turns", actions, re.IGNORECASE))


def attack_issues(attack: WeaponAttack, actions: str) -> list[str]:
    issues: list[str] = []
    weapon = attack.weapon
    if weapon.name.lower() not in actions:
        issues.append(f"attack-name-missing:{attack.id}")
    if not re.search(rf"Attack Roll:\s*\+?{attack.attack_bonus}\b", actions, re.IGNORECASE):
        issues.append(f"attack-bonus-mismatch:{attack.id}")
    if attack.fixed_damage is not None:
        if not re.search(rf"Hit:\s*{attack.fixed_damage}\b", actions, re.IGNORECASE):
            issues.append(f"fixed-damage-mismatch:{attack.id}")
    elif not _dice_pattern(weapon.dice_count, weapon.dice_size, attack.damage_bonus).search(actions):
        issues.append(f"damage-dice-mismatch:{attack.id}")
    if weapon.damage_type.value.lower() not in actions:
        issues.append(f"damage-type-missing:{attack.id}")
    if weapon.attack_kind.value == "melee" and not _melee_reach_pattern(weapon.reach_ft).search(actions):
        issues.append(f"melee-reach-mismatch:{attack.id}")
    if weapon.attack_kind.value == "ranged" and weapon.normal_range_ft is not None:
        ranged = rf"range\s+{weapon.normal_range_ft}\s*/\s*{weapon.long_range_ft}\s*(?:ft\.?|feet)\b"
        if not re.search(ranged, actions, re.IGNORECASE):
            issues.append(f"ranged-range-mismatch:{attack.id}")
    for extra in attack.on_hit_damage:
        if extra.dice_count == 0:
            fixed = rf"\bplus\s+{extra.damage_bonus}\s+{extra.damage_type.value}\s+damage\b"
            if not re.search(fixed, actions, re.IGNORECASE):
                issues.append(f"on-hit-fixed-missing:{attack.id}:{extra.source}")
        elif not _dice_pattern(extra.dice_count, extra.dice_size, extra.damage_bonus).search(actions):
            issues.append(f"on-hit-dice-missing:{attack.id}:{extra.source}")
        if extra.damage_type.value.lower() not in actions:
            issues.append(f"on-hit-type-missing:{attack.id}:{extra.source}")
    for conditional in attack.conditional_damage:
        if not _conditional_clause_pattern(conditional).search(actions):
            issues.append(f"conditional-damage-mismatch:{attack.id}:{conditional.trigger}")
    issues.extend(hit_modifier_issues(attack, actions))
    if attack.knocks_prone_max_size is not None and not _max_size_rider_present(actions, attack.knocks_prone_max_size, "prone"):
        issues.append(f"prone-rider-mismatch:{attack.id}")
    if attack.forbid_target_grappled_by_self:
        untargetable = re.search(r"can(?:not|'t|’t)\s+be\s+targeted", actions, re.IGNORECASE)
        if not untargetable or weapon.name.lower() not in actions:
            issues.append(f"grappled-target-restriction-mismatch:{attack.id}")
    issues.extend(hit_control_issues(attack, actions))
    return issues


def save_action_issues(action: Any, actions: str) -> list[str]:
    issues: list[str] = []
    if action.name.lower() not in actions:
        issues.append(f"save-action-name-missing:{action.id}")
    save = rf"{action.save_ability}\s+Saving Throw:\s*DC\s*{action.dc}\b"
    if not re.search(save, actions, re.IGNORECASE):
        issues.append(f"save-dc-mismatch:{action.id}")
    if action.damage_dice_count and not _dice_pattern(action.damage_dice_count, action.damage_dice_size, action.damage_bonus).search(actions):
        issues.append(f"save-damage-mismatch:{action.id}")
    if action.grapple_escape_dc is not None:
        if "grappled" not in actions or f"escape dc {action.grapple_escape_dc}" not in actions:
            issues.append(f"save-grapple-rider-mismatch:{action.id}")
    for effect in action.failure_conditions:
        condition = effect.condition_id.lower()
        if not re.search(rf"\b{re.escape(condition)}\s+condition\b", actions, re.IGNORECASE):
            issues.append(f"save-condition-missing:{action.id}:{condition}")
        if not _save_condition_timing_present(effect, actions):
            issues.append(f"save-condition-timing-mismatch:{action.id}:{condition}")
        if not _repeat_save_timing_present(effect, actions):
            issues.append(f"save-repeat-timing-mismatch:{action.id}:{condition}")
    return issues
