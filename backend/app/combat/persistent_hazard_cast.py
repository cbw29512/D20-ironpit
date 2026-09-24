from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.grid_geometry import footprint_distance_ft, footprints_overlap, position_in_bounds
from app.combat.spellcasting import mark_slot_spell_cast
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import BattleEvent
from app.domain.persistent_hazards import PersistentHazardAction, PersistentHazardState

logger = logging.getLogger(__name__)


def _slot_resource(caster: EncounterCombatant, level: int):
    resource_id = f"spell-slot-{level}"
    return next((item for item in caster.state.resources if item.id == resource_id), None)


def _position_legal(
    setup: EncounterSetup,
    action: PersistentHazardAction,
    position: GridPosition,
) -> bool:
    if setup.map_definition is None:
        return False
    if not position_in_bounds(setup.map_definition, position, action.footprint_size):
        return False
    for member in [*setup.heroes, *setup.monsters]:
        if member.state.position is None:
            continue
        if footprints_overlap(
            position, action.footprint_size,
            member.state.position, member.state.template.size,
        ):
            return False
    return not any(
        footprints_overlap(
            position, action.footprint_size,
            hazard.position, hazard.footprint_size,
        )
        for hazard in setup.persistent_hazards
    )


def cast_persistent_hazard(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: PersistentHazardAction,
    position: GridPosition,
    turn_key: str,
) -> tuple[BattleEvent, int]:
    """Spend the action/slot and place one stationary source-independent hazard."""
    try:
        if setup.map_definition is None or caster.state.position is None:
            raise ValueError("Persistent hazards require the authoritative grid.")
        if not is_available(caster.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        distance = footprint_distance_ft(
            caster.state.position, caster.state.template.size,
            position, action.footprint_size,
        )
        if distance > action.cast_range_ft:
            raise ValueError(f"{action.name} placement exceeds its cast range.")
        if not _position_legal(setup, action, position):
            raise ValueError(f"{action.name} requires a legal unoccupied placement.")

        resource = _slot_resource(caster, action.level)
        if action.level > 0 and (resource is None or resource.current_uses < 1):
            raise ValueError(f"No level {action.level} spell slot remains.")
        if action.level > 0:
            mark_slot_spell_cast(caster.state, turn_key)
            resource.current_uses -= 1
        spend(caster.state, action.action_cost)

        hazard_id = f"{caster.combatant_id}:{action.id}:{round_number}:{len(setup.persistent_hazards) + 1}"
        setup.persistent_hazards.append(PersistentHazardState(
            hazard_id=hazard_id, source_id=caster.combatant_id, source_side=caster.side,
            action_id=action.id, action_name=action.name,
            position=position.model_copy(deep=True), footprint_size=action.footprint_size,
            trigger_radius_ft=action.trigger_radius_ft, save_ability=action.save_ability,
            dc=action.dc, failure_damage=action.failure_damage,
            success_damage=action.success_damage, damage_type=action.damage_type,
            remaining_damage_capacity=action.max_total_damage,
            expires_round=round_number + action.duration_rounds,
            animation=action.animation,
        ))
        event = BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=caster.combatant_id, actor_name=caster.state.template.name,
            feature_id=action.id,
            resource_remaining=resource.current_uses if resource is not None else None,
            animation=action.animation,
            description=f"{caster.state.template.name} creates {action.name}.",
        )
        return event, sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Persistent hazard cast failed for %s.", caster.combatant_id)
        raise RuntimeError("Persistent hazard could not be created.") from exc
