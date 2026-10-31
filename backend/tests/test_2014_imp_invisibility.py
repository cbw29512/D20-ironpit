"""2014 immutable source family: Imp and Sprite Invisible expiry variants."""
from __future__ import annotations

import logging
import pytest

from app.combat.owner_action_expiry import expire_on_owner_event
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def cards():
    try:
        result = load_monster_source_2014()
        assert len(result) == 327
        return {card.id: card for card in result}
    except Exception:
        logger.exception("Failed loading immutable 2014 invisibility source corpus.")
        raise


def test_full_327_card_source_audit_is_parameter_driven(cards):
    try:
        matches = {
            card.id: source_invisibility_action_2014(card)
            for card in cards.values()
            if source_invisibility_action_2014(card)
        }
        assert set(matches) == {"sprite", "imp"}
        sprite, imp = matches["sprite"][0], matches["imp"][0]
        assert sprite.ends_on_owner_attack and sprite.ends_on_owner_spell_cast
        assert imp.ends_on_owner_attack and not imp.ends_on_owner_spell_cast
        for action in (sprite, imp):
            assert action.condition_ids == ["invisible"]
            assert action.concentration and action.magical_effect
            assert action.action_cost == "action"
            assert action.resource_id is None and action.duration_rounds is None
        # Quasit uses Scare and Will-o'-Wisp uses Consume Life: distinct exits
        # not represented by an arbitrary spell-cast event. Never weaken them.
        assert not source_invisibility_action_2014(cards["quasit"])
        assert not source_invisibility_action_2014(cards["will-o-wisp"])
    except Exception:
        logger.exception("2014 invisibility source scan failed.")
        raise


def test_imp_real_compiled_buff_survives_spell_cast_but_ends_on_attack(cards):
    try:
        source = cards["imp"]
        definition = adapt_monster_mechanics_2014(source)
        compiled = compile_combatant(definition)
        action = next(a for a in compiled.timed_self_buff_actions if a.id == "invisibility")
        assert action.ends_on_owner_attack and not action.ends_on_owner_spell_cast
        state = build_combatant_state(compiled)
        member = EncounterCombatant(
            combatant_id="source", side="monsters", position_ft=0, state=state,
        )
        resolve_timed_self_buff(1, 0, member, action, spend_action_cost=False)
        assert state.concentration.effect_id == "invisibility"
        assert "invisible" in state.active_effect_ids
        assert expire_on_owner_event(state, "spell_cast", [state]) == []
        assert state.concentration is not None
        assert expire_on_owner_event(state, "attack", [state]) == ["invisible"]
        assert state.concentration is None
        assert "invisible" not in state.active_effect_ids
    except Exception:
        logger.exception("Compiled Imp Invisibility combat expiry regression failed.")
        raise


def test_source_mutation_and_renaming_fail_closed(cards):
    try:
        for monster_id in ("sprite", "imp"):
            original = cards[monster_id]
            previous = original.model_dump_json()
            altered = original.model_copy(update={"source_actions":
                original.source_actions.replace(
                    "or until its concentration ends",
                    "or until any ally falls unconscious",
                ),
            })
            assert source_invisibility_action_2014(altered) == []
            named = original.model_copy(update={"id": "renamed-homebrew", "name": "New Source"})
            assert source_invisibility_action_2014(named)
            assert original.model_dump_json() == previous
    except Exception:
        logger.exception("2014 invisibility strict source proof failed.")
        raise
