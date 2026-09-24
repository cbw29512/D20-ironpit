from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile


def test_2014_seraphine_is_one_persistent_character_across_levels() -> None:
    levels = [build_seraphine_dawnshield_2014_profile(level) for level in range(1, 21)]

    for index, profile in enumerate(levels, start=1):
        assert profile.level == index
        assert profile.character_name == "Seraphine Dawnshield"
        assert profile.ruleset == "2014"
        assert profile.template_id == f"seraphine-dawnshield-2014-l{index}"
        assert profile.species_id == "hill-dwarf"
        assert profile.background_id == "acolyte"
        assert profile.subclass_id == "life-domain"
        assert profile.base_ability_scores == levels[0].base_ability_scores
        assert profile.species_increases == levels[0].species_increases
        assert_canonical_profile_policy(profile)

    # RAW 2014 canonical construction: standard array first, then Hill Dwarf racial increases.
    assert sorted(levels[0].base_ability_scores.model_dump().values()) == [8, 10, 12, 13, 14, 15]
    assert [(item.ability, item.amount) for item in levels[0].species_increases] == [
        ("constitution", 2),
        ("wisdom", 1),
    ]
    assert levels[0].final_ability_scores.wisdom == 16
    assert levels[0].final_ability_scores.constitution == 16
    assert levels[3].final_ability_scores.wisdom == 18
    assert levels[7].final_ability_scores.wisdom == 20
    assert levels[11].final_ability_scores.constitution == 18
    assert levels[15].final_ability_scores.constitution == 20
    assert levels[19].final_ability_scores.strength == 15


def test_each_2014_cleric_level_preserves_previous_level_history() -> None:
    previous = build_seraphine_dawnshield_2014_profile(1)
    for level in range(2, 21):
        current = build_seraphine_dawnshield_2014_profile(level)
        assert current.character_name == previous.character_name
        assert current.class_id == previous.class_id
        assert current.species_id == previous.species_id
        assert current.background_id == previous.background_id
        assert current.subclass_id == previous.subclass_id
        assert current.class_equipment == previous.class_equipment
        assert current.background_equipment == previous.background_equipment
        assert current.feature_audits[: len(previous.feature_audits)] == previous.feature_audits
        assert current.advancement_increases[: len(previous.advancement_increases)] == previous.advancement_increases
        previous = current


def test_2014_seraphine_level_one_spell_package() -> None:
    package = build_cleric_2014_spell_package(1, 3)
    assert [spell.id for spell in package.cantrips] == [
        "guidance", "sacred-flame", "thaumaturgy",
    ]
    assert [spell.id for spell in package.spells] == [
        "healing-word", "guiding-bolt", "shield-of-faith", "inflict-wounds",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless", "cure-wounds",
    ]


def test_2014_seraphine_cantrip_progression_matches_raw_cleric_table() -> None:
    level_one = build_cleric_2014_spell_package(1, 3)
    level_four = build_cleric_2014_spell_package(4, 4)
    level_ten = build_cleric_2014_spell_package(10, 5)

    assert [spell.id for spell in level_one.cantrips] == [
        "guidance", "sacred-flame", "thaumaturgy",
    ]
    assert [spell.id for spell in level_four.cantrips] == [
        "guidance", "sacred-flame", "thaumaturgy", "mending",
    ]
    assert [spell.id for spell in level_ten.cantrips] == [
        "guidance", "sacred-flame", "thaumaturgy", "mending", "light",
    ]


def test_2014_seraphine_level_two_extends_level_one_spell_capacity() -> None:
    level_one = build_seraphine_dawnshield_2014_profile(1)
    level_two = build_seraphine_dawnshield_2014_profile(2)
    one_package = build_cleric_2014_spell_package(1, level_one.final_ability_scores.modifier("wisdom"))
    two_package = build_cleric_2014_spell_package(2, level_two.final_ability_scores.modifier("wisdom"))

    assert [spell.id for spell in one_package.spells] == [
        "healing-word", "guiding-bolt", "shield-of-faith", "inflict-wounds",
    ]
    assert [spell.id for spell in two_package.spells] == [
        "healing-word", "guiding-bolt", "shield-of-faith", "inflict-wounds", "sanctuary",
    ]
