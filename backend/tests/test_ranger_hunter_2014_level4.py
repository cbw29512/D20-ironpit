from __future__ import annotations

from app.content.canonical_spell_policy import canonical_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_2014_hunter_ranger_level_four_asi_recomputes_combat_values() -> None:
    hero = build_rowan_ashtrail_2014(4)
    profile = build_rowan_ashtrail_2014_profile(4)

    assert hero.level == 4
    assert hero.max_hp == 36
    assert hero.ability_scores.dexterity == 19
    assert hero.armor_class == 15
    assert hero.initiative_bonus == 4
    assert hero.weapon_attack.weapon.id == "longbow"
    assert (hero.weapon_attack.attack_bonus, hero.weapon_attack.damage_bonus) == (8, 4)
    assert (hero.alternate_weapon_attacks[0].attack_bonus, hero.alternate_weapon_attacks[0].damage_bonus) == (6, 4)
    assert profile.advancement_increases[-1].ability == "dexterity"
    assert profile.advancement_increases[-1].amount == 2


def test_2014_hunter_ranger_level_four_spell_package_is_unchanged() -> None:
    package = canonical_spell_package("ranger", 4, "2014")
    assert package is not None
    assert [spell.id for spell in package.spells] == ["longstrider", "cure-wounds", "detect-magic"]
