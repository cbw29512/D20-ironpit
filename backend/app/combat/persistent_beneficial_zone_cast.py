from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.persistent_beneficial_zone_effects import sync_persistent_beneficial_zones
from app.combat.persistent_beneficial_zone_geometry import (
    beneficial_zone_position_legal,
    beneficial_zone_source_distance,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import BattleEvent
from app.domain.persistent_beneficial_zones import (
    PersistentBeneficialZoneAction,
    PersistentBeneficialZoneState,
)

logger = logging.getLogger(__name__)


def _resource(caster: EncounterCombatant, resource_id: str | None):
    if resource_id is None:
        return None
    return next((item for item in caster.state.resources if item.id == resource_id), None)


def cast_persistent_beneficial_zone(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: PersistentBeneficialZoneAction,
    position: GridPosition,
) -> tuple[BattleEvent, int]:
    try:
        if not is_available(caster.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        if not beneficial_zone_position_legal(setup, position, action):
            raise ValueError(f"{action.name} requires a legal in-bounds placement.")
        if beneficial_zone_source_distance(caster, position, action) > action.cast_range_ft:
            raise ValueError(f"{action.name} placement exceeds its cast range.")

        resource = _resource(caster, action.resource_id)
        if action.resource_id and (
            resource is None or resource.current_uses < action.resource_cost
        ):
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")

        spend(caster.state, action.action_cost)
        if resource is not None:
            resource.current_uses -= action.resource_cost

        zone_id = (
            f"{caster.combatant_id}:{action.id}:{round_number}:"
            f"{len(setup.persistent_beneficial_zones) + 1}"
        )
        setup.persistent_beneficial_zones.append(PersistentBeneficialZoneState(
            zone_id=zone_id,
            source_id=caster.combatant_id,
            source_side=caster.side,
            action_id=action.id,
            action_name=action.name,
            position=position.model_copy(deep=True),
            applied_round=round_number,
            expires_round=round_number + action.duration_rounds,
            length_ft=action.length_ft,
            armor_class_bonus=action.armor_class_bonus,
            saving_throw_bonus=action.saving_throw_bonus,
            saving_throw_abilities=list(action.saving_throw_abilities),
            ally_damage_resistances=list(action.ally_damage_resistances),
            include_source_for_defense=action.include_source_for_defense,
            end_if_source_incapacitated=action.end_if_source_incapacitated,
            end_if_source_dead=action.end_if_source_dead,
            animation=action.animation,
        ))
        sync_persistent_beneficial_zones(setup, round_number)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            feature_id=action.id,
            resource_remaining=resource.current_uses if resource is not None else None,
            animation=action.animation,
            description=f"{caster.state.template.name} creates {action.name}.",
        ), sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Persistent beneficial zone cast failed for %s.", caster.combatant_id)
        raise RuntimeError("Persistent beneficial zone could not be created.") from exc
