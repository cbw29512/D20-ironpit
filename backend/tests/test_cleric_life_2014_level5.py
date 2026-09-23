from app.combat.cleric_channel_divinity import resolve_turn_undead
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_level_five_advances_level_four_without_rebuilding_character() -> None:
    level_four = build_seraphine_dawnshield_2014_profile(4)
    level_five = build_seraphine_dawnshield_2014_profile(5)

    assert level_five.character_name == level_four.character_name == "Seraphine Dawnshield"
    assert level_five.species_id == level_four.species_id == "hill-dwarf"
    assert level_five.background_id == level_four.background_id == "acolyte"
    assert level_five.subclass_id == level_four.subclass_id == "life-domain"
    assert level_five.class_equipment == level_four.class_equipment
    assert level_five.advancement_increases == level_four.advancement_increases
    assert level_five.final_ability_scores == level_four.final_ability_scores
    assert level_five.feature_audits[: len(level_four.feature_audits)] == level_four.feature_audits
    assert level_five.feature_audits[-1].feature_id == "destroy-undead-half"
    assert level_five.feature_audits[-1].automated is True


def test_level_five_spell_package_keeps_prior_preparations_and_adds_domain_spells() -> None:
    package = build_cleric_2014_spell_package(5, 4)

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
        "prayer-of-healing",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless",
        "cure-wounds",
        "lesser-restoration",
        "spiritual-weapon",
        "beacon-of-hope",
        "revivify",
    ]


def test_level_five_runtime_applies_only_level_five_combat_deltas() -> None:
    hero = build_seraphine_dawnshield_2014(5)
    profile = build_seraphine_dawnshield_2014_profile(5)
    combat = build_seraphine_2014_combat_profile(5)

    assert hero.max_hp == 48
    assert hero.armor_class == 16
    assert hero.ability_scores is not None and hero.ability_scores.wisdom == 18
    assert hero.progression_features.turning_failure_destroy_max_cr == "1/2"
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 2,
        "channel-divinity": 1,
    }

    sacred_flame = next(item for item in hero.spell_save_actions if item.id == "sacred-flame")
    guiding_bolt = next(item for item in hero.spell_attack_actions if item.id == "guiding-bolt")
    spiritual_weapon = hero.persistent_spell_attack_actions[0]
    beacon = next(item for item in hero.defensive_spell_actions if item.id == "beacon-of-hope")

    assert sacred_flame.dc == 15
    assert sacred_flame.damage_dice_count == 2
    assert guiding_bolt.attack_bonus == 7
    assert spiritual_weapon.attack.attack_bonus == 7
    assert spiritual_weapon.attack.damage_bonus == 4
    assert {effect.kind for effect in beacon.modifier_effects} == {
        "saving-throw-advantage", "death-save-advantage", "healing-maximize",
    }

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_destroy_undead_uses_cr_threshold_inside_shared_turning_resolution() -> None:
    cleric = _member(build_seraphine_dawnshield_2014(5), "cleric-low", "heroes", 0)
    skeleton_template = build_combatant_from_capabilities("2014-skeleton")
    skeleton = _member(skeleton_template, "skeleton-low", "monsters", 10)
    setup = EncounterSetup(
        heroes=[cleric], monsters=[skeleton],
        hero_total_levels=5, monster_total_cr="1/4", ruleset="2014",
    )

    events, _ = resolve_turn_undead(1, 1, cleric, setup, (skeleton,), FixedDiceProvider([1]))

    assert events[0].save_succeeded is False
    assert skeleton.state.current_hp == 0
    assert skeleton.state.is_dead is True
    assert events[0].applied_condition_ids == []
    assert "trembling" not in skeleton.state.active_effect_ids

    cleric_high = _member(build_seraphine_dawnshield_2014(5), "cleric-high", "heroes", 0)
    high_template = skeleton_template.model_copy(update={
        "id": "test-cr2-undead",
        "name": "CR 2 Test Undead",
        "challenge_rating": "2",
        "max_hp": 40,
    })
    high = _member(high_template, "skeleton-high", "monsters", 10)
    high_setup = EncounterSetup(
        heroes=[cleric_high], monsters=[high],
        hero_total_levels=5, monster_total_cr="2", ruleset="2014",
    )

    high_events, _ = resolve_turn_undead(
        1, 1, cleric_high, high_setup, (high,), FixedDiceProvider([1]),
    )

    assert high_events[0].save_succeeded is False
    assert high.state.is_dead is False
    assert high.state.current_hp == 40
    assert "trembling" in high.state.active_effect_ids
