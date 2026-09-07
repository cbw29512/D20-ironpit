from app.content.monster_catalog import load_monster_rows
from app.content.simple_monster_source_bonus_saves import parse_simple_bonus_save_actions


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_pirate_captain_charm_uses_generic_timed_condition_save() -> None:
    actions = parse_simple_bonus_save_actions(_row("Pirate Captain"))
    charm = next(action for action in actions if action["name"] == "Captain’s Charm")
    assert charm["action_cost"] == "bonus_action"
    assert charm["save_ability"] == "wisdom"
    assert charm["dc"] == 14
    assert charm["range_ft"] == 30
    assert charm["failure_conditions"] == [{
        "kind": "condition", "condition": "charmed", "expiry_timing": "source_turn_start",
    }]
