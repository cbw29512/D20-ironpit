from __future__ import annotations

from app.combat.replacement_forms import enter_replacement_form, revert_replacement_form
from app.combat.state import build_combatant_state
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.domain.combatants import ResourceDefinition
from app.domain.modifiers import ConcentrationState


def _wolf_form(template):
    wolf = canonical_wild_shape_template_2014(2)
    return compile_replacement_form_template(template, wolf)


def test_replacement_form_spends_action_and_resource_but_preserves_concentration() -> None:
    template = build_thalen_greenbough_2014(1).model_copy(update={
        "resources": [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2)],
    })
    state = build_combatant_state(template)
    state.concentration = ConcentrationState(source_id="druid", effect_id="faerie-fire", started_round=0)

    result = enter_replacement_form(
        state,
        source_id="wild-shape",
        source_name="Wild Shape",
        form_template=_wolf_form(template),
        action_cost="action",
        resource_id="wild-shape",
    )

    assert state.action_available is False
    assert state.replacement_form is not None
    assert state.template.id.endswith("--form-2014-wolf")
    assert state.replacement_form.form_hp == state.template.max_hp
    assert state.resources[0].current_uses == 1
    assert state.concentration is not None
    assert state.concentration.effect_id == "faerie-fire"
    assert result.resource_remaining == 1


def test_voluntary_revert_uses_bonus_action_and_keeps_original_hp() -> None:
    template = build_thalen_greenbough_2014(1).model_copy(update={
        "resources": [ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2)],
    })
    state = build_combatant_state(template)
    state.current_hp = 6
    enter_replacement_form(
        state,
        source_id="wild-shape",
        source_name="Wild Shape",
        form_template=_wolf_form(template),
        action_cost="action",
        resource_id="wild-shape",
    )
    state.bonus_action_available = True

    result = revert_replacement_form(state, spend_voluntary_action=True)

    assert result.reverted is True
    assert state.replacement_form is None
    assert state.template.id == template.id
    assert state.current_hp == 6
    assert state.bonus_action_available is False
