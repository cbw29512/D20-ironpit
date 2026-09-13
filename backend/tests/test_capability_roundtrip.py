from app.content.basic_condition_actions import wake_sleeper_action
from app.content.capability_equivalence import semantic_template_dump, templates_semantically_equal
from app.content.capability_registry import build_monster_templates_from_capabilities
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def _semantic_difference_keys(left: object, right: object) -> list[str]:
    left_dump = semantic_template_dump(left)
    right_dump = semantic_template_dump(right)
    return sorted(
        key for key in set(left_dump) | set(right_dump)
        if left_dump.get(key) != right_dump.get(key)
    )


def test_registry_preserves_every_legacy_monster_semantics_and_source_audit() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    legacy = build_legacy_monster_templates()
    compiled = build_monster_templates_from_capabilities()
    compiled_by_id = {monster.id: monster for monster in compiled}
    legacy_ids = [monster.id for monster in legacy]
    assert legacy
    assert len(compiled_by_id) == len(compiled)
    assert [monster.id for monster in compiled if monster.id in set(legacy_ids)] == legacy_ids
    for original in legacy:
        rebuilt = compiled_by_id[original.id]
        source_row = rows[original.name]
        assert templates_semantically_equal(original, rebuilt), (
            f"{original.id}: differing_fields={_semantic_difference_keys(original, rebuilt)}"
        )
        assert audit_monster_source(rebuilt, source_row) == audit_monster_source(original, source_row), original.id


def test_engine_global_wake_action_does_not_change_content_semantic_parity() -> None:
    original = build_legacy_monster_templates()[0]
    with_engine_default = original.model_copy(update={
        "condition_removal_actions": [*original.condition_removal_actions, wake_sleeper_action()],
    })
    assert templates_semantically_equal(original, with_engine_default)
    assert semantic_template_dump(original) == semantic_template_dump(with_engine_default)


def test_production_roster_uses_the_compiled_capability_monster_set() -> None:
    production = build_arena_roster().monsters
    compiled = build_monster_templates_from_capabilities()
    assert [monster.id for monster in production] == [monster.id for monster in compiled]
    for actual, expected in zip(production, compiled, strict=True):
        assert templates_semantically_equal(actual, expected), actual.id
