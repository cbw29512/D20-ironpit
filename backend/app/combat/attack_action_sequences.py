"""Select one immutable sequence before spending; preview and execution share it."""
from __future__ import annotations
import logging
from app.combat.attack_action_choices import attack_choice, save_choice
from app.combat.attack_action_rules import validate_attack_action_slots
from app.combat.printed_damage import weapon_mean_damage, save_mean_damage
from app.domain.attack_action_definitions import AttackActionVariant
from app.domain.models import WeaponAttackKind
logger = logging.getLogger(__name__)


def _preview_slot(attacker, setup, slot, mode, previous_target, previous_attack_available):
    try:
        if slot.requires_previous_hit and not previous_attack_available:
            return None, None
        if slot.same_target_as_previous and previous_target is None:
            return None, None
        target = previous_target if slot.same_target_as_previous else None
        chosen = attack_choice(attacker, setup, slot, mode=mode, target_override=target)
        saved = save_choice(attacker, setup, slot, target_override=target) if chosen is None else None
        return chosen, saved
    except Exception:
        logger.exception("Failed conditional sequence preview for %s.", attacker.combatant_id)
        raise


def sequence_damage(attacker, setup, variant, mode) -> float:
    try:
        total = 0.0
        previous_target = None
        previous_attack_available = False
        for slot in variant.slots:
            chosen, saved = _preview_slot(
                attacker, setup, slot, mode, previous_target, previous_attack_available,
            )
            if chosen:
                total += weapon_mean_damage(chosen[1])
                previous_target, previous_attack_available = chosen[0], True
            elif saved:
                total += save_mean_damage(saved[1])
                previous_target, previous_attack_available = saved[0], False
            else:
                previous_target, previous_attack_available = None, False
        return total
    except Exception:
        logger.exception("Failed sequence scoring for %s / %s.", attacker.combatant_id, variant.id)
        raise


def sequence_has_legal_choice(attacker, setup, variant, mode) -> bool:
    try:
        previous_target = None
        previous_attack_available = False
        for slot in variant.slots:
            chosen, saved = _preview_slot(
                attacker, setup, slot, mode, previous_target, previous_attack_available,
            )
            if chosen:
                return True
            if saved:
                return True
            previous_target, previous_attack_available = None, False
        return False
    except Exception:
        logger.exception("Failed sequence legality probe for %s / %s.", attacker.combatant_id, variant.id)
        raise


def select_sequence(attacker, setup):
    try:
        definition = attacker.state.template.attack_action
        if definition is None:
            return None
        validate_attack_action_slots(attacker)
        variants = definition.variants or [AttackActionVariant(id=definition.id, slots=definition.slots)]
        # Probe the printed sequences, not unrelated standalone weapons.
        melee = any((choice := attack_choice(attacker, setup, slot, mode=WeaponAttackKind.MELEE))
                    and choice[1].weapon.attack_kind is WeaponAttackKind.MELEE
                    for v in variants if v.attack_kind in {None, WeaponAttackKind.MELEE} for slot in v.slots)
        mode = WeaponAttackKind.MELEE if melee else WeaponAttackKind.RANGED
        permitted = [v for v in variants if v.attack_kind in {None, mode}]
        if not permitted:
            return None
        chosen = max(permitted, key=lambda v: sequence_damage(attacker, setup, v, mode))
        return (chosen, mode) if sequence_has_legal_choice(attacker, setup, chosen, mode) else None
    except Exception:
        logger.exception("Failed complete attack sequence selection for %s.", attacker.combatant_id)
        raise


def attack_action_melee_legal(attacker, setup) -> bool:
    try:
        selected = select_sequence(attacker, setup)
        return bool(selected and any((choice := attack_choice(attacker, setup, slot, mode=selected[1]))
                    and choice[1].weapon.attack_kind is WeaponAttackKind.MELEE for slot in selected[0].slots))
    except Exception:
        logger.exception("Failed melee sequence probe for %s.", attacker.combatant_id)
        raise


def attack_action_damage(attacker, setup) -> float:
    try:
        selected = select_sequence(attacker, setup)
        return sequence_damage(attacker, setup, *selected) if selected else 0.0
    except Exception:
        logger.exception("Failed sequence damage probe for %s.", attacker.combatant_id)
        raise
