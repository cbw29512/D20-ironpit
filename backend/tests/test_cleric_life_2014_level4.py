from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_four_is_level_three_plus_only_the_raw_asi_delta() -> None:
    level_three = build_seraphine_dawnshield_2014_profile(3)
    level_four = build_seraphine_dawnshield_2014_profile(4)

    assert level_four.character_name == level_three.character_name == "Seraphine Dawnshield"
    assert level_four.species_id == level_three.species_id == "hill-dwarf"
    assert level_four.background_id == level_three.background_id == "acolyte"
    assert level_four.subclass_id == level_three.subclass_id == "life-domain"
    assert level_four.class_equipment == level_three.class_equipment
    assert level_four.background_equipment == level_three.background_equipment
    assert level_four.feature_audits[: len(level_three.feature_audits)] == level_three.feature_audits
    assert level_four.advancement_increases[:-1] == level_three.advancement_increases
    assert (level_four.advancement_increases[-1].ability, level_four.advancement_increases[-1].amount) == (
        "wisdom", 2,
    )
    assert level_three.final_ability_scores.wisdom == 16
    assert level_four.final_ability_scores.wisdom == 18


def test_level_four_spell_package_expands_without_rebuilding_seraphine() -> None:
    package = build_cleric_2014_spell_package(4, 4)

    assert [spell.id for spell in package.cantrips] == [
        "guidance", "sacred-flame", "thaumaturgy", "mending",
    ]
    assert [spell.id for spell in package.spells] == [
        "healing-word",
        "guiding-bolt",
        "shield-of-faith",
        "inflict-wounds",
        "sanctuary",
        "aid",
        "detect-magic",
        "augury",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless",
        "cure-wounds",
        "lesser-restoration",
        "spiritual-weapon",
    ]


def test_level_four_runtime_recomputes_all_wisdom_derived_values() -> None:
    hero = build_seraphine_dawnshield_2014(4)
    profile = build_seraphine_dawnshield_2014_profile(4)
    combat = build_seraphine_2014_combat_profile(4)

    assert hero.max_hp == 39
    assert hero.armor_class == 16
    assert hero.ability_scores is not None and hero.ability_scores.wisdom == 18
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "channel-divinity": 1,
    }

    sacred_flame = next(item for item in hero.spell_save_actions if item.id == "sacred-flame")
    sanctuary = next(item for item in hero.defensive_spell_actions if item.id == "sanctuary")
    spiritual_weapon = hero.persistent_spell_attack_actions[0]
    guiding_bolt = next(item for item in hero.spell_attack_actions if item.id == "guiding-bolt")
    healing_word = next(item for item in hero.healing_actions if item.id == "healing-word")

    assert sacred_flame.dc == 14
    assert sanctuary.modifier_effects[0].save_dc == 14
    assert guiding_bolt.attack_bonus == 6
    assert spiritual_weapon.attack.attack_bonus == 6
    assert spiritual_weapon.attack.damage_bonus == 4
    assert healing_word.healing_bonus == 7

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)
