from __future__ import annotations

import logging

from app.combat.pit_policy import (
    choose_attack,
    flexible_slot_has_both,
    save_distance,
    target_order,
)
from app.combat.saving_throws import legal_save_action
from app.combat.resources import resource_available
from app.domain.actions import AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import WeaponAttackKind

logger = logging.getLogger(__name__)


def slot_grapple_eligible(attacker, setup, slot) -> bool:
    """Check current fight state, not a previous attack's cached outcome."""
    if not slot.requires_source_grapple:
        return True
    return any(
        any(grapple.source_id == attacker.combatant_id for grapple in target.state.grapple_sources)
        for target in [*setup.heroes, *setup.monsters]
        if target.combatant_id != attacker.combatant_id and not target.state.is_dead
    )


def target_grappled_by_actor(actor, target) -> bool:
    """Only an actor's own grapple authorizes grapple-gated target actions."""
    return any(source.source_id == actor.combatant_id for source in target.state.grapple_sources)


def save_choice(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    slot: AttackActionSlot,
):
    try:
        allowed = set(slot.save_action_ids)
        for target in target_order(attacker, setup):
            if slot.requires_source_grapple and not target_grappled_by_actor(attacker, target):
                continue
            for action in attacker.state.template.saving_throw_actions:
                if action.id not in allowed:
                    continue
                if getattr(action, 'resource_id', None) is not None and not resource_available(attacker.state, action.resource_id, action.resource_cost):
                    continue
                distance = save_distance(attacker, target, action.range_ft)
                if legal_save_action(action, target, distance, source_id=attacker.combatant_id, actor=attacker):
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
    *, mode: WeaponAttackKind | None = None, target_id: str | None = None,
):
    """Choose a printed Multiattack option using legal melee reach before damage scoring."""
    try:
        if flexible_slot_has_both(attacker, slot.attack_ids):
            preferred = mode or flexible_attack_mode(attacker, setup)
            return choose_attack(attacker, setup, slot.attack_ids, kind=preferred, target_id=target_id)

        melee = choose_attack(attacker, setup, slot.attack_ids, kind=WeaponAttackKind.MELEE, target_id=target_id)
        if melee is not None:
            return melee
        return choose_attack(attacker, setup, slot.attack_ids, kind=WeaponAttackKind.RANGED, target_id=target_id)
    except Exception:
        logger.exception("Failed to choose attack slot for %s.", attacker.combatant_id)
        raise


def followup_target(slot, previous_hit, previous_target_id):
    """Require the immediately preceding slot's attack outcome, then lock if printed."""
    try:
        rule = slot.previous_attack
        if rule is None:
            return True, None
        if previous_hit is None or (rule.hit and previous_hit is not True):
            return False, None
        if rule.same_target and not previous_target_id:
            return False, None
        return True, previous_target_id if rule.same_target else None
    except Exception:
        logger.exception("Failed previous-attack slot condition for target %s.", previous_target_id)
        raise
