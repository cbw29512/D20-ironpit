"""Strict 2014 Light Sensitivity source proof over all 327 immutable cards."""
from __future__ import annotations

import logging
import pytest

from app.content.environment_context_reactions import (
    light_sensitivity_2014, verified_light_sensitivity_2014,
)
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_environment_context_bindings_2014 import environment_context_reactions_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import bound_trait_names_2014

logger = logging.getLogger(__name__)


def test_all_327_2014_source_cards_have_exact_one_supported_trait():
    try:
        monsters = load_monster_source_2014()
        assert len(monsters) == 327
        applicable = [card for card in monsters if verified_light_sensitivity_2014(card)]
        assert [card.id for card in applicable] == ["cloaker"]
        card = applicable[0]
        assert environment_context_reactions_2014(card) == [light_sensitivity_2014()]
        assert "Light Sensitivity" in bound_trait_names_2014(card)
        assert "Light Sensitivity" not in unsupported_traits_2014(card)
        assert "Damage Transfer" in unsupported_traits_2014(card)
        renamed = card.model_copy(update={"id": "renamed-bat", "name": "Renamed Bat"})
        assert verified_light_sensitivity_2014(renamed)
    except Exception:
        logger.exception("327-card Light Sensitivity source proof failed.")
        raise


@pytest.mark.parametrize("before,after", [
    ("bright light", "dim light"),
    ("attack rolls", "ability checks"),
    ("Wisdom (Perception)", "Intelligence (Investigation)"),
])
def test_printed_combat_source_mutation_fails_closed(before, after):
    try:
        card = next(m for m in load_monster_source_2014() if m.id == "cloaker")
        assert before in card.source_traits
        edited = card.model_copy(update={
            "source_traits": card.source_traits.replace(before, after),
        })
        assert not verified_light_sensitivity_2014(edited)
        assert "Light Sensitivity" in unsupported_traits_2014(edited)
    except Exception:
        logger.exception("Light Sensitivity mutation was not rejected.")
        raise


def test_unheaded_extra_combat_clause_fails_closed():
    try:
        card = next(m for m in load_monster_source_2014() if m.id == "cloaker")
        changed = card.model_copy(update={"source_traits": card.source_traits +
            "<p>In bright light the creature also becomes stunned.</p>"})
        assert not verified_light_sensitivity_2014(changed)
    except Exception:
        logger.exception("Unheaded extra combat clause was not rejected.")
        raise
