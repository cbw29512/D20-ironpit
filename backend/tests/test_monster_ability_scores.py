from app.content.capability_registry import build_monster_templates_from_capabilities
from app.content.monster_ability_scores import parse_ability_scores
from app.content.monster_catalog import load_monster_rows


def test_every_runtime_monster_has_source_derived_ability_scores() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    for monster in build_monster_templates_from_capabilities():
        assert monster.ability_scores == parse_ability_scores(rows[monster.name])


def test_shadow_strength_score_is_canonical_source_value() -> None:
    shadow = next(monster for monster in build_monster_templates_from_capabilities() if monster.name == "Shadow")
    assert shadow.ability_scores is not None
    assert shadow.ability_scores.strength == 6
