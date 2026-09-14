from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.grid_geometry import footprint_distance_ft
from app.combat.saving_throws import resolve_save_action
from app.domain.actions import SavingThrowAction
from app.domain.death_triggers import DeathTriggeredSaveEffect
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def _action(effect: DeathTriggeredSaveEffect) -> SavingThrowAction:
    try:
        return SavingThrowAction(
            id=effect.id,
            name=effect.name,
            save_ability=effect.save_ability,
            dc=effect.dc,
            range_ft=effect.radius_ft,
            damage_dice_count=effect.damage_dice_count,
            damage_dice_size=effect.damage_dice_size,
            damage_bonus=effect.damage_bonus,
            damage_type=effect.damage_type.value,
            success_damage="half" if effect.half_damage_on_success else "none",
            animation="death-trigger",
        )
    except Exception:
        logger.exception("Failed to compile death-trigger effect %s.", effect.id)
        raise


def _distance(source: EncounterCombatant, target: EncounterCombatant) -> int:
    try:
        if source.state.position is None or target.state.position is None:
            raise ValueError("Death-trigger resolution requires authoritative grid positions.")
        return footprint_distance_ft(
            source.state.position,
            source.state.template.size,
            target.state.position,
            target.state.template.size,
        )
    except Exception:
        logger.exception("Failed death-trigger distance check: %s -> %s.", source.combatant_id, target.combatant_id)
        raise


def resolve_death_triggers(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    *,
    resolved: set[str] | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve immutable on-death save effects once, including deterministic chain deaths."""
    try:
        if not source.state.is_dead:
            return [], sequence
        resolved_keys = resolved if resolved is not None else set()
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        events: list[BattleEvent] = []
        members = [*setup.heroes, *setup.monsters]
        for effect in source.state.template.death_trigger_effects:
            key = f"{source.combatant_id}:{effect.id}"
            if key in resolved_keys:
                continue
            resolved_keys.add(key)
            action = _action(effect)
            targets = [
                target for target in members
                if target.combatant_id != source.combatant_id
                and not target.state.is_dead
                and _distance(source, target) <= effect.radius_ft
            ]
            shared_rolls: list[int] = []
            newly_dead: list[EncounterCombatant] = []
            for index, target in enumerate(targets):
                was_dead = target.state.is_dead
                event = resolve_save_action(
                    sequence,
                    round_number,
                    source,
                    target,
                    action,
                    _distance(source, target),
                    dice,
                    spend_action=False,
                    spend_resource_cost=False,
                    shared_damage_rolls=shared_rolls or None,
                    capture_shared_damage_rolls=shared_rolls if index == 0 else None,
                    affected_states=affected_states,
                    setup=setup,
                )
                events.append(event)
                sequence += 1
                if not was_dead and target.state.is_dead and target.state.template.death_trigger_effects:
                    newly_dead.append(target)
            for dead_target in newly_dead:
                chained, sequence = resolve_death_triggers(
                    sequence,
                    round_number,
                    dead_target,
                    setup,
                    dice,
                    resolved=resolved_keys,
                )
                events.extend(chained)
        return events, sequence
    except Exception as exc:
        logger.exception("Death-trigger resolution failed for %s.", source.combatant_id)
        raise RuntimeError("Death-trigger resolution could not be completed.") from exc


def resolve_event_death_triggers(
    sequence: int, round_number: int, event: BattleEvent, setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Dispatch a target's on-death effects immediately after its lethal battle event."""
    try:
        if not event.target_id:
            return [], sequence
        target = next(
            (member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == event.target_id),
            None,
        )
        if target is None or not target.state.is_dead or not target.state.template.death_trigger_effects:
            return [], sequence
        return resolve_death_triggers(sequence, round_number, target, setup, dice)
    except Exception:
        logger.exception("Failed to dispatch death triggers after event %s.", event.sequence)
        raise
