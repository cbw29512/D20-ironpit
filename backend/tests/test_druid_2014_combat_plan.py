from __future__ import annotations

from app.content.druid_2014_combat_plan import druid_2014_combat_plan


def test_land_druid_combat_plan_preserves_opening_buff_then_concentration_then_form() -> None:
    level_two = druid_2014_combat_plan(2)
    level_four = druid_2014_combat_plan(4)
    level_eight = druid_2014_combat_plan(8)

    assert level_two.opening_buff_id == "longstrider"
    assert level_two.concentration_spell_id == "faerie-fire"
    assert level_two.wild_shape_form_id == "2014-wolf"
    assert level_two.opening_buff_before_initiative is True
    assert level_two.concentration_before_wild_shape is True

    assert level_four.wild_shape_form_id == "2014-crocodile"
    assert level_eight.wild_shape_form_id == "2014-brown-bear"
