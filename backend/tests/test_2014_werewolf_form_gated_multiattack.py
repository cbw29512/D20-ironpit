"""Werewolf form-gated Multiattack is the existing multiattack under inert Shapechanger.

Exact printed clause match. Mutation of Shapechanger or Multiattack text fails closed.
No combat name dispatch.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_lycanthrope_form_multiattack_2014 import (
    verified_lycanthrope_form_gated_multiattack_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_supported_extra_actions_2014 import source_supported_extra_action_labels_2014

logger = logging.getLogger(__name__)


def _werewolf():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "werewolf")
    except Exception:
        logger.exception("Pinned Werewolf source unavailable")
        raise


def test_werewolf_form_gated_multiattack_is_source_verified():
    try:
        monster = _werewolf()
        original = monster.model_dump_json()
        name = "Multiattack. (Humanoid or Hybrid Form Only)"
        assert verified_lycanthrope_form_gated_multiattack_2014(monster, name)
        assert "multiattack. (humanoid or hybrid form only)" in source_supported_extra_action_labels_2014(monster)
        assert "source:extra-action" not in basic_blockers_2014(monster)
        assert monster.model_dump_json() == original
    except Exception:
        logger.exception("Werewolf form-gated Multiattack proof failed")
        raise


def test_mutated_werewolf_multiattack_fails_closed():
    try:
        monster = _werewolf()
        name = "Multiattack. (Humanoid or Hybrid Form Only)"
        altered = monster.model_copy(update={
            "source_actions": monster.source_actions.replace(
                "one with its bite and one with its claws or spear",
                "three attacks with its bite",
            ),
        })
        assert not verified_lycanthrope_form_gated_multiattack_2014(altered, name)
        assert "source:extra-action" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Werewolf Multiattack mutation must fail closed")
        raise


def test_mutated_shapechanger_fails_multiattack_proof():
    try:
        monster = _werewolf()
        name = "Multiattack. (Humanoid or Hybrid Form Only)"
        altered = monster.model_copy(update={
            "source_traits": monster.source_traits.replace(
                "Its statistics, other than its AC, are the same in each form",
                "Its statistics and damage change in each form",
            ),
        })
        assert not verified_lycanthrope_form_gated_multiattack_2014(altered, name)
        assert "source:extra-action" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Werewolf Shapechanger mutation must fail Multiattack proof")
        raise


def test_unrelated_multiattack_does_not_inherit():
    try:
        monster = next(row for row in load_monster_source_2014() if row.id == "werebear")
        for name in monster.action_names:
            assert not verified_lycanthrope_form_gated_multiattack_2014(monster, name)
    except Exception:
        logger.exception("Werebear isolation failed")
        raise
