"""Prove Roper's full printed ordered Multiattack reaches the shared executor."""
from __future__ import annotations

import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_multiattack_2014 import multiattack_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_control_damage_multiattack_2014 import (
    source_proven_control_then_damage_slots_2014,
)
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "roper")
    except Exception:
        logger.exception("Missing pinned 2014 Roper source")
        raise


def test_source_sequence_compiles_through_shared_attack_slots():
    try:
        card = _source()
        original = card.model_dump_json()
        slots = source_proven_control_then_damage_slots_2014(card)
        assert slots is not None and len(slots) == 5
        control = "2014-roper-tendril"
        bite = "2014-roper-bite"
        assert [slot.attack_ids for slot in slots] == [[control]] * 4 + [[bite]]
        action = multiattack_2014(card)
        assert action is not None and action.is_attack_action is False
        assert len(action.slots) == 5
        combatant = compile_combatant(adapt_monster_mechanics_2014(card))
        assert len(combatant.attack_action.slots) == 5
        payload = template_row(combatant)
        assert len(payload["attack_action"]["slots"]) == 5
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("Roper source Multiattack slot binding failed")
        raise


def test_source_and_identity_mutations_fail_closed():
    try:
        card = _source()
        for old, replacement in (
            ("four attacks with its tendrils", "three attacks with its tendrils"),
            ("uses Reel", "uses Paralyze"),
            ("one attack with its bite", "two attacks with its bite"),
        ):
            assert old in card.source_actions
            changed = card.model_copy(update={
                "source_actions": card.source_actions.replace(old, replacement),
            })
            assert source_proven_control_then_damage_slots_2014(changed) is None
        renamed = card.model_copy(update={
            "id": "other-appendage-beast", "name": "Other Appendage Beast",
        })
        slots = source_proven_control_then_damage_slots_2014(renamed)
        assert slots is not None and len(slots) == 5
        assert slots[0].attack_ids == ["2014-other-appendage-beast-tendril"]
    except Exception:
        logger.exception("Roper Multiattack source mutations not rejected")
        raise

def test_tendril_does_not_reel_target_into_bite_range():
    """The ordinary attack scheduler, not the monster name, owns reach and Advantage."""
    try:
        from app.combat.attack_action_choices import attack_choice
        from app.combat.attack_actions import resolve_attack_action
        from app.combat.conditions import apply_hit_conditions, attack_roll_condition_sources
        from app.combat.dice import SeededDiceProvider
        from app.combat.state import build_combatant_state
        from app.combat.encounter_setup import build_encounter_setup
        from app.domain.encounters import EncounterCombatant, EncounterSetup
        from app.domain.models import EncounterSelection, RollMode

        card = _source()
        immutable_source = card.model_dump_json()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        tendril = next(item for item in attacks if item and item.id == "2014-roper-tendril")
        bite = next(item for item in attacks if item and item.id == "2014-roper-bite")
        assert (tendril.weapon.reach_ft, bite.weapon.reach_ft) == (50, 5)

        hero_template = build_encounter_setup(EncounterSelection(
            ruleset="2014", hero_ids=["karnok-stoneward-2014-l5"],
            monster_ids=["2014-goblin"],
        )).heroes[0].state.template

        for distance_ft in (40, 5):
            roper = EncounterCombatant(
                combatant_id="owner", side="monsters", position_ft=0,
                state=build_combatant_state(template),
            )
            victim = EncounterCombatant(
                combatant_id="victim", side="heroes", position_ft=distance_ft,
                state=build_combatant_state(hero_template),
            )
            setup = EncounterSetup(
                heroes=[victim], monsters=[roper], ruleset="2014",
                hero_total_levels=5, monster_total_cr="5",
            )
            slots = template.attack_action.slots
            # Four Tendril slots can legally reach the distant victim.
            assert attack_choice(roper, setup, slots[0]) is not None
            # Reel is not an executable movement slot in the Iron Pit.
            assert len(slots) == 5
            assert (attack_choice(roper, setup, slots[-1]) is not None) == (distance_ft == 5)

            if distance_ft == 5:
                # Use the ordinary Grappled/Restrained state before testing Bite.
                assert apply_hit_conditions(tendril, victim.state, "owner", setup=setup) == [
                    "grappled", "restrained",
                ]
                advantage, disadvantage = attack_roll_condition_sources(
                    roper.state, victim.state, 5, "victim", setup=setup,
                )
                assert advantage > disadvantage

            # Resolve the real source-built sequence through universal attacks.
            events, _ = resolve_attack_action(
                1, 1, roper, setup, SeededDiceProvider(19),
            )
            names = [event.attack_name for event in events if event.event_type == "attack"]
            assert names.count("Tendril") == 4
            assert names.count("Bite") == (1 if distance_ft == 5 else 0)
            if distance_ft == 5:
                bite_event = next(event for event in events if event.attack_name == "Bite")
                assert bite_event.attack_roll.mode is RollMode.ADVANTAGE
            # No Tendril hit or omitted Reel silently relocates its target.
            assert victim.position_ft == distance_ft
        assert card.model_dump_json() == immutable_source
    except Exception:
        logger.exception("Source Roper Tendril/Reel/Bite reach and Advantage parity failed")
        raise
