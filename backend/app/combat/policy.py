from __future__ import annotations

import logging

from app.combat.range import resolve_attack_roll_mode
from app.combat.stealth import can_hide
from app.domain.models import (
    BattlefieldState,
    CombatantState,
    DuelMode,
    WeaponAttack,
    WeaponAttackKind,
)

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


def should_use_nimble_escape_disengage(state: CombatantState, distance_ft: int) -> bool:
    """Retreat from melee when Nimble Escape and a ranged attack are available."""
    try:
        has_ranged_attack = any(
            attack.weapon.attack_kind is WeaponAttackKind.RANGED
            for attack in state.template.alternate_weapon_attacks
        )
        return bool(
            "nimble-escape" in state.template.bonus_action_features
            and state.bonus_action_available
            and state.movement_remaining_ft > 0
            and distance_ft <= 5
            and has_ranged_attack
        )
    except Exception as exc:
        logger.exception("Failed to evaluate Nimble Escape policy for %s.", state.template.name)
        raise RuntimeError("Nimble Escape policy could not be evaluated.") from exc


def should_use_nimble_escape_hide(
    state: CombatantState,
    battlefield: BattlefieldState,
) -> bool:
    """Hide before attacking when terrain permits and a current attack is legal."""
    try:
        return bool(
            "nimble-escape" in state.template.bonus_action_features
            and state.bonus_action_available
            and not state.hidden
            and battlefield.distance_ft > 5
            and can_hide(state, battlefield)
            and select_weapon_attack(state, battlefield.distance_ft) is not None
        )
    except Exception as exc:
        logger.exception("Failed to evaluate Nimble Escape Hide policy for %s.", state.template.name)
        raise RuntimeError("Nimble Escape Hide policy could not be evaluated.") from exc


def _legal_attacks(state: CombatantState, distance_ft: int) -> list[WeaponAttack]:
    profiles = [state.template.weapon_attack, *state.template.alternate_weapon_attacks]
    legal: list[WeaponAttack] = []
    for attack in profiles:
        try:
            resolve_attack_roll_mode(attack.weapon, distance_ft)
            legal.append(attack)
        except ValueError:
            continue
    return legal


def select_weapon_attack(
    state: CombatantState,
    distance_ft: int,
    duel_mode: DuelMode = DuelMode.OPEN,
) -> WeaponAttack | None:
    """Pick a legal attack matching the controlled arena mode when possible."""
    try:
        legal = _legal_attacks(state, distance_ft)
        if not legal or duel_mode is DuelMode.OPEN:
            return legal[0] if legal else None
        preferred_kind = (
            WeaponAttackKind.MELEE
            if duel_mode is DuelMode.MELEE or distance_ft <= 5
            else WeaponAttackKind.RANGED
        )
        return next(
            (attack for attack in legal if attack.weapon.attack_kind is preferred_kind),
            legal[0],
        )
    except Exception as exc:
        logger.exception("Failed to select attack profile for %s.", state.template.name)
        raise RuntimeError("Attack selection policy could not be evaluated.") from exc


def preferred_approach_distance(
    state: CombatantState,
    duel_mode: DuelMode = DuelMode.OPEN,
) -> int:
    """Choose the distance needed for the combat style being tested."""
    try:
        profiles = [state.template.weapon_attack, *state.template.alternate_weapon_attacks]
        if duel_mode is DuelMode.RANGED:
            ranged = next(
                (attack.weapon for attack in profiles if attack.weapon.attack_kind is WeaponAttackKind.RANGED),
                None,
            )
            if ranged is not None:
                if ranged.normal_range_ft is None:
                    raise ValueError("Ranged weapon has no normal range.")
                return ranged.normal_range_ft
        if duel_mode is DuelMode.MELEE:
            melee = next(
                (attack.weapon for attack in profiles if attack.weapon.attack_kind is WeaponAttackKind.MELEE),
                None,
            )
            return melee.reach_ft if melee is not None else 5

        weapon = state.template.weapon_attack.weapon
        if weapon.attack_kind is WeaponAttackKind.MELEE:
            return weapon.reach_ft
        if weapon.normal_range_ft is None:
            raise ValueError("Primary ranged weapon has no normal range.")
        return weapon.normal_range_ft
    except Exception as exc:
        logger.exception("Failed to choose approach distance for %s.", state.template.name)
        raise RuntimeError("Approach policy could not be evaluated.") from exc
