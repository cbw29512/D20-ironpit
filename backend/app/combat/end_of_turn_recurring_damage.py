"""Universal typed recurring damage at the affected combatant's turn end."""
from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import roll_dice
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, DamageRollComponent, DamageType

logger = logging.getLogger(__name__)


def resolve_end_turn_recurring_damage(sequence, round_number, member, setup, dice):
    """Apply all pending source-owned packets with normal damage/death lifecycle."""
    try:
        events = []
        state = member.state
        if not state.is_alive or state.is_dead:
            return events, sequence
        affected = [entry.state for entry in [*setup.heroes, *setup.monsters]]
        for effect in list(state.timed_effects):
            if effect not in state.timed_effects or not effect.end_of_turn_dice_count:
                continue
            if effect.end_of_turn_damage_type is None:
                raise ValueError("End-turn damage requires a typed source packet.")
            dtype = DamageType(effect.end_of_turn_damage_type)
            rolled = roll_dice(
                dice, effect.end_of_turn_dice_count, effect.end_of_turn_dice_size,
            )
            label = effect.source_name or effect.source_effect_id or effect.effect_id
            part = DamageRollComponent(
                source=label,
                notation=f"{effect.end_of_turn_dice_count}d{effect.end_of_turn_dice_size}",
                rolls=[], modifier=0, damage_type=dtype, total=rolled,
            )
            before = state.current_hp
            applied, _ = apply_damage_defenses(state, [part])
            apply_damage(
                state, applied, critical=False, damage_types={dtype},
                dice=dice, affected_states=affected, setup=setup,
            )
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id, actor_name=state.template.name,
                target_id=member.combatant_id, target_name=state.template.name,
                feature_id=effect.source_effect_id or effect.effect_id,
                hp_before=before, hp_after=state.current_hp, animation="feature",
                description=(
                    f"{label} deals {applied} {dtype.value} damage "
                    f"to {state.template.name} at turn end."
                ),
            ))
            sequence += 1
            if state.is_dead or not state.is_alive:
                break
        return events, sequence
    except Exception:
        logger.exception(
            "End-turn recurring damage failed: %s, round %s.",
            member.combatant_id, round_number,
        )
        raise
