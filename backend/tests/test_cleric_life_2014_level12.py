from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_twelve_advances_level_eleven_and_applies_constitution_asi() -> None:
    level_eleven = build_seraphine_dawnshield_2014_profile(11)
    level_twelve = build_seraphine_dawnshield_2014_profile(12)

    assert level_twelve.character_name == level_eleven.character_name == "Seraphine Dawnshield"
    assert level_twelve.species_id == level_eleven.species_id == "hill-dwarf"
    assert level_twelve.background_id == level_eleven.background_id == "acolyte"
    assert level_twelve.subclass_id == level_eleven.subclass_id == "life-domain"
    assert level_twelve.class_equipment == level_eleven.class_equipment
    assert level_twelve.advancement_increases[:-1] == level_eleven.advancement_increases
    assert (level_twelve.advancement_increases[-1].ability, level_twelve.advancement_increases[-1].amount) == (
        "constitution", 2,
    )
    assert level_eleven.final_ability_scores.constitution == 16
    assert level_twelve.final_ability_scores.constitution == 18


def test_level_twelve_runtime_recalculates_hp_from_same_character() -> None:
    hero = build_seraphine_dawnshield_2014(12)
    profile = build_seraphine_dawnshield_2014_profile(12)
    combat = build_seraphine_2014_combat_profile(12)

    assert hero.max_hp == 123
    assert hero.armor_class == 16
    assert hero.ability_scores is not None
    assert hero.ability_scores.constitution == 18
    assert hero.ability_scores.wisdom == 20
    assert hero.progression_features.turning_failure_destroy_max_cr == "2"
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "channel-divinity": 2,
        "divine-intervention": 1,
    }

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.percentile_success_max == 12

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_twelve_spell_package_expands_prepared_count_without_rebuild() -> None:
    package = build_cleric_2014_spell_package(12, 5)

    assert len(package.spells) == 17
    assert package.casting_ability == "wisdom"
    assert package.spells[-1].id == "remove-curse"
