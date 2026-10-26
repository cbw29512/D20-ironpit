"""Unit-level Rust/Gray Ooze-compatible weapon-instance corrosion semantics."""
from __future__ import annotations

import pytest

from app.combat.state import build_combatant_state
from app.combat.weapon_corrosion import (
    apply_weapon_corrosion_damage_penalty, corrode_weapon_after_hit,
    corrosion_penalty, weapon_available_after_corrosion,
)
from app.content.demo import build_demo_fighter


def test_independent_fight_only_weapon_corrosion_and_immutable_card():
    hero = build_demo_fighter()
    before = hero.model_dump_json()
    state = build_combatant_state(hero)
    for eligible in (False,):
        assert corrode_weapon_after_hit(state, "steel-one", hit=True, nonmagical_metal=eligible) == 0
    assert corrode_weapon_after_hit(state, "steel-one", hit=False, nonmagical_metal=True) == 0
    for n in range(1, 6):
        assert corrode_weapon_after_hit(state, "steel-one", hit=True, nonmagical_metal=True) == -n
        assert corrosion_penalty(state, "steel-one") == -n
        assert weapon_available_after_corrosion(state, "steel-one") == (n < 5)
        assert corrosion_penalty(state, "steel-two") == 0
    assert apply_weapon_corrosion_damage_penalty(state, "steel-two", 2) == 2
    with pytest.raises(ValueError, match="Destroyed weapon"):
        apply_weapon_corrosion_damage_penalty(state, "steel-one", 9)
    with pytest.raises(ValueError, match="destroyed weapon"):
        corrode_weapon_after_hit(state, "steel-one", hit=True, nonmagical_metal=True)
    assert build_combatant_state(hero).weapon_corrosion_penalties == {}
    assert hero.model_dump_json() == before


def test_weapon_penalty_reduces_damage_only_and_clamps_at_zero():
    state = build_combatant_state(build_demo_fighter())
    corrode_weapon_after_hit(state, "steel", hit=True, nonmagical_metal=True)
    assert apply_weapon_corrosion_damage_penalty(state, "steel", 7) == 6
    assert apply_weapon_corrosion_damage_penalty(state, "steel", 0) == 0
    assert corrosion_penalty(state, "steel") == -1
    with pytest.raises(ValueError, match="weapon-instance"):
        corrode_weapon_after_hit(state, "", hit=True, nonmagical_metal=True)
    with pytest.raises(ValueError, match="nonnegative"):
        apply_weapon_corrosion_damage_penalty(state, "steel", -1)
