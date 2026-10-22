from __future__ import annotations

import pytest
from app.combat.state import build_combatant_state
from app.combat.replacement_forms import enter_declared_precombat_form
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def _forms():
    original = build_thalen_greenbough_2014(1)
    beast = original.model_copy(update={"id": "beast-form", "name": "Beast"})
    hybrid = original.model_copy(update={"id": "hybrid-form", "name": "Hybrid"})
    humanoid = original.model_copy(update={"id": "humanoid-form", "name": "Humanoid"})
    return original, {"beast": beast, "hybrid": hybrid, "humanoid": humanoid}


def test_declared_beast_form_enters_before_initiative_without_spending_turn_or_hp():
    original, forms = _forms()
    state = build_combatant_state(original)
    state.current_hp = original.max_hp - 4
    result = enter_declared_precombat_form(
        state, forms=forms, opening_form="beast",
        required_forms=("beast", "hybrid", "humanoid"),
    )
    assert result.form_name == "Beast"
    assert state.template.id == "beast-form"
    assert state.replacement_form.original_template.id == original.id
    assert state.replacement_form.hp_mode == "retain_owner"
    assert state.current_hp == original.max_hp - 4
    assert state.action_available and state.bonus_action_available
    assert set(forms) == {"beast", "hybrid", "humanoid"}


def test_precombat_form_rejects_missing_alternative_and_started_fight():
    original, forms = _forms()
    state = build_combatant_state(original)
    with pytest.raises(ValueError, match="Required source form"):
        enter_declared_precombat_form(state, forms={"beast": forms["beast"]},
                                     opening_form="beast", required_forms=("beast", "hybrid"))
    assert state.replacement_form is None
    state.initiative_roll = 12
    with pytest.raises(ValueError, match="fresh untransformed"):
        enter_declared_precombat_form(state, forms=forms, opening_form="beast")
