"""2014 rest-recharge Invisibility uses the shared timed self-buff and owner expiry."""
from __future__ import annotations

import logging

import pytest

from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_invisibility_2014 import (
    source_invisibility_action_2014, source_invisibility_resources_2014,
)
from app.domain.encounters import EncounterCombatant
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def _card():
    try:
        return next(c for c in load_monster_source_2014() if c.id == "duergar")
    except Exception:
        logger.exception("Duergar immutable 2014 source record not found")
        raise


def test_rest_recharge_source_compiles_with_existing_invisibility_runtime():
    try:
        card = _card()
        actions = source_invisibility_action_2014(card)
        assert len(actions) == 1
        action = actions[0]
        assert action.id == "invisibility"
        assert action.condition_ids == ["invisible"]
        assert action.resource_id == "invisibility"
        assert action.duration_rounds == 600
        assert action.concentration and action.magical_effect
        assert action.ends_on_owner_attack and action.ends_on_owner_spell_cast
        assert action.ends_on_owner_action_ids == ["enlarge"]
        assert len(source_invisibility_resources_2014(card)) == 1
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        assert any(a.id == "invisibility" for a in template.timed_self_buff_actions)
        assert any(r.id == "invisibility" and r.max_uses == 1 for r in template.resources)
    except Exception:
        logger.exception("Rest recharge invisibility source binding failed")
        raise


def test_invisible_resource_concentration_and_named_action_expiry():
    try:
        template = compile_combatant(adapt_monster_mechanics_2014(_card()))
        state = build_combatant_state(template)
        actor = EncounterCombatant(
            combatant_id="actor", side="monsters", position_ft=0, state=state,
        )
        invis = next(a for a in template.timed_self_buff_actions if a.id == "invisibility")
        resource = next(r for r in state.resources if r.id == "invisibility")
        assert resource.current_uses == 1
        resolve_timed_self_buff(1, 1, actor, invis, spend_action_cost=False)
        assert resource.current_uses == 0
        assert state.concentration is not None
        assert "invisible" in state.active_effect_ids
        assert any(x.expires_round == 601 for x in state.timed_effects)
        # This is a synthetic timed Action, not a special Duergar resolver:
        # casting any source-named self-buff must trigger generic owner expiry.
        enlarge = TimedSelfBuffAction(
            id="enlarge", name="Alternate Shape", duration_rounds=1,
            condition_ids=["invisible"], magical_effect=True,
        )
        # An unrelated self-action does not end the declared source.
        other = enlarge.model_copy(update={"id": "other"})
        resolve_timed_self_buff(2, 1, actor, other, spend_action_cost=False)
        assert state.concentration is not None
        resolve_timed_self_buff(3, 1, actor, enlarge, spend_action_cost=False)
        assert state.concentration is None
        assert resource.current_uses == 0
        with pytest.raises(ValueError, match="Resource"):
            resolve_timed_self_buff(4, 1, actor, invis, spend_action_cost=False)
    except Exception:
        logger.exception("Invisibility resource and owner-action expiry failed")
        raise


def test_rewritten_source_or_missing_named_exit_is_not_silently_admitted():
    try:
        original = _card()
        changed = original.source_actions.replace(
            "up to 1 hour", "up to 3 hours",
        )
        assert changed != original.source_actions
        mutated = original.model_copy(update={"source_actions": changed})
        assert source_invisibility_action_2014(mutated) == []
        missing_action = original.model_copy(update={
            "action_names": [
                name for name in original.action_names if not name.startswith("Enlarge")
            ],
        })
        assert source_invisibility_action_2014(missing_action) == []
        renamed = original.model_copy(update={"id": "other-entity", "name": "Other"})
        assert source_invisibility_action_2014(renamed) == source_invisibility_action_2014(original)
    except Exception:
        logger.exception("Rest-invisibility mutation/rename source proof failed")
        raise
