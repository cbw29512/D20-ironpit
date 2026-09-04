from app.content.simple_save_damage_spells import build_simple_save_damage_spell


def test_fireball_is_data_only_save_half_area_damage() -> None:
    spell = build_simple_save_damage_spell("fireball", 16)
    assert (spell.level, spell.range_ft, spell.area_radius_ft) == (3, 150, 20)
    assert (spell.save_ability, spell.dc) == ("dexterity", 16)
    assert (spell.damage_dice_count, spell.damage_dice_size, spell.damage_type) == (8, 6, "fire")
    assert (spell.success_damage, spell.upcast_dice_per_level) == ("half", 1)


def test_shatter_blight_and_finger_of_death_share_one_builder() -> None:
    shatter = build_simple_save_damage_spell("shatter", 15)
    blight = build_simple_save_damage_spell("blight", 17)
    finger = build_simple_save_damage_spell("finger-of-death", 18)
    assert (shatter.area_radius_ft, shatter.damage_type) == (10, "thunder")
    assert (blight.area_radius_ft, blight.damage_dice_count, blight.damage_type) == (None, 8, "necrotic")
    assert (finger.damage_dice_count, finger.damage_dice_size, finger.damage_bonus) == (7, 8, 30)


def test_unknown_spell_fails_closed() -> None:
    try:
        build_simple_save_damage_spell("ice-storm", 16)
    except ValueError as exc:
        assert "Unsupported simple save-damage spell" in str(exc)
    else:
        raise AssertionError("Unsupported spell must fail closed.")
