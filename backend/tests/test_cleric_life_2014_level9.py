from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.demo import build_goblin_warrior
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup


def test_level_nine_advances_level_eight_without_rebuilding_seraphine() -> None:
    level_eight = build_seraphine_dawnshield_2014_profile(8)
    level_nine = build_seraphine_dawnshield_2014_profile(9)

    assert level_nine.character_name == level_eight.character_name == "Seraphine Dawnshield"
    assert level_nine.species_id == level_eight.species_id == "hill-dwarf"
    assert level_nine.background_id == level_eight.background_id == "acolyte"
    assert level_nine.subclass_id == level_eight.subclass_id == "life-domain"
    assert level_nine.class_equipment == level_eight.class_equipment
    assert level_nine.advancement_increases == level_eight.advancement_increases
    assert level_nine.final_ability_scores == level_eight.final_ability_scores
    assert level_nine.feature_audits == level_eight.feature_audits


def test_level_nine_runtime_adds_fifth_level_slot_damage_and_domain_healing() -> None:
    hero = build_seraphine_dawnshield_2014(9)
    profile = build_seraphine_dawnshield_2014_profile(9)
    combat = build_seraphine_2014_combat_profile(9)

    assert hero.max_hp == 84
    assert hero.armor_class == 16
    assert hero.ability_scores is not None and hero.ability_scores.wisdom == 20
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 1,
        "channel-divinity": 2,
    }

    upcast = next(item for item in hero.spell_attack_actions if item.id == "inflict-wounds-l5")
    assert upcast.name == "Inflict Wounds (5th-Level)"
    assert upcast.level == 5
    assert upcast.attack_bonus == 9
    assert (upcast.damage_dice_count, upcast.damage_dice_size, upcast.damage_type) == (
        7, 10, "necrotic",
    )

    mass = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds")
    assert mass.range_ft == 60
    assert mass.area_radius_ft == 30
    assert mass.max_targets == 6
    assert (mass.dice_count, mass.dice_size, mass.healing_bonus) == (3, 8, 12)
    assert mass.resource_id == "spell-slot-5"
    assert mass.excluded_creature_types == ["undead", "construct"]

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_nine_policy_prefers_fifth_level_inflict_wounds_in_melee() -> None:
    caster = EncounterCombatant(
        combatant_id="cleric",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_seraphine_dawnshield_2014(9)),
    )
    target = EncounterCombatant(
        combatant_id="goblin",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(build_goblin_warrior()),
    )
    setup = EncounterSetup(
        heroes=[caster],
        monsters=[target],
        hero_total_levels=9,
        monster_total_cr="1/4",
        starting_distance_ft=5,
        ruleset="2014",
    )

    choice = choose_spell_attack(caster, setup, "1:cleric")
    assert choice is not None
    assert choice.action.id == "inflict-wounds-l5"
    assert choice.action.damage_dice_count == 7


def test_level_nine_spell_package_keeps_domain_spells_on_same_character() -> None:
    package = build_cleric_2014_spell_package(9, 5)

    assert len(package.spells) == 14
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless",
        "cure-wounds",
        "lesser-restoration",
        "spiritual-weapon",
        "beacon-of-hope",
        "revivify",
        "death-ward",
        "guardian-of-faith",
        "mass-cure-wounds",
        "raise-dead",
    ]
