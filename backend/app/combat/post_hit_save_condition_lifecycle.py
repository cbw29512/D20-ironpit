from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import end_concentration
from app.combat.dice import roll_dice
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _linked_action(member: EncounterCombatant, setup: EncounterSetup):
    for source in [*setup.heroes, *setup.monsters]:
        concentration = source.state.concentration
        if concentration is None:
            continue
        action = next(
            (
                item
                for item in source.state.template.post_hit_save_condition_spells
                if item.id == concentration.effect_id
            ),
            None,
        )
        if action is None:
            continue
        linked = any(
            effect.effect_id == action.failed_condition_id
            and effect.source_id == source.combatant_id
            and effect.source_effect_id == action.id
            for effect in member.state.timed_effects
        )
        if linked:
            return source, action, concentration
    return None


def start_of_turn_save_condition_damage(
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> list[tuple[str, int, str]]:
    """Apply printed start-of-turn damage while the save-condition remains active."""
    try:
        match = _linked_action(member, setup)
        if match is None:
            return []
        _source, action, concentration = match
        if action.start_of_turn_dice_count <= 0:
            return []
        if action.failed_condition_id not in member.state.active_effect_ids:
            return []
        slot = concentration.slot_level or action.level
        count = action.start_of_turn_dice_count + action.start_of_turn_dice_per_slot_above * max(
            0, slot - action.level
        )
        total = roll_dice(dice, count, action.start_of_turn_dice_size)
        return [(action.name, total, action.start_of_turn_damage_type)]
    except Exception:
        logger.exception("Start-of-turn save-condition damage failed for %s.", member.combatant_id)
        raise


def escape_post_hit_save_condition(
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> bool:
    """Spend an Action on the printed Strength (Athletics) check to end the spell."""
    try:
        if not is_available(member.state, "action"):
            return False
        athletics = member.state.template.skill_bonuses.get("athletics")
        if athletics is None:
            return False
        match = _linked_action(member, setup)
        if match is None:
            return False
        source, action, _concentration = match
        spend(member.state, action.escape_action_cost)
        roll = dice.roll("1d20") + athletics
        if roll >= action.save_dc:
            end_concentration(
                source.state,
                [item.state for item in [*setup.heroes, *setup.monsters]],
            )
            return True
        return False
    except Exception:
        logger.exception("Save-condition escape failed for %s.", member.combatant_id)
        raise
