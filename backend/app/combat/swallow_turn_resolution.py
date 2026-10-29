"""Resolve card-declared swallowed-victim damage thresholds at turn end."""
from __future__ import annotations

from app.combat.swallowed_damage_accounting import record_swallowed_victim_damage
from app.combat.swallow_regurgitation import resolve_swallow_regurgitation
from app.domain.models import BattleEvent


def resolve_swallowed_end_turn(events, sequence, round_number, actor, setup, dice, turn_key):
    """Count this actor's actual HP/temporary-HP damage to its swallowing owner."""
    record = actor.state.swallowed
    if record is None or record.regurgitation_damage_threshold is None:
        return [], sequence
    owner = next((
        member for member in [*setup.heroes, *setup.monsters]
        if member.combatant_id == record.source_id
    ), None)
    if owner is None or owner.state.is_dead or not owner.state.is_alive:
        return [], sequence
    total = 0
    for event in events:
        if event.actor_id != actor.combatant_id or event.target_id != owner.combatant_id:
            continue
        if event.hp_before is not None and event.hp_after is not None:
            total += max(0, event.hp_before - event.hp_after)
        before = event.temporary_hp_before
        after = event.temporary_hp_after
        if before is not None and after is not None:
            total += max(0, before - after)
    accumulated = record_swallowed_victim_damage(
        record, victim_id=actor.combatant_id, attacker_id=actor.combatant_id,
        owner_id=owner.combatant_id, actual_damage=total, turn_key=turn_key,
    )
    released, roll = resolve_swallow_regurgitation(
        owner.state, actor.state, owner_id=owner.combatant_id,
        target_id=actor.combatant_id, damage_from_swallowed_on_turn=accumulated,
        dice=dice, round_number=round_number, owner_member=owner, setup=setup,
    )
    if roll is None:
        return [], sequence
    event = BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=owner.combatant_id, actor_name=owner.state.template.name,
        target_id=actor.combatant_id, target_name=actor.state.template.name,
        feature_id="swallow-regurgitation", saving_throw_roll=roll,
        save_ability=record.regurgitation_save_ability,
        save_dc=record.regurgitation_save_dc,
        save_succeeded=not released, animation="feature",
        description=(
            f"{owner.state.template.name} {'regurgitates' if released else 'retains'} "
            f"{actor.state.template.name} after the swallowed creature dealt "
            f"{accumulated} damage this turn."
        ),
    )
    return [event], sequence + 1
