from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_immunity import condition_is_immune
from app.combat.damage import aggregate_damage_components, roll_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.grapple import release_grapple
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.size import size_at_most
from app.domain.swallow import SwallowAction, SwallowedState

logger = logging.getLogger(__name__)


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def swallowed_targets(source_id: str, setup: EncounterSetup) -> list[EncounterCombatant]:
    try:
        return [member for member in _members(setup) if member.state.swallowed and member.state.swallowed.source_id == source_id]
    except Exception as exc:
        logger.exception("Failed to inspect swallowed targets for %s.", source_id)
        raise RuntimeError("Swallowed targets could not be evaluated.") from exc


def choose_swallow(source: EncounterCombatant, setup: EncounterSetup) -> tuple[EncounterCombatant, SwallowAction] | None:
    try:
        swallowed_count = len(swallowed_targets(source.combatant_id, setup))
        opponents = setup.monsters if source.side == "heroes" else setup.heroes
        for target in opponents:
            if target.state.is_dead or not target.state.is_alive or target.state.swallowed is not None:
                continue
            held = any(item.source_id == source.combatant_id for item in target.state.grapple_sources)
            for action in source.state.template.swallow_actions:
                if not is_available(source.state, action.action_cost):
                    continue
                if swallowed_count >= action.max_swallowed_targets:
                    continue
                if action.requires_grappled_target and not held:
                    continue
                if size_at_most(target.state.template.size, action.max_target_size):
                    return target, action
        return None
    except Exception as exc:
        logger.exception("Failed to choose Swallow action for %s.", source.combatant_id)
        raise RuntimeError("Swallow choice could not be evaluated.") from exc


def resolve_swallow(
    sequence: int, round_number: int, source: EncounterCombatant, target: EncounterCombatant,
    action: SwallowAction, setup: EncounterSetup,
) -> BattleEvent:
    try:
        choice = choose_swallow(source, setup)
        if choice is None or choice[0].combatant_id != target.combatant_id or choice[1].id != action.id:
            raise ValueError("Swallow requires an eligible target and available action economy.")
        applied = []
        if action.applies_blinded and not condition_is_immune(target.state, "blinded"):
            applied.append("blinded")
        if action.applies_restrained and not condition_is_immune(target.state, "restrained"):
            applied.append("restrained")
        if any(item.source_id == source.combatant_id for item in target.state.grapple_sources):
            release_grapple(target.state, source.combatant_id)
        target.state.swallowed = SwallowedState(
            source_id=source.combatant_id, action_id=action.id, applied_round=round_number,
            first_tick_round=round_number + action.first_tick_delay_rounds,
            applied_condition_ids=applied, total_cover_from_outside=action.total_cover_from_outside,
        )
        target.position_ft = source.position_ft
        target.state.position = source.state.position
        spend(source.state, action.action_cost)
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=action.id, applied_condition_ids=applied, animation="swallow",
            description=f"{source.state.template.name} swallows {target.state.template.name}.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve Swallow for %s.", source.combatant_id)
        raise RuntimeError("Swallow could not be resolved.") from exc


def release_swallowed(source: EncounterCombatant, target: EncounterCombatant, *, prone: bool) -> list[str]:
    try:
        removed = list(target.state.swallowed.applied_condition_ids) if target.state.swallowed else []
        target.state.swallowed = None
        target.position_ft = source.position_ft
        target.state.position = source.state.position
        if prone and not condition_is_immune(target.state, "prone") and "prone" not in target.state.active_effect_ids:
            target.state.active_effect_ids.append("prone")
        return removed
    except Exception as exc:
        logger.exception("Failed to release swallowed target %s.", target.combatant_id)
        raise RuntimeError("Swallowed target could not be released.") from exc


def resolve_swallow_turn_end(
    sequence: int, round_number: int, source: EncounterCombatant, setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        actions = {action.id: action for action in source.state.template.swallow_actions}
        affected_states = [member.state for member in _members(setup)]
        for target in swallowed_targets(source.combatant_id, setup):
            swallowed = target.state.swallowed
            if swallowed is None or round_number < swallowed.first_tick_round:
                continue
            action = actions.get(swallowed.action_id)
            if action is None:
                raise ValueError(f"Missing Swallow action {swallowed.action_id!r} on {source.state.template.name}.")
            component = roll_damage_component(
                dice, action.name, action.damage_dice_count, action.damage_dice_size,
                action.damage_bonus, action.damage_type, False,
            )
            total, components = apply_damage_defenses(target.state, [component])
            hp_before = target.state.current_hp
            apply_damage(target.state, total, damage_types={action.damage_type}, dice=dice, affected_states=affected_states)
            removed = release_swallowed(source, target, prone=True) if action.disgorge_after_first_tick and not target.state.is_dead else []
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=source.combatant_id, actor_name=source.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                feature_id=action.id, damage_roll=aggregate_damage_components(components), damage_components=components,
                hp_before=hp_before, hp_after=target.state.current_hp, removed_condition_ids=removed,
                animation="swallow-damage", description=f"{action.name} deals {total} {action.damage_type.value} damage to {target.state.template.name}.",
            ))
            sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed Swallow end-of-turn resolution for %s.", source.combatant_id)
        raise RuntimeError("Swallow turn-end effects could not be resolved.") from exc
