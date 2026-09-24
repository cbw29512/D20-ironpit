from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.grid_geometry import footprint_distance_ft
from app.combat.persistent_spell_attack_support import (
    PERSISTENT_EFFECT_SIZE,
    active_state,
    attack_for_slot,
    cast_slot_level,
    effect_position,
)
from app.combat.pit_policy import target_order
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.persistent_spell_attacks import PersistentSpellAttackState

logger = logging.getLogger(__name__)


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
            active = active_state(member, action, round_number)
            origin = active.position if active is not None else member.state.position
            origin_size = PERSISTENT_EFFECT_SIZE if active is not None else member.state.template.size
            movement = action.move_ft if active is not None else action.attack.range_ft
            for target in target_order(member, setup):
                placement = effect_position(
                    origin,
                    origin_size,
                    target,
                    setup,
                    movement,
                    action.attack_reach_ft,
                )
                if placement is None:
                    continue
                position, moved = placement
                slot_level = (
                    active.slot_level
                    if active is not None
                    else cast_slot_level(member, action, turn_key)
                )
                if slot_level is None:
                    continue
                attack = attack_for_slot(action, slot_level, repeat=active is not None)
                distance = footprint_distance_ft(
                    position,
                    PERSISTENT_EFFECT_SIZE,
                    target.state.position,
                    target.state.template.size,
                )
                event = resolve_spell_attack(
                    sequence,
                    round_number,
                    member,
                    target,
                    attack,
                    setup,
                    turn_key,
                    dice,
                    distance_override_ft=distance,
                )
                if active is None:
                    member.state.persistent_spell_attacks = [
                        item
                        for item in member.state.persistent_spell_attacks
                        if item.action_id != action.id
                    ]
                    member.state.persistent_spell_attacks.append(
                        PersistentSpellAttackState(
                            action_id=action.id,
                            slot_level=slot_level,
                            position=position,
                            applied_round=round_number,
                            expires_round=round_number + action.duration_rounds,
                        )
                    )
                else:
                    active.position = position
                event.movement_ft = moved
                event.grid_position_after = position
                return event
        return None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Persistent spell attack resolution failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Persistent spell attack could not be resolved.") from exc
