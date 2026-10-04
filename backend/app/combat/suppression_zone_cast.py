from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import start_concentration
from app.combat.encounter_targeting import combatant_distance
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.combat.suppression_zone_effects import sync_suppression_zone_effects
from app.combat.suppression_zone_geometry import verbal_casting_blocked, zone_center_legal
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import BattleEvent
from app.domain.suppression_zones import PersistentSuppressionZoneAction, PersistentSuppressionZoneState

logger = logging.getLogger(__name__)


def _resource(caster: EncounterCombatant, resource_id: str | None):
    if resource_id is None:
        return None
    return next((item for item in caster.state.resources if item.id == resource_id), None)


def choose_suppression_zone_center(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: PersistentSuppressionZoneAction,
) -> GridPosition | None:
    try:
        if setup.map_definition is None or caster.state.position is None:
            return None
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        living = [
            enemy for enemy in enemies
            if enemy.state.is_alive and not enemy.state.is_dead and enemy.state.position is not None
        ]
        if not living:
            return None
        target = min(living, key=lambda enemy: (combatant_distance(caster, enemy), enemy.combatant_id))
        if not zone_center_legal(setup, target.state.position, action.cast_range_ft, caster):
            return None
        return target.state.position.model_copy(deep=True)
    except Exception:
        logger.exception("Failed to choose suppression-zone center for %s.", caster.combatant_id)
        raise


def choose_suppression_zone_action(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> tuple[PersistentSuppressionZoneAction, GridPosition] | None:
    try:
        if verbal_casting_blocked(caster, setup):
            return None
        for action in caster.state.template.suppression_zone_actions:
            if not is_available(caster.state, action.action_cost):
                continue
            if action.concentration and caster.state.concentration is not None:
                continue
            if action.expends_spell_slot and not slot_spell_available(caster.state, turn_key):
                continue
            resource = _resource(caster, action.resource_id)
            if action.resource_id and (resource is None or resource.current_uses < action.resource_cost):
                continue
            center = choose_suppression_zone_center(caster, setup, action)
            if center is not None:
                return action, center
        return None
    except Exception:
        logger.exception("Failed suppression-zone choice for %s.", caster.combatant_id)
        raise


def cast_suppression_zone(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: PersistentSuppressionZoneAction,
    position: GridPosition,
    turn_key: str,
) -> tuple[BattleEvent, int]:
    try:
        if verbal_casting_blocked(caster, setup):
            raise ValueError(f"{action.name} cannot be cast inside a Silence effect.")
        if not is_available(caster.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        if not zone_center_legal(setup, position, action.cast_range_ft, caster):
            raise ValueError(f"{action.name} placement exceeds its cast range.")
        resource = _resource(caster, action.resource_id)
        if action.resource_id and (resource is None or resource.current_uses < action.resource_cost):
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        if action.expends_spell_slot:
            mark_slot_spell_cast(caster.state, turn_key)
        spend(caster.state, action.action_cost)
        if resource is not None:
            resource.current_uses -= action.resource_cost
        if action.concentration:
            start_concentration(
                caster.state,
                caster.combatant_id,
                action.id,
                round_number,
                [member.state for member in [*setup.heroes, *setup.monsters]],
                expires_round=round_number + action.duration_rounds,
            )
        setup.suppression_zones.append(PersistentSuppressionZoneState(
            zone_id=f"{caster.combatant_id}:{action.id}:{round_number}:{len(setup.suppression_zones) + 1}",
            source_id=caster.combatant_id,
            action_id=action.id,
            action_name=action.name,
            position=position.model_copy(deep=True),
            radius_ft=action.radius_ft,
            expires_round=round_number + action.duration_rounds,
            deafens=action.deafens,
            blocks_verbal_spells=action.blocks_verbal_spells,
            thunder_immunity=action.thunder_immunity,
            concentration=action.concentration,
        ))
        sync_suppression_zone_effects(setup, round_number)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            feature_id=action.id,
            resource_remaining=resource.current_uses if resource is not None else None,
            concentration_started_effect_id=action.id if action.concentration else None,
            animation=action.animation,
            description=f"{caster.state.template.name} casts {action.name}.",
        ), sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Suppression zone cast failed for %s.", caster.combatant_id)
        raise RuntimeError("Suppression zone could not be created.") from exc
