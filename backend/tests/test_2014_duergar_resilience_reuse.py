"""2014 Duergar Resilience reuses universal context-tagged saving-throw Advantage."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.opening_modifiers import opening_modifiers
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_passive_grants_2014 import (
    bound_passive_trait_names_2014, saving_throw_advantage_grants_2014,
)
from app.content.monster_resilience_save_grants_2014 import source_proven_resilience_grants_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def _source(key: str):
    try:
        return next(card for card in load_monster_source_2014() if card.id == key)
    except Exception:
        logger.exception("Could not load 2014 monster source %s", key)
        raise


def _state():
    try:
        # An unrelated creature proves behavior comes from reusable grant data,
        # not the runtime's source monster name.
        card = compile_combatant(adapt_basic_monster_2014(_source("commoner")))
        features = card.progression_features.model_copy(update={
            "saving_throw_advantage_grants": source_proven_resilience_grants_2014(
                _source("duergar")
            ),
        })
        card = card.model_copy(update={"progression_features": features})
        state = build_combatant_state(card)
        state.active_modifiers = opening_modifiers(card)
        return state
    except Exception:
        logger.exception("Could not create synthetic resilience combatant")
        raise


def test_all_327_cards_only_bind_the_printed_resilience_source():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        matched = {
            card.id for card in cards if source_proven_resilience_grants_2014(card)
        }
        assert matched == {"duergar"}
    except Exception:
        logger.exception("Full 2014 source resilience audit failed")
        raise


def test_source_grants_compile_without_new_ability_resolver():
    try:
        source = _source("duergar")
        original = source.model_dump_json()
        grants = saving_throw_advantage_grants_2014(source)
        matching = [item for item in grants if item.source_name == "Duergar Resilience"]
        assert len(matching) == 5
        assert len([item for item in matching if item.requires_spell_effect]) == 1
        assert {tuple(item.required_effect_tags) for item in matching if not item.requires_spell_effect} == {
            ("poison",), ("illusion",), ("charm",), ("paralyzed",),
        }
        assert all(len(item.abilities) == 6 for item in matching)
        assert "Duergar Resilience" in bound_passive_trait_names_2014(source)
        assert "Duergar Resilience" not in unsupported_traits_2014(source)
        assert basic_blockers_2014(source)  # Other Actions are still outstanding.
        assert source.model_dump_json() == original
    except Exception:
        logger.exception("Duergar trait grant classification failed")
        raise


def test_source_mutation_fails_closed_and_renaming_preserves_semantics():
    try:
        source = _source("duergar")
        renamed = source.model_copy(update={"id": "homebrew-other", "name": "Other"})
        assert source_proven_resilience_grants_2014(renamed) == source_proven_resilience_grants_2014(source)
        changed = source.source_traits.replace(
            "poison, spells, and illusions", "poison, roars, and illusions",
        )
        assert changed != source.source_traits
        mutated = source.model_copy(update={"source_traits": changed})
        assert source_proven_resilience_grants_2014(mutated) == []
        assert "Duergar Resilience" in unsupported_traits_2014(mutated)
    except Exception:
        logger.exception("Duergar source integrity/renaming test failed")
        raise


def test_each_qualifying_context_uses_generic_advantage():
    try:
        state = _state()
        contexts = [
            SavingThrowContext(spell_effect=True, magical_effect=True),
            SavingThrowContext(effect_tags=frozenset({"poison"})),
            SavingThrowContext(effect_tags=frozenset({"illusion"})),
            SavingThrowContext(effect_tags=frozenset({"charm"})),
            SavingThrowContext(effect_tags=frozenset({"paralyzed"})),
            SavingThrowContext(spell_effect=True, effect_tags=frozenset({"poison"})),
        ]
        for context in contexts:
            result, _ = resolve_saving_throw(
                state, "wisdom", 99, FixedDiceProvider([3, 17]), context,
            )
            assert result.mode == "advantage" and result.rolls == [3, 17]
        # Magic without a spell, and an unrelated condition, are not covered.
        for context in [
            SavingThrowContext(magical_effect=True),
            SavingThrowContext(effect_tags=frozenset({"frightened"})),
            SavingThrowContext(),
        ]:
            result, _ = resolve_saving_throw(
                state, "wisdom", 99, FixedDiceProvider([11]), context,
            )
            assert result.mode == "normal" and result.rolls == [11]
    except Exception:
        logger.exception("Universal Duergar contextual save parity failed")
        raise
