from __future__ import annotations

import pytest

from app.combat.modifier_stack import add_modifier, effective_armor_class
from app.combat.state import build_combatant_state
from app.content.armor_class_rules import compile_armored_base_ac, defense_fighting_style_bonus
from app.content.audited_fighter import build_karnok_stoneward
from app.content.fighter_progression import build_karnok_stoneward_level
from app.domain.modifiers import CombatModifier, ModifierKind


def test_defense_style_adds_one_only_when_wearing_armor() -> None:
    assert defense_fighting_style_bonus("Defense", "heavy") == 1
    assert defense_fighting_style_bonus("Defense", "medium") == 1
    assert defense_fighting_style_bonus("Defense", "light") == 1
    assert defense_fighting_style_bonus("Defense", "none") == 0
    assert defense_fighting_style_bonus("Great Weapon Fighting", "heavy") == 0


def test_chain_mail_plus_defense_compiles_to_seventeen_ac() -> None:
    assert compile_armored_base_ac(16, "Defense", "heavy") == 17
    fighter = build_karnok_stoneward()
    assert fighter.fighting_style == "Defense"
    assert fighter.visual.armor == "chain-mail"
    assert fighter.armor_class == 17


def test_fighter_progression_retains_compiled_defense_ac() -> None:
    assert all(build_karnok_stoneward_level(level).armor_class == 17 for level in range(1, 10))


def test_runtime_effective_ac_starts_from_compiled_defense_ac_then_adds_temporary_modifiers() -> None:
    state = build_combatant_state(build_karnok_stoneward())
    assert effective_armor_class(state) == 17
    add_modifier(state, CombatModifier(
        id="test:shield-of-faith",
        source_id="cleric",
        source_effect_id="shield-of-faith",
        kind=ModifierKind.ARMOR_CLASS,
        flat_bonus=2,
    ))
    assert effective_armor_class(state) == 19


def test_invalid_armor_inputs_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unsupported armor category"):
        defense_fighting_style_bonus("Defense", "plate-ish")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="cannot be negative"):
        compile_armored_base_ac(-1, "Defense", "heavy")
