from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_fifteen_advances_level_fourteen_without_rebuilding_seraphine() -> None:
    level_fourteen = build_seraphine_dawnshield_2014_profile(14)
    level_fifteen = build_seraphine_dawnshield_2014_profile(15)

    assert level_fifteen.character_name == level_fourteen.character_name == "Seraphine Dawnshield"
    assert level_fifteen.species_id == level_fourteen.species_id == "hill-dwarf"
    assert level_fifteen.background_id == level_fourteen.background_id == "acolyte"
    assert level_fifteen.subclass_id == level_fourteen.subclass_id == "life-domain"
    assert level_fifteen.class_equipment == level_fourteen.class_equipment
    assert level_fifteen.advancement_increases == level_fourteen.advancement_increases
    assert level_fifteen.final_ability_scores == level_fourteen.final_ability_scores
    assert level_fifteen.feature_audits == level_fourteen.feature_audits


def test_level_fifteen_runtime_adds_eighth_level_slot_and_upcast_damage() -> None:
    hero = build_seraphine_dawnshield_2014(15)
    profile = build_seraphine_dawnshield_2014_profile(15)
    combat = build_seraphine_2014_combat_profile(15)

    assert hero.max_hp == 153
    assert hero.armor_class == 16
    assert hero.ability_scores is not None
    assert hero.ability_scores.constitution == 18
    assert hero.ability_scores.wisdom == 20
    assert hero.progression_features.turning_failure_destroy_max_cr == "3"
    rider = hero.progression_features.once_per_turn_weapon_hit_damage_rider
    assert rider is not None and rider.dice_count == 2

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "channel-divinity": 2,
        "divine-intervention": 1,
    }

    upcast = next(item for item in hero.spell_attack_actions if item.id == "inflict-wounds-l8")
    assert upcast.name == "Inflict Wounds (8th-Level)"
    assert upcast.level == 8
    assert upcast.attack_bonus == 10
    assert (upcast.damage_dice_count, upcast.damage_dice_size, upcast.damage_type) == (
        10, 10, "necrotic",
    )

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.percentile_success_max == 15

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_fifteen_spell_package_expands_prepared_count_legally() -> None:
    package = build_cleric_2014_spell_package(15, 5)

    assert len(package.spells) == 20
    assert package.spells[-1].id == "flame-strike"
    assert package.casting_ability == "wisdom"
