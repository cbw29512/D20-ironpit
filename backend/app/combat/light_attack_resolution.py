from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_action_targeting import select_slot_target
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.light_weapons import (
    LightExtraAttackPlan,
    mark_light_extra_attack_used,
    plan_light_extra_attack,
)
from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.actions import AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def _in_range(attack: WeaponAttack, distance_ft: int) -> bool:
    weapon = attack.weapon
    if weapon.attack_kind is WeaponAttackKind.MELEE:
        return distance_ft <= weapon.reach_ft
    return weapon.long_range_ft is not None and distance_ft <= weapon.long_range_ft


def _preferred_distance(attack: WeaponAttack) -> int:
    weapon = attack.weapon
    if weapon.attack_kind is WeaponAttackKind.MELEE:
        return weapon.reach_ft
    if weapon.normal_range_ft is None:
        raise ValueError(f"Ranged Light weapon {weapon.id!r} has no normal range.")
    return weapon.normal_range_ft


def _target_for_plan(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    plan: LightExtraAttackPlan,
):
    slot = AttackActionSlot(attack_ids=[plan.attack.id])
    return select_slot_target(attacker, setup, slot)


def resolve_light_extra_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    trigger_attack: WeaponAttack,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve the Light extra attack; Nick changes timing, never attack count."""
    try:
        plan = plan_light_extra_attack(attacker.state, trigger_attack, turn_key)
        if plan is None:
            return [], sequence
        if plan.uses_bonus_action and not is_available(attacker.state, "bonus_action"):
            return [], sequence
        target = _target_for_plan(attacker, setup, plan)
        if target is None:
            return [], sequence
        events: list[BattleEvent] = []
        distance = combatant_distance(attacker, target)
        if not _in_range(plan.attack, distance):
            moved, sequence, _ = move_toward_with_reactions(
                sequence,
                round_number,
                attacker,
                target,
                setup,
                _preferred_distance(plan.attack),
                dice,
                turn_key=turn_key,
            )
            events.extend(moved)
            if attacker.state.is_dead or attacker.state.is_unconscious:
                return events, sequence
            distance = combatant_distance(attacker, target)
            if not _in_range(plan.attack, distance):
                return events, sequence
        if plan.uses_bonus_action:
            spend(attacker.state, "bonus_action")
        mark_light_extra_attack_used(attacker.state, turn_key)
        pack = pack_tactics_active(attacker, target, setup)
        events.append(resolve_encounter_attack(
            sequence,
            round_number,
            attacker,
            target,
            plan.attack,
            distance,
            dice,
            setup,
            spend_action=False,
            advantage_sources=1 if pack else 0,
            feature_id=plan.feature_id,
            turn_key=turn_key,
            allow_reckless=True,
        ))
        return events, sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Light extra attack resolution failed for %s.", attacker.combatant_id)
        raise RuntimeError("Light extra attack could not be resolved.") from exc
