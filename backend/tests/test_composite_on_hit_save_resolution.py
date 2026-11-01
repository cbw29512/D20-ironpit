"""Permanent resolution proof: one shared save applies ordered damage and timed condition.

Reuses existing on-hit save-damage and timed-condition primitives. No source-name dispatch.
"""
from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType
from app.domain.on_hit_conditions import OnHitConditionSave
from app.domain.weapons import OnHitSaveDamage

logger = logging.getLogger(__name__)


def _attacker():
    try:
        state = build_combatant_state(build_karnok_stoneward().model_copy(update={"combat_traits": []}, deep=True))
        attack = state.template.weapon_attack.model_copy(update={
            "id": "composite-poison-test",
            "on_hit_save_damage": OnHitSaveDamage(
                source="Quasit-style Poison",
                save_ability="constitution",
                dc=10,
                dice_count=2,
                dice_size=4,
                damage_type=DamageType.POISON,
                success_damage="none",
                failed_save_condition=OnHitConditionSave(
                    save_ability="constitution",
                    dc=10,
                    condition_id="poisoned",
                    duration_rounds=10,
                    repeat_save_timing="target_turn_end",
                ),
            ),
        }, deep=True)
        return state, attack
    except Exception:
        logger.exception("Composite test attacker setup failed")
        raise


def _target():
    try:
        source = build_goblin_warrior()
        bonuses = dict(source.saving_throw_bonuses)
        bonuses["constitution"] = 0
        template = source.model_copy(update={
            "armor_class": 10,
            "max_hp": 40,
            "saving_throw_bonuses": bonuses,
        }, deep=True)
        return build_combatant_state(template)
    except Exception:
        logger.exception("Composite test target setup failed")
        raise


def test_failed_composite_save_applies_damage_and_poisoned():
    try:
        target = _target()
        attacker, attack = _attacker()
        event = resolve_attack(1, 1, attacker, target, attack, 5, FixedDiceProvider([15, 3, 2, 5]), spend_action=False)
        assert event.hit is True
        assert event.save_succeeded is False
        poison = next(c for c in event.damage_components if c.source == "Quasit-style Poison")
        assert poison.total == 5
        assert "poisoned" in event.applied_conditions
        assert target.conditions.get("poisoned") is not None
    except Exception:
        logger.exception("Failed composite resolution test")
        raise


def test_successful_composite_save_applies_neither():
    try:
        target = _target()
        attacker, attack = _attacker()
        event = resolve_attack(1, 1, attacker, target, attack, 5, FixedDiceProvider([15, 3, 2, 15]), spend_action=False)
        assert event.hit is True
        assert event.save_succeeded is True
        poison = next((c for c in event.damage_components if c.source == "Quasit-style Poison"), None)
        assert poison is None or poison.applied_total == 0
        assert "poisoned" not in event.applied_conditions
        assert target.conditions.get("poisoned") is None
    except Exception:
        logger.exception("Successful composite resolution test")
        raise
