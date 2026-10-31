"""2014 Invisibility must not silently drop named-action expiry."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.capability_compiler import compile_combatant
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.combat.owner_action_expiry import expire_on_owner_event
from app.domain.encounters import EncounterCombatant
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014

logger = logging.getLogger(__name__)


def test_quasit_invisibility_requires_generic_named_action_expiry():
    try:
        quasit = next(row for row in load_monster_source_2014() if row.id == "quasit")
        assert "or uses Scare" in quasit.source_actions
        # Until a named-action owner-event listener is implemented, the
        # source action must remain unbound instead of expiring incorrectly.
        action, = source_invisibility_action_2014(quasit)
        assert action.ends_on_owner_action_ids == ["scare"]
        assert action.ends_on_owner_attack
        assert not action.ends_on_owner_spell_cast
    except Exception:
        logger.exception("Quasit Invisibility named-exit guard failed")
        raise


def test_imp_invisibility_retains_attack_only_exit():
    try:
        imp = next(row for row in load_monster_source_2014() if row.id == "imp")
        action, = source_invisibility_action_2014(imp)
        assert action.ends_on_owner_attack
        assert not action.ends_on_owner_spell_cast
    except Exception:
        logger.exception("Imp Invisibility exit regression failed")
        raise

def test_quasit_named_action_ends_only_the_correct_invisible_buff():
    try:
        monster = next(row for row in load_monster_source_2014() if row.id == "quasit")
        compiled = compile_combatant(adapt_monster_mechanics_2014(monster))
        action = next(a for a in compiled.timed_self_buff_actions if a.id == "invisibility")
        state = build_combatant_state(compiled)
        member = EncounterCombatant(combatant_id="quasit-1", side="monsters", position_ft=0, state=state)
        resolve_timed_self_buff(1, 1, member, action, spend_action_cost=False)
        assert "invisible" in state.active_effect_ids
        assert expire_on_owner_event(state, "action", [state], action_id="unrelated") == []
        assert expire_on_owner_event(state, "spell_cast", [state]) == []
        assert state.concentration is not None
        assert expire_on_owner_event(state, "action", [state], action_id="scare") == ["invisible"]
        assert state.concentration is None
        assert "invisible" not in state.active_effect_ids
    except Exception:
        logger.exception("Quasit named action live state expiry failed")
        raise
