"""Universal source-owned named-action expiry regression."""
from __future__ import annotations

import logging

import pytest

from app.combat.owner_action_expiry import expire_on_owner_event
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def test_named_action_expiry_requires_action_id():
    try:
        # Invalid action-event requests must fail before dereferencing state.
        with pytest.raises(ValueError, match="action ID"):
            expire_on_owner_event(None, "action")
    except Exception:
        logger.exception("Named-action event validation regressed")
        raise


def test_declared_action_ids_are_normalized_and_serializable():
    try:
        effect = TimedEffect(
            effect_id="invisible", source_id="source",
            source_effect_id="invisibility",
            ends_on_owner_attack=True,
            ends_on_owner_action_ids=["scare"],
        )
        assert effect.ends_on_owner_action_ids == ["scare"]
        assert effect.model_dump()["ends_on_owner_action_ids"] == ["scare"]
        assert not effect.ends_on_owner_spell_cast
    except Exception:
        logger.exception("Named-action timed-effect schema regression")
        raise
