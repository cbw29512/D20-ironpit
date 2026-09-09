from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.pit_policy import (
    allied_frontline_active,
    choose_attack,
    flexible_slot_has_both,
    has_backline_target,
    has_frontline_target,
    is_backline,
    save_distance,
    target_order,
)
from app.combat.resources import resource_available
from app.combat.saving_throws import legal_save_action
from app.domain.actions import AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import WeaponAttackKind

logger = logging.getLogger(__name__)


def save_choice(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    slot: AttackActionSlot,
):
    try:
        allowed = set(slot.save_action_ids)
        for target in target_order(attacker, setup):
            for action in attacker.state.template.saving_throw_actions:
                if action.id not in allowed:
                    continue
                if not resource_available(attacker.state, action.resource_id, action.resource_cost):
                    continue
                distance = save_distance(attacker, target, action.range_ft)
                if legal_save_action(action, target, distance):
                    return target, action, distance
        return None
    except Exception:
        logger.exception("Failed to choose save slot for %s.", attacker.combatant_id)
        raise


def attack_choice(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    slot: AttackActionSlot,
    *,
    ranged_backline: bool = False,
):
    try:
        if ranged_backline:
            choice = choose_attack(
                attacker, setup, slot.attack_ids,
                kind=WeaponAttackKind.RANGED, prefer_backline=True,
            )
            if choice is not None:
                return choice
        if is_backline(attacker) and allied_frontline_active(attacker, setup):
            ranged = choose_attack(attacker, setup, slot.attack_ids, kind=WeaponAttackKind.RANGED)
            if ranged is not None:
                return ranged
        melee = choose_attack(attacker, setup, slot.attack_ids, kind=WeaponAttackKind.MELEE)
        if melee is not None:
            return melee
        return choose_attack(attacker, setup, slot.attack_ids, kind=WeaponAttackKind.RANGED)
    except Exception:
        logger.exception("Failed to choose attack slot for %s.", attacker.combatant_id)
        raise


def slot_has_legal_choice(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    slot: AttackActionSlot,
) -> bool:
    try:
        return attack_choice(attacker, setup, slot) is not None or save_choice(attacker, setup, slot) is not None
    except Exception:
        logger.exception("Failed to prove legal Attack/Multiattack slot for %s.", attacker.combatant_id)
        raise


def use_ranged_split(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    slots: list[AttackActionSlot],
    dice: DiceProvider,
) -> bool:
    """Frontline mixed attackers have a 25% chance for one later shot at the enemy backline."""
    try:
        if is_backline(attacker):
            return False
        if not has_frontline_target(attacker, setup) or not has_backline_target(attacker, setup):
            return False
        if not any(flexible_slot_has_both(attacker, slot.attack_ids) for slot in slots[1:]):
            return False
        return dice.roll(100) >= 76
    except Exception:
        logger.exception("Failed to evaluate ranged split for %s.", attacker.combatant_id)
        raise
