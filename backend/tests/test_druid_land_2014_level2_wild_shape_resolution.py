from __future__ import annotations

from app.combat.replacement_forms import resolve_replacement_form_action
from app.combat.state import build_combatant_state
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.replacement_form_compiler import compile_replacement_form_template


def test_level_two_wild_shape_action_enters_certified_wolf_form() -> None:
    thalen = build_thalen_greenbough_2014(2)
    state = build_combatant_state(thalen)
    action = thalen.replacement_form_actions[0]
    wolf = canonical_wild_shape_template_2014(2)
    active_form = compile_replacement_form_template(
        thalen,
        wolf,
        retain_spellcasting=action.retain_spellcasting,
    )

    result = resolve_replacement_form_action(state, action, active_form)

    assert result.source_id == "wild-shape"
    assert result.form_name == thalen.name
    assert result.resource_remaining == 1
    assert state.replacement_form is not None
    assert state.replacement_form.form_template.id.endswith("--form-2014-wolf")
    assert state.template.id.endswith("--form-2014-wolf")
    assert state.template.armor_class == wolf.armor_class
    assert state.template.speed_ft == wolf.speed_ft
    assert state.template.weapon_attack.weapon.id == wolf.weapon_attack.weapon.id
    assert state.action_available is False
    assert next(item for item in state.resources if item.id == "wild-shape").current_uses == 1
