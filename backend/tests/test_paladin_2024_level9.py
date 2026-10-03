from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.dice import FixedDiceProvider
from app.combat.multi_target_save_actions import (
    choose_multi_target_save_action,
    resolve_multi_target_save_action,
)
from app.combat.state import begin_turn, build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup() -> tuple[EncounterSetup, EncounterCombatant, list[EncounterCombatant]]:
    paladin = _member(build_aurelia_brightshield_2024(9), "aurelia", "heroes", 0)
    enemies = [
        _member(build_commoner().model_copy(update={"ruleset": "2024"}), f"enemy-{index}", "monsters", 10 + index * 5)
        for index in range(3)
    ]
    return EncounterSetup(
        heroes=[paladin],
        monsters=enemies,
        hero_total_levels=9,
        monster_total_cr="0",
        ruleset="2024",
    ), paladin, enemies


def test_2024_paladin_level_nine_progression_is_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(9)
    hero = build_aurelia_brightshield_2024(9)
    combat = next(item for item in build_aurelia_2024_combat_profiles() if item.level == 9)

    assert profile.final_ability_scores.strength == 20
    assert profile.final_ability_scores.charisma == 15
    assert (hero.max_hp, hero.armor_class) == (76, 19)
    assert hero.weapon_attack.attack_bonus == 9
    assert hero.weapon_attack.damage_bonus == 5
    assert hero.skill_bonuses["athletics"] == 9
    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 45,
        "spell-slot-1": 4,
        "paladins-smite-free-cast": 1,
        "channel-divinity": 2,
        "spell-slot-2": 3,
        "faithful-steed-free-cast": 1,
        "spell-slot-3": 2,
    }

    package = canonical_spell_package("paladin", 9, "2024", 2)
    assert package is not None
    assert [spell.id for spell in package.spells] == [
        "cure-wounds", "divine-favor", "bless", "searing-smite",
        "thunderous-smite", "shining-smite", "lesser-restoration",
        "aura-of-vitality", "blinding-smite",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "divine-smite", "protection-from-evil-and-good", "shield-of-faith",
        "find-steed", "aid", "zone-of-truth", "beacon-of-hope", "dispel-magic",
    ]

    abjure = next(action for action in hero.saving_throw_actions if action.id == "abjure-foes")
    assert (abjure.save_ability, abjure.dc, abjure.range_ft, abjure.max_targets) == ("wisdom", 14, 60, 2)
    assert abjure.resource_id == "channel-divinity"
    assert abjure.requires_target_sight is True
    assert abjure.failed_save_timed_effect is not None
    assert abjure.failed_save_timed_effect.turn_behavior == "single_activity"
    assert abjure.failed_save_timed_effect.ends_on_damage is True

    beacon = next(action for action in hero.defensive_spell_actions if action.id == "beacon-of-hope")
    assert (beacon.level, beacon.range_ft, beacon.concentration) == (3, 30, True)
    dispel = next(action for action in hero.effect_removal_actions if action.id == "dispel-magic")
    assert (dispel.level, dispel.range_ft, dispel.casting_ability) == (3, 120, "charisma")

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)


def test_abjure_foes_caps_targets_spends_once_and_uses_single_activity_turns() -> None:
    setup, paladin, enemies = _setup()
    selection = choose_multi_target_save_action(paladin, setup)
    assert selection is not None
    action, targets = selection
    assert action.id == "abjure-foes"
    assert [target.combatant_id for target in targets] == ["enemy-0", "enemy-1"]

    events, sequence = resolve_multi_target_save_action(
        1, 1, paladin, setup, FixedDiceProvider([1, 1]), selection,
    )
    assert sequence == 3
    assert len(events) == 2
    assert next(item for item in paladin.state.resources if item.id == "channel-divinity").current_uses == 1
    assert paladin.state.action_available is False
    assert "frightened" in enemies[0].state.active_effect_ids
    assert "frightened" in enemies[1].state.active_effect_ids
    assert "frightened" not in enemies[2].state.active_effect_ids

    begin_turn(enemies[0].state)
    assert is_available(enemies[0].state, "action") is True
    assert is_available(enemies[0].state, "bonus_action") is True
    assert is_available(enemies[0].state, "reaction") is True
    spend(enemies[0].state, "action")
    assert is_available(enemies[0].state, "bonus_action") is False
    assert enemies[0].state.movement_remaining_ft == 0
    assert is_available(enemies[0].state, "reaction") is True

    apply_damage(enemies[1].state, 1, damage_types={"slashing"}, affected_states=[enemy.state for enemy in enemies])
    assert "frightened" not in enemies[1].state.active_effect_ids


def test_level_eight_snapshot_remains_stable_after_level_nine() -> None:
    level8 = build_aurelia_brightshield_2024(8)
    assert level8.ability_scores.strength == 20
    assert level8.ability_scores.charisma == 15
    assert level8.weapon_attack.attack_bonus == 8
    assert not level8.saving_throw_actions
