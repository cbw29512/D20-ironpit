"""Permanent combat proof for shared on-hit single-save damage + timed condition.

One Constitution save after hit: failure applies both typed poison damage and
Poisoned condition with source-declared duration/repeat; success applies neither.
No second save is rolled. Names never dispatch.
"""
from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType
from app.domain.on_hit_conditions import OnHitConditionSave
from app.domain.weapons import OnHitSaveDamage


def _attacker():
    state = build_combatant_state(build_karnok_stoneward().model_copy(update={"combat_traits": []}, deep=True))
    condition = OnHitConditionSave(
        save_ability="constitution", dc=10,
        condition_id="poisoned", duration_rounds=10,
        repeat_save_timing="target_turn_end",
    )
    attack = state.template.weapon_attack.model_copy(update={
        "id": "composite-poison-test",
        "on_hit_save_damage": OnHitSaveDamage(
            source="Quasit-style Poison", save_ability="constitution", dc=10,
            dice_count=2, dice_size=4, damage_type=DamageType.POISON,
            success_damage="none",
            failed_save_condition=condition,
        ),
    }, deep=True)
    return state, attack


def _target():
    source = build_goblin_warrior()
    bonuses = dict(source.saving_throw_bonuses); bonuses["constitution"] = 0
    template = source.model_copy(update={
        "armor_class": 10, "max_hp": 40, "saving_throw_bonuses": bonuses,
    }, deep=True)
    return build_combatant_state(template)


def test_failed_composite_save_applies_damage_and_poisoned():
    attacker, attack = _attacker()
    target = _target()
    # attack 15, weapon dmg 4+4, save 5 (fail), poison 2+2
    event = resolve_attack(1, 1, attacker, target, attack, 5, FixedDiceProvider([15, 4, 4, 5, 2, 2]), spend_action=False)
    assert event.hit is True
    assert event.save_succeeded is False
    assert event.save_dc == 10
    assert event.save_ability == "constitution"
    poison = next(c for c in event.damage_components if c.source == "Quasit-style Poison")
    assert poison.total == 4 and poison.applied_total == 4
    assert "poisoned" in event.applied_condition_ids
    assert target.active_effect_ids and any("poison" in e for e in target.active_effect_ids)


def test_successful_composite_save_applies_neither():
    attacker, attack = _attacker()
    target = _target()
    # attack 15, weapon dmg 4+4, save 15 (success), no poison dice consumed
    event = resolve_attack(1, 1, attacker, target, attack, 5, FixedDiceProvider([15, 4, 4, 15]), spend_action=False)
    assert event.hit is True
    assert event.save_succeeded is True
    assert all(c.source != "Quasit-style Poison" for c in event.damage_components)
    assert "poisoned" not in event.applied_condition_ids
    assert not any("poison" in e for e in (target.active_effect_ids or []))
