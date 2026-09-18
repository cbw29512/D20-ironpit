from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def apply_turned_creature_effects(
    source: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    round_number: int,
    *,
    source_effect_id: str,
    turned_effect_id: str,
) -> list[str]:
    """Apply the shared 1-minute forced-retreat turn package used by holy turning features."""
    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    common = dict(
        source_effect_id=source_effect_id,
        applied_round=round_number,
        expires_round=round_number + 10,
        expiry_timing="source_turn_start",
        affected_states=states,
        ends_on_damage=True,
        ends_if_source_incapacitated=True,
        ends_if_source_dead=True,
    )
    applied = [
        apply_timed_condition(
            target.state,
            turned_effect_id,
            source.combatant_id,
            turn_behavior="forced_retreat",
            **common,
        )
    ]
    for condition in ("frightened", "incapacitated"):
        if not condition_is_immune(target.state, condition):
            applied.append(apply_timed_condition(
                target.state,
                condition,
                source.combatant_id,
                **common,
            ))
    return [effect for effect in applied if effect is not None]


def resolve_turning_saves(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    targets: tuple[EncounterCombatant, ...],
    dice: DiceProvider,
    *,
    save_dc: int,
    source_effect_id: str,
    turned_effect_id: str,
    resource_remaining: int,
    feature_name: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve the shared Wisdom-save/event loop for creature-turning features."""
    events: list[BattleEvent] = []
    for target in targets:
        roll, succeeded = resolve_saving_throw(target.state, "wisdom", save_dc, dice)
        applied = [] if succeeded else apply_turned_creature_effects(
            source, target, setup, round_number,
            source_effect_id=source_effect_id, turned_effect_id=turned_effect_id,
        )
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            saving_throw_roll=roll, save_ability="wisdom", save_dc=save_dc, save_succeeded=succeeded,
            applied_condition_ids=applied, feature_id=source_effect_id,
            resource_remaining=resource_remaining, animation="turn-undead",
            description=(
                f"{target.state.template.name} {'resists' if succeeded else 'fails'} "
                f"{source.state.template.name}'s {feature_name}."
            ),
        ))
        sequence += 1
    return events, sequence
