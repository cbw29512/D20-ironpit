from __future__ import annotations

from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014


def test_level_two_thalen_declares_canonical_wolf_wild_shape() -> None:
    hero = build_thalen_greenbough_2014(2)

    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 3,
        "wild-shape": 2,
    }
    assert len(hero.replacement_form_actions) == 1
    action = hero.replacement_form_actions[0]
    assert action.id == "wild-shape"
    assert action.action_cost == "action"
    assert action.form_template_id == "2014-wolf"
    assert action.resource_id == "wild-shape"
    assert action.resource_cost == 1
    assert action.voluntary_revert_action == "bonus_action"
    assert action.retain_spellcasting is False
