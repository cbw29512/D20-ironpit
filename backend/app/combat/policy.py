from __future__ import annotations

import logging

from app.combat.range import resolve_attack_roll_mode
from app.domain.models import CombatantState, Weapon, WeaponAttackKind

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


def select_attack_weapon(state: CombatantState, distance_ft: int) -> Weapon | None:
    """Arena tactic: prefer the primary weapon, otherwise use the first legal alternate weapon."""
    try:
        for weapon in [state.template.weapon, *state.template.alternate_weapons]:
            try:
                resolve_attack_roll_mode(weapon, distance_ft)
                return weapon
            except ValueError:
                continue
        return None
    except Exception as exc:
        logger.exception("Failed to select weapon for %s.", state.template.name)
        raise RuntimeError("Weapon selection policy could not be evaluated.") from exc


def preferred_approach_distance(state: CombatantState) -> int:
    """Arena tactic: close to primary melee reach or primary normal ranged distance."""
    try:
        weapon = state.template.weapon
        if weapon.attack_kind is WeaponAttackKind.MELEE:
            return weapon.reach_ft
        if weapon.normal_range_ft is None:
            raise ValueError("Primary ranged weapon has no normal range.")
        return weapon.normal_range_ft
    except Exception as exc:
        logger.exception("Failed to choose approach distance for %s.", state.template.name)
        raise RuntimeError("Approach policy could not be evaluated.") from exc
