from app.content.combat_ir_support_adapters import condition_removal_action_to_ir, healing_action_to_ir
from app.content.combat_ir_support_reverse_adapters import condition_removal_ir_to_action, healing_ir_to_action
from app.domain.actions import ConditionRemovalAction, HealingAction


def test_healing_action_round_trips_target_cost_and_amount() -> None:
    action = HealingAction(
        id="healing-word",
        name="Healing Word",
        action_cost="bonus_action",
        range_ft=60,
        target_mode="self_or_ally",
        dice_count=2,
        dice_size=4,
        healing_bonus=3,
        resource_id="spell-slot-2",
        resource_cost=1,
        animation="healing-word",
    )
    rebuilt = healing_ir_to_action(healing_action_to_ir(action))
    assert rebuilt.model_dump() == action.model_dump()


def test_condition_removal_round_trips_reaction_and_resource_modes() -> None:
    action = ConditionRemovalAction(
        id="reactive-cleansing",
        name="Reactive Cleansing",
        action_cost="reaction",
        range_ft=30,
        target_mode="ally",
        removable_conditions=["frightened", "poisoned"],
        max_conditions_per_use=2,
        resource_costs={"spell-slot-2": 1},
        resource_costs_per_condition={"cleansing-charge": 1},
        reaction_trigger="condition_applied_to_ally",
        expends_spell_slot=True,
        animation="cleanse",
    )
    rebuilt = condition_removal_ir_to_action(condition_removal_action_to_ir(action))
    assert rebuilt.model_dump() == action.model_dump()
