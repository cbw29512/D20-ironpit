from __future__ import annotations

from app.content.canonical_spell_policy import canonical_spell_package
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_2014_ranger_level_two_reuses_archery_and_spell_primitives() -> None:
    hero = build_rowan_ashtrail_2014(2)
    profile = build_rowan_ashtrail_2014_profile(2)

    assert hero.level == 2
    assert hero.max_hp == 20
    assert hero.fighting_styles == ["Archery"]
    assert profile.fighting_styles == ["Archery"]
    assert hero.weapon_attack.weapon.id == "longbow"
    assert hero.weapon_attack.attack_bonus == 7
    assert hero.weapon_attack.damage_bonus == 3
    assert hero.alternate_weapon_attacks[0].weapon.id == "shortsword"
    assert hero.alternate_weapon_attacks[0].attack_bonus == 5
    assert {item.id: item.max_uses for item in hero.resources} == {"spell-slot-1": 2}
    assert [item.id for item in hero.defensive_spell_actions] == ["longstrider"]
    assert [item.id for item in hero.healing_actions] == ["cure-wounds"]


def test_2014_ranger_level_two_known_spells_are_legal() -> None:
    package = canonical_spell_package("ranger", 2, "2014")

    assert package is not None
    assert package.class_id == "ranger"
    assert package.casting_ability == "wisdom"
    assert package.cantrips == []
    assert [spell.id for spell in package.spells] == ["longstrider", "cure-wounds"]


def test_2014_ranger_level_two_feature_audits_use_shared_mechanics() -> None:
    audits = {item.feature_id: item for item in build_rowan_ashtrail_2014_profile(2).feature_audits}

    assert audits["fighting-style"].combat_relevant is True
    assert audits["fighting-style"].automated is True
    assert "universal Archery" in audits["fighting-style"].notes
    assert audits["spellcasting"].combat_relevant is True
    assert audits["spellcasting"].automated is True
