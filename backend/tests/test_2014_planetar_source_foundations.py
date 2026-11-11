"""2014 printed-source tests for shared healing and strict wall/utility proofs.

Partial bindings must not pretend a missing damaging spell is certified.
"""
from __future__ import annotations

import logging

import pytest

from app.content.arena_wall_spell_policy import is_arena_unavailable_wall_effect
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_healing_2014 import (
    healing_actions_2014, healing_resources_2014, supports_healing_2014,
)
from app.content.monster_innate_support_2014 import supports_innate_spellcasting_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_angelic_innate_2014 import (
    source_proven_angelic_arena_exclusions_2014,
)
from app.content.monster_source_healing_touch_2014 import (
    source_proven_missing_healing_touch_2014,
)

logger = logging.getLogger(__name__)


def _planetar():
    try:
        rows = load_monster_source_2014()
        assert len(rows) == 327
        return next(row for row in rows if row.id == "planetar")
    except Exception:
        logger.exception("Could not inspect Planetar printed source.")
        raise


def test_unparsed_healing_touch_reuses_shared_healing_schema():
    try:
        card = _planetar()
        before = card.model_dump_json()
        assert not card.healing_actions and not card.limited_action_uses
        proof = source_proven_missing_healing_touch_2014(card)
        assert proof is not None
        action, uses = proof
        assert (action.name, action.dice_count, action.dice_size,
                action.healing_bonus, uses) == ("Healing Touch", 6, 8, 3, 4)
        assert action.target_mode == "other" and action.range_ft == 5
        assert action.removable_conditions == ["poisoned", "blinded", "deafened"]
        assert healing_actions_2014(card) == [action]
        assert [(x.id, x.max_uses) for x in healing_resources_2014(card)] == [
            ("healing-touch", 4),
        ]
        assert supports_healing_2014(card)
        assert "source:extra-action" not in basic_blockers_2014(card)
        assert card.model_dump_json() == before
        renamed = card.model_copy(update={"id": "anonymous-celestial", "name": "Other"})
        assert source_proven_missing_healing_touch_2014(renamed) == proof
    except Exception:
        logger.exception("Planetar shared healing/action resource proof failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("4/Day", "5/Day"),
    ("6d8 + 3", "8d8 + 3"),
    ("30 (6d8 + 3)", "50 (6d8 + 3)"),
    ("touches another creature", "touches any creature"),
    ("poison, blindness, or deafness", "poison or deafness"),
])
def test_healing_text_mutation_fails_closed(old, new):
    try:
        card = _planetar()
        assert old in card.source_actions
        modified = card.model_copy(update={
            "source_actions": card.source_actions.replace(old, new),
        })
        assert source_proven_missing_healing_touch_2014(modified) is None
        assert "source:extra-action" in basic_blockers_2014(modified)
    except Exception:
        logger.exception("Planetar healing-source mutation failed: %s", old)
        raise


def test_blade_wall_exclusion_requires_full_innate_clause():
    try:
        card = _planetar()
        before = card.model_dump_json()
        assert source_proven_angelic_arena_exclusions_2014(card) == {
            "blade-barrier", "control-weather",
        }
        assert is_arena_unavailable_wall_effect("blade-barrier")
        assert not is_arena_unavailable_wall_effect("flame-strike")
        assert not is_arena_unavailable_wall_effect("insect-plague")
        renamed = card.model_copy(update={"id": "unnamed-caster", "name": "Other"})
        assert source_proven_angelic_arena_exclusions_2014(renamed) == {
            "blade-barrier", "control-weather",
        }
        # Insect Plague now composes the existing placed-save and temporary-
        # terrain primitives; no Planetar-named runtime effect is introduced.
        assert supports_innate_spellcasting_2014(card)
        assert basic_blockers_2014(card) == ()
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("Planetar source wall/utility exclusion test failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("spell save DC 20", "spell save DC 21"),
    ("blade barrier", "fireball"),
    ("control weather", "control water"),
    ("insect plague", "wall of fire"),
])
def test_innate_printed_mutations_do_not_prove_exclusions(old, new):
    try:
        card = _planetar()
        assert old in card.source_traits
        modified = card.model_copy(update={
            "source_traits": card.source_traits.replace(old, new),
        })
        assert not source_proven_angelic_arena_exclusions_2014(modified)
    except Exception:
        logger.exception("Planetar innate spell printed mutation failed: %s", old)
        raise
