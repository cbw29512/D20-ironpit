import pytest

from app.content.basic_condition_actions import WAKE_SLEEPER_ID
from app.content.monster_catalog import load_monster_rows
from app.content.monster_save_failure_source_audit import failure_effect_issues
from app.content.monster_source_save_candidates import source_save_candidates
from app.domain.save_effects import ConditionEffectDefinition


@pytest.mark.parametrize(
    ("name", "dc", "cone_ft", "sleep_rounds"),
    [
        ("Brass Dragon Wyrmling", 11, 15, 10),
        ("Young Brass Dragon", 14, 30, 10),
        ("Adult Brass Dragon", 18, 60, 100),
        ("Ancient Brass Dragon", 21, 90, 100),
    ],
)
def test_sleep_breath_compiles_staged_wakeable_unconscious_lifecycle(
    name: str,
    dc: int,
    cone_ft: int,
    sleep_rounds: int,
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
    assert action.resource_id is None
    assert all(item.name != "Sleep Breath" for item in resources)

    effect = action.failure_effects[0]
    assert isinstance(effect, ConditionEffectDefinition)
    assert effect.condition == "incapacitated"
    assert effect.repeat_save_timing == "target_turn_end"
    assert effect.repeat_save_failure_condition == "unconscious"
    assert effect.repeat_save_failure_continues is False
    assert effect.repeat_save_failure_duration_rounds == sleep_rounds
    assert effect.repeat_save_failure_ends_on_damage is True
    assert effect.repeat_save_failure_allowed_removal_action_ids == [WAKE_SLEEPER_ID]
    assert failure_effect_issues(action, str(row["actions"])) == []
