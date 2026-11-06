"""Universal conditional Multiattack slot browser serialization regression."""
from __future__ import annotations

import logging
from types import SimpleNamespace as NS

from scripts.browser_attack_action_slots import attack_slot_row

logger = logging.getLogger(__name__)


def test_held_target_slot_is_source_gated_after_browser_serialization():
    try:
        held = NS(
            attack_ids=[], save_action_ids=["renamed-save"],
            requires_source_grapple=True, previous_attack=None,
        )
        normal = NS(
            attack_ids=["renamed-pincer"], save_action_ids=[],
            requires_source_grapple=False, previous_attack=None,
        )
        assert attack_slot_row(held) == {
            "attackIds": [], "saveActionIds": ["renamed-save"],
            "requiresSourceGrapple": True,
        }
        assert attack_slot_row(normal) == {
            "attackIds": ["renamed-pincer"], "saveActionIds": [],
        }
    except Exception:
        logger.exception("Generic grapple-conditional Multiattack slot lost a source gate")
        raise
