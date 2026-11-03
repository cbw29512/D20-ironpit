from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_priest_divine_eminence_binds_slot_scaled_bonus_actions():
    source = next(m for m in load_monster_source_2014() if m.name == "Priest")
    definition = adapt_monster_mechanics_2014(source)
    actions = [action for action in definition.timed_self_buff_actions if action.id.startswith("divine-eminence-slot-")]
    assert len(actions) == 3
    by_level = {int(action.id.rsplit("-", 1)[1]): action for action in actions}
    assert by_level[1].resource_id == "spell-slot-1"
    assert by_level[1].action_cost == "bonus_action"
    assert by_level[1].duration_rounds == 1
    assert by_level[1].expiry_timing == "source_turn_end"
    assert by_level[1].magical_effect is True
    effect = by_level[1].modifier_effects[0]
    assert effect.kind == "bonus-damage"
    assert effect.dice_count == 3
    assert effect.dice_size == 6
    assert effect.damage_type == "radiant"
    assert by_level[2].modifier_effects[0].dice_count == 4
    assert by_level[3].modifier_effects[0].dice_count == 5
    assert by_level[2].resource_id == "spell-slot-2"
    assert by_level[3].resource_id == "spell-slot-3"


def test_priest_divine_eminence_trait_is_bound():
    from app.content.monster_trait_bindings_2014 import bound_trait_names_2014
    source = next(m for m in load_monster_source_2014() if m.name == "Priest")
    assert "Divine Eminence" in bound_trait_names_2014(source)
