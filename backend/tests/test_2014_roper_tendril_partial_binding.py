"""Roper Tendril partial binding: reuse hit/Grapple, preserve unmet riders."""
from __future__ import annotations

import logging

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_damage_free_grapple_2014 import (
    source_proven_damage_free_grapple_attacks_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _source():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        return next(card for card in cards if card.id == "roper")
    except Exception:
        logger.exception("Could not load pinned 2014 Roper card")
        raise


def test_tendril_uses_existing_zero_damage_attack_and_grapple_schema():
    try:
        card = _source()
        original = card.model_dump_json()
        (attack,) = source_proven_damage_free_grapple_attacks_2014(card)
        assert attack.name == "Tendril"
        assert attack.attack_kind == "melee"
        assert attack.attack_bonus == 7 and attack.reach_ft == 50
        assert attack.fixed_damage == 0
        (effect,) = attack.effects
        assert effect.kind == "grapple"
        assert effect.escape_dc == 15
        assert effect.restrains is True
        assert effect.max_active_grapples == 6
        assert card.model_dump_json() == original
        # Printed Strength debuff, individual tendril destruction,
        # regrowth, and complete Multiattack are not certified by this slice.
        assert "source:extra-action" in basic_blockers_2014(card)
        assert "source:trait" in basic_blockers_2014(card)
    except Exception:
        logger.exception("Roper partial Tendril compile failed")
        raise


@pytest.mark.parametrize("before,after", [
    ("+7 to hit", "+8 to hit"),
    ("reach 50 ft.", "reach 60 ft."),
    ("escape DC 15", "escape DC 16"),
    ("disadvantage on Strength checks", "advantage on Strength checks"),
    ("one creature.", "two creatures."),
    ("on another target.", "on another target. It deals 4 poison damage."),
])
def test_tendril_action_mutations_fail_closed(before, after):
    try:
        card = _source()
        assert before in card.source_actions
        changed = card.model_copy(update={
            "source_actions": card.source_actions.replace(before, after),
        })
        assert not source_proven_damage_free_grapple_attacks_2014(changed)
    except Exception:
        logger.exception("Roper Tendril action mutation failed: %s", before)
        raise


@pytest.mark.parametrize("before,after", [
    ("six tendrils", "eight tendrils"),
    ("AC 20", "AC 21"),
    ("10 hit points", "11 hit points"),
    ("immunity to poison and psychic damage", "immunity to fire damage"),
    ("next turn", "same turn"),
    ("DC 15 Strength check", "DC 13 Strength check"),
])
def test_tendril_trait_mutations_fail_closed(before, after):
    try:
        card = _source()
        assert before in card.source_traits
        changed = card.model_copy(update={
            "source_traits": card.source_traits.replace(before, after),
        })
        assert not source_proven_damage_free_grapple_attacks_2014(changed)
    except Exception:
        logger.exception("Roper trait mutation failed: %s", before)
        raise


def test_tendril_compiles_on_renamed_source_identity():
    try:
        card = _source()
        renamed = card.model_copy(update={"id": "alternate-grappler", "name": "Other"})
        (attack,) = source_proven_damage_free_grapple_attacks_2014(renamed)
        assert attack.name == "Tendril"
        assert attack.id.startswith("2014-alternate-grappler-")
    except Exception:
        logger.exception("Roper Tendril renamed-card test failed")
        raise


def test_tendril_reaches_actual_shared_combatant_compiler():
    try:
        card = _source()
        definition = adapt_monster_mechanics_2014(card)
        attack = next(row for row in definition.attacks if row.name == "Tendril")
        assert attack.fixed_damage == 0
        assert attack.reach_ft == 50 and attack.attack_bonus == 7
        template = compile_combatant(definition)
        compiled = [template.weapon_attack, *template.alternate_weapon_attacks]
        assert any(row.id == "2014-roper-tendril" for row in compiled)
        assert "source:extra-action" in basic_blockers_2014(card)
    except Exception:
        logger.exception("Tendril did not reach universal combatant template")
        raise
