from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.suppression_zone_geometry import verbal_casting_blocked
from app.combat.teleport_cancel import clear_teleport_cancelable_effects
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.grid import GridPosition
from app.domain.teleport_actions import TeleportAction

logger = logging.getLogger(__name__)


def _resource(caster: EncounterCombatant, resource_id: str | None):
    if resource_id is None:
        return None
    return next((item for item in caster.state.resources if item.id == resource_id), None)


def _passengers(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: TeleportAction,
) -> list[EncounterCombatant]:
    if not action.passenger_count:
        return []
    allies = setup.heroes if caster.side == "heroes" else setup.monsters
    near = [
        ally
        for ally in allies
        if ally.combatant_id != caster.combatant_id
        and ally.state.is_alive
        and not ally.state.is_dead
        and combatant_distance(caster, ally) <= action.passenger_range_ft
    ]
    near.sort(key=lambda ally: (ally.state.current_hp, ally.combatant_id))
    return near[: action.passenger_count]


def resolve_teleport(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: TeleportAction,
    destination: GridPosition,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve a pit-banned teleport in place. Destination never changes grid x/y."""
    try:
        if verbal_casting_blocked(caster, setup):
            raise ValueError(f"{action.name} cannot be cast inside a Silence effect.")
        if setup.map_definition is None or caster.state.position is None:
            raise ValueError(f"{action.name} requires the authoritative grid.")
        if destination is None:
            raise ValueError(f"{action.name} requires a destination argument.")
        if not is_available(caster.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        origin = caster.state.position.model_copy(deep=True)
        # Iron Pit: supplied destinations are ignored; teleport never changes x/y.
        _ = (destination, dice)
        resource = _resource(caster, action.resource_id)
        if action.resource_id and (resource is None or resource.current_uses < action.resource_cost):
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        if action.expends_spell_slot:
            mark_slot_spell_cast(caster.state, turn_key)
        spend(caster.state, action.action_cost)
        if resource is not None:
            resource.current_uses -= action.resource_cost
        travelers = [caster, *_passengers(caster, setup, action)]
        removed: list[str] = []
        for traveler in travelers:
            for condition_id in clear_teleport_cancelable_effects(traveler):
                if condition_id not in removed:
                    removed.append(condition_id)
        names = ", ".join(item.replace("_", " ").title() for item in removed)
        description = f"{caster.state.template.name} uses {action.name} without leaving its spot."
        if names:
            description += f" {names} ends."
        events = [BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            feature_id=action.id,
            removed_condition_ids=removed,
            resource_remaining=resource.current_uses if resource is not None else None,
            grid_position_before=origin,
            grid_position_after=origin,
            animation=action.animation,
            description=description,
        )]
        return events, sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Teleport resolution failed for %s.", caster.combatant_id)
        raise RuntimeError("Teleport could not be resolved.") from exc
