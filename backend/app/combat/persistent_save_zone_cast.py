from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import start_concentration
from app.combat.encounter_targeting import combatant_distance
from app.combat.persistent_save_zone_resolution import resolve_save_zone_trigger
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.combat.suppression_zone_geometry import verbal_casting_blocked, zone_center_legal
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import BattleEvent
from app.domain.persistent_save_zones import PersistentSaveZoneAction, PersistentSaveZoneState

logger = logging.getLogger(__name__)


def _resource(caster: EncounterCombatant, resource_id: str | None):
    if resource_id is None:
        return None
    return next((item for item in caster.state.resources if item.id == resource_id), None)


def _scaled_dice(action: PersistentSaveZoneAction, slot_level: int) -> int:
    extra = max(0, slot_level - action.level) * action.upcast_dice_per_level
    return action.damage_dice_count + extra


def choose_save_zone_center(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: PersistentSaveZoneAction,
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
        logger.exception("Failed to choose save-zone center for %s.", caster.combatant_id)
        raise


def choose_save_zone_action(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> tuple[PersistentSaveZoneAction, GridPosition] | None:
    try:
        if verbal_casting_blocked(caster, setup):
            return None
        for action in caster.state.template.persistent_save_zone_actions:
            if not is_available(caster.state, action.action_cost):
                continue
            if action.concentration and caster.state.concentration is not None:
                continue
            if action.expends_spell_slot and not slot_spell_available(caster.state, turn_key):
                continue
            resource = _resource(caster, action.resource_id)
            if action.resource_id and (resource is None or resource.current_uses < action.resource_cost):
                continue
            center = choose_save_zone_center(caster, setup, action)
            if center is not None:
                return action, center
        return None
    except Exception:
        logger.exception("Failed save-zone choice for %s.", caster.combatant_id)
        raise


def cast_save_zone(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: PersistentSaveZoneAction,
    position: GridPosition,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
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
        slot_level = action.level
        if action.resource_id and action.resource_id.startswith("spell-slot-"):
            slot_level = int(action.resource_id.rsplit("-", 1)[1])
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
        zone = PersistentSaveZoneState(
            zone_id=f"{caster.combatant_id}:{action.id}:{round_number}:{len(setup.save_zones) + 1}",
            source_id=caster.combatant_id,
            source_side=caster.side,
            action_id=action.id,
            action_name=action.name,
            position=position.model_copy(deep=True),
            radius_ft=action.radius_ft,
            expires_round=round_number + action.duration_rounds,
            save_ability=action.save_ability,
            dc=action.dc,
            triggers=list(action.triggers),
            save_triggers=list(action.save_triggers),
            once_per_turn=action.once_per_turn,
            damage_dice_count=_scaled_dice(action, slot_level),
            damage_dice_size=action.damage_dice_size,
            damage_type=action.damage_type,
            success_damage=action.success_damage,
            failed_save_condition_id=action.failed_save_condition_id,
            failed_save_duration_rounds=action.failed_save_duration_rounds,
            failed_save_suppress_action=action.failed_save_suppress_action,
            failed_save_suppress_bonus_action=action.failed_save_suppress_bonus_action,
            concentration=action.concentration,
            animation=action.animation,
        )
        setup.save_zones.append(zone)
        events = [BattleEvent(
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
        )]
        sequence += 1
        if "appear" in action.triggers:
            for member in [*setup.heroes, *setup.monsters]:
                more, sequence = resolve_save_zone_trigger(
                    sequence, round_number, member, setup, zone, dice, turn_key, "appear",
                )
                events.extend(more)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Save zone cast failed for %s.", caster.combatant_id)
        raise RuntimeError("Save zone could not be created.") from exc
