"""Real save/damage/maximum-HP fight with an immutable 2014 source Action."""
from __future__ import annotations

import logging

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_legality import legal_save_action
from app.combat.save_action_targeting import save_action_target_order
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_owned_condition_drain_2014 import (
    source_proven_owned_condition_drains_2014,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.debuffs import DebuffCounter
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def _fight():
    try:
        card = next(
            row for row in load_monster_source_2014()
            if source_proven_owned_condition_drains_2014(row)
        )
        (capability,) = source_proven_owned_condition_drains_2014(card)
        action = _compile_save(capability)
        source = EncounterCombatant(
            combatant_id="source", side="monsters", position_ft=0,
            state=build_combatant_state(
                build_goblin_warrior().model_copy(update={"name": "Renamed Actor"})
            ),
        )
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=5,
            state=build_combatant_state(
                build_demo_fighter().model_copy(update={"max_hp": 100})
            ),
        )
        setup = EncounterSetup(
            heroes=[target], monsters=[source], ruleset="2014",
            hero_total_levels=1, monster_total_cr="1/4",
        )
        return source, target, setup, action
    except Exception:
        logger.exception("Failed preparing source-owned save combat test.")
        raise


def test_owned_condition_is_required_and_wrong_source_cannot_authorize():
    try:
        source, target, _setup, action = _fight()
        assert not legal_save_action(
            action, target, 5, source.combatant_id, source,
        )
        assert apply_timed_condition(
            target.state, "charmed", "different-source",
            source_effect_id="renamed-control",
            use_default_poison_recovery=False,
        ) == "charmed"
        assert not legal_save_action(
            action, target, 5, source.combatant_id, source,
        )
        assert apply_timed_condition(
            target.state, "charmed", source.combatant_id,
            source_effect_id="source-owned-control",
            use_default_poison_recovery=False,
        ) == "charmed"
        assert legal_save_action(
            action, target, 5, source.combatant_id, source,
        )
        assert not legal_save_action(action, target, 10, source.combatant_id, source)
    except Exception:
        logger.exception("Source-owned condition save target legality failed.")
        raise


def test_suppressed_owned_charm_does_not_borrow_another_sources_condition():
    try:
        source, target, _setup, action = _fight()
        # A magical-only ward suppresses the owner's magical Charmed effect,
        # but another actor's nonmagical Charmed is still operational.
        apply_timed_condition(
            target.state, "charmed", source.combatant_id,
            source_effect_id="owner-magic", source_is_magical=True,
            use_default_poison_recovery=False,
        )
        apply_timed_condition(
            target.state, "charmed", "other-actor",
            source_effect_id="other-nonmagic", source_is_magical=False,
            use_default_poison_recovery=False,
        )
        target.state.timed_effects.append(TimedEffect(
            effect_id="protection", source_id="ward",
            owned_debuff_counters=[DebuffCounter(
                debuff_id="charmed", source_scope="magical", mode="prevent",
            )],
        ))
        assert not legal_save_action(
            action, target, 5, source.combatant_id, source,
        ), "The unsuppressed other actor's Charmed cannot authorize an owned Kiss."
        # Equivalent nonmagical owner Charm is not suppressed by this ward.
        apply_timed_condition(
            target.state, "charmed", source.combatant_id,
            source_effect_id="owner-nonmagic", source_is_magical=False,
            use_default_poison_recovery=False,
        )
        assert legal_save_action(action, target, 5, source.combatant_id, source)
    except Exception:
        logger.exception("Source-owned per-instance suppression regression failed.")
        raise


@pytest.mark.parametrize("save_roll,expected_damage", [(1, 55), (20, 27)])
def test_renamed_actor_executes_real_source_kiss_as_generic_save(
    save_roll: int, expected_damage: int,
):
    try:
        source, target, setup, action = _fight()
        apply_timed_condition(
            target.state, "charmed", source.combatant_id,
            source_effect_id="source-owned-control",
            use_default_poison_recovery=False,
        )
        original_template = target.state.template.model_dump_json()
        event = resolve_save_action(
            1, 1, source, target, action, 5,
            FixedDiceProvider([save_roll, 10, 10, 10, 10, 10]),
            spend_action=False, check_resource=False,
            spend_resource=False, setup=setup,
            affected_states=[source.state, target.state],
        )
        assert event.feature_id == "draining-kiss"
        assert "Draining Kiss" in event.description
        assert event.save_succeeded == (save_roll == 20)
        assert event.damage_roll is not None
        assert event.is_dead is False
        assert target.state.current_hp == 100 - expected_damage
        assert target.state.hit_point_maximum_reduction == expected_damage
        assert target.state.template.model_dump_json() == original_template
    except Exception:
        logger.exception("Real 2014 source-owned drain save fight failed.")
        raise


def test_willing_creature_can_be_an_ally_but_not_the_source_itself():
    try:
        source, target, setup, action = _fight()
        ally = EncounterCombatant(
            combatant_id="willing-ally", side="monsters", position_ft=5,
            state=build_combatant_state(
                build_demo_fighter().model_copy(update={"name": "Willing Ally", "max_hp": 60})
            ),
        )
        setup.monsters.append(ally)

        assert ally in save_action_target_order(source, setup, action.target_scope)
        assert source not in save_action_target_order(source, setup, action.target_scope)
        assert not legal_save_action(action, ally, 5, source.combatant_id, source)

        ally.state.willing_attack_source_ids.append(source.combatant_id)
        assert legal_save_action(action, ally, 5, source.combatant_id, source)
        assert not legal_save_action(action, source, 0, source.combatant_id, source)

        enemy_only = action.model_copy(update={"target_scope": "enemies"})
        assert not legal_save_action(enemy_only, ally, 5, source.combatant_id, source)

        # Willingness is an independent alternative, not an additional AND gate.
        target.state.willing_attack_source_ids.append(source.combatant_id)
        assert legal_save_action(action, target, 5, source.combatant_id, source)
    except Exception:
        logger.exception("Willing-target scope or qualification regression failed.")
        raise


def test_willing_ally_can_execute_the_compiled_draining_kiss_save():
    try:
        source, _target, setup, action = _fight()
        ally = EncounterCombatant(
            combatant_id="willing-ally", side="monsters", position_ft=5,
            state=build_combatant_state(
                build_demo_fighter().model_copy(update={"name": "Willing Ally", "max_hp": 100})
            ),
        )
        ally.state.willing_attack_source_ids.append(source.combatant_id)
        setup.monsters.append(ally)
        event = resolve_save_action(
            1, 1, source, ally, action, 5,
            FixedDiceProvider([1, 10, 10, 10, 10, 10]),
            spend_action=False, check_resource=False,
            spend_resource=False, setup=setup,
            affected_states=[source.state, ally.state],
        )
        assert event.feature_id == "draining-kiss"
        assert event.damage_roll is not None
        assert ally.state.hit_point_maximum_reduction > 0
        assert ally.state.current_hp < 100
    except Exception:
        logger.exception("Willing ally Draining Kiss execution failed.")
        raise
