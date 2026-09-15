from app.content.monster_source_save_candidates import source_save_candidates
from app.domain.save_effects import ConditionEffectDefinition, TurnRestrictionEffectDefinition


def test_daily_control_save_keeps_resource_and_condition_bound_restriction() -> None:
    row = {
        "name": "Test Fiend",
        "actions": (
            "Fetid Cloud (1/Day). Constitution Saving Throw: DC 11, each creature in a 10-foot Emanation "
            "originating from the fiend. Failure: The target has the Poisoned condition until the end of its next turn. "
            "While Poisoned, the creature can take either an action or a Bonus Action on its turn, not both, and it can’t take Reactions."
        ),
        "bonusActions": "",
    }
    actions, resources = source_save_candidates(row)
    assert len(actions) == 1
    assert len(resources) == 1
    action = actions[0]
    resource = resources[0]
    assert action.name == "Fetid Cloud"
    assert action.resource_id == resource.id
    assert resource.max_uses == 1
    assert resource.recharge is None
    condition = next(effect for effect in action.failure_effects if isinstance(effect, ConditionEffectDefinition))
    restriction = next(effect for effect in action.failure_effects if isinstance(effect, TurnRestrictionEffectDefinition))
    assert condition.condition == "poisoned"
    assert condition.expiry_timing == "target_turn_end"
    assert restriction.action_or_bonus_only is True
    assert restriction.reactions_disabled is True
    assert restriction.requires_condition == "poisoned"
    assert restriction.expiry_timing == "target_turn_end"
