from __future__ import annotations
import re
from typing import Any
from app.content.monster_ability_reduction_source_audit import ability_reduction_issues
from app.content.monster_attachment_source_audit import attachment_issues
from app.content.monster_attack_advantage_source_audit import conditional_attack_advantage_issues
from app.content.monster_attack_modifier_source_audit import hit_modifier_issues
from app.content.monster_forced_movement_source_audit import forced_movement_issues
from app.content.monster_grapple_source_audit import grapple_issues
from app.content.monster_save_action_source_audit import save_action_issues
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
    else:
        trigger = r"if\s+the\s+(?!target\b)[a-z][a-z -]*\s+is\s+bloodied"
    return re.compile(
        rf"\b{connective}\s+\d+\s*\(\s*{dice}\s*\)\s+{conditional.damage_type.value}\s+damage\s+{trigger}",
        re.IGNORECASE,
    )


def _melee_reach_pattern(reach_ft: int) -> re.Pattern[str]:
    return re.compile(rf"\breach\s+{reach_ft}\s*(?:ft\.?|feet)\b", re.IGNORECASE)


def _ranged_pattern(normal_ft: int, long_ft: int) -> re.Pattern[str]:
    return re.compile(rf"\brange\s+{normal_ft}\s*/\s*{long_ft}\s*(?:ft\.?|feet)\b", re.IGNORECASE)


def _max_size_rider_present(actions: str, size: Any, condition: str) -> bool:
    size_name = getattr(size, "value", size)
    return bool(
        re.search(rf"\b{re.escape(str(size_name))}\s+or\s+smaller\b", actions, re.IGNORECASE)
        and condition.lower() in actions
    )


def _condition_timing_present(actions: str, control: Any) -> bool:
    condition = control.condition_id
    if condition is None:
        return True
    if not re.search(rf"\b{re.escape(condition)}\s+condition\b", actions, re.IGNORECASE):
        return False
    timing = control.expiry_timing
    if timing is None and control.expires_at_start_of_source_turn:
        timing = "source_turn_start"
    target = {
        "target_turn_start": r"until\s+the\s+start\s+of\s+its\s+next\s+turn",
        "target_turn_end": r"until\s+the\s+end\s+of\s+its\s+next\s+turn",
    }.get(timing)
    if target:
        return bool(re.search(target, actions, re.IGNORECASE))
    source = {"source_turn_start": "start", "source_turn_end": "end"}.get(timing)
    if source:
        pattern = rf"until\s+the\s+{source}\s+of\s+the\s+[^.]+?[’']s\s+next\s+turn"
        return bool(re.search(pattern, actions, re.IGNORECASE))
    return True


def _max_hp_reduction_present(actions: str, rider: Any) -> bool:
    damage = r"damage"
    if rider.damage_type is not None:
        damage = rf"{re.escape(rider.damage_type.value)}\s+damage"
    pattern = rf"hit\s+point\s+maximum\s+decreases\s+by\s+an\s+amount\s+equal\s+to\s+the\s+{damage}\s+taken"
    return bool(re.search(pattern, actions, re.IGNORECASE))


def attack_issues(attack: WeaponAttack, actions: str, traits: str = "") -> list[str]:
    issues: list[str] = []
    weapon = attack.weapon
    if weapon.name.lower() not in actions:
        issues.append(f"attack-name-missing:{attack.id}")
    if not re.search(rf"Attack Roll:\s*\+?{attack.attack_bonus}\b", actions, re.IGNORECASE):
        issues.append(f"attack-bonus-mismatch:{attack.id}")
    deals_damage = attack.fixed_damage is not None or weapon.dice_count > 0
    if attack.fixed_damage is not None:
        if not re.search(rf"Hit:\s*{attack.fixed_damage}\b", actions, re.IGNORECASE):
            issues.append(f"fixed-damage-mismatch:{attack.id}")
    elif weapon.dice_count > 0 and not _dice_pattern(weapon.dice_count, weapon.dice_size, attack.damage_bonus).search(actions):
        issues.append(f"damage-dice-mismatch:{attack.id}")
    if deals_damage and weapon.damage_type.value.lower() not in actions:
        issues.append(f"damage-type-missing:{attack.id}")
    kind = weapon.attack_kind.value
    if kind in {"melee", "melee_or_ranged"} and not _melee_reach_pattern(weapon.reach_ft).search(actions):
        issues.append(f"melee-reach-mismatch:{attack.id}")
    if kind in {"ranged", "melee_or_ranged"} and weapon.normal_range_ft is not None:
        if not _ranged_pattern(weapon.normal_range_ft, weapon.long_range_ft).search(actions):
            issues.append(f"ranged-range-mismatch:{attack.id}")
    if kind == "melee_or_ranged" and not re.search(r"Melee\s+or\s+Ranged\s+Attack\s+Roll", actions, re.IGNORECASE):
        issues.append(f"hybrid-attack-kind-mismatch:{attack.id}")
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
    if attack.max_hp_reduction_on_hit is not None and not _max_hp_reduction_present(actions, attack.max_hp_reduction_on_hit):
        issues.append(f"max-hp-reduction-rider-mismatch:{attack.id}")
    issues.extend(ability_reduction_issues(attack, actions))
    issues.extend(attachment_issues(attack, actions))
    issues.extend(hit_modifier_issues(attack, actions))
    issues.extend(conditional_attack_advantage_issues(attack, actions, traits))
    issues.extend(forced_movement_issues(attack, actions))
    issues.extend(grapple_issues(attack, actions))
    if attack.knocks_prone_max_size is not None and not _max_size_rider_present(actions, attack.knocks_prone_max_size, "prone"):
        issues.append(f"prone-rider-mismatch:{attack.id}")
    if attack.forbid_target_grappled_by_self:
        untargetable = re.search(r"can(?:not|'t|’t)\s+be\s+targeted", actions, re.IGNORECASE)
        if not untargetable or weapon.name.lower() not in actions:
            issues.append(f"grappled-target-restriction-mismatch:{attack.id}")
    control = attack.control_effect
    if control and control.condition_id is not None and not _condition_timing_present(actions, control):
        issues.append(f"condition-rider-mismatch:{attack.id}:{control.condition_id}")
    return issues
