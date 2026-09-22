from app.combat.cleric_channel_divinity import resolve_turn_undead
from app.combat.dice import FixedDiceProvider
from app.combat.group_healing import choose_group_healing_targets, resolve_group_healing
from app.combat.healing_riders import apply_slot_healing_self_rider
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_profile import (
    build_seraphine_dawnshield_level5_profile,
    build_seraphine_dawnshield_level6_profile,
)
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _resources(member: EncounterCombatant) -> dict[str, int]:
    return {item.id: item.current_uses for item in member.state.resources}


def test_level_five_is_incremental_and_has_complete_spell_package() -> None:
    level4 = build_seraphine_dawnshield_level(4)
    hero = build_seraphine_dawnshield_level(5)
    profile = build_seraphine_dawnshield_level5_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 5)

    assert hero.max_hp == level4.max_hp + 5 == 28
    assert hero.ability_scores == profile.final_ability_scores == combat.abilities
    assert hero.spell_save_actions[0].damage_dice_count == 2
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4, "spell-slot-2": 3, "spell-slot-3": 2,
        "channel-divinity": 2, "adrenaline-rush": 3, "relentless-endurance": 1,
    }
    assert [spell.id for spell in package.spells] == [
        "guiding-bolt", "shield-of-faith", "healing-word", "detect-magic",
        "create-or-destroy-water", "augury", "inflict-wounds",
        "dispel-magic", "create-food-and-water",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless", "cure-wounds", "aid", "lesser-restoration",
        "mass-healing-word", "revivify",
    ]
    mass = next(item for item in hero.healing_actions if item.id == "mass-healing-word")
    assert (mass.max_targets, mass.dice_count, mass.dice_size, mass.healing_bonus) == (6, 2, 4, 9)
    assert [item.id for item in hero.effect_removal_actions] == ["dispel-magic"]
    assert hero.progression_features.turning_failure_damage is not None
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_sear_undead_reuses_turning_save_and_keeps_failed_target_turned() -> None:
    cleric = _member(build_seraphine_dawnshield_level(5), "cleric", "heroes", 0)
    skeleton = _member(build_combatant_from_capabilities("srd-skeleton"), "skeleton", "monsters", 10)
    setup = EncounterSetup(
        heroes=[cleric], monsters=[skeleton],
        hero_total_levels=5, monster_total_cr="1/4", ruleset="2024",
    )

    before = skeleton.state.current_hp
    events, sequence = resolve_turn_undead(
        1, 1, cleric, setup, (skeleton,), FixedDiceProvider([1, 1, 1, 1, 1]),
    )

    assert sequence == 2
    event = events[0]
    assert event.save_succeeded is False
    assert event.damage_roll is not None and event.damage_roll.total == 4
    assert skeleton.state.current_hp == before - 4
    assert "turned-undead" in skeleton.state.active_effect_ids
    assert event.damage_components[0].damage_type.value == "radiant"


def test_mass_healing_word_heals_multiple_targets_with_one_slot_and_bonus_action() -> None:
    cleric = _member(build_seraphine_dawnshield_level(5), "cleric", "heroes", 0)
    ally1 = _member(build_seraphine_dawnshield_level(4), "ally1", "heroes", 5)
    ally2 = _member(build_seraphine_dawnshield_level(4), "ally2", "heroes", 10)
    enemy = _member(build_combatant_from_capabilities("srd-skeleton"), "enemy", "monsters", 20)
    ally1.state.current_hp = 1
    ally2.state.current_hp = 2
    setup = EncounterSetup(
        heroes=[cleric, ally1, ally2], monsters=[enemy],
        hero_total_levels=13, monster_total_cr="1/4", ruleset="2024",
    )
    action = next(item for item in cleric.state.template.healing_actions if item.id == "mass-healing-word")
    targets = choose_group_healing_targets(cleric, setup, action, "1:cleric")
    assert [item.combatant_id for item in targets] == ["ally1", "ally2"]

    events, sequence = resolve_group_healing(
        1, 1, cleric, targets, action, FixedDiceProvider([4, 4, 3, 3]), "1:cleric",
    )
    assert sequence == 3
    assert [event.hp_after - event.hp_before for event in events] == [17, 15]
    assert _resources(cleric)["spell-slot-3"] == 1
    assert cleric.state.bonus_action_available is False
    assert cleric.state.action_available is True


def test_level_six_blessed_healer_reuses_post_heal_self_rider() -> None:
    cleric = _member(build_seraphine_dawnshield_level(6), "cleric", "heroes", 0)
    ally = _member(build_seraphine_dawnshield_level(4), "ally", "heroes", 5)
    enemy = _member(build_combatant_from_capabilities("srd-skeleton"), "enemy", "monsters", 20)
    cleric.state.current_hp = 10
    ally.state.current_hp = 1
    action = next(item for item in cleric.state.template.healing_actions if item.id == "mass-healing-word")
    setup = EncounterSetup(
        heroes=[cleric, ally], monsters=[enemy],
        hero_total_levels=10, monster_total_cr="1/4", ruleset="2024",
    )
    targets = choose_group_healing_targets(cleric, setup, action, "1:cleric")
    before = cleric.state.current_hp
    events, sequence = resolve_group_healing(
        1, 1, cleric, targets, action, FixedDiceProvider([2, 2, 2, 2]), "1:cleric",
    )
    assert events
    rider = apply_slot_healing_self_rider(3, 1, cleric, True, action)
    assert rider is not None
    assert cleric.state.current_hp == before + 5
    assert rider.feature_id == "blessed-healer"

    profile = build_seraphine_dawnshield_level6_profile()
    hero = cleric.state.template
    assert hero.max_hp == 33
    assert _resources(cleric)["channel-divinity"] == 3
    assert hero.progression_features.slot_healing_other_self_rider is not None
    assert_character_build_raw_ready(profile, hero)
