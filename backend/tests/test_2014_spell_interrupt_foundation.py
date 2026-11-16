"""2014 visible spell-interrupt reaction: slot, check and legality tests."""
from __future__ import annotations

import logging

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.spell_interrupt_reactions import (
    interrupt_legal, interrupt_slot, resolve_spell_interrupt,
)
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.runtime import ResourceState
from app.domain.spell_interrupt_reactions import SpellInterruptReaction

logger = logging.getLogger(__name__)


def fixture(slots=(3,)):
    try:
        caster = EncounterCombatant(
            combatant_id="interrupter", side="heroes", position_ft=0,
            state=build_combatant_state(build_aurelia_brightshield_2014(9)),
        )
        target = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=30,
            state=build_combatant_state(
                build_commoner().model_copy(update={"ruleset": "2014"}),
            ),
        )
        for level in (3, 4, 5):
            item = next(
                (x for x in caster.state.resources if x.id == f"spell-slot-{level}"), None,
            )
            if item is not None:
                item.current_uses = int(level in slots)
            elif level in slots:
                caster.state.resources.append(ResourceState(
                    id=f"spell-slot-{level}", name=f"Slot {level}", current_uses=1, max_uses=1,
                ))
        action = SpellInterruptReaction(
            id="counterspell", name="Counterspell", printed_level=3,
            range_ft=60, casting_ability="charisma",
        )
        setup = EncounterSetup(
            heroes=[caster], monsters=[target], hero_total_levels=9,
            monster_total_cr="0", ruleset="2014",
        )
        return caster, target, setup, action
    except Exception:
        logger.exception("Failed to build Counterspell foundation fixture")
        raise


def test_upcast_auto_interrupt_spends_one_slot_and_reaction():
    try:
        caster, target, setup, action = fixture((3, 4))
        assert interrupt_slot(caster, action, 4) == 4
        event, stopped = resolve_spell_interrupt(
            1, 1, caster, target, setup, action, "Fireball", 4,
            FixedDiceProvider([1]), is_spell_cast=True,
        )
        assert stopped and event.ability_check_roll is None
        assert not caster.state.reaction_available
        assert next(r.current_uses for r in caster.state.resources if r.id == "spell-slot-3") == 1
        assert next(r.current_uses for r in caster.state.resources if r.id == "spell-slot-4") == 0
        assert "Counterspell" in event.description
    except Exception:
        logger.exception("Automatic higher-slot interrupt failed")
        raise


@pytest.mark.parametrize("die,expected", [(1, False), (20, True)])
def test_low_slot_checks_dc_14_and_spends_even_on_failure(die, expected):
    try:
        caster, target, setup, action = fixture((3,))
        event, stopped = resolve_spell_interrupt(
            1, 1, caster, target, setup, action, "Blight", 4,
            FixedDiceProvider([die]), is_spell_cast=True,
        )
        assert stopped == expected
        assert event.check_dc == 14 and event.check_succeeded == expected
        assert next(r.current_uses for r in caster.state.resources if r.id == "spell-slot-3") == 0
        assert not caster.state.reaction_available
    except Exception:
        logger.exception("Higher spell reaction check failed at roll %s", die)
        raise


@pytest.mark.parametrize("reason", ["nonspell", "friendly", "range", "reaction", "slot"])
def test_invalid_interrupt_never_spends_resources(reason):
    try:
        caster, target, setup, action = fixture((3,))
        is_spell = True
        if reason == "nonspell":
            is_spell = False
        elif reason == "friendly":
            target.side = "heroes"
        elif reason == "range":
            target.position_ft = 65
        elif reason == "reaction":
            caster.state.reaction_available = False
        elif reason == "slot":
            next(r for r in caster.state.resources if r.id == "spell-slot-3").current_uses = 0
        assert not interrupt_legal(caster, target, action, 3, is_spell_cast=is_spell)
        before = [(r.id, r.current_uses) for r in caster.state.resources]
        with pytest.raises(ValueError):
            resolve_spell_interrupt(
                1, 1, caster, target, setup, action, "Fireball", 3,
                FixedDiceProvider([20]), is_spell_cast=is_spell,
            )
        assert before == [(r.id, r.current_uses) for r in caster.state.resources]
    except Exception:
        logger.exception("Illegal spell interrupt mutated resources: %s", reason)
        raise
