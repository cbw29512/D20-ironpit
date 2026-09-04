from app.content.simple_damage_cantrips import build_simple_damage_cantrip
from app.domain.spells import SpellAttackAction, SpellSaveAction


def test_attack_cantrips_share_one_scaling_builder() -> None:
    fire = build_simple_damage_cantrip(
        "fire-bolt", character_level=17, attack_bonus=11, save_dc=19,
    )
    poison = build_simple_damage_cantrip(
        "poison-spray", character_level=11, attack_bonus=9, save_dc=17,
    )
    ray = build_simple_damage_cantrip(
        "ray-of-frost", character_level=11, attack_bonus=9, save_dc=17,
    )
    assert isinstance(fire, SpellAttackAction)
    assert isinstance(poison, SpellAttackAction)
    assert isinstance(ray, SpellAttackAction)
    assert (fire.damage_dice_count, fire.damage_dice_size, fire.range_ft) == (4, 10, 120)
    assert (poison.damage_dice_count, poison.damage_dice_size, poison.range_ft) == (3, 12, 30)
    assert (ray.damage_dice_count, ray.damage_dice_size, ray.damage_type, ray.range_ft) == (3, 8, "cold", 60)
    assert ray.on_hit_modifier_effects == []


def test_save_cantrips_share_one_scaling_builder() -> None:
    acid = build_simple_damage_cantrip(
        "acid-splash", character_level=5, attack_bonus=7, save_dc=15,
    )
    sacred = build_simple_damage_cantrip(
        "sacred-flame", character_level=20, attack_bonus=11, save_dc=19,
    )
    assert isinstance(acid, SpellSaveAction)
    assert isinstance(sacred, SpellSaveAction)
    assert (acid.damage_dice_count, acid.area_radius_ft, acid.damage_type) == (2, 5, "acid")
    assert (sacred.damage_dice_count, sacred.area_radius_ft, sacred.damage_type) == (4, None, "radiant")
    assert acid.success_damage == sacred.success_damage == "none"


def test_unmodeled_damage_cantrips_still_fail_closed() -> None:
    for cantrip_id in ("starry-wisp", "produce-flame"):
        try:
            build_simple_damage_cantrip(
                cantrip_id, character_level=20, attack_bonus=11, save_dc=19,
            )
        except ValueError as exc:
            assert "Unsupported simple damage cantrip" in str(exc)
        else:
            raise AssertionError(f"{cantrip_id} must fail closed until its damage component is audited.")
