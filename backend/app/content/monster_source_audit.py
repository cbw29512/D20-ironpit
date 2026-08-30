from __future__ import annotations

import logging
import re
from typing import Any

from app.domain.models import CombatantTemplate, WeaponAttack

logger = logging.getLogger(__name__)


def _first_int(value: object) -> int:
    match = re.search(r"-?\d+", str(value))
    if not match:
        raise ValueError(f"No integer found in SRD value: {value!r}")
    return int(match.group())


def _initiative(row: dict[str, object]) -> int:
    match = re.search(r"\bInitiative\s+([+-]?\d+)", str(row.get("rawText", "")), re.IGNORECASE)
    if not match:
        raise ValueError(f"SRD initiative could not be parsed for {row.get('name')!r}.")
    return int(match.group(1))


def _challenge(row: dict[str, object]) -> str:
    return str(row["challenge"]).split()[0]


def _normalized(text: object) -> str:
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def _dice_pattern(count: int, size: int, bonus: int) -> re.Pattern[str]:
    base = rf"{count}\s*d\s*{size}"
    if bonus == 0:
        return re.compile(base + r"(?:\s*\+\s*0)?", re.IGNORECASE)
    sign = r"\+" if bonus > 0 else "-"
    return re.compile(base + rf"\s*{sign}\s*{abs(bonus)}", re.IGNORECASE)


def _attack_issues(attack: WeaponAttack, actions: str) -> list[str]:
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
    if weapon.attack_kind.value == "melee" and f"reach {weapon.reach_ft} ft" not in actions:
        issues.append(f"melee-reach-mismatch:{attack.id}")
    if weapon.attack_kind.value == "ranged" and weapon.normal_range_ft is not None:
        ranged = rf"range\s+{weapon.normal_range_ft}\s*/\s*{weapon.long_range_ft}\s*ft"
        if not re.search(ranged, actions, re.IGNORECASE):
            issues.append(f"ranged-range-mismatch:{attack.id}")
    for extra in attack.on_hit_damage:
        if not _dice_pattern(extra.dice_count, extra.dice_size, extra.damage_bonus).search(actions):
            issues.append(f"on-hit-dice-missing:{attack.id}:{extra.source}")
        if extra.damage_type.value.lower() not in actions:
            issues.append(f"on-hit-type-missing:{attack.id}:{extra.source}")
    control = attack.control_effect
    if control and control.grapple_escape_dc is not None:
        if "grappled" not in actions or f"escape dc {control.grapple_escape_dc}" not in actions:
            issues.append(f"grapple-rider-mismatch:{attack.id}")
        if control.restrains_while_grappled and "restrained" not in actions:
            issues.append(f"restrained-rider-mismatch:{attack.id}")
    return issues


def _save_action_issues(action: Any, actions: str) -> list[str]:
    issues: list[str] = []
    if action.name.lower() not in actions:
        issues.append(f"save-action-name-missing:{action.id}")
    save = rf"{action.save_ability}\s+Saving Throw:\s*DC\s*{action.dc}\b"
    if not re.search(save, actions, re.IGNORECASE):
        issues.append(f"save-dc-mismatch:{action.id}")
    if action.damage_dice_count and not _dice_pattern(
        action.damage_dice_count, action.damage_dice_size, action.damage_bonus,
    ).search(actions):
        issues.append(f"save-damage-mismatch:{action.id}")
    if action.grapple_escape_dc is not None:
        if "grappled" not in actions or f"escape dc {action.grapple_escape_dc}" not in actions:
            issues.append(f"save-grapple-rider-mismatch:{action.id}")
    return issues


def audit_monster_source(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Reconcile a RAW-ready runtime monster against its vended SRD 5.2.1 record."""
    try:
        issues: list[str] = []
        checks = (
            (template.name == str(row["name"]), "name-mismatch"),
            (template.size.value.lower() == str(row["size"]).lower(), "size-mismatch"),
            (template.armor_class == _first_int(row["armorClass"]), "armor-class-mismatch"),
            (template.max_hp == _first_int(row["hitPoints"]), "hit-points-mismatch"),
            (template.speed_ft == _first_int(row["speed"]), "speed-mismatch"),
            (template.challenge_rating == _challenge(row), "challenge-rating-mismatch"),
            (template.initiative_bonus == _initiative(row), "initiative-mismatch"),
        )
        issues.extend(label for passed, label in checks if not passed)
        actions = _normalized(row.get("actions", ""))
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]:
            issues.extend(_attack_issues(attack, actions))
        for action in template.saving_throw_actions:
            issues.extend(_save_action_issues(action, actions))
        if template.attack_action is not None and "multiattack" not in actions:
            issues.append("multiattack-source-missing")
        return issues
    except (KeyError, ValueError):
        raise
    except Exception as exc:
        logger.exception("SRD monster reconciliation failed for %s.", template.id)
        raise RuntimeError(f"Monster source audit failed for {template.id}.") from exc
