from app.combat.dice import FixedDiceProvider
from app.combat.save_action_resources import consume_resource, recharge_start_of_turn, resource_available
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities


def test_recharge_save_action_resource_lifecycle_is_generic() -> None:
    template = build_combatant_from_capabilities("srd-hell-hound")
    state = build_combatant_state(template)
    action = template.saving_throw_actions[0]
    resource = next(item for item in state.resources if item.id == action.resource_id)

    assert resource_available(state, action)
    assert consume_resource(state, action) == 0
    assert not resource_available(state, action)

    recharge_start_of_turn(state, FixedDiceProvider([4]))
    assert resource.current_uses == 0
    recharge_start_of_turn(state, FixedDiceProvider([5]))
    assert resource.current_uses == 1
    assert resource_available(state, action)


def test_recharge_batch_compiles_area_and_priority_data() -> None:
    hell_hound = build_combatant_from_capabilities("srd-hell-hound")
    red = build_combatant_from_capabilities("srd-young-red-dragon")
    assert (hell_hound.saving_throw_actions[0].area_slots, hell_hound.saving_throw_actions[0].priority) == (3, 100)
    assert (red.saving_throw_actions[0].area_slots, red.saving_throw_actions[0].priority) == (6, 100)
    assert red.resources[0].recharge_min_d6 == 5
