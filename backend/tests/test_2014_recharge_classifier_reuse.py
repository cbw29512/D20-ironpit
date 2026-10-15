"""Classifier reuse tests: one decision per monster, unchanged source semantics."""
from __future__ import annotations

from unittest.mock import patch

from app.content import monster_basic_candidates_2014 as candidates
from app.content import monster_save_capabilities_2014 as saves
from app.content.monster_source_2014 import load_monster_source_2014


def _recharging_monster():
    # Select a real source card, not a synthetic card with missing source fields.
    return next(monster for monster in load_monster_source_2014()
                if monster.action_recharges and monster.id not in {"stirge", "frog"})


def test_blocker_classification_reuses_one_recharge_decision():
    monster = _recharging_monster()
    original = candidates.supports_recharge_rules_2014
    before = candidates.basic_blockers_2014(monster)
    seen = []

    def counted(source):
        try:
            seen.append(source.id)
            return original(source)
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Recharge classifier spy failed")
            raise

    with patch.object(candidates, "supports_recharge_rules_2014", counted):
        after = candidates.basic_blockers_2014(monster)

    assert after == before
    assert seen == [monster.id]


def test_direct_source_action_callers_retain_recharge_fallback():
    monster = _recharging_monster()
    supported = saves.supports_recharge_rules_2014(monster)
    expected = saves.unsupported_source_actions_2014(monster)

    # Supplying the certified value must skip recomputation.
    with patch.object(saves, "supports_recharge_rules_2014",
                      side_effect=AssertionError("Recharge was recomputed")):
        actual = saves.unsupported_source_actions_2014(
            monster, recharge_supported=supported,
        )
    assert actual == expected


def test_explicit_false_recharge_proof_keeps_breath_weapon_blocked():
    monster = _recharging_monster()
    expected = saves.unsupported_source_actions_2014(
        monster, recharge_supported=False,
    )
    with patch.object(saves, "supports_recharge_rules_2014",
                      side_effect=AssertionError("Unexpected recharge check")):
        unsupported = saves.unsupported_source_actions_2014(
            monster, recharge_supported=False,
        )
    assert unsupported == expected
