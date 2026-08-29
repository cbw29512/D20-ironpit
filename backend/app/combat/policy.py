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


def weapon_attack_profiles(state: CombatantState) -> list[WeaponAttack]:
    return [state.template.weapon_attack, *state.template.alternate_weapon_attacks]


def select_allowed_weapon_attack(
    state: CombatantState,
    distance_ft: int,
    allowed_ids: list[str],
) -> WeaponAttack | None:
    """Choose the first listed attack that is both allowed for this slot and legal at range."""
    try:
        allowed = set(allowed_ids)
        for attack in weapon_attack_profiles(state):
            if attack.id not in allowed:
                continue
            try:
                resolve_attack_roll_mode(attack.weapon, distance_ft)
                return attack
            except ValueError:
                continue
        return None
    except Exception as exc:
        logger.exception("Failed to select allowed attack for %s.", state.template.name)
        raise RuntimeError("Allowed attack selection could not be evaluated.") from exc


def select_weapon_attack(state: CombatantState, distance_ft: int) -> WeaponAttack | None:
    """Use a melee option when engaged; otherwise preserve the card's attack priority."""
    profiles = weapon_attack_profiles(state)
    melee_ids = [
        attack.id
        for attack in profiles
        if attack.weapon.attack_kind is WeaponAttackKind.MELEE
        and distance_ft <= attack.weapon.reach_ft
    ]
    if melee_ids:
        return select_allowed_weapon_attack(state, distance_ft, melee_ids)
    return select_allowed_weapon_attack(state, distance_ft, [attack.id for attack in profiles])


def preferred_distance_for_attacks(state: CombatantState, allowed_ids: list[str]) -> int:
    """Use the first allowed profile's melee reach or normal ranged distance as approach range."""
    try:
        allowed = set(allowed_ids)
        attack = next(profile for profile in weapon_attack_profiles(state) if profile.id in allowed)
        weapon = attack.weapon
        if weapon.attack_kind is WeaponAttackKind.MELEE:
            return weapon.reach_ft
        if weapon.normal_range_ft is None:
            raise ValueError("Allowed ranged weapon has no normal range.")
        return weapon.normal_range_ft
    except Exception as exc:
        logger.exception("Failed to choose allowed approach distance for %s.", state.template.name)
        raise RuntimeError("Allowed approach policy could not be evaluated.") from exc


def preferred_approach_distance(state: CombatantState) -> int:
    """Close to the primary attack's melee reach or normal ranged distance."""
    return preferred_distance_for_attacks(state, [state.template.weapon_attack.id])
