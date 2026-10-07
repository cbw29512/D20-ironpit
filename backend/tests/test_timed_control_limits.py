from __future__ import annotations

import json
import re
from pathlib import Path

from app.combat.action_economy import is_available, spend
from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_flat_bonuses import saving_throw_flat_bonus
from app.combat.modifier_stack import effective_armor_class, effective_speed
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.saving_throws import resolve_save_action
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_ability_d20 import timed_ability_d20_disadvantage_sources
from app.combat.timed_attack_cap import turn_attack_allowed
from app.combat.timed_conditions import apply_timed_condition
from app.combat.exhaustion import ability_check_disadvantage_sources
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_save_control_2014 import (
    compile_failed_save_control_2014,
    supports_failed_save_control_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.timed_control_limits import TimedControlLimits, TimedSaveFlatBonus

_COPPER = {
    "copper-dragon-wyrmling": {"dc": 11, "cone_ft": 15},
    "young-copper-dragon": {"dc": 14, "cone_ft": 30},
    "adult-copper-dragon": {"dc": 18, "cone_ft": 60},
    "ancient-copper-dragon": {"dc": 22, "cone_ft": 90},
}
_GOLD = {
    "gold-dragon-wyrmling": {"dc": 13, "cone_ft": 15},
    "young-gold-dragon": {"dc": 17, "cone_ft": 30},
    "adult-gold-dragon": {"dc": 21, "cone_ft": 60},
    "ancient-gold-dragon": {"dc": 24, "cone_ft": 90},
}
_SLOW_COMBAT_KEYS = {
    "speed_multiplier": 0.5,
    "blocks_reactions": True,
    "action_bonus_exclusive": True,
    "max_attacks_per_turn": 1,
}


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


_CATALOG_PATH = Path(__file__).resolve().parents[1] / "app/content/data/srd_5_1_monsters_catalog.json"


def _printed_action_plain(monster_id: str, heading: str) -> str:
    catalog = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    html = next(item["source_actions"] for item in catalog if item["id"] == monster_id)
    for part in re.findall(r"<p>(.*?)</p>", html, flags=re.IGNORECASE | re.DOTALL):
        plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", part)).strip()
        if plain.startswith(heading):
            return plain
    raise AssertionError(f"{monster_id} has no printed {heading!r} paragraph.")


def _catalog_action(monster_id: str, action_id: str) -> dict:
    source = next(item for item in load_monster_source_2014() if item.id == monster_id)
    return next(
        item for item in source.saving_throw_actions
        if isinstance(item, dict) and item.get("id") == action_id
    )


def _rider_from_catalog(action: dict) -> FailedSaveTimedEffect:
    control = action["failure_control_effect"]
    return FailedSaveTimedEffect(
        effect_id=str(control["effect_id"]),
        duration_rounds=control.get("duration_rounds"),
        expiry_timing=control.get("expiry_timing", "target_turn_end"),
        repeat_save_ability=control.get("repeat_save_ability"),
        repeat_save_dc=control.get("repeat_save_dc"),
        repeat_save_timing=control.get("repeat_save_timing"),
        speed_multiplier=float(control.get("speed_multiplier", 1.0)),
        blocks_reactions=bool(control.get("blocks_reactions")),
        action_bonus_exclusive=bool(control.get("action_bonus_exclusive")),
        max_attacks_per_turn=control.get("max_attacks_per_turn"),
        disadvantage_strength_d20_tests=bool(control.get("disadvantage_strength_d20_tests")),
        armor_class_bonus=int(control.get("armor_class_bonus", 0) or 0),
        saving_throw_flat_bonuses=list(control.get("saving_throw_flat_bonuses") or []),
    )


def test_2014_classifier_compiles_catalog_slow_and_weaken() -> None:
    for monster_id in (*_COPPER, *_GOLD, "stone-golem"):
        action_id = "slow" if monster_id == "stone-golem" else (
            "slowing-breath" if monster_id in _COPPER else "weakening-breath"
        )
        action = _catalog_action(monster_id, action_id)
        assert supports_failed_save_control_2014(action) is True
        rider = compile_failed_save_control_2014(action)
        assert rider is not None
        compiled = rider.compiled_limits()
        assert compiled is not None
        if monster_id in _COPPER or monster_id == "stone-golem":
            assert (compiled.speed_multiplier, compiled.action_bonus_exclusive, compiled.max_attacks_per_turn) == (0.5, True, 1)
            assert compiled.d20_disadvantage_abilities == []
            assert compiled.armor_class_bonus == 0
        else:
            assert compiled.d20_disadvantage_abilities == ["strength"]
            assert compiled.speed_multiplier == 1.0
            assert compiled.max_attacks_per_turn is None


def test_copper_slowing_breath_payloads_match_printed_text() -> None:
    for monster_id, expected in _COPPER.items():
        action = _catalog_action(monster_id, "slowing-breath")
        control = action["failure_control_effect"]
        assert action["save_ability"] == "constitution"
        assert action["dc"] == expected["dc"]
        assert action["area"]["length_ft"] == expected["cone_ft"]
        assert control["repeat_save_ability"] == "constitution"
        assert control["repeat_save_dc"] == expected["dc"]
        assert control["repeat_save_timing"] == "target_turn_end"
        assert control["duration_rounds"] == 10
        for key, value in _SLOW_COMBAT_KEYS.items():
            assert control[key] == value
        assert "disadvantage_strength_d20_tests" not in control
        assert "armor_class_bonus" not in control
        assert "saving_throw_flat_bonuses" not in control


def test_stone_golem_slow_matches_printed_golem_text_not_slow_spell() -> None:
    action = _catalog_action("stone-golem", "slow")
    control = action["failure_control_effect"]
    assert (action["save_ability"], action["dc"], action["range_ft"]) == ("wisdom", 17, 10)
    assert control["repeat_save_ability"] == "wisdom"
    assert control["repeat_save_dc"] == 17
    for key, value in _SLOW_COMBAT_KEYS.items():
        assert control[key] == value
    assert "disadvantage_strength_d20_tests" not in control
    assert "armor_class_bonus" not in control
    assert "saving_throw_flat_bonuses" not in control


def test_gold_weakening_breath_payloads_are_strength_disadvantage_only() -> None:
    for monster_id, expected in _GOLD.items():
        action = _catalog_action(monster_id, "weakening-breath")
        control = action["failure_control_effect"]
        assert action["save_ability"] == "strength"
        assert action["dc"] == expected["dc"]
        assert action["area"]["length_ft"] == expected["cone_ft"]
        assert control["disadvantage_strength_d20_tests"] is True
        assert control["repeat_save_ability"] == "strength"
        assert control["repeat_save_dc"] == expected["dc"]
        assert control["duration_rounds"] == 10
        for key in _SLOW_COMBAT_KEYS:
            assert key not in control
        assert "armor_class_bonus" not in control
        assert "saving_throw_flat_bonuses" not in control


def test_printed_2014_slow_weaken_stat_blocks_are_not_one_bundle() -> None:
    for monster_id in _COPPER:
        text = _printed_action_plain(monster_id, "Slowing Breath")
        assert "can't use reactions" in text
        assert "speed is halved" in text
        assert "can't make more than one attack on its turn" in text
        assert "action or a bonus action" in text
        assert "1 minute" in text
        assert "Constitution" in text
        assert "-2" not in text
        assert "AC" not in text
        assert "Dexterity" not in text
        assert "disadvantage" not in text.casefold()
    golem = _printed_action_plain("stone-golem", "Slow")
    assert "can't use reactions" in golem
    assert "speed is halved" in golem
    assert "can't make more than one attack on its turn" in golem
    assert "action or a bonus action" in golem
    assert "Wisdom" in golem
    assert "-2" not in golem
    assert "AC" not in golem
    assert "Dexterity" not in golem
    assert "disadvantage" not in golem.casefold()
    for monster_id in _GOLD:
        text = _printed_action_plain(monster_id, "Weakening Breath")
        assert "disadvantage on Strength-based attack rolls, Strength checks, and Strength saving throws" in text
        assert "1 minute" in text
        assert "speed is halved" not in text
        assert "can't use reactions" not in text
        assert "can't make more than one attack" not in text
        assert "bonus action" not in text.casefold()
        assert "-2" not in text


def test_2014_slow_weaken_unlocks_only_save_action_only_cards() -> None:
    unlocked = {
        "copper-dragon-wyrmling", "young-copper-dragon", "adult-copper-dragon",
        "gold-dragon-wyrmling", "young-gold-dragon", "stone-golem",
    }
    parked = {
        "ancient-copper-dragon": "source:extra-action",
        "adult-gold-dragon": "source:extra-action",
        "ancient-gold-dragon": "source:extra-action",
    }
    by_id = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in unlocked:
        assert basic_blockers_2014(by_id[monster_id]) == ()
    for monster_id, blocker in parked.items():
        remaining = basic_blockers_2014(by_id[monster_id])
        assert blocker in remaining
        assert "mechanic:save-action" not in remaining


def test_copper_slowing_breath_applies_only_printed_combat_limits() -> None:
    dragon = _member(build_commoner().model_copy(update={"ruleset": "2014"}), "copper", "monsters", 0)
    hero = _member(build_karnok_stoneward_level(5), "hero", "heroes", 5)
    action = SavingThrowAction(
        id="slowing-breath",
        name="Slowing Breath",
        save_ability="constitution",
        dc=11,
        range_ft=15,
        failed_save_timed_effect=_rider_from_catalog(_catalog_action("copper-dragon-wyrmling", "slowing-breath")),
    )
    ac_before = effective_armor_class(hero.state)
    event = resolve_save_action(1, 1, dragon, hero, action, 10, FixedDiceProvider([1]))
    assert event.save_succeeded is False
    begin_turn(hero.state)
    assert effective_speed(hero.state) == 15
    assert hero.state.movement_remaining_ft == 15
    assert is_available(hero.state, "reaction") is False
    spend(hero.state, "action")
    assert is_available(hero.state, "bonus_action") is False
    assert hero.state.movement_remaining_ft == 15
    assert timed_ability_d20_disadvantage_sources(hero.state, "strength") == 0
    assert effective_armor_class(hero.state) == ac_before
    assert saving_throw_flat_bonus(hero.state, "dexterity") == 0


def test_stone_golem_slow_does_not_apply_slow_spell_penalties() -> None:
    golem = _member(build_commoner().model_copy(update={"ruleset": "2014"}), "golem", "monsters", 0)
    hero = _member(build_karnok_stoneward_level(5), "hero", "heroes", 5)
    action = SavingThrowAction(
        id="slow",
        name="Slow",
        save_ability="wisdom",
        dc=17,
        range_ft=10,
        failed_save_timed_effect=_rider_from_catalog(_catalog_action("stone-golem", "slow")),
    )
    ac_before = effective_armor_class(hero.state)
    event = resolve_save_action(1, 1, golem, hero, action, 5, FixedDiceProvider([1]))
    assert event.save_succeeded is False
    begin_turn(hero.state)
    assert effective_speed(hero.state) == 15
    assert is_available(hero.state, "reaction") is False
    assert effective_armor_class(hero.state) == ac_before
    assert saving_throw_flat_bonus(hero.state, "dexterity") == 0
    assert timed_ability_d20_disadvantage_sources(hero.state, "strength") == 0


def test_gold_weakening_breath_applies_strength_disadvantage_only() -> None:
    dragon = _member(build_commoner().model_copy(update={"ruleset": "2014"}), "gold", "monsters", 0)
    hero = _member(build_karnok_stoneward_level(5), "hero", "heroes", 5)
    action = SavingThrowAction(
        id="weakening-breath",
        name="Weakening Breath",
        save_ability="strength",
        dc=13,
        range_ft=15,
        failed_save_timed_effect=_rider_from_catalog(_catalog_action("gold-dragon-wyrmling", "weakening-breath")),
    )
    ac_before = effective_armor_class(hero.state)
    event = resolve_save_action(1, 1, dragon, hero, action, 10, FixedDiceProvider([1]))
    assert event.save_succeeded is False
    begin_turn(hero.state)
    assert effective_speed(hero.state) == 30
    assert is_available(hero.state, "reaction") is True
    spend(hero.state, "action")
    assert is_available(hero.state, "bonus_action") is True
    assert hero.state.movement_remaining_ft == 30
    assert timed_ability_d20_disadvantage_sources(hero.state, "strength") == 1
    assert timed_ability_d20_disadvantage_sources(hero.state, "dexterity") == 0
    assert ability_check_disadvantage_sources(hero.state, "strength") == 1
    assert saving_throw_mode(hero.state, "strength") is RollMode.DISADVANTAGE
    assert saving_throw_mode(hero.state, "dexterity") is RollMode.NORMAL
    assert effective_armor_class(hero.state) == ac_before
    assert turn_attack_allowed(hero.state) is True


def test_slow_spell_penalties_apply_only_when_printed() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(5))
    ac_before = effective_armor_class(state)
    apply_timed_condition(
        state,
        "slowed",
        "wizard",
        source_effect_id="slow",
        suppress_reactions=True,
        control_limits=TimedControlLimits(
            speed_multiplier=0.5,
            action_bonus_exclusive=True,
            max_attacks_per_turn=1,
            armor_class_bonus=-2,
            saving_throw_flat_bonuses=[TimedSaveFlatBonus(ability="dexterity", flat_bonus=-2)],
        ),
    )
    assert effective_armor_class(state) == ac_before - 2
    assert saving_throw_flat_bonus(state, "dexterity") == -2
    assert saving_throw_flat_bonus(state, "constitution") == 0
    assert timed_ability_d20_disadvantage_sources(state, "strength") == 0


