from __future__ import annotations

from app.combat.modifier_stack import effective_armor_class
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.state import build_combatant_state
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.spell_modifiers import SpellModifierEffect


def test_minimum_ac_modifier_sets_floor_without_erasing_higher_ac() -> None:
    state = build_combatant_state(build_thalen_greenbough_2014(1))
    modifier = build_spell_modifier(
        "druid", "druid", "barkskin",
        SpellModifierEffect(kind="armor-class-minimum", minimum_value=16),
        0, "Barkskin", concentration_required=True, round_number=1,
    )
    state.active_modifiers.append(modifier)
    assert effective_armor_class(state) == 16

    state.template = state.template.model_copy(update={"armor_class": 18})
    assert effective_armor_class(state) == 18
