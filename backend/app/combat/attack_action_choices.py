from __future__ import annotations

import logging

from app.combat.pit_policy import (
    choose_attack,
    flexible_slot_has_both,
    save_distance,
    target_order,
)
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


def flexible_attack_mode(attacker: EncounterCombatant, setup: EncounterSetup) -> WeaponAttackKind:
    try:
        ids = [attacker.state.template.weapon_attack.id,
               *(a.id for a in attacker.state.template.alternate_weapon_attacks)]
        return WeaponAttackKind.MELEE if choose_attack(attacker, setup, ids, kind=WeaponAttackKind.MELEE) else WeaponAttackKind.RANGED
    except Exception:
        logger.exception("Failed flexible attack mode for %s.", attacker.combatant_id)
        raise


def attack_choice(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    slot: AttackActionSlot,
    *, mode: WeaponAttackKind | None = None,
):
    """Choose a printed Multiattack option using legal melee reach before damage scoring."""
    try:
        if flexible_slot_has_both(attacker, slot.attack_ids):
            preferred = mode or flexible_attack_mode(attacker, setup)
            return choose_attack(attacker, setup, slot.attack_ids, kind=preferred)

        melee = choose_attack(attacker, setup, slot.attack_ids, kind=WeaponAttackKind.MELEE)
        if melee is not None:
            return melee
        return choose_attack(attacker, setup, slot.attack_ids, kind=WeaponAttackKind.RANGED)
    except Exception:
        logger.exception("Failed to choose attack slot for %s.", attacker.combatant_id)
        raise
