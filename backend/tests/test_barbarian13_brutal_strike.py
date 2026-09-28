from __future__ import annotations

import pytest

from app.combat.defensive_modifier_rules import saving_throw_disadvantage_sources
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.incoming_attack_bonus import next_incoming_attack_roll_flat_bonus
from app.combat.opportunity_attack_rules import opportunity_attacks_suppressed
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_berserker_endgame_profile import build_rokhan_stonefury_level13_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.hero_combat_feature_registry import compile_progression_feature_fields
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="hero-1:rokhan-stonefury-l13",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_rokhan_stonefury_level(13)),
    )
    enemy = EncounterCombatant(
        combatant_id="monster-1:test-fighter",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    setup = EncounterSetup(heroes=[hero], monsters=[enemy], hero_total_levels=13, monster_total_cr="0")
    return hero, enemy, setup


def _strike(effect_id: str):
    hero, enemy, setup = _setup()
    turn_key = f"1:{hero.combatant_id}"
    event = resolve_encounter_attack(
        1,
        1,
        hero,
        enemy,
        hero.state.template.weapon_attack,
        5,
        FixedDiceProvider([15, 4, 8, 6]),
        setup,
        spend_action=False,
        allow_reckless=True,
        turn_key=turn_key,
        brutal_strike_effect_ids=(effect_id,),
    )
    return hero, enemy, setup, event


def test_level13_progression_exposes_all_four_effects_but_only_one_choice() -> None:
    template = build_rokhan_stonefury_level(13)
    profile = build_rokhan_stonefury_level13_profile()
    effects = template.progression_features.brutal_strike_effect_ids

    assert profile.level == 13
    assert set(effects) == {"forceful-blow", "hamstring-blow", "staggering-blow", "sundering-blow"}
    assert template.progression_features.brutal_strike_damage_dice == 1
    assert template.progression_features.brutal_strike_max_effects == 1


def test_level9_and_level17_brutal_strike_shape_is_data_driven() -> None:
    level9 = build_rokhan_stonefury_level(9).progression_features
    assert level9.brutal_strike_effect_ids == ["forceful-blow", "hamstring-blow"]
    assert level9.brutal_strike_max_effects == 1
    assert level9.brutal_strike_damage_dice == 1

    level17 = compile_progression_feature_fields(
        ["brutal-strike", "improved-brutal-strike", "brutal-strike-2d10"],
        17,
    )
    assert level17["brutal_strike_damage_dice"] == 2
    assert level17["brutal_strike_max_effects"] == 2
    assert set(level17["brutal_strike_effect_ids"]) == {
        "forceful-blow", "hamstring-blow", "staggering-blow", "sundering-blow",
    }


def test_level13_real_attack_applies_staggering_blow_after_brutal_strike_hit() -> None:
    _, enemy, _, event = _strike("staggering-blow")

    assert event.hit is True
    assert any(part.source == "Brutal Strike" for part in event.damage_components)
    assert saving_throw_disadvantage_sources(enemy.state) == 1
    assert opportunity_attacks_suppressed(enemy) is True
    assert "Brutal Strike applies Staggering Blow." in event.description


def test_level13_real_attack_applies_sundering_blow_to_other_creature_only() -> None:
    hero, enemy, _, event = _strike("sundering-blow")

    assert event.hit is True
    assert next_incoming_attack_roll_flat_bonus(enemy.state, hero.combatant_id) == 0
    assert next_incoming_attack_roll_flat_bonus(enemy.state, "other-creature") == 5
    assert "Brutal Strike applies Sundering Blow." in event.description


def test_level13_rejects_two_effects_until_level17() -> None:
    hero, enemy, setup = _setup()
    with pytest.raises(RuntimeError, match="Attack resolution failed"):
        resolve_encounter_attack(
            1,
            1,
            hero,
            enemy,
            hero.state.template.weapon_attack,
            5,
            FixedDiceProvider([15, 4, 8, 6]),
            setup,
            spend_action=False,
            allow_reckless=True,
            turn_key=f"1:{hero.combatant_id}",
            brutal_strike_effect_ids=("staggering-blow", "sundering-blow"),
        )
