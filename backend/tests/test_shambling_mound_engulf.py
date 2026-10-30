from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import release_grapple
from app.combat.grapple_periodic_damage import resolve_grapple_periodic_damage
from app.combat.save_action_legality import legal_save_action
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _member(template_id: str, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=position_ft,
            state=build_combatant_state(build_combatant_from_capabilities(template_id)),
        )
    except Exception:
        logger.exception("Failed to build Engulf test member %s.", template_id)
        raise


def test_shambling_mound_engulf_is_one_multiattack_replacement() -> None:
    try:
        mound = build_combatant_from_capabilities("srd-shambling-mound")
        engulf = next(action for action in mound.saving_throw_actions if action.name == "Engulf")
        multi = mound.attack_action

        assert multi is not None
        assert len(multi.slots) == 3
        assert engulf.id in multi.slots[0].save_action_ids
        assert multi.slots[1].save_action_ids == []
        assert multi.slots[2].save_action_ids == []
        assert all(slot.attack_ids for slot in multi.slots)
    except Exception:
        logger.exception("Shambling Mound mixed Multiattack regression failed.")
        raise


def test_engulf_applies_linked_conditions_periodic_damage_and_capacity() -> None:
    try:
        mound = _member("srd-shambling-mound", "mound", "monsters", 5)
        first = _member("srd-commoner", "first", "heroes", 0)
        second = _member("srd-commoner", "second", "heroes", 5)
        setup = EncounterSetup(
            heroes=[first, second],
            monsters=[mound],
            hero_total_levels=2,
            monster_total_cr="5",
        )
        engulf = next(action for action in mound.state.template.saving_throw_actions if action.name == "Engulf")

        event = resolve_save_action(
            1, 1, mound, first, engulf, 5, FixedDiceProvider([1]),
            setup=setup,
            affected_states=[first.state, second.state, mound.state],
        )

        assert event.save_succeeded is False
        assert set(first.state.active_effect_ids) >= {"grappled", "restrained", "blinded"}
        assert first.state.grapple_sources[0].source_effect_id == engulf.id
        assert legal_save_action(engulf, second, 0, mound, setup) is False

        hp_before = first.state.current_hp
        events, sequence = resolve_grapple_periodic_damage(
            2, 2, first, setup, FixedDiceProvider([3, 3, 3]),
        )
        assert sequence == 3
        assert len(events) == 1
        assert events[0].feature_id == engulf.id
        assert events[0].damage_roll is not None
        assert events[0].damage_roll.total == 9
        assert first.state.current_hp == hp_before - 9

        release_grapple(first.state, mound.combatant_id)
        assert "blinded" not in first.state.active_effect_ids
        assert "restrained" not in first.state.active_effect_ids
        events, sequence_after = resolve_grapple_periodic_damage(
            sequence, 3, first, setup, FixedDiceProvider([6, 6, 6]),
        )
        assert events == []
        assert sequence_after == sequence
        assert legal_save_action(engulf, second, 0, mound, setup) is True
    except Exception:
        logger.exception("Shambling Mound Engulf lifecycle regression failed.")
        raise
