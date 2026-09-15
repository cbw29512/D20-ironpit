from app.content.monster_catalog_2014 import compile_monster_2014, load_catalog_2014, unsupported_mechanics_2014
from app.content.monster_catalog_2014_arena_policy import is_arena_disabled_attack_detail_2014


def test_form_only_alternate_damage_is_arena_neutral() -> None:
    assert is_arena_disabled_attack_detail_2014(
        "or 9 (1d10 + 4) slashing damage in Small or Medium form"
    ) is True
    assert is_arena_disabled_attack_detail_2014(
        "If the target is a creature, it must succeed on a DC 15 Strength saving throw or be knocked prone"
    ) is False


def test_oni_uses_printed_large_form_glaive_without_change_shape() -> None:
    catalog = {monster.id: monster for monster in load_catalog_2014()}
    oni = catalog["oni"]
    assert "Change Shape" in oni.action_names
    assert "attack-detail:Glaive" not in unsupported_mechanics_2014(oni)
    template = compile_monster_2014(oni)
    glaive = next(attack for attack in [template.weapon_attack, *template.alternate_weapon_attacks] if attack.id == "glaive")
    assert glaive.weapon.dice_count == 2
    assert glaive.weapon.dice_size == 10
    assert glaive.damage_bonus == 4
