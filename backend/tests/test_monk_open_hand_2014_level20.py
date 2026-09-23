from __future__ import annotations

from unittest.mock import patch

import app.combat.encounter_engine as encounter_engine
from app.combat.dice import SeededDiceProvider
from app.combat.encounter_engine import run_encounter
from app.combat.encounter_setup import build_encounter_setup
from app.combat.initiative_resource_refill import resolve_initiative_resource_refills
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.domain.encounters import EncounterSelection


def test_level20_snapshot_preserves_progression_and_binds_perfect_self() -> None:
    profile = build_kael_stillwater_2014_profile(20)
    combat = build_kael_2014_combat_profile(20)
    hero = build_kael_stillwater_2014(20)

    assert profile.final_ability_scores == combat.abilities == hero.ability_scores
    assert hero.ability_scores.strength == 14
    assert hero.ability_scores.dexterity == 20
    assert hero.ability_scores.constitution == 14
    assert hero.ability_scores.wisdom == 20
    assert hero.armor_class == 20
    assert hero.max_hp == 143
    assert hero.speed_ft == 60
    assert combat.speed_ft == 60
    assert hero.initiative_bonus == 5
    assert {item.id: item.max_uses for item in hero.resources} == {
        "ki": 20,
        "wholeness-of-body": 1,
    }
    assert hero.saving_throw_bonuses == {
        "strength": 8,
        "dexterity": 11,
        "constitution": 8,
        "intelligence": 6,
        "wisdom": 11,
        "charisma": 5,
    }
    assert all(
        attack.attack_bonus == 11
        for attack in [hero.weapon_attack, *hero.alternate_weapon_attacks]
    )
    assert hero.progression_features.opening_targeting_ward is not None
    assert hero.progression_features.opening_targeting_ward.save_dc == 19
    assert hero.progression_features.deferred_save_effect is not None
    assert hero.progression_features.deferred_save_effect.save_dc == 19
    assert hero.timed_self_buff_actions[0].id == "empty-body"

    assert len(hero.initiative_resource_refill_grants) == 1
    grant = hero.initiative_resource_refill_grants[0]
    assert grant.source_id == "perfect-self"
    assert grant.source_name == "Perfect Self"
    assert grant.resource_id == "ki"
    assert grant.when_at_or_below == 0
    assert grant.restore_amount == 4

    audit = next(item for item in profile.feature_audits if item.feature_id == "perfect-self")
    assert audit.automated is True


def test_perfect_self_only_refills_when_ki_is_zero() -> None:
    selection = EncounterSelection(
        ruleset="2014",
        hero_ids=["kael-stillwater-2014-l20"],
        monster_ids=["2014-wolf"],
    )
    setup = build_encounter_setup(selection)
    monk = setup.heroes[0]
    ki = next(item for item in monk.state.resources if item.id == "ki")

    ki.current_uses = 1
    events, sequence = resolve_initiative_resource_refills(1, setup)
    assert events == []
    assert sequence == 1
    assert ki.current_uses == 1

    ki.current_uses = 0
    events, sequence = resolve_initiative_resource_refills(1, setup)
    assert sequence == 2
    assert ki.current_uses == 4
    assert events[0].feature_id == "perfect-self"
    assert events[0].resource_remaining == 4
    assert "Perfect Self" in events[0].description


def test_live_encounter_applies_perfect_self_after_initiative_before_turns() -> None:
    selection = EncounterSelection(
        ruleset="2014",
        hero_ids=["kael-stillwater-2014-l20"],
        monster_ids=["2014-wolf"],
    )
    setup = build_encounter_setup(selection)
    ki = next(item for item in setup.heroes[0].state.resources if item.id == "ki")
    ki.current_uses = 0

    with patch.object(encounter_engine, "build_encounter_setup", return_value=setup):
        result = run_encounter(selection, SeededDiceProvider(2020))

    perfect = next(event for event in result.events if event.feature_id == "perfect-self")
    initiative_sequences = [
        event.sequence for event in result.events if event.event_type == "initiative"
    ]
    first_turn_event = next(
        event for event in result.events
        if event.round_number >= 1 and event.actor_id != "arena"
    )
    assert perfect.round_number == 0
    assert perfect.resource_remaining == 4
    assert perfect.sequence > max(initiative_sequences)
    assert perfect.sequence < first_turn_event.sequence
