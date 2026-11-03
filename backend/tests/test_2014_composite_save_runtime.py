"""Runtime proof that one on-hit save applies both damage and timed condition or neither.

Source: 2014 Quasit Claws. Shared save roll; success negates both; failure applies both.
No second save. Universal, no name dispatch.
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from app.combat.on_hit_save_damage import resolve_on_hit_save_damage
from app.combat.on_hit_condition_save import resolve_on_hit_condition_save
from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.capability_effects import SaveDamageEffectDefinition
from app.domain.models import CombatantState, WeaponAttack
from app.domain.weapons import OnHitSaveDamage, OnHitConditionSave

logger = logging.getLogger(__name__)


def _compiled_attack():
    monster = next(m for m in load_monster_source_2014() if m.id == "quasit")
    source_attack = next(a for a in monster.attacks if a.id == "claws-bite-in-beast-form")
    effects = basic_attack_effects_2014(source_attack)
    composite = next(e for e in effects if isinstance(e, SaveDamageEffectDefinition))
    # Minimal WeaponAttack carrying the compiled effect for resolution.
    save_damage = OnHitSaveDamage(
        source=composite.source,
        save_ability=composite.save_ability,
        dc=composite.dc,
        dice_count=composite.dice.count,
        dice_size=composite.dice.size,
        damage_bonus=composite.dice.bonus,
        damage_type=composite.damage_type,
        success_damage=composite.success_damage,
        failed_save_condition=OnHitConditionSave(
            save_ability=composite.failed_save_condition.save_ability,
            dc=composite.failed_save_condition.dc,
            condition_id=composite.failed_save_condition.condition,
            duration_rounds=composite.failed_save_condition.duration_rounds,
            repeat_save_timing=composite.failed_save_condition.repeat_save_timing,
        ) if composite.failed_save_condition else None,
    )
    attack = WeaponAttack(
        id=source_attack.id,
        name=source_attack.name,
        on_hit_save_damage=save_damage,
    )
    return attack


def test_composite_failed_save_applies_damage_and_condition_once():
    try:
        attack = _compiled_attack()
        defender = CombatantState(id="target", current_hp=20, max_hp=20, is_alive=True)
        dice = MagicMock()
        # Force fail save (low roll) and fixed damage rolls.
        dice.roll.side_effect = [1, 2, 2]  # save 1, then 2d4=4
        resolution = resolve_on_hit_save_damage(defender, attack, dice)
        assert resolution.save_succeeded is False
        assert resolution.component is not None
        assert resolution.component.total > 0
        # Condition uses shared save, no second roll.
        cond = resolve_on_hit_condition_save(
            defender, attack, dice, source_template=None,
            source_id="quasit", round_number=1, affected_states=[], setup=None,
            target_id="target", shared_save=(resolution.save_roll, False),
        )
        assert cond.applied_condition == "poisoned"
        # Dice called only for save + damage, not second save.
        assert dice.roll.call_count == 3
    except Exception:
        logger.exception("Composite failed-save runtime failed")
        raise


def test_composite_successful_save_applies_neither():
    try:
        attack = _compiled_attack()
        defender = CombatantState(id="target", current_hp=20, max_hp=20, is_alive=True)
        dice = MagicMock()
        dice.roll.side_effect = [20]  # success, no damage roll
        resolution = resolve_on_hit_save_damage(defender, attack, dice)
        assert resolution.save_succeeded is True
        assert resolution.component is None
        cond = resolve_on_hit_condition_save(
            defender, attack, dice, source_template=None,
            source_id="quasit", round_number=1, affected_states=[], setup=None,
            target_id="target", shared_save=(resolution.save_roll, True),
        )
        assert cond.applied_condition is None
        assert dice.roll.call_count == 1  # only the save
    except Exception:
        logger.exception("Composite success runtime failed")
        raise
