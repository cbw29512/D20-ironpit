"""A renamed character or monster uses identical attack resource mechanics."""
from __future__ import annotations

import logging

import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.attack_action_sequences import select_sequence
from app.combat.state import begin_turn, build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.domain.capabilities import CombatantDefinition
from app.domain.grid import GridPosition
from test_manticore_attack_ammunition_2014 import FixedDice, _monster, _setup

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("kind", ["character", "monster"])
def test_renamed_form_spends_declared_cost_and_resets_without_source_dispatch(kind):
    try:
        # Author the same finished-combatant schema with unrelated labels and costs.
        payload = adapt_basic_monster_2014(_monster("manticore")).model_dump()
        payload.update(id="crystal-warden", name="Crystal Warden", kind=kind)
        id_map = {attack["id"]: f"crystal-attack-{index}" for index, attack in enumerate(payload["attacks"])}
        for attack in payload["attacks"]:
            attack["id"] = id_map[attack["id"]]
            attack["weapon_id"] = attack["id"]
            if attack["resource_id"] is not None:
                attack.update(name="Crystal Bolt", resource_id="crystals", resource_cost=2)
            else:
                attack["name"] = "Crystal Strike"
        payload["primary_attack_id"] = id_map[payload["primary_attack_id"]]
        payload["resources"] = [{"id": "crystals", "name": "Crystal Reserve", "max_uses": 6}]
        action = payload["attack_action"]
        action.update(id="crystal-volley", name="Crystal Volley")
        for index, variant in enumerate(action["variants"]):
            variant["id"] = f"crystal-sequence-{index}"
            for slot in variant["slots"]:
                slot["attack_ids"] = [id_map[attack_id] for attack_id in slot["attack_ids"]]

        # Validate and compile through the real form pipeline before building state.
        card = compile_combatant(CombatantDefinition.model_validate(payload))
        card_before = card.model_dump()
        actor, _, setup = _setup()
        actor.state = build_combatant_state(card)
        actor.state.position = GridPosition(x=6, y=6)
        before_preview = actor.state.model_dump()
        assert select_sequence(actor, setup)[0].attack_kind.value == "ranged"
        assert actor.state.model_dump() == before_preview
        events, _ = resolve_attack_action(1, 1, actor, setup, FixedDice(d20=2))
        attacks = [event for event in events if event.event_type == "attack"]
        assert [event.resource_remaining for event in attacks] == [4, 2, 0]
        assert all(event.attack_name == "Crystal Bolt" and not event.hit for event in attacks)
        assert select_sequence(actor, setup) is None
        assert card.model_dump() == card_before
        fresh = build_combatant_state(card)
        assert fresh.resources[0].current_uses == 6
        assert actor.state.resources[0].current_uses == 0
    except Exception:
        logger.exception("Renamed %s form failed universal attack-resource accounting.", kind)
        raise


def test_source_card_exhausts_all_spikes_then_keeps_its_melee_sequence():
    try:
        actor, target, setup = _setup()
        card = actor.state.template
        before = card.model_dump()
        shots = []
        for round_number in range(1, 9):
            begin_turn(actor.state)
            events, _ = resolve_attack_action(1, round_number, actor, setup, FixedDice(d20=2))
            attacks = [event for event in events if event.event_type == "attack"]
            assert len(attacks) == 3
            assert all(event.attack_name == "Tail Spike" and not event.hit for event in attacks)
            shots.extend(attacks)
        assert [event.resource_remaining for event in shots] == list(range(23, -1, -1))
        assert select_sequence(actor, setup) is None
        target.state.position = GridPosition(x=5, y=6)
        begin_turn(actor.state)
        events, _ = resolve_attack_action(1, 9, actor, setup, FixedDice(d20=2))
        assert [event.attack_name for event in events if event.event_type == "attack"] == ["Bite", "Claw", "Claw"]
        assert actor.state.resources[0].current_uses == 0
        assert build_combatant_state(card).resources[0].current_uses == 24
        assert card.model_dump() == before
    except Exception:
        logger.exception("Canonical Manticore failed full ammunition depletion/melee fallback/reset.")
        raise


def test_source_natural_one_spends_only_the_attempted_shot_and_does_not_refill_next_turn():
    try:
        actor, _, setup = _setup()
        events, _ = resolve_attack_action(1, 1, actor, setup, FixedDice(d20=1))
        attacks = [event for event in events if event.event_type == "attack"]
        assert len(attacks) == 1
        assert attacks[0].resource_remaining == 23
        assert actor.state.turn_terminated
        begin_turn(actor.state)
        assert actor.state.resources[0].current_uses == 23
    except Exception:
        logger.exception("Canonical Manticore failed ammunition interruption/turn lifecycle.")
        raise
