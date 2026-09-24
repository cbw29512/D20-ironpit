from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_eighteen_advances_level_seventeen_without_rebuilding_seraphine() -> None:
    level_seventeen = build_seraphine_dawnshield_2014_profile(17)
    level_eighteen = build_seraphine_dawnshield_2014_profile(18)

    assert level_eighteen.character_name == level_seventeen.character_name == "Seraphine Dawnshield"
    assert level_eighteen.species_id == level_seventeen.species_id == "hill-dwarf"
    assert level_eighteen.background_id == level_seventeen.background_id == "acolyte"
    assert level_eighteen.subclass_id == level_seventeen.subclass_id == "life-domain"
    assert level_eighteen.class_equipment == level_seventeen.class_equipment
    assert level_eighteen.advancement_increases == level_seventeen.advancement_increases
    assert level_eighteen.final_ability_scores == level_seventeen.final_ability_scores
    assert level_eighteen.feature_audits[: len(level_seventeen.feature_audits)] == level_seventeen.feature_audits
    assert level_eighteen.feature_audits[-1].feature_id == "channel-divinity-3"


def test_level_eighteen_runtime_adds_third_channel_divinity_use_only() -> None:
    hero = build_seraphine_dawnshield_2014(18)
    profile = build_seraphine_dawnshield_2014_profile(18)
    combat = build_seraphine_2014_combat_profile(18)

    assert hero.max_hp == 201
    assert hero.armor_class == 16
    assert hero.ability_scores is not None
    assert hero.ability_scores.constitution == 20
    assert hero.ability_scores.wisdom == 20
    assert hero.progression_features.turning_failure_destroy_max_cr == "4"
    assert hero.progression_features.outgoing_healing_dice_maximizer is not None

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 3,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
        "channel-divinity": 3,
        "divine-intervention": 1,
    }

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.percentile_success_max == 18

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_eighteen_spell_package_expands_prepared_count_legally() -> None:
    package = build_cleric_2014_spell_package(18, 5)

    assert len(package.spells) == 23
    assert package.spells[-1].id == "harm"
    assert package.casting_ability == "wisdom"