def test_single_activity_still_zeros_movement_after_an_action() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(5))
    apply_timed_condition(
        state,
        "frightened",
        "paladin",
        source_effect_id="abjure-foes",
        turn_behavior="single_activity",
    )
    begin_turn(state)
    spend(state, "action")
    assert state.movement_remaining_ft == 0
    assert is_available(state, "bonus_action") is False


def test_copper_slowing_breath_caps_extra_attack_at_one() -> None:
    hero = _member(build_karnok_stoneward_level(5), "hero-1:karnok-l5", "heroes", 0)
    target = _member(
        build_commoner().model_copy(update={"max_hp": 200, "ruleset": "2014"}),
        "monster-1",
        "monsters",
        5,
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[target], hero_total_levels=5, monster_total_cr="0", ruleset="2014",
    )
    apply_timed_condition(
        hero.state,
        "slowed",
        "copper",
        source_effect_id="slowing-breath",
        suppress_reactions=True,
        control_limits=_rider_from_catalog(
            _catalog_action("copper-dragon-wyrmling", "slowing-breath")
        ).compiled_limits(),
    )
    begin_turn(hero.state)
    events, _ = resolve_attack_action(1, 1, hero, setup, FixedDiceProvider([2, 2, 2, 2]))
    assert len([event for event in events if event.event_type == "attack"]) == 1
    assert turn_attack_allowed(hero.state) is False
