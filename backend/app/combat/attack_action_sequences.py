"""Select one immutable sequence before spending; preview and execution share it."""
from __future__ import annotations
import logging
from app.combat.dice import roll_dice
from app.combat.attack_action_choices import attack_choice, save_choice, followup_target
from app.combat.attack_action_rules import validate_attack_action_slots
from app.combat.printed_damage import weapon_mean_damage, save_mean_damage
from app.domain.attack_action_definitions import AttackActionVariant
from app.domain.models import WeaponAttackKind, DiceRoll
logger = logging.getLogger(__name__)


def sequence_choices(attacker, setup, variant, mode):
    """Printed maximum damage preview assumes a legal preceding attack hits."""
    try:
        choices, previous = [], None
        for slot in variant.slots:
            eligible, target_id = followup_target(slot, True if previous else None,
                                                  previous[0].combatant_id if previous else None)
            chosen = attack_choice(attacker, setup, slot, mode=mode, target_id=target_id) if eligible else None
            saved = save_choice(attacker, setup, slot) if eligible and chosen is None else None
            choices.append((chosen, saved))
            previous = chosen
        return choices
    except Exception:
        logger.exception("Failed sequence preview for %s / %s.", attacker.combatant_id, variant.id)
        raise


def sequence_damage(attacker, setup, variant, mode) -> float:
    try:
        multiplier = variant.repetitions.dice_count * (variant.repetitions.dice_size + 1) / 2 if variant.repetitions else 1
        return multiplier * sum(weapon_mean_damage(chosen[1]) if chosen else save_mean_damage(saved[1]) if saved else 0
                   for chosen, saved in sequence_choices(attacker, setup, variant, mode))
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
        melee = any(choice and choice[1].weapon.attack_kind is WeaponAttackKind.MELEE
                    for v in variants if v.attack_kind in {None, WeaponAttackKind.MELEE}
                    for choice, _ in sequence_choices(attacker, setup, v, WeaponAttackKind.MELEE))
        mode = WeaponAttackKind.MELEE if melee else WeaponAttackKind.RANGED
        permitted = [v for v in variants if v.attack_kind in {None, mode}]
        if not permitted:
            return None
        chosen = max(permitted, key=lambda v: sequence_damage(attacker, setup, v, mode))
        legal = any(attack or saved for attack, saved in sequence_choices(attacker, setup, chosen, mode))
        return (chosen, mode) if legal else None
    except Exception:
        logger.exception("Failed complete attack sequence selection for %s.", attacker.combatant_id)
        raise


def attack_action_melee_legal(attacker, setup) -> bool:
    try:
        selected = select_sequence(attacker, setup)
        return bool(selected and any(choice and choice[1].weapon.attack_kind is WeaponAttackKind.MELEE
                    for choice, _ in sequence_choices(attacker, setup, *selected)))
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


def expanded_sequence_slots(variant, dice):
    """Freeze a printed random count once, after Action spending, using shared dice."""
    try:
        if variant.repetitions is None:
            return variant.slots, None
        spec = variant.repetitions
        rolls = [roll_dice(dice, 1, spec.dice_size) for _ in range(spec.dice_count)]
        roll = DiceRoll(notation=f"{spec.dice_count}d{spec.dice_size}", rolls=rolls, total=sum(rolls))
        return variant.slots * roll.total, roll
    except Exception:
        logger.exception("Failed sequence repetition for %s.", variant.id)
        raise
