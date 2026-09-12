from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_save_candidates import source_save_candidates
from app.domain.save_effects import ConditionEffectDefinition


def test_chuul_paralyzing_tentacles_compiles_from_source() -> None:
    row = next(row for row in load_monster_rows() if row["name"] == "Chuul")
    actions, _ = source_save_candidates(row)
    action = next(item for item in actions if item.name == "Paralyzing Tentacles")

    assert action.save_ability == "constitution"
    assert action.dc == 13
    assert action.range_ft == 10
    assert action.required_target_grappled_by_self is True
    assert len(action.failure_effects) == 1

    effect = action.failure_effects[0]
    assert isinstance(effect, ConditionEffectDefinition)
    assert effect.condition == "poisoned"
    assert effect.linked_conditions == ["paralyzed"]
    assert effect.repeat_save_ability == "constitution"
    assert effect.repeat_save_dc == 13
    assert effect.repeat_save_timing == "target_turn_end"
    assert effect.automatic_success_after_rounds == 10
