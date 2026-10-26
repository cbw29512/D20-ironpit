"""Fight-only weapon penalties reach typed damage pipeline without harming riders."""
from __future__ import annotations

import pytest

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.models import OnHitDamage, RollMode


def _damage(state, attack):
    return resolve_weapon_damage(
        state, attack, FixedDiceProvider([6, 4]),
        critical=False, attack_mode=RollMode.NORMAL, turn_key="1:attacker",
    )


def test_corrosion_reduces_only_base_weapon_component_and_resets_next_fight():
    card = build_demo_fighter()
    before = card.model_dump_json()
    original = card.weapon_attack
    attack = original.model_copy(update={
        "on_hit_damage": [
            OnHitDamage(source="Acid rider", dice_count=1, dice_size=6, damage_type="acid"),
        ]
    })
    clean_state = build_combatant_state(card)
    clean, clean_parts = _damage(clean_state, attack)
    corroded_state = build_combatant_state(card)
    corroded_state.weapon_corrosion_penalties[attack.weapon.id] = 2
    damaged, parts = _damage(corroded_state, attack)
    assert parts[0].total == max(0, clean_parts[0].total - 2)
    assert parts[0].modifier == clean_parts[0].modifier - 2
    assert "corrosion -2" in parts[0].notation
    assert parts[1] == clean_parts[1]
    assert parts[1].total == 4
    assert damaged.total == clean.total - 2
    assert build_combatant_state(card).weapon_corrosion_penalties == {}
    assert card.model_dump_json() == before


def test_corrode_only_matching_weapon_and_clamp_base_to_zero():
    card = build_demo_fighter()
    attack = card.weapon_attack
    state = build_combatant_state(card)
    state.weapon_corrosion_penalties["different-weapon"] = 4
    clean, parts = _damage(state, attack.model_copy(update={"on_hit_damage": [
        OnHitDamage(source="Acid rider", dice_count=1, dice_size=6, damage_type="acid")
    ]}))
    assert "corrosion" not in parts[0].notation
    assert parts[1].total == 4
    state.weapon_corrosion_penalties[attack.weapon.id] = 4
    roll, affected = resolve_weapon_damage(
        state, attack.model_copy(update={"on_hit_damage": [
            OnHitDamage(source="Acid rider", dice_count=1, dice_size=6, damage_type="acid")
        ]}), FixedDiceProvider([1, 4]), critical=False,
        attack_mode=RollMode.NORMAL, turn_key="2:attacker",
    )
    assert affected[0].total >= 0
    assert affected[1].total == 4
    assert roll.total == affected[0].total + 4


def test_destroyed_weapon_fails_closed_in_shared_damage_pipeline():
    card = build_demo_fighter()
    state = build_combatant_state(card)
    state.weapon_corrosion_penalties[card.weapon_attack.weapon.id] = 5
    with pytest.raises(RuntimeError, match="Weapon damage could not be resolved"):
        resolve_weapon_damage(
            state, card.weapon_attack, FixedDiceProvider([6]), critical=False,
            attack_mode=RollMode.NORMAL, turn_key="3:attacker",
        )
