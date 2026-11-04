"""Source-only proof that 2014 Telepathic Bond cannot change a Pit combat outcome."""
from __future__ import annotations

import logging
import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _monsters():
    try:
        return [m for m in load_monster_source_2014() if "Telepathic Bond" in (m.trait_names or [])]
    except Exception:
        logger.exception("Failed to load Telepathic Bond monsters")
        raise


def test_telepathic_bond_is_arena_inert() -> None:
    try:
        for monster in _monsters():
            before = monster.model_dump_json()
            assert verified_arena_inert_trait_2014(monster, "Telepathic Bond")
            assert "Telepathic Bond" not in unsupported_traits_2014(monster)
            assert monster.model_dump_json() == before
    except Exception:
        logger.exception("Telepathic Bond inert proof failed")
        raise


@pytest.mark.parametrize("monster_id,old,new", [
    ("homunculus", "communicate telepathically", "communicate by speech"),
    ("succubus-incubus", "its telepathy", "its speech"),
])
def test_telepathic_bond_mutation_fails_closed(monster_id, old, new) -> None:
    try:
        monster = next(m for m in load_monster_source_2014() if m.id == monster_id)
        original = monster.source_traits
        monster.source_traits = original.replace(old, new)
        assert not verified_arena_inert_trait_2014(monster, "Telepathic Bond")
        monster.source_traits = original
    except Exception:
        logger.exception("Telepathic Bond mutation fail-closed failed")
        raise
