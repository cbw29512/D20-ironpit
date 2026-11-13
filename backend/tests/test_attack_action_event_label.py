"""Extra Attack labels belong to actual additional Attack Action slots."""
from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from app.combat.attack_action_rules import attack_action_event_feature_id

logger = logging.getLogger(__name__)


def test_extra_attack_labels_follow_source_neutral_slots():
    try:
        action = SimpleNamespace(is_attack_action=True)
        variant = SimpleNamespace(id="attack")
        assert attack_action_event_feature_id(action, variant, 1) == "attack"
        assert attack_action_event_feature_id(action, variant, 2) == "extra-attack"
        assert attack_action_event_feature_id(action, variant, 3) == "extra-attack"
        multi = SimpleNamespace(is_attack_action=False)
        original = SimpleNamespace(id="printed-sequence")
        assert attack_action_event_feature_id(multi, original, 1) == "printed-sequence"
        assert attack_action_event_feature_id(multi, original, 3) == "printed-sequence"
    except Exception:
        logger.exception("Generic Attack Action log labeling regression failed.")
        raise


def test_attack_slot_index_must_be_valid():
    with pytest.raises(ValueError):
        attack_action_event_feature_id(SimpleNamespace(is_attack_action=True),
                                       SimpleNamespace(id="attack"), 0)
