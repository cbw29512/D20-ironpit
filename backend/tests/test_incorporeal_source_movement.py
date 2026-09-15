from app.content.movement_modes import source_movement_modes


def test_wraith_incorporeal_movement_is_source_bound() -> None:
    movement = source_movement_modes("Wraith")

    assert movement.pass_through_creatures_as_difficult_terrain is True


def test_ordinary_monster_does_not_gain_incorporeal_movement() -> None:
    movement = source_movement_modes("Ogre")

    assert movement.pass_through_creatures_as_difficult_terrain is False
