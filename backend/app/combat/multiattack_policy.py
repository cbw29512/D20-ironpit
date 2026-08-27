from __future__ import annotations

import logging

from app.combat.conditions import has_condition
from app.combat.range import resolve_attack_roll_mode
from app.domain.models import CombatantState, MultiattackDefinition, SaveAction, WeaponAttack

logger = logging.getLogger(__name__)


def select_multiattack_weapon(
    state: CombatantState,
    routine: MultiattackDefinition,
    distance_ft: int,
) -> WeaponAttack | None:
    try:
        profiles = [state.template.weapon_attack, *state.template.alternate_weapon_attacks]
        for attack in profiles:
            if attack.id not in routine.allowed_attack_ids:
                continue
            try:
                resolve_attack_roll_mode(attack.weapon, distance_ft)
                return attack
            except ValueError:
                continue
        return None
    except Exception as exc:
        logger.exception("Multiattack weapon selection failed for %s.", state.template.name)
        raise RuntimeError("Multiattack weapon policy could not be evaluated.") from exc


def select_save_replacement(
    actor: CombatantState,
    target: CombatantState,
    routine: MultiattackDefinition,
    distance_ft: int,
    replacements_used: int,
) -> SaveAction | None:
    """Arena tactic: prefer a legal replacement that can apply a new condition."""
    try:
        if replacements_used >= routine.max_save_replacements:
            return None
        for action in actor.template.save_actions:
            if action.id not in routine.replacement_save_action_ids or distance_ft > action.range_ft:
                continue
            useful = any(
                effect.condition not in target.template.condition_immunities
                and not has_condition(target, effect.condition)
                for effect in action.failure_effects
                if effect.effect_type == "condition"
            )
            if useful:
                return action
        return None
    except Exception as exc:
        logger.exception("Multiattack replacement policy failed for %s.", actor.template.name)
        raise RuntimeError("Multiattack replacement policy could not be evaluated.") from exc
