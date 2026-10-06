from __future__ import annotations

import logging

from app.combat.pit_policy import (
    allied_frontline_active,
    choose_attack,
    flexible_slot_has_both,
    is_backline,
    save_distance,
    target_order,
)
from app.combat.printed_damage import weapon_mean_damage, save_mean_damage as _save_mean_damage
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
                distance = save_distance(attacker, target, action.range_ft)
                if legal_save_action(action, target, distance, source_id=attacker.combatant_id):
                    return target, action, distance
        return None
    except Exception:
        logger.exception("Failed to choose save slot for %s.", attacker.combatant_id)
        raise


def attack_choice(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    slot: AttackActionSlot,
):
    """Choose a printed Multiattack option using deterministic formation-row policy."""
    try:
        if flexible_slot_has_both(attacker, slot.attack_ids):
            if is_backline(attacker):
                preferred = (
                    WeaponAttackKind.RANGED
                    if allied_frontline_active(attacker, setup)
                    else WeaponAttackKind.MELEE
                )
            else:
                preferred = WeaponAttackKind.MELEE
            return choose_attack(attacker, setup, slot.attack_ids, kind=preferred)

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


def attack_action_melee_legal(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    try:
        definition = attacker.state.template.attack_action
        if definition is None:
            return False
        for slot in definition.slots:
            choice = attack_choice(attacker, setup, slot)
            if choice is not None and choice[1].weapon.attack_kind is WeaponAttackKind.MELEE:
                return True
        return False
    except Exception:
        logger.exception("Failed melee Attack-action probe for %s.", attacker.combatant_id)
        raise


def attack_action_damage(attacker: EncounterCombatant, setup: EncounterSetup) -> float:
    try:
        definition = attacker.state.template.attack_action
        if definition is None:
            return 0.0
        total = 0.0
        for slot in definition.slots:
            chosen = attack_choice(attacker, setup, slot)
            saved = save_choice(attacker, setup, slot) if chosen is None else None
            total += weapon_mean_damage(chosen[1]) if chosen else _save_mean_damage(saved[1]) if saved else 0.0
        return total
    except Exception:
        logger.exception("Failed Attack/Multiattack damage scoring for %s.", attacker.combatant_id)
        raise
