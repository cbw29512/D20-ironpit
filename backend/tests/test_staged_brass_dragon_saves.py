import pytest

from app.content.basic_condition_actions import WAKE_SLEEPER_ID
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_save_candidates import source_save_candidates
from app.domain.save_effects import ConditionEffectDefinition


@pytest.mark.parametrize(
    ("name", "dc", "cone_ft"),
    [
        ("Brass Dragon Wyrmling", 11, 15),
        ("Young Brass Dragon", 14, 30),
    ],
)
def test_sleep_breath_compiles_staged_wakeable_unconscious_lifecycle(
    name: str,
    dc: int,
    cone_ft: int,
) -> None:
    row = next(row for row in load_monster_rows() if row["name"] == name)
    actions, resources = source_save_candidates(row)
    action = next(item for item in actions if item.name == "Sleep Breath")

    assert action.save_ability == "constitution"
    assert action.dc == dc
    assert action.area is not None
    assert action.area.shape == "cone"
    assert action.area.length_ft == cone_ft
    assert len(action.failure_effects) == 1

    assert action.resource_id is not None
    resource = next(item for item in resources if item.id == action.resource_id)
    assert resource.max_uses == 1
    assert resource.recharge is not None
    assert resource.recharge.minimum_roll == 5

    effect = action.failure_effects[0]
    assert isinstance(effect, ConditionEffectDefinition)
    assert effect.condition == "incapacitated"
    assert effect.repeat_save_timing == "target_turn_end"
    assert effect.repeat_save_failure_condition == "unconscious"
    assert effect.repeat_save_failure_continues is False
    assert effect.repeat_save_failure_duration_rounds == 10
    assert effect.repeat_save_failure_ends_on_damage is True
    assert effect.repeat_save_failure_allowed_removal_action_ids == [WAKE_SLEEPER_ID]
