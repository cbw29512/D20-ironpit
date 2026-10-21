from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.combat.timed_condition_saves import resolve_repeat_save
from app.combat.timed_conditions import remove_effect_group
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState


def end_damage_sensitive_effects(state: CombatantState) -> list[str]:
    removed: list[str] = []
    handled: set[tuple[str, str | None]] = set()
    for effect in list(state.timed_effects):
        key = (effect.source_id, effect.source_effect_id)
        if not effect.ends_on_damage or key in handled:
            continue
        handled.add(key)
        removed.extend(remove_effect_group(state, effect))
    return removed


def resolve_damage_repeat_saves(
    sequence: int,
    round_number: int,
    damage_source: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Repeat eligible grouped-effect saves after damage from a qualified source."""
    if target.state.is_dead or not target.state.is_alive:
        return [], sequence
    events: list[BattleEvent] = []
    handled: set[tuple[str, str | None]] = set()
    for effect in list(target.state.timed_effects):
        key = (effect.source_id, effect.source_effect_id)
        if key in handled or effect.damage_repeat_save_trigger == "none":
            continue
        handled.add(key)
        if (
            effect.damage_repeat_save_trigger == "other_than_effect_source"
            and damage_source.combatant_id == effect.source_id
        ):
            continue
        roll, succeeded, buffs = resolve_repeat_save(
            target, effect, dice, round_number, setup
        )
        removed = remove_effect_group(target.state, effect) if succeeded else []
        if not succeeded:
            effect.repeat_save_failure_count += 1
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=target.combatant_id, actor_name=target.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            saving_throw_roll=roll, save_ability=effect.repeat_save_ability,
            save_dc=effect.repeat_save_dc, save_succeeded=succeeded,
            removed_condition_ids=removed,
            feature_id=effect.source_effect_id or "condition-damage-repeat-save",
            animation="condition-save",
            description=(
                f"{target.state.template.name} repeats the "
                f"{effect.repeat_save_ability.title()} save after damage from "
                f"{damage_source.state.template.name}: "
                f"{'SUCCESS' if succeeded else 'FAILURE'}."
                + (f" Save Advantage: {', '.join(buffs)}." if buffs else "")
            ),
        ))
        sequence += 1
    return events, sequence


def cleanup_disabled_source_effects(setup: EncounterSetup) -> None:
    members = [*setup.heroes, *setup.monsters]
    by_id = {member.combatant_id: member for member in members}
    for target in members:
        handled: set[tuple[str, str | None]] = set()
        for effect in list(target.state.timed_effects):
            key = (effect.source_id, effect.source_effect_id)
            if key in handled:
                continue
            source = by_id.get(effect.source_id)
            if source is None:
                continue
            dead = source.state.is_dead or not source.state.is_alive or source.state.current_hp <= 0
            incapacitated = is_incapacitated(source.state)
            if (effect.ends_if_source_dead and dead) or (effect.ends_if_source_incapacitated and incapacitated):
                handled.add(key)
                remove_effect_group(target.state, effect)
