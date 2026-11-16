"""2014 generic visible-spell interruption: legal Reaction, slot and ability check.

The future casting hook must invoke this BEFORE triggering spell effects resolve.
A successful interrupt cancels the attempted spell's effects, not its slot cost.
"""
from __future__ import annotations

import logging

from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome
from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import can_see
from app.combat.encounter_targeting import combatant_distance
from app.combat.rolls import roll_d20
from app.domain.events import BattleEvent
from app.domain.spell_interrupt_reactions import SpellInterruptReaction

logger = logging.getLogger(__name__)


def interrupt_slot(interrupter, action, interrupted_level):
    """Choose cheapest source-legal slot that automatically interrupts, if any."""
    try:
        levels = [
            level for level in range(action.printed_level, 10)
            if (action.allows_higher_slots or level == action.printed_level)
            and any(resource.id == f"{action.resource_prefix}{level}"
                    and resource.current_uses > 0 for resource in interrupter.state.resources)
        ]
        if not levels:
            return None
        return next((level for level in levels if level >= interrupted_level), levels[0])
    except Exception:
        logger.exception("Could not select spell-interrupt slot for %s", action.id)
        raise


def interrupt_legal(interrupter, caster, action, interrupted_level, *, is_spell_cast):
    """Fail closed for non-spells, unseen casts, invalid Reaction or absent slot."""
    try:
        if interrupted_level < 0 or interrupted_level > 9:
            raise ValueError("Interrupted spell level must be 0 through 9.")
        if not is_spell_cast or interrupter.side == caster.side:
            return False
        if not caster.state.is_alive or caster.state.is_dead:
            return False
        if not is_available(interrupter.state, "reaction"):
            return False
        distance = combatant_distance(interrupter, caster)
        return (
            distance <= action.range_ft
            and can_see(interrupter.state, caster.state, distance)
            and interrupt_slot(interrupter, action, interrupted_level) is not None
        )
    except Exception:
        logger.exception("Failed to evaluate visible spell interruption eligibility")
        raise


def resolve_spell_interrupt(
    sequence, round_number, interrupter, caster, setup,
    action: SpellInterruptReaction, interrupted_name: str,
    interrupted_level: int, dice, *, is_spell_cast: bool,
):
    """Return (combat event, interrupted), leaving original spell cost to caller."""
    try:
        if not interrupt_legal(
            interrupter, caster, action, interrupted_level,
            is_spell_cast=is_spell_cast,
        ):
            raise ValueError("Spell-interrupt Reaction is not currently legal.")
        scores = interrupter.state.template.ability_scores
        if scores is None:
            raise ValueError("Spell-interrupt check requires certified casting scores.")
        level = interrupt_slot(interrupter, action, interrupted_level)
        if level is None:
            raise ValueError("No spell-interrupt slot remains.")
        resource = next(
            item for item in interrupter.state.resources
            if item.id == f"{action.resource_prefix}{level}" and item.current_uses > 0
        )
        # Resolve before paying to avoid partial resource mutation on invalid dice.
        check, dc, succeeded = None, None, True
        if interrupted_level > level:
            dc = 10 + interrupted_level
            check = roll_d20(
                dice, scores.modifier(action.casting_ability),
                ability_check_roll_mode(
                    interrupter.state, ability=action.casting_ability,
                    member=interrupter, setup=setup,
                ),
            )
            check, succeeded = resolve_ability_check_outcome(
                interrupter.state, action.casting_ability, check, dc,
                dice=dice, round_number=round_number,
                encounter_roller=interrupter, setup=setup,
            )
        spend(interrupter.state, "reaction")
        resource.current_uses -= 1
        result = "interrupted" if succeeded else "continues"
        event = BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=interrupter.combatant_id, actor_name=interrupter.state.template.name,
            target_id=caster.combatant_id, target_name=caster.state.template.name,
            feature_id=action.id, animation="counterspell",
            resource_remaining=resource.current_uses,
            ability_check_roll=check,
            check_ability=action.casting_ability if check else None,
            check_dc=dc, check_succeeded=succeeded if check else None,
            description=(
                f"{interrupter.state.template.name} uses {action.name} (level {level} slot) "
                f"against {caster.state.template.name}'s {interrupted_name} "
                f"(level {interrupted_level}): {result}."
            ),
        )
        return event, succeeded
    except Exception:
        logger.exception("Failed to resolve spell-interruption Reaction")
        raise
