from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.canonical_hero_policy import assert_canonical_profile_policy


def test_2014_seraphine_is_one_persistent_character_across_levels() -> None:
    one = build_seraphine_dawnshield_2014_profile(1)
    four = build_seraphine_dawnshield_2014_profile(4)
    eight = build_seraphine_dawnshield_2014_profile(8)
    twelve = build_seraphine_dawnshield_2014_profile(12)
    twenty = build_seraphine_dawnshield_2014_profile(20)

    for profile in (one, four, eight, twelve, twenty):
        assert profile.character_name == "Seraphine Dawnshield"
        assert profile.species_id == "hill-dwarf"
        assert profile.background_id == "acolyte"
        assert profile.subclass_id == "life-domain"
        assert profile.base_ability_scores == one.base_ability_scores
        assert profile.species_increases == one.species_increases

    assert one.final_ability_scores.wisdom == 16
    assert four.final_ability_scores.wisdom == 18
    assert eight.final_ability_scores.wisdom == 20
    assert twelve.final_ability_scores.constitution == 18
    assert twenty.final_ability_scores.constitution == 20
    assert twenty.final_ability_scores.strength == 15


def test_2014_seraphine_level_one_profile_is_canonical_and_source_specific() -> None:
    profile = build_seraphine_dawnshield_2014_profile(1)
    assert_canonical_profile_policy(profile)
    assert profile.ruleset == "2014"
    assert profile.final_ability_scores.model_dump() == {
        "strength": 13,
        "dexterity": 10,
        "constitution": 16,
        "intelligence": 8,
        "wisdom": 16,
        "charisma": 12,
    }
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["dwarven-resilience"].automated is False
    assert audits["disciple-of-life"].automated is True


def test_2014_seraphine_level_one_spell_package_extends_original_example() -> None:
    package = build_cleric_2014_spell_package(1, 3)
    assert [spell.id for spell in package.cantrips] == [
        "guidance", "sacred-flame", "spare-the-dying",
    ]
    assert [spell.id for spell in package.spells] == [
        "healing-word", "guiding-bolt", "shield-of-faith", "sanctuary",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless", "cure-wounds",
    ]
