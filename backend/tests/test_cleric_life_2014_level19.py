from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_nineteen_advances_level_eighteen_and_applies_existing_strength_asi() -> None:
    level_eighteen = build_seraphine_dawnshield_2014_profile(18)
    level_nineteen = build_seraphine_dawnshield_2014_profile(19)

    assert level_nineteen.character_name == level_eighteen.character_name == "Seraphine Dawnshield"
    assert level_nineteen.species_id == level_eighteen.species_id == "hill-dwarf"
    assert level_nineteen.background_id == level_eighteen.background_id == "acolyte"
    assert level_nineteen.subclass_id == level_eighteen.subclass_id == "life-domain"
    assert level_nineteen.class_equipment == level_eighteen.class_equipment
    assert level_nineteen.advancement_increases[:-1] == level_eighteen.advancement_increases
    assert (
        level_nineteen.advancement_increases[-1].ability,
        level_nineteen.advancement_increases[-1].amount,
    ) == ("strength", 2)
    assert level_eighteen.final_ability_scores.strength == 13
    assert level_nineteen.final_ability_scores.strength == 15


def test_level_nineteen_runtime_recalculates_weapon_math_without_new_engine_behavior() -> None:
    hero = build_seraphine_dawnshield_2014(19)
    profile = build_seraphine_dawnshield_2014_profile(19)
    combat = build_seraphine_2014_combat_profile(19)

    assert hero.max_hp == 212
    assert hero.armor_class == 16
    assert hero.ability_scores is not None
    assert hero.ability_scores.strength == 15
    assert hero.ability_scores.constitution == 20
    assert hero.ability_scores.wisdom == 20
    assert hero.progression_features.turning_failure_destroy_max_cr == "4"
    assert hero.progression_features.outgoing_healing_dice_maximizer is not None

    warhammer = hero.weapon_attack
    assert warhammer.weapon.id == "warhammer"
    assert warhammer.attack_bonus == 8
    assert warhammer.damage_bonus == 2

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 3,
        "spell-slot-6": 2,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
        "channel-divinity": 3,
        "divine-intervention": 1,
    }

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.percentile_success_max == 19

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_nineteen_spell_package_expands_prepared_count_legally() -> None:
    package = build_cleric_2014_spell_package(19, 5)

    assert len(package.spells) == 24
    assert package.spells[-1].id == "heal"
    assert package.casting_ability == "wisdom"
