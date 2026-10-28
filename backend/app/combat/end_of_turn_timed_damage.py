"""Shared typed recurring damage resolved at the affected combatant's turn end."""
from __future__ import annotations

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import roll_dice
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, DamageRollComponent, DamageType


def resolve_end_of_turn_timed_damage(sequence, round_number, member, setup, dice):
    events = []
    state = member.state
    if state.is_dead or not state.is_alive:
        return events, sequence
    affected = [m.state for m in [*setup.heroes, *setup.monsters]]
    for effect in list(state.timed_effects):
        if effect not in state.timed_effects or effect.end_of_turn_dice_count <= 0:
            continue
        if effect.end_of_turn_damage_type is None:
            raise ValueError("Recurring end-turn damage requires a type")
        total = roll_dice(dice, effect.end_of_turn_dice_count, effect.end_of_turn_dice_size)
        damage_type = DamageType(effect.end_of_turn_damage_type)
        packet = DamageRollComponent(
            source=effect.source_effect_id or effect.effect_id,
            notation=f"{effect.end_of_turn_dice_count}d{effect.end_of_turn_dice_size}",
            rolls=[], modifier=0, damage_type=damage_type, total=total,
        )
        hp_before = state.current_hp
        applied, _ = apply_damage_defenses(state, [packet])
        apply_damage(state, applied, critical=False, damage_types={damage_type},
                     dice=dice, affected_states=affected, setup=setup)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=member.combatant_id, actor_name=state.template.name,
            target_id=member.combatant_id, target_name=state.template.name,
            feature_id=effect.source_effect_id or effect.effect_id,
            hp_before=hp_before, hp_after=state.current_hp, animation="feature",
            description=f"{effect.effect_id} deals {applied} {damage_type.value} damage at turn end.",
        ))
        sequence += 1
        if state.is_dead or not state.is_alive:
            break
    return events, sequence
