from __future__ import annotations

from app.combat.state import build_combatant_state
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.domain.replacement_forms import ReplacementFormState


def test_replacement_form_state_preserves_original_template_and_separate_hp_pool() -> None:
    thalen = build_thalen_greenbough_2014(1)
    state = build_combatant_state(thalen)
    form = thalen.model_copy(update={
        "id": "test-wolf-form",
        "name": "Wolf",
        "max_hp": 11,
        "armor_class": 13,
        "speed_ft": 40,
    })

    state.replacement_form = ReplacementFormState(
        source_id="wild-shape",
        source_name="Wild Shape",
        original_template=thalen,
        form_template=form,
        original_hp=state.current_hp,
        form_hp=form.max_hp,
        form_max_hp=form.max_hp,
        resource_id="wild-shape",
    )

    assert state.template.id == thalen.id
    assert state.current_hp == thalen.max_hp
    assert state.replacement_form.original_template.id == thalen.id
    assert state.replacement_form.form_template.id == "test-wolf-form"
    assert state.replacement_form.form_hp == 11
