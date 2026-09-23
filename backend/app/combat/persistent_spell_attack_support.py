from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_spell_attacks import PersistentSpellAttackAction, PersistentSpellAttackState
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)
PERSISTENT_EFFECT_SIZE = CreatureSize.MEDIUM


def effect_position(
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
                moved = footprint_distance_ft(
                    origin, origin_size, point, PERSISTENT_EFFECT_SIZE,
                )
                if moved > movement_ft:
                    continue
                distance = footprint_distance_ft(
                    point,
                    PERSISTENT_EFFECT_SIZE,
                    target_position,
                    target.state.template.size,
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


def active_state(
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


def cast_slot_level(
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
            if item.id.startswith("spell-slot-")
            and item.current_uses > 0
            and int(item.id.removeprefix("spell-slot-")) >= action.attack.level
        )
        return levels[0] if levels else None
    except Exception as exc:
        logger.exception("Persistent spell slot lookup failed for %s.", member.combatant_id)
        raise RuntimeError("Persistent spell slot could not be resolved.") from exc


def attack_for_slot(
    action: PersistentSpellAttackAction,
    slot_level: int,
    *,
    repeat: bool,
):
    try:
        extra_dice = max(
            0,
            (slot_level - action.attack.level) // action.upcast_interval_levels,
        )
        return action.attack.model_copy(update={
            "level": 0 if repeat else slot_level,
            "range_ft": action.attack_reach_ft if repeat else action.attack.range_ft,
            "damage_dice_count": action.attack.damage_dice_count + extra_dice,
        })
    except Exception as exc:
        logger.exception("Persistent spell attack scaling failed for %s.", action.id)
        raise RuntimeError("Persistent spell attack could not be scaled.") from exc
