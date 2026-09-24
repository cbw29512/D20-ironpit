from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


# Exact-head verification guard: level 13 remains one persistent Seraphine progression.
def test_level_thirteen_advances_level_twelve_without_rebuilding_seraphine() -> None:
    level_twelve = build_seraphine_dawnshield_2014_profile(12)
    level_thirteen = build_seraphine_dawnshield_2014_profile(13)

    assert level_thirteen.character_name == level_twelve.character_name == "Seraphine Dawnshield"
    assert level_thirteen.species_id == level_twelve.species_id == "hill-dwarf"
    assert level_thirteen.background_id == level_twelve.background_id == "acolyte"
    assert level_thirteen.subclass_id == level_twelve.subclass_id == "life-domain"
    assert level_thirteen.class_equipment == level_twelve.class_equipment
    assert level_thirteen.advancement_increases == level_twelve.advancement_increases
    assert level_thirteen.final_ability_scores == level_twelve.final_ability_scores
    assert level_thirteen.feature_audits == level_twelve.feature_audits


def test_level_thirteen_runtime_adds_seventh_level_slot_and_upcast_damage() -> None:
    hero = build_seraphine_dawnshield_2014(13)
    profile = build_seraphine_dawnshield_2014_profile(13)
    combat = build_seraphine_2014_combat_profile(13)

    assert hero.max_hp == 133
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
        "spell-slot-7": 1,
        "channel-divinity": 2,
        "divine-intervention": 1,
    }

    upcast = next(item for item in hero.spell_attack_actions if item.id == "inflict-wounds-l7")
    assert upcast.name == "Inflict Wounds (7th-Level)"
    assert upcast.level == 7
    assert upcast.attack_bonus == 10
    assert (upcast.damage_dice_count, upcast.damage_dice_size, upcast.damage_type) == (
        9, 10, "necrotic",
    )

    sacred_flame = next(item for item in hero.spell_save_actions if item.id == "sacred-flame")
    assert sacred_flame.damage_dice_count == 3
    assert sacred_flame.dc == 18

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.percentile_success_max == 13

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_thirteen_spell_package_expands_prepared_count_legally() -> None:
    package = build_cleric_2014_spell_package(13, 5)

    assert len(package.spells) == 18
    assert package.spells[-1].id == "freedom-of-movement"
    assert package.casting_ability == "wisdom"
