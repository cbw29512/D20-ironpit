import pytest

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_source_save_count import source_action_save_count
from app.content.roster import build_arena_roster


@pytest.mark.parametrize(
    "name",
    [
        "Bearded Devil", "Brass Dragon Wyrmling", "Chuul", "Death Dog", "Harpy",
        "Homunculus", "Salamander", "Young Brass Dragon",
    ],
)
def test_source_save_count_drift_remains_an_explicit_blocker(name: str) -> None:
    row = next(row for row in load_monster_rows() if row["name"] == name)
    template = next(monster for monster in build_arena_roster().monsters if monster.name == name)
    source_count = source_action_save_count(str(row.get("actions", "")))
    runtime_count = sum(
        action.action_cost == "action" for action in template.saving_throw_actions
    ) + sum(
        attack.on_hit_saving_throw is not None
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
    )

    assert runtime_count != source_count, (
        f"{name} now reconciles its source save count; remove it from this blocker regression."
    )
    assert "source-save-action-count-mismatch" in audit_monster_source(template, row)
