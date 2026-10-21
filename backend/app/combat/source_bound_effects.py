from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.persistent_hazards import position_enters_damaging_hazard
from app.combat.timed_condition_saves import resolve_repeat_save
from app.combat.timed_conditions import remove_effect_group
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


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
    sequence: int, round_number: int, damage_source: EncounterCombatant,
    target: EncounterCombatant, setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    if target.state.is_dead or not target.state.is_alive:
        return [], sequence
    events: list[BattleEvent] = []
    handled: set[tuple[str, str | None]] = set()
    for effect in list(target.state.timed_effects):
        key = (effect.source_id, effect.source_effect_id)
        if key in handled or effect.damage_repeat_save_trigger == "none":
            continue
        handled.add(key)
        if (effect.damage_repeat_save_trigger == "other_than_effect_source"
                and damage_source.combatant_id == effect.source_id):
            continue
        roll, succeeded, buffs = resolve_repeat_save(target, effect, dice, round_number, setup)
        removed = remove_effect_group(target.state, effect) if succeeded else []
        if not succeeded:
            effect.repeat_save_failure_count += 1
        events.append(_repeat_save_event(
            sequence, round_number, target, effect, roll, succeeded, removed, buffs,
            f"after damage from {damage_source.state.template.name}",
        ))
        sequence += 1
    return events, sequence


def resolve_damaging_terrain_repeat_saves(
    sequence: int, round_number: int, target: EncounterCombatant,
    destination: GridPosition, setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int, bool]:
    """Resolve a grouped save before a compelled step enters damaging terrain."""
    try:
        if target.state.is_dead or not target.state.is_alive:
            return [], sequence, False
        if not position_enters_damaging_hazard(target, destination, setup, round_number):
            return [], sequence, False
        events: list[BattleEvent] = []
        handled: set[tuple[str, str | None]] = set()
        released = False
        for effect in list(target.state.timed_effects):
            key = (effect.source_id, effect.source_effect_id)
            if key in handled or not effect.repeat_save_before_damaging_terrain:
                continue
            handled.add(key)
            roll, succeeded, buffs = resolve_repeat_save(
                target, effect, dice, round_number, setup,
            )
            removed = remove_effect_group(target.state, effect) if succeeded else []
            if succeeded and effect.turn_behavior == "forced_approach_source":
                released = True
            if not succeeded:
                effect.repeat_save_failure_count += 1
            events.append(_repeat_save_event(
                sequence, round_number, target, effect, roll, succeeded, removed, buffs,
                "before entering damaging terrain",
            ))
            sequence += 1
        return events, sequence, released
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Damaging-terrain repeat save failed for %s.", target.combatant_id)
        raise RuntimeError("Damaging-terrain repeat save could not be resolved.") from exc


def _repeat_save_event(
    sequence: int, round_number: int, target: EncounterCombatant, effect,
    roll, succeeded: bool, removed: list[str], buffs: list[str], reason: str,
) -> BattleEvent:
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="saving_throw",
        actor_id=target.combatant_id, actor_name=target.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        saving_throw_roll=roll, save_ability=effect.repeat_save_ability,
        save_dc=effect.repeat_save_dc, save_succeeded=succeeded,
        removed_condition_ids=removed,
        feature_id=effect.source_effect_id or "condition-repeat-save",
        animation="condition-save",
        description=(
            f"{target.state.template.name} repeats the "
            f"{effect.repeat_save_ability.title()} save {reason}: "
            f"{'SUCCESS' if succeeded else 'FAILURE'}."
            + (f" Save Advantage: {', '.join(buffs)}." if buffs else "")
        ),
    )


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
