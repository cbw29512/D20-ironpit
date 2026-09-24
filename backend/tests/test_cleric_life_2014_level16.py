from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


# Exact-head verification guard: level 16 remains one persistent Seraphine progression.
def test_level_sixteen_advances_level_fifteen_and_applies_existing_constitution_asi() -> None:
    level_fifteen = build_seraphine_dawnshield_2014_profile(15)
    level_sixteen = build_seraphine_dawnshield_2014_profile(16)

    assert level_sixteen.character_name == level_fifteen.character_name == "Seraphine Dawnshield"
    assert level_sixteen.species_id == level_fifteen.species_id == "hill-dwarf"
    assert level_sixteen.background_id == level_fifteen.background_id == "acolyte"
    assert level_sixteen.subclass_id == level_fifteen.subclass_id == "life-domain"
    assert level_sixteen.class_equipment == level_fifteen.class_equipment
    assert level_sixteen.advancement_increases[:-1] == level_fifteen.advancement_increases
    assert (
        level_sixteen.advancement_increases[-1].ability,
        level_sixteen.advancement_increases[-1].amount,
    ) == ("constitution", 2)
    assert level_fifteen.final_ability_scores.constitution == 18
    assert level_sixteen.final_ability_scores.constitution == 20


def test_level_sixteen_runtime_recalculates_hp_without_new_engine_behavior() -> None:
    hero = build_seraphine_dawnshield_2014(16)
    profile = build_seraphine_dawnshield_2014_profile(16)
    combat = build_seraphine_2014_combat_profile(16)

    assert hero.max_hp == 179
    assert hero.armor_class == 16
    assert hero.ability_scores is not None
    assert hero.ability_scores.constitution == 20
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

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.percentile_success_max == 16

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_sixteen_spell_package_expands_prepared_count_legally() -> None:
    package = build_cleric_2014_spell_package(16, 5)

    assert len(package.spells) == 21
    assert package.spells[-1].id == "greater-restoration"
    assert package.casting_ability == "wisdom"
