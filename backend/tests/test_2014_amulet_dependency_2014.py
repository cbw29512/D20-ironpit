"""Pinned 2014 amulet-only source clauses are inert with no external wearer."""
from __future__ import annotations

import logging

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_arena_unavailable_reactions_2014 import arena_unavailable_reaction_names_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "shield-guardian")
    except Exception:
        logger.exception("Pinned 2014 amulet-dependent monster unavailable")
        raise


def test_full_327_card_source_proof_and_complete_combat_admission():
    try:
        roster = load_monster_source_2014()
        assert len(roster) == 327
        affected = [
            (card.id, trait)
            for card in roster for trait in card.trait_names
            if verified_arena_inert_trait_2014(card, trait)
            and trait in {"Bound", "Spell Storing"}
        ]
        reactions = [
            (card.id, name)
            for card in roster
            for name in arena_unavailable_reaction_names_2014(card)
            if name == "Shield"
        ]
        assert affected == [
            ("shield-guardian", "Bound"), ("shield-guardian", "Spell Storing"),
        ]
        assert reactions == [("shield-guardian", "Shield")]
        card = _source()
        snapshot = card.model_dump_json()
        assert unsupported_traits_2014(card) == ()
        assert basic_blockers_2014(card) == ()
        template = compile_combatant(adapt_basic_monster_2014(card))
        assert template.name == card.name
        assert template.max_hp == card.max_hp
        assert template.armor_class == card.armor_class
        assert template.regeneration is not None
        assert template.weapon_attack is not None
        assert card.model_dump_json() == snapshot
    except Exception:
        logger.exception("Full 327-card amulet dependency proof failed")
        raise


@pytest.mark.parametrize("trait,old,new", [
    ("Bound", "half of any damage the wearer takes", "all damage the wearer takes"),
    ("Bound", "within 60 feet", "within 120 feet"),
    ("Spell Storing", "4th level or lower", "5th level or lower"),
    ("Spell Storing", "any previously stored spell is lost", "previously stored spell remains"),
])
def test_complete_mutated_trait_fails_closed(trait, old, new):
    try:
        card = _source()
        assert old in card.source_traits
        modified = card.model_copy(update={
            "source_traits": card.source_traits.replace(old, new),
        })
        assert not verified_arena_inert_trait_2014(modified, trait)
        assert trait in unsupported_traits_2014(modified)
        assert "source:trait" in basic_blockers_2014(modified)
    except Exception:
        logger.exception("Changed amulet-only source trait failed closed check")
        raise


def test_modified_reaction_and_unheaded_continuations_fail_closed():
    try:
        card = _source()
        changed = card.model_copy(update={
            "source_reactions": card.source_reactions.replace(
                "+2 bonus to the wearer's AC",
                "+4 bonus to the wearer's AC",
            ),
        })
        assert "Shield" not in arena_unavailable_reaction_names_2014(changed)
        assert "source:reaction" in basic_blockers_2014(changed)
        hidden = card.model_copy(update={
            "source_traits": card.source_traits + (
                "<p>It also deals 1d6 acid damage to nearby enemies.</p>"
            ),
        })
        assert not verified_arena_inert_trait_2014(hidden, "Spell Storing")
        assert "source:trait" in basic_blockers_2014(hidden)
        extra = card.model_copy(update={
            "source_reactions": card.source_reactions + (
                "<p>It also reflects the attack at its attacker.</p>"
            ),
        })
        assert "Shield" not in arena_unavailable_reaction_names_2014(extra)
    except Exception:
        logger.exception("Unexpected amulet source continuation was accepted")
        raise


def test_renaming_source_card_does_not_change_semantic_classifier():
    try:
        card = _source()
        renamed = card.model_copy(update={
            "id": "renamed-guardian-form", "name": "Unrelated Guardian Form",
        })
        assert verified_arena_inert_trait_2014(renamed, "Bound")
        assert verified_arena_inert_trait_2014(renamed, "Spell Storing")
        assert "Shield" in arena_unavailable_reaction_names_2014(renamed)
        assert basic_blockers_2014(renamed) == ()
    except Exception:
        logger.exception("Amulet proof must not dispatch by creature identity")
        raise
