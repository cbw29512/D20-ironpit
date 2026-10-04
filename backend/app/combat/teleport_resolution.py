from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance
from app.combat.grid_geometry import footprint_distance_ft
from app.combat.grid_pathing_support import overlapping_occupants
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.suppression_zone_geometry import verbal_casting_blocked
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll
from app.domain.grid import GridPosition
from app.domain.teleport_actions import TeleportAction
from app.domain.weapons_base import DamageType

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
    """Teleport the caster and optional passenger, or deal 4d6 force and fail if occupied."""
    try:
        if verbal_casting_blocked(caster, setup):
            raise ValueError(f"{action.name} cannot be cast inside a Silence effect.")
        if setup.map_definition is None or caster.state.position is None:
            raise ValueError(f"{action.name} requires the authoritative grid.")
        if not is_available(caster.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        if footprint_distance_ft(
            caster.state.position,
            caster.state.template.size,
            destination,
            caster.state.template.size,
        ) > action.range_ft:
            raise ValueError(f"{action.name} destination exceeds its range.")
        resource = _resource(caster, action.resource_id)
        if action.resource_id and (resource is None or resource.current_uses < action.resource_cost):
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        if action.expends_spell_slot:
            mark_slot_spell_cast(caster.state, turn_key)
        spend(caster.state, action.action_cost)
        if resource is not None:
            resource.current_uses -= action.resource_cost
        members = [*setup.heroes, *setup.monsters]
        occupied = overlapping_occupants(caster, destination, members)
        travelers = [caster, *_passengers(caster, setup, action)]
        events: list[BattleEvent] = []
        if occupied:
            for traveler in travelers:
                rolls = [dice.roll(6) for _ in range(4)]
                amount = sum(rolls)
                hp_before = traveler.state.current_hp
                apply_damage(
                    traveler.state,
                    amount,
                    damage_types={DamageType.FORCE},
                    dice=dice,
                    affected_states=[member.state for member in members],
                    setup=setup,
                )
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=round_number,
                    event_type="feature",
                    actor_id=caster.combatant_id,
                    actor_name=caster.state.template.name,
                    target_id=traveler.combatant_id,
                    target_name=traveler.state.template.name,
                    damage_roll=DiceRoll(notation="4d6", rolls=rolls, modifier=0, total=amount),
                    damage_components=[DamageRollComponent(
                        source=action.name, notation="4d6", rolls=rolls, modifier=0,
                        damage_type=DamageType.FORCE, total=amount, applied_total=amount,
                    )],
                    hp_before=hp_before,
                    hp_after=traveler.state.current_hp,
                    feature_id=action.id,
                    animation=action.animation,
                    description=(
                        f"{traveler.state.template.name} takes {amount} force damage as "
                        f"{action.name} fails in an occupied space."
                    ),
                ))
                sequence += 1
            return events, sequence
        origin = caster.state.position.model_copy(deep=True)
        offset_x = destination.x - origin.x
        offset_y = destination.y - origin.y
        for traveler in travelers:
            if traveler.state.position is None:
                continue
            traveler.state.position = GridPosition(
                x=traveler.state.position.x + offset_x,
                y=traveler.state.position.y + offset_y,
            )
        events.append(BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="movement",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            feature_id=action.id,
            resource_remaining=resource.current_uses if resource is not None else None,
            grid_position_before=origin,
            grid_position_after=destination.model_copy(deep=True),
            animation=action.animation,
            description=f"{caster.state.template.name} teleports with {action.name}.",
        ))
        return events, sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Teleport resolution failed for %s.", caster.combatant_id)
        raise RuntimeError("Teleport could not be resolved.") from exc
