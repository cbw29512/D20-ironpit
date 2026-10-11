"""Resolve source-owned start-of-turn direct HP loss without damage events."""

import logging

from app.combat.dice import roll_dice
from app.combat.hit_point_loss import lose_hit_points
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def resolve_start_of_turn_hp_loss_events(sequence, round_number, member, setup, dice):
    try:
        events = []
        affected = [item.state for item in [*setup.heroes, *setup.monsters]]
        for effect in list(member.state.timed_effects):
            count = effect.start_of_turn_hp_loss_dice_count
            if count <= 0 or member.state.is_dead or member.state.current_hp <= 0:
                continue
            before = member.state.current_hp
            total = roll_dice(dice, count, effect.start_of_turn_hp_loss_dice_size)
            lost = lose_hit_points(member.state, total, dice=dice, affected_states=affected)
            name = effect.source_effect_id or effect.effect_id
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number,
                event_type="feature", actor_id=member.combatant_id,
                actor_name=member.state.template.name,
                target_id=member.combatant_id, target_name=member.state.template.name,
                feature_id=name, hp_before=before, hp_after=member.state.current_hp,
                is_dead=member.state.is_dead, animation="feature",
                description=f"{member.state.template.name} loses {lost} Hit Points from {name} at the start of the turn (not damage).",
            ))
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Start-of-turn HP loss failed for %s.", member.combatant_id)
        raise
