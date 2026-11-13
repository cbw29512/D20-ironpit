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
