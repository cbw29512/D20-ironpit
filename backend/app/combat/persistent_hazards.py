from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.damage import aggregate_damage_components, fixed_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.grid_geometry import footprint_distance_ft, footprints_overlap, position_in_bounds
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import BattleEvent, DamageType
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
            hazard_id=hazard_id,
            source_id=caster.combatant_id,
            source_side=caster.side,
            action_id=action.id,
            action_name=action.name,
            position=position.model_copy(deep=True),
            footprint_size=action.footprint_size,
            trigger_radius_ft=action.trigger_radius_ft,
            save_ability=action.save_ability,
            dc=action.dc,
            failure_damage=action.failure_damage,
            success_damage=action.success_damage,
            damage_type=action.damage_type,
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


def resolve_persistent_hazard_entries(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve first movement-to-radius triggers after one authoritative position step."""
    try:
        if mover.state.position is None:
            return [], sequence
        events: list[BattleEvent] = []
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        expired = [h for h in setup.persistent_hazards if round_number >= h.expires_round or h.remaining_damage_capacity <= 0]
        for hazard in expired:
            setup.persistent_hazards.remove(hazard)

        for hazard in list(setup.persistent_hazards):
            if hazard.source_side == mover.side:
                continue
            if hazard.triggered_turn_keys.get(mover.combatant_id) == turn_key:
                continue
            distance = footprint_distance_ft(
                mover.state.position, mover.state.template.size,
                hazard.position, hazard.footprint_size,
            )
            if distance > hazard.trigger_radius_ft:
                continue

            hazard.triggered_turn_keys[mover.combatant_id] = turn_key
            roll, succeeded = resolve_saving_throw(
                mover.state, hazard.save_ability, hazard.dc, dice,
            )
            raw_damage = hazard.success_damage if succeeded else hazard.failure_damage
            component = fixed_damage_component(
                hazard.action_name, raw_damage, DamageType(hazard.damage_type),
            )
            applied_total, components = apply_damage_defenses(mover.state, [component])
            hp_before = mover.state.current_hp
            if applied_total:
                apply_damage(
                    mover.state,
                    applied_total,
                    damage_types={DamageType(hazard.damage_type)},
                    dice=dice,
                    affected_states=affected_states,
                )
            hazard.remaining_damage_capacity = max(
                0, hazard.remaining_damage_capacity - applied_total,
            )
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="saving_throw",
                actor_id=hazard.source_id, actor_name=hazard.action_name,
                target_id=mover.combatant_id, target_name=mover.state.template.name,
                saving_throw_roll=roll, save_ability=hazard.save_ability,
                save_dc=hazard.dc, save_succeeded=succeeded,
                damage_roll=aggregate_damage_components(components),
                damage_components=components,
                hp_before=hp_before, hp_after=mover.state.current_hp,
                is_dead=mover.state.is_dead,
                feature_id=hazard.action_id,
                animation=hazard.animation,
                description=(
                    f"{mover.state.template.name} {'succeeds' if succeeded else 'fails'} "
                    f"the save against {hazard.action_name} and takes {applied_total} "
                    f"{hazard.damage_type} damage."
                ),
            ))
            sequence += 1
            if hazard.remaining_damage_capacity <= 0:
                setup.persistent_hazards.remove(hazard)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Persistent hazard entry resolution failed for %s.", mover.combatant_id)
        raise RuntimeError("Persistent hazard entry could not be resolved.") from exc
