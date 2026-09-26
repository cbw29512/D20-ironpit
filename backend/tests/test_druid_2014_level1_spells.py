from __future__ import annotations

from app.content.druid_2014_level1_spells import longstrider_2014, poison_spray_2014, produce_flame_2014
from app.content.druid_2014_spell_package import build_druid_2014_spell_package


def test_level_one_druid_spell_package_is_legal_and_combat_first() -> None:
    package = build_druid_2014_spell_package(1, 3)
    assert [spell.id for spell in package.cantrips] == ["produce-flame", "poison-spray"]
    assert [spell.id for spell in package.spells] == [
        "healing-word", "cure-wounds", "longstrider", "detect-magic",
    ]


def test_produce_flame_uses_cantrip_scaling() -> None:
    assert produce_flame_2014(5, 1).damage_dice_count == 1
    assert produce_flame_2014(7, 5).damage_dice_count == 2
    assert produce_flame_2014(9, 11).damage_dice_count == 3
    assert produce_flame_2014(11, 17).damage_dice_count == 4


def test_poison_spray_uses_cantrip_scaling() -> None:
    one = poison_spray_2014(13, 1)
    seventeen = poison_spray_2014(19, 17)
    assert (one.save_ability, one.damage_dice_count, one.damage_dice_size, one.damage_type) == (
        "constitution", 1, 12, "poison",
    )
    assert seventeen.damage_dice_count == 4


def test_longstrider_reuses_universal_speed_modifier() -> None:
    spell = longstrider_2014()
    assert spell.concentration is False
    assert spell.duration_minutes == 60
    assert len(spell.modifier_effects) == 1
    effect = spell.modifier_effects[0]
    assert effect.kind == "speed"
    assert effect.flat_bonus == 10
