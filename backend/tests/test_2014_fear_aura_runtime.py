from __future__ import annotations

import logging
from unittest.mock import Mock

from app.combat.dice import DiceProvider, FixedDiceProvider
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.state import build_combatant_state
from app.combat.timed_emanations import resolve_target_turn_start_emanations
from app.content.demo import build_demo_fighter
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _no_rolls():
    try:
        dice = Mock(spec=DiceProvider)
        dice.roll.side_effect = AssertionError("Suppressed Fear Aura must not roll.")
        return dice
    except Exception:
        logger.exception("Failed to build no-roll Fear Aura dice provider.")
        raise


def _fight():
    try:
        card = next(
            monster for monster in load_monster_source_2014()
            if monster.id == "pit-fiend"
        )
        action, = condition_auras_from_source(card.source_traits, "2014")
        source_template = build_demo_fighter().model_copy(update={
            "id": "renamed-fear-emitter",
            "name": "Renamed Fear Emitter",
            "kind": "monster",
            "ruleset": "2014",
            "creature_type": "fiend",
            "timed_self_buff_actions": [action],
        }, deep=True)
        target_template = build_demo_fighter().model_copy(update={
            "id": "renamed-target",
            "name": "Renamed Target",
            "saving_throw_bonuses": {
                **build_demo_fighter().saving_throw_bonuses,
                "wisdom": 5,
            },
        }, deep=True)
        source = EncounterCombatant(
            combatant_id="source", side="monsters", position_ft=0,
            state=build_combatant_state(source_template),
        )
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=20,
            state=build_combatant_state(target_template),
        )
        setup = EncounterSetup(
            heroes=[target], monsters=[source], hero_total_levels=1,
            monster_total_cr="20", ruleset="2014",
        )
        return source, target, setup
    except Exception:
        logger.exception("Failed to build universal 2014 Fear Aura test fight.")
        raise


def test_fear_aura_suppresses_while_source_incapacitated_then_resumes() -> None:
    try:
        source, target, setup = _fight()
        source.state.active_effect_ids.append("incapacitated")
        events, sequence = resolve_target_turn_start_emanations(
            1, 1, target, setup, _no_rolls()
        )
        assert (events, sequence) == ([], 1)
        assert "frightened" not in target.state.active_effect_ids

        source.state.active_effect_ids.remove("incapacitated")
        events, sequence = resolve_target_turn_start_emanations(
            sequence, 2, target, setup, FixedDiceProvider([1])
        )
        assert len(events) == 1
        assert events[0].applied_condition_ids == ["frightened"]
        effect, = target.state.timed_effects
        assert effect.expiry_timing == "target_turn_start"
        assert effect.expires_round is None
    except Exception:
        logger.exception("Fear Aura source-incapacitation lifecycle regression failed.")
        raise


def test_fear_aura_success_grants_source_specific_match_immunity() -> None:
    try:
        source, target, setup = _fight()
        events, sequence = resolve_target_turn_start_emanations(
            1, 1, target, setup, FixedDiceProvider([20])
        )
        assert events[0].save_succeeded is True
        assert has_source_effect_immunity(
            target.state, "fear-aura", source.combatant_id
        )
        repeated, sequence = resolve_target_turn_start_emanations(
            sequence, 500, target, setup, _no_rolls()
        )
        assert repeated == []
        assert sequence == 2
    except Exception:
        logger.exception("Fear Aura success-immunity regression failed.")
        raise
