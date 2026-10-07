"""Select one immutable sequence before spending; preview and execution share it."""
from __future__ import annotations
import logging
from app.combat.attack_action_choices import attack_choice, save_choice
from app.combat.attack_action_rules import validate_attack_action_slots
from app.combat.printed_damage import weapon_mean_damage, save_mean_damage
from app.domain.attack_action_definitions import AttackActionVariant
from app.domain.models import WeaponAttackKind
logger = logging.getLogger(__name__)


def sequence_damage(attacker, setup, variant, mode) -> float:
    try:
        total = 0.0
        for slot in variant.slots:
            chosen = attack_choice(attacker, setup, slot, mode=mode)
            saved = save_choice(attacker, setup, slot) if chosen is None else None
            total += weapon_mean_damage(chosen[1]) if chosen else save_mean_damage(saved[1]) if saved else 0
        return total
    except Exception:
        logger.exception("Failed sequence scoring for %s / %s.", attacker.combatant_id, variant.id)
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
        legal = any(attack_choice(attacker, setup, slot, mode=mode) or save_choice(attacker, setup, slot)
                    for slot in chosen.slots)
        return (chosen, mode) if legal else None
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
