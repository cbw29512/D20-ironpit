from __future__ import annotations

import logging

from app.combat.bloodied import is_bloodied
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
            and state.current_hp > 0
            and is_bloodied(state)
        )
    except Exception as exc:
        logger.exception("Failed to evaluate Second Wind policy for %s.", state.template.name)
        raise RuntimeError("Second Wind policy could not be evaluated.") from exc


def weapon_attack_profiles(state: CombatantState) -> list[WeaponAttack]:
    return [state.template.weapon_attack, *state.template.alternate_weapon_attacks]


def _legal_attack(attack: WeaponAttack, distance_ft: int) -> bool:
    try:
        resolve_attack_roll_mode(attack.weapon, distance_ft)
        return True
    except ValueError:
        return False


def select_allowed_weapon_attack(
    state: CombatantState,
    distance_ft: int,
    allowed_ids: list[str],
) -> WeaponAttack | None:
    """Prefer legal melee while engaged; otherwise use the first legal allowed profile."""
    try:
        allowed = set(allowed_ids)
        profiles = [attack for attack in weapon_attack_profiles(state) if attack.id in allowed]
        melee = next((
            attack for attack in profiles
            if attack.weapon.attack_kind is WeaponAttackKind.MELEE and _legal_attack(attack, distance_ft)
        ), None)
        if melee is not None:
            return melee
        return next((attack for attack in profiles if _legal_attack(attack, distance_ft)), None)
    except Exception as exc:
        logger.exception("Failed to select allowed attack for %s.", state.template.name)
        raise RuntimeError("Allowed attack selection could not be evaluated.") from exc


def select_weapon_attack(state: CombatantState, distance_ft: int) -> WeaponAttack | None:
    """Use a melee option when engaged; otherwise preserve the card's attack priority."""
    return select_allowed_weapon_attack(
        state,
        distance_ft,
        [attack.id for attack in weapon_attack_profiles(state)],
    )


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
