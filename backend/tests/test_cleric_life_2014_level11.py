from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_eleven_advances_level_ten_without_rebuilding_seraphine() -> None:
    level_ten = build_seraphine_dawnshield_2014_profile(10)
    level_eleven = build_seraphine_dawnshield_2014_profile(11)

    assert level_eleven.character_name == level_ten.character_name == "Seraphine Dawnshield"
    assert level_eleven.species_id == level_ten.species_id == "hill-dwarf"
    assert level_eleven.background_id == level_ten.background_id == "acolyte"
    assert level_eleven.subclass_id == level_ten.subclass_id == "life-domain"
    assert level_eleven.class_equipment == level_ten.class_equipment
    assert level_eleven.advancement_increases == level_ten.advancement_increases
    assert level_eleven.final_ability_scores == level_ten.final_ability_scores
    assert level_eleven.feature_audits[:-1] == level_ten.feature_audits
    assert level_eleven.feature_audits[-1].feature_id == "destroy-undead-2"


def test_level_eleven_runtime_adds_sixth_level_slot_and_cr_two_destroy_undead() -> None:
    hero = build_seraphine_dawnshield_2014(11)
    profile = build_seraphine_dawnshield_2014_profile(11)
    combat = build_seraphine_2014_combat_profile(11)

    assert hero.max_hp == 102
    assert hero.armor_class == 16
    assert hero.ability_scores is not None and hero.ability_scores.wisdom == 20
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

    upcast = next(item for item in hero.spell_attack_actions if item.id == "inflict-wounds-l6")
    assert upcast.name == "Inflict Wounds (6th-Level)"
    assert upcast.level == 6
    assert upcast.attack_bonus == 9
    assert (upcast.damage_dice_count, upcast.damage_dice_size, upcast.damage_type) == (
        8, 10, "necrotic",
    )

    sacred_flame = next(item for item in hero.spell_save_actions if item.id == "sacred-flame")
    assert sacred_flame.damage_dice_count == 3
    assert sacred_flame.dc == 17

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_eleven_spell_package_remains_legal_on_same_character() -> None:
    package = build_cleric_2014_spell_package(11, 5)

    assert len(package.spells) == 16
    assert package.casting_ability == "wisdom"
    assert any(spell.id == "spirit-guardians" for spell in package.spells)
    assert [spell.id for spell in package.always_prepared_spells][-2:] == [
        "mass-cure-wounds",
        "raise-dead",
    ]
