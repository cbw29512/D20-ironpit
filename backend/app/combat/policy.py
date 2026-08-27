from __future__ import annotations

import logging

from app.combat.range import resolve_attack_roll_mode
from app.domain.models import CombatantState, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def should_use_second_wind(state: CombatantState) -> bool:
    """Arena tactic: spend Second Wind at or below half HP when a use and Bonus Action remain."""
    try:
        resource = next((item for item in state.resources if item.id == "second-wind"), None)
        return bool(
            resource
            and resource.current_uses > 0
            and state.bonus_action_available
            and 0 < state.current_hp <= state.template.max_hp // 2
        )
    except Exception as exc:
        logger.exception("Failed to evaluate Second Wind policy for %s.", state.template.name)
        raise RuntimeError("Second Wind policy could not be evaluated.") from exc


def should_use_action_surge(state: CombatantState) -> bool:
    """Arena tactic: spend Action Surge after the normal action if a use remains."""
    try:
        resource = next((item for item in state.resources if item.id == "action-surge"), None)
        return bool(
            resource
            and resource.current_uses > 0
            and not state.action_available
            and not state.action_surge_used_this_turn
            and state.is_alive
        )
    except Exception as exc:
        logger.exception("Failed to evaluate Action Surge policy for %s.", state.template.name)
        raise RuntimeError("Action Surge policy could not be evaluated.") from exc


def attack_uses_melee(attack: WeaponAttack, distance_ft: int) -> bool:
    weapon = attack.weapon
    return weapon.attack_kind is WeaponAttackKind.MELEE or (
        weapon.attack_kind is WeaponAttackKind.THROWN and distance_ft <= weapon.reach_ft
    )


def _legal_attack(attack: WeaponAttack, distance_ft: int) -> bool:
    try:
        resolve_attack_roll_mode(attack.weapon, distance_ft)
        return True
    except ValueError:
        return False


def select_weapon_attack(state: CombatantState, distance_ft: int) -> WeaponAttack | None:
    """Prefer a legal melee use once engaged; otherwise use the first legal profile."""
    try:
        profiles = [state.template.weapon_attack, *state.template.alternate_weapon_attacks]
        legal = [attack for attack in profiles if _legal_attack(attack, distance_ft)]
        melee = [attack for attack in legal if attack_uses_melee(attack, distance_ft)]
        return (melee or legal or [None])[0]
    except Exception as exc:
        logger.exception("Failed to select attack profile for %s.", state.template.name)
        raise RuntimeError("Attack selection policy could not be evaluated.") from exc


def preferred_approach_distance(state: CombatantState) -> int:
    """Close toward the first melee-capable profile; pure ranged combatants close to normal range."""
    try:
        profiles = [state.template.weapon_attack, *state.template.alternate_weapon_attacks]
        for attack in profiles:
            if attack.weapon.attack_kind in {WeaponAttackKind.MELEE, WeaponAttackKind.THROWN}:
                return attack.weapon.reach_ft

        weapon = state.template.weapon_attack.weapon
        if weapon.normal_range_ft is None:
            raise ValueError("Primary ranged weapon has no normal range.")
        return weapon.normal_range_ft
    except Exception as exc:
        logger.exception("Failed to choose approach distance for %s.", state.template.name)
        raise RuntimeError("Approach policy could not be evaluated.") from exc
