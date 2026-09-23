from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.grid_geometry import footprint_distance_ft
from app.combat.pit_policy import target_order
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_spell_attacks import PersistentSpellAttackAction, PersistentSpellAttackState
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)
_EFFECT_SIZE = CreatureSize.MEDIUM


def _effect_position(
    origin: GridPosition,
    origin_size: CreatureSize,
    target: EncounterCombatant,
    setup: EncounterSetup,
    movement_ft: int,
    reach_ft: int,
) -> tuple[GridPosition, int] | None:
    try:
        battle_map = setup.map_definition
        target_position = target.state.position
        if battle_map is None or target_position is None:
            raise ValueError("Persistent spell attacks require authoritative grid state.")
        candidates: list[tuple[int, int, int, GridPosition]] = []
        for x in range(battle_map.width_squares):
            for y in range(battle_map.height_squares):
                point = GridPosition(x=x, y=y)
                moved = footprint_distance_ft(origin, origin_size, point, _EFFECT_SIZE)
                if moved > movement_ft:
                    continue
                distance = footprint_distance_ft(
                    point, _EFFECT_SIZE, target_position, target.state.template.size,
                )
                if distance <= reach_ft:
                    candidates.append((moved, y, x, point))
        if not candidates:
            return None
        moved, _, _, point = min(candidates, key=lambda item: item[:3])
        return point, moved
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Persistent spell position search failed for %s.", target.combatant_id)
        raise RuntimeError("Persistent spell position could not be resolved.") from exc


def _active_state(
    member: EncounterCombatant,
    action: PersistentSpellAttackAction,
    round_number: int,
) -> PersistentSpellAttackState | None:
    try:
        member.state.persistent_spell_attacks = [
            item for item in member.state.persistent_spell_attacks
            if round_number < item.expires_round
        ]
        return next(
            (item for item in member.state.persistent_spell_attacks if item.action_id == action.id),
            None,
        )
    except Exception as exc:
        logger.exception("Persistent spell state lookup failed for %s.", member.combatant_id)
        raise RuntimeError("Persistent spell state could not be resolved.") from exc


def _cast_slot_level(
    member: EncounterCombatant,
    action: PersistentSpellAttackAction,
    turn_key: str,
) -> int | None:
    try:
        if not slot_spell_available(member.state, turn_key):
            return None
        levels = sorted(
            int(item.id.removeprefix("spell-slot-"))
            for item in member.state.resources
            if item.id.startswith("spell-slot-") and item.current_uses > 0
            and int(item.id.removeprefix("spell-slot-")) >= action.attack.level
        )
        return levels[0] if levels else None
    except Exception as exc:
        logger.exception("Persistent spell slot lookup failed for %s.", member.combatant_id)
        raise RuntimeError("Persistent spell slot could not be resolved.") from exc


def _attack_for_slot(
    action: PersistentSpellAttackAction,
    slot_level: int,
    *,
    repeat: bool,
):
    try:
        extra_dice = max(0, (slot_level - action.attack.level) // action.upcast_interval_levels)
        return action.attack.model_copy(update={
            "level": 0 if repeat else slot_level,
            "range_ft": action.attack_reach_ft if repeat else action.attack.range_ft,
            "damage_dice_count": action.attack.damage_dice_count + extra_dice,
        })
    except Exception as exc:
        logger.exception("Persistent spell attack scaling failed for %s.", action.id)
        raise RuntimeError("Persistent spell attack could not be scaled.") from exc


def resolve_persistent_spell_attack(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    dice,
):
    """Cast or repeat the first legal persistent spell attack declared by the combatant."""
    try:
        if not is_available(member.state, "bonus_action") or member.state.position is None:
            return None
        for action in member.state.template.persistent_spell_attack_actions:
            active = _active_state(member, action, round_number)
            origin = active.position if active is not None else member.state.position
            origin_size = _EFFECT_SIZE if active is not None else member.state.template.size
            movement = action.move_ft if active is not None else action.attack.range_ft
            for target in target_order(member, setup):
                placement = _effect_position(
                    origin, origin_size, target, setup, movement, action.attack_reach_ft,
                )
                if placement is None:
                    continue
                position, moved = placement
                slot_level = active.slot_level if active is not None else _cast_slot_level(member, action, turn_key)
                if slot_level is None:
                    continue
                attack = _attack_for_slot(action, slot_level, repeat=active is not None)
                distance = footprint_distance_ft(
                    position, _EFFECT_SIZE, target.state.position, target.state.template.size,
                )
                event = resolve_spell_attack(
                    sequence, round_number, member, target, attack, setup, turn_key, dice,
                    distance_override_ft=distance,
                )
                if active is None:
                    member.state.persistent_spell_attacks = [
                        item for item in member.state.persistent_spell_attacks if item.action_id != action.id
                    ]
                    member.state.persistent_spell_attacks.append(PersistentSpellAttackState(
                        action_id=action.id,
                        slot_level=slot_level,
                        position=position,
                        applied_round=round_number,
                        expires_round=round_number + action.duration_rounds,
                    ))
                else:
                    active.position = position
                event.movement_ft = moved
                event.grid_position_after = position
                return event
        return None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Persistent spell attack resolution failed for %s.", member.combatant_id)
        raise RuntimeError("Persistent spell attack could not be resolved.") from exc
