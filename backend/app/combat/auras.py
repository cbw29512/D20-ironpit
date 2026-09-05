from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.formation import distance_between
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll
from app.combat.dice import DiceProvider


def _targets(source: EncounterCombatant, setup: EncounterSetup, radius: int, mode: str) -> list[EncounterCombatant]:
    members = [*setup.heroes, *setup.monsters]
    return [
        member for member in members
        if member.combatant_id != source.combatant_id
        and not member.state.is_dead
        and (mode == "all_others" or member.side != source.side)
        and distance_between(source, member) <= radius
    ]


def resolve_end_turn_aura(
    sequence: int, round_number: int, source: EncounterCombatant, setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    aura = source.state.template.end_turn_damage_aura
    if aura is None or source.state.is_dead or (aura.disabled_while_incapacitated and is_incapacitated(source.state)):
        return [], sequence
    targets = _targets(source, setup, aura.radius_ft, aura.target_mode)
    if not targets:
        return [], sequence
    rolls = [dice.roll(aura.dice_size) for _ in range(aura.dice_count)]
    raw = sum(rolls) + aura.damage_bonus
    notation = f"{aura.dice_count}d{aura.dice_size}" + (f"+{aura.damage_bonus}" if aura.damage_bonus > 0 else f"{aura.damage_bonus}" if aura.damage_bonus < 0 else "")
    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    events: list[BattleEvent] = []
    for target in targets:
        before, temp_before = target.state.current_hp, target.state.temporary_hp
        success_before, failure_before = target.state.death_save_successes, target.state.death_save_failures
        applied = adjusted_damage_amount(raw, aura.damage_type, target.state)
        component = DamageRollComponent(source=aura.name, notation=notation, rolls=rolls, modifier=aura.damage_bonus,
                                        damage_type=aura.damage_type, total=raw, applied_total=applied)
        apply_damage(target.state, applied, damage_types={aura.damage_type} if applied else set(), dice=dice, affected_states=states)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature", actor_id=source.combatant_id,
            actor_name=source.state.template.name, target_id=target.combatant_id, target_name=target.state.template.name,
            damage_roll=DiceRoll(notation=notation, rolls=rolls, modifier=aura.damage_bonus, total=applied), damage_components=[component],
            hp_before=before, hp_after=target.state.current_hp, temporary_hp_before=temp_before, temporary_hp_after=target.state.temporary_hp,
            death_save_successes_before=success_before, death_save_failures_before=failure_before,
            death_save_successes=target.state.death_save_successes, death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable, is_dead=target.state.is_dead, feature_id="end-turn-damage-aura", animation="fire",
            description=f"{source.state.template.name}'s {aura.name} deals {applied} {aura.damage_type.value.title()} damage to {target.state.template.name}.",
        )); sequence += 1
    return events, sequence
