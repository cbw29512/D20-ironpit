import pytest

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_save_count import source_action_save_count
from app.content.roster import build_arena_roster


@pytest.mark.parametrize(
    "name",
    ["Bearded Devil", "Chuul", "Death Dog", "Harpy", "Homunculus", "Salamander"],
)
def test_source_and_runtime_save_counts_match(name: str) -> None:
    row = next(row for row in load_monster_rows() if row["name"] == name)
    template = next(monster for monster in build_arena_roster().monsters if monster.name == name)
    source_count = source_action_save_count(str(row.get("actions", "")))
    runtime_count = sum(
        action.action_cost == "action" for action in template.saving_throw_actions
    ) + sum(
        attack.on_hit_saving_throw is not None
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
    )
    assert runtime_count == source_count, (
        f"{name}: runtime={runtime_count} source={source_count}; "
        f"save_actions={[(a.name, a.action_cost) for a in template.saving_throw_actions]}; "
        f"on_hit={[(a.weapon.name, a.on_hit_saving_throw is not None) for a in [template.weapon_attack, *template.alternate_weapon_attacks]]}"
    )
