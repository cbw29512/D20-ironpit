from __future__ import annotations

from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.state import build_combatant_state
from app.content.bard_lore_2014_combat_profile import build_lyra_2014_combat_profile
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.demo import build_goblin_warrior
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup


def test_level_six_advances_persistent_lyra_and_binds_lore_support_tools() -> None:
    level_five = build_lyra_silverstring_2014_profile(5)
    profile = build_lyra_silverstring_2014_profile(6)
    hero = build_lyra_silverstring_2014(6)
    combat = build_lyra_2014_combat_profile(6)

    assert profile.character_name == level_five.character_name == "Lyra Silverstring"
    assert profile.species_id == level_five.species_id == "half-elf"
    assert profile.background_id == level_five.background_id == "entertainer"
    assert profile.subclass_id == level_five.subclass_id == "college-lore"
    assert profile.advancement_increases == level_five.advancement_increases
    assert profile.final_ability_scores == level_five.final_ability_scores

    assert {item.id: item.max_uses for item in hero.resources} == {
        "bardic-inspiration": 4,
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
    }
    assert [item.id for item in hero.timed_self_buff_actions] == ["countercharm"]
    assert [item.id for item in hero.persistent_spell_attack_actions] == ["spiritual-weapon"]
    assert [item.id for item in hero.defensive_spell_actions] == ["bless"]

    spiritual_weapon = hero.persistent_spell_attack_actions[0]
    assert spiritual_weapon.attack.attack_bonus == 7
    assert spiritual_weapon.attack.damage_bonus == 4
    assert hero.skill_bonuses["performance"] == 10
    assert hero.skill_bonuses["persuasion"] == 10

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_seven_adds_shared_freedom_of_movement_and_fourth_level_slot() -> None:
    profile = build_lyra_silverstring_2014_profile(7)
    hero = build_lyra_silverstring_2014(7)
    combat = build_lyra_2014_combat_profile(7)

    assert {item.id: item.max_uses for item in hero.resources} == {
        "bardic-inspiration": 4,
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
    }
    assert [item.id for item in hero.defensive_spell_actions] == [
        "bless",
        "freedom-of-movement",
    ]

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_seven_uses_one_free_opening_buff_without_spending_action() -> None:
    lyra = EncounterCombatant(
        combatant_id="lyra",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_lyra_silverstring_2014(7)),
    )
    goblin = EncounterCombatant(
        combatant_id="goblin",
        side="monsters",
        position_ft=40,
        state=build_combatant_state(build_goblin_warrior()),
    )
    setup = EncounterSetup(
        heroes=[lyra],
        monsters=[goblin],
        hero_total_levels=7,
        monster_total_cr="1/4",
        ruleset="2014",
    )

    events, _ = prepare_opening_buffs(setup)

    assert [event.feature_id for event in events] == ["freedom-of-movement"]
    assert lyra.state.opening_buff_id == "freedom-of-movement"
    assert lyra.state.action_available is True
    assert lyra.state.bonus_action_available is True
    assert next(
        item for item in lyra.state.resources if item.id == "spell-slot-4"
    ).current_uses == 0
