"""Initiative-order spell interrupt dispatch must never double-spend a Reaction."""
from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

import app.combat.spell_interrupt_priority as priority
from app.domain.spell_interrupt_reactions import SpellInterruptReaction

logger = logging.getLogger(__name__)


def scenario():
    try:
        def member(id, side):
            return SimpleNamespace(
                combatant_id=id, side=side,
                state=SimpleNamespace(reaction_available=True, slots=1),
            )
        high, low, caster = (
            member("high", "heroes"), member("low", "heroes"),
            member("caster", "monsters"),
        )
        action = SpellInterruptReaction(
            id="counterspell", name="Counterspell", printed_level=3,
            range_ft=60, casting_ability="intelligence",
        )
        return high, low, caster, SimpleNamespace(
            heroes=[high, low], monsters=[caster],
        ), {"high": [action], "low": [action]}
    except Exception:
        logger.exception("Failed to initialize generic reaction priority scenario")
        raise


def patch_reactions(monkeypatch, outcomes):
    try:
        calls = []

        def legal(actor, caster, action, spell_level, *, is_spell_cast):
            return actor.side != caster.side and actor.state.reaction_available

        def resolve(sequence, round_number, actor, caster, setup, action,
                    spell_name, spell_level, dice, *, is_spell_cast):
            calls.append(actor.combatant_id)
            assert actor.state.slots == 1
            actor.state.reaction_available = False
            actor.state.slots -= 1
            return SimpleNamespace(actor_id=actor.combatant_id), outcomes[actor.combatant_id]

        monkeypatch.setattr(priority, "interrupt_legal", legal)
        monkeypatch.setattr(priority, "resolve_spell_interrupt", resolve)
        return calls
    except Exception:
        logger.exception("Failed to patch isolated initiative Reaction fixture")
        raise


def test_failed_higher_priority_reaction_allows_next_actor(monkeypatch):
    try:
        high, low, caster, setup, actions = scenario()
        calls = patch_reactions(monkeypatch, {"high": False, "low": True})
        events, stopped, next_seq = priority.dispatch_spell_interrupts(
            7, 2, caster, setup, ["high", "caster", "low"],
            actions, "Fireball", 3, object(), is_spell_cast=True,
        )
        assert stopped and next_seq == 9
        assert [event.actor_id for event in events] == ["high", "low"]
        assert calls == ["high", "low"]
        assert (high.state.slots, low.state.slots) == (0, 0)
    except Exception:
        logger.exception("Failed Counterspell check did not advance initiative priority")
        raise


def test_first_success_stops_later_reactors(monkeypatch):
    try:
        high, low, caster, setup, actions = scenario()
        calls = patch_reactions(monkeypatch, {"high": True, "low": True})
        events, stopped, next_seq = priority.dispatch_spell_interrupts(
            7, 2, caster, setup, ["high", "low", "caster"],
            actions, "Blight", 4, object(), is_spell_cast=True,
        )
        assert stopped and next_seq == 8 and calls == ["high"]
        assert len(events) == 1 and low.state.slots == 1
        assert low.state.reaction_available
    except Exception:
        logger.exception("Successful interrupt incorrectly spent another Reaction")
        raise


@pytest.mark.parametrize("order", [
    ["high", "caster"],
    ["high", "high", "caster"],
    ["high", "low", "unknown"],
])
def test_invalid_initiative_order_fails_before_any_mutation(monkeypatch, order):
    try:
        high, low, caster, setup, actions = scenario()
        calls = patch_reactions(monkeypatch, {"high": True, "low": True})
        with pytest.raises(ValueError):
            priority.dispatch_spell_interrupts(
                7, 2, caster, setup, order, actions, "Blight", 4, object(),
                is_spell_cast=True,
            )
        assert not calls
        assert (high.state.slots, low.state.slots) == (1, 1)
    except Exception:
        logger.exception("Invalid initiative order did not fail closed")
        raise


def test_nonspell_ability_never_triggers_a_reaction(monkeypatch):
    try:
        high, low, caster, setup, actions = scenario()
        calls = patch_reactions(monkeypatch, {"high": True, "low": True})
        events, stopped, next_seq = priority.dispatch_spell_interrupts(
            7, 2, caster, setup, ["high", "low", "caster"],
            actions, "Fire Breath", 0, object(), is_spell_cast=False,
        )
        assert not events and not stopped and next_seq == 7
        assert not calls and high.state.slots == 1 and low.state.slots == 1
    except Exception:
        logger.exception("Nonspell ability improperly triggered Counterspell")
        raise
