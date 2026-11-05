"""Source-only classification of 2014 Mimic False Appearance as arena-neutral."""

from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def test_mimic_false_appearance_is_arena_neutral():
    try:
        monsters = load_monster_source_2014()
        mimic = next(m for m in monsters if m.id == "mimic")
        assert verified_arena_inert_trait_2014(mimic, "False Appearance (Object Form Only)")
    except Exception:
        logger.exception("Mimic False Appearance positive proof failed.")
        raise


def test_mimic_false_appearance_mutation_fails_closed():
    try:
        monsters = load_monster_source_2014()
        mimic = next(m for m in monsters if m.id == "mimic")
        original = mimic.source_traits
        # Mutate a required token
        mimic.source_traits = original.replace("motionless", "moving")
        assert not verified_arena_inert_trait_2014(mimic, "False Appearance (Object Form Only)")
        mimic.source_traits = original  # restore
    except Exception:
        logger.exception("Mimic False Appearance mutation fail-closed failed.")
        raise
