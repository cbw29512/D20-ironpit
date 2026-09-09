from app.content.monster_catalog import load_monster_rows
from app.content.monster_simple_save_parser import parse_simple_save_actions, strip_simple_save_actions
from app.domain.size import CreatureSize


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_constrict_compiles_as_generic_save_failure_control() -> None:
    row = _row("Constrictor Snake")
    actions = parse_simple_save_actions(row)
    constrict = next(action for action in actions if action.name == "Constrict")

    assert constrict.save_ability == "strength"
    assert constrict.dc == 12
    assert constrict.range_ft == 5
    assert constrict.target_max_size is CreatureSize.MEDIUM
    assert (constrict.damage_dice_count, constrict.damage_dice_size, constrict.damage_type) == (3, 4, "bludgeoning")
    assert constrict.failure_control is not None
    assert constrict.failure_control.max_target_size is CreatureSize.MEDIUM
    assert constrict.failure_control.grapple_escape_dc == 12
    assert constrict.failure_control.restrains_while_grappled is False


def test_modeled_constrict_save_is_removed_from_complex_source_scan() -> None:
    actions = str(_row("Constrictor Snake")["actions"])
    clean = strip_simple_save_actions(actions)
    assert "Constrict." not in clean
    assert "Saving Throw" not in clean
    assert "Grappled condition" not in clean
