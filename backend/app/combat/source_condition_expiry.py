from __future__ import annotations

from app.combat.timed_conditions import remove_effect_group
from app.domain.models import BattleEvent, EncounterCombatant, EncounterSetup, TimedEffect


def _source_start_expired(effect: TimedEffect, round_number: int) -> bool:
    source_start = effect.expiry_timing == "source_turn_start" or effect.expires_at_start_of_source_turn
    return source_start and (effect.expires_round is None or round_number >= effect.expires_round)


def expire_start_of_turn_conditions(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for target in [*setup.heroes, *setup.monsters]:
        expiring = [
            effect for effect in target.state.timed_effects
            if effect.source_id == source.combatant_id and _source_start_expired(effect, round_number)
        ]
        for effect in expiring:
            if effect not in target.state.timed_effects:
                continue
            removed = remove_effect_group(target.state, effect)
            if not removed:
                continue
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=source.combatant_id,
                actor_name=source.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                removed_condition_ids=removed,
                feature_id=effect.source_effect_id or "condition-ended",
                animation="condition-ended",
                description=(
                    f"{target.state.template.name} is no longer affected by "
                    f"{effect.source_effect_id or effect.effect_id}."
                ),
            ))
            sequence += 1
    return events, sequence
