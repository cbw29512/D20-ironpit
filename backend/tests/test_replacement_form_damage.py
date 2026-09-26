from __future__ import annotations

from app.combat.replacement_forms import enter_replacement_form
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.combatants import ResourceDefinition


class FixedDice:
    def roll(self, sides: int) -> int:
        return 10


def _state():
    template = build_thalen_greenbough_2014(1).model_copy(update={
        "resources": [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2)],
    })
    state = build_combatant_state(template)
    form = template.model_copy(update={
        "id": "test-wolf-form",
        "name": "Wolf",
        "kind": "monster",
        "max_hp": 11,
        "armor_class": 13,
        "speed_ft": 40,
    })
    enter_replacement_form(
        state,
        source_id="wild-shape",
        source_name="Wild Shape",
        form_template=form,
        action_cost="action",
        resource_id="wild-shape",
    )
    return state


def test_damage_is_absorbed_by_form_hp_before_original_hp() -> None:
    state = _state()
    original_hp = state.current_hp

    outcome = apply_damage(state, 5, dice=FixedDice())

    assert outcome == "damaged"
    assert state.current_hp == original_hp
    assert state.replacement_form is not None
    assert state.replacement_form.form_hp == 6


def test_zero_form_hp_reverts_and_excess_damage_hits_original_body() -> None:
    state = _state()
    original_hp = state.current_hp

    outcome = apply_damage(state, 15, dice=FixedDice())

    assert outcome == "damaged"
    assert state.replacement_form is None
    assert state.current_hp == original_hp - 4


def test_exact_form_hp_damage_reverts_without_harming_original_body() -> None:
    state = _state()
    original_hp = state.current_hp

    outcome = apply_damage(state, 11, dice=FixedDice())

    assert outcome == "damaged"
    assert state.replacement_form is None
    assert state.current_hp == original_hp
