from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _member_for_state(setup: EncounterSetup, target_state) -> EncounterCombatant | None:
    return next(
        (member for member in [*setup.heroes, *setup.monsters] if member.state is target_state),
        None,
    )


def clear_damage_share(target: EncounterCombatant) -> None:
    try:
        effect_id = target.state.damage_share_effect_id
        source_id = target.state.damage_share_source_id
        target.state.damage_share_source_id = None
        target.state.damage_share_range_ft = 0
        target.state.damage_share_effect_id = None
        if effect_id and source_id:
            from app.combat.modifier_stack import remove_source_modifiers
            from app.combat.timed_condition_lifecycle import remove_effect_instance

            remove_source_modifiers([target.state], source_id, effect_id)
            for effect in list(target.state.timed_effects):
                if effect.source_id == source_id and effect.source_effect_id == effect_id:
                    remove_effect_instance(target.state, effect)
            target.state.active_buff_effect_ids = [
                item for item in target.state.active_buff_effect_ids if item != effect_id
            ]
    except Exception:
        logger.exception("Failed to clear damage share on %s.", target.combatant_id)
        raise


def resolve_damage_share(
    target: EncounterCombatant,
    amount: int,
    setup: EncounterSetup,
    dice,
) -> int:
    """Apply Warding Bond-style shared damage to the linked source within range."""
    try:
        source_id = target.state.damage_share_source_id
        range_ft = target.state.damage_share_range_ft
        if not source_id or amount <= 0 or range_ft <= 0:
            return 0
        source = next(
            (member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == source_id),
            None,
        )
        if source is None or source.combatant_id == target.combatant_id:
            return 0
        if source.state.is_dead or not source.state.is_alive or source.state.current_hp <= 0:
            clear_damage_share(target)
            return 0
        if combatant_distance(target, source) > range_ft:
            clear_damage_share(target)
            return 0
        apply_damage(
            source.state,
            amount,
            dice=dice,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
        )
        if source.state.current_hp <= 0 or source.state.is_dead:
            clear_damage_share(target)
        return amount
    except Exception:
        logger.exception("Failed to share damage from %s.", target.combatant_id)
        raise


def resolve_damage_share_for_state(target_state, amount: int, setup: EncounterSetup | None, dice) -> int:
    try:
        if setup is None or not target_state.damage_share_source_id:
            return 0
        target = _member_for_state(setup, target_state)
        if target is None:
            return 0
        return resolve_damage_share(target, amount, setup, dice)
    except Exception:
        logger.exception("Failed state-level damage share lookup.")
        raise
