"""Immutable body-control source proof; no fake Ghost Possession runtime."""
from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_body_control_2014 import source_proven_body_control_2014

logger = logging.getLogger(__name__)


def _ghost():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        return next(card for card in cards if card.id == "ghost")
    except Exception:
        logger.exception("Failed to load pinned 2014 Ghost")
        raise


def test_complete_source_contract_is_typed_and_does_not_admit_ghost():
    try:
        card = _ghost()
        original = card.model_dump_json()
        (definition,) = source_proven_body_control_2014(card)
        assert definition.source_action_id == "possession"
        assert (definition.range_ft, definition.save_dc) == (5, 13)
        assert definition.required_creature_type == "humanoid"
        assert definition.save_ability == "charisma"
        assert definition.recharge_minimum == 6
        assert definition.release_bonus_action
        assert definition.ends_on_host_zero_hp
        assert definition.owner_untargetable_except_turning
        assert definition.host_uses_own_statistics
        assert definition.owner_retains_mental_scores
        assert definition.post_end_immunity_hours == 24
        assert "mechanic:recharge" in basic_blockers_2014(card)
        assert "source:extra-action" in basic_blockers_2014(card)
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("Body-control source contract test failed")
        raise


def test_new_control_riders_fail_closed_and_identity_is_not_the_dispatch_key():
    try:
        card = _ghost()
        for old, new in (
            ("One humanoid", "One beast"),
            ("within 5 feet", "within 30 feet"),
            ("the target is incapacitated", "the target is stunned"),
            ("can't be targeted by any attack", "can be targeted by any attack"),
            ("ends it as a bonus action", "ends it as an action"),
            ("body drops to 0 hit points", "body drops to 1 hit point"),
            ("immunity to being charmed and frightened", "immunity to being poisoned"),
            ("for 24 hours after", "for 48 hours after"),
        ):
            assert old in card.source_actions
            edited = card.model_copy(update={
                "source_actions": card.source_actions.replace(old, new),
            })
            assert source_proven_body_control_2014(edited) == []
        # Numeric source parameters are data, not a name-locked resolver.
        changed_dc = card.model_copy(update={
            "source_actions": card.source_actions.replace(
                "DC 13 Charisma", "DC 17 Charisma",
            ),
        })
        (scaled,) = source_proven_body_control_2014(changed_dc)
        assert scaled.save_dc == 17
        renamed = card.model_copy(update={"id": "unrelated-controller", "name": "Other"})
        assert len(source_proven_body_control_2014(renamed)) == 1
    except Exception:
        logger.exception("Body-control source mutations failed")
        raise
