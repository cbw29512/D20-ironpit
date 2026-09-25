from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_seven_advances_level_six_without_rebuilding_seraphine() -> None:
    level_six = build_seraphine_dawnshield_2014_profile(6)
    level_seven = build_seraphine_dawnshield_2014_profile(7)

    assert level_seven.character_name == level_six.character_name == "Seraphine Dawnshield"
    assert level_seven.species_id == level_six.species_id == "hill-dwarf"
    assert level_seven.background_id == level_six.background_id == "acolyte"
    assert level_seven.subclass_id == level_six.subclass_id == "life-domain"
    assert level_seven.class_equipment == level_six.class_equipment
    assert level_seven.advancement_increases == level_six.advancement_increases
    assert level_seven.final_ability_scores == level_six.final_ability_scores
    assert level_seven.feature_audits == level_six.feature_audits


def test_level_seven_runtime_adds_only_level_seven_spell_capacity() -> None:
    hero = build_seraphine_dawnshield_2014(7)
    profile = build_seraphine_dawnshield_2014_profile(7)
    combat = build_seraphine_2014_combat_profile(7)

    assert hero.max_hp == 66
    assert hero.armor_class == 16
    assert hero.ability_scores is not None and hero.ability_scores.wisdom == 18
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
        "channel-divinity": 2,
    }

    death_ward = next(item for item in hero.defensive_spell_actions if item.id == "death-ward")
    assert death_ward.level == 4
    zero_hp = next(
        effect for effect in death_ward.modifier_effects
        if effect.kind == "zero-hp-replacement"
    )
    assert zero_hp.replacement_hp == 1
    assert zero_hp.prevents_instant_death is True

    assert [item.id for item in hero.persistent_hazard_actions] == ["guardian-of-faith"]
    guardian = hero.persistent_hazard_actions[0]
    assert guardian.level == 4
    assert guardian.failure_damage == 20
    assert guardian.success_damage == 10
    assert guardian.max_total_damage == 60
    assert guardian.damage_type == "radiant"

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_seven_spell_package_preserves_preparations_and_adds_domain_spells() -> None:
    package = build_cleric_2014_spell_package(7, 4)

    assert [spell.id for spell in package.spells] == [
        "healing-word",
        "guiding-bolt",
        "shield-of-faith",
        "inflict-wounds",
        "sanctuary",
        "aid",
        "detect-magic",
        "augury",
        "prayer-of-healing",
        "warding-bond",
        "hold-person",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless",
        "cure-wounds",
        "lesser-restoration",
        "spiritual-weapon",
        "beacon-of-hope",
        "revivify",
        "death-ward",
        "guardian-of-faith",
    ]
