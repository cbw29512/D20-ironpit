"""Source-neutral target capacity in the real save and timed-condition engine."""
from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.debuffs import DebuffCounter
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def _party(limit: int = 1):
    try:
        owner = EncounterCombatant(
            combatant_id="owner", side="monsters", position_ft=0,
            state=build_combatant_state(build_goblin_warrior()),
        )
        targets = [
            EncounterCombatant(
                combatant_id=f"target-{i}", side="heroes", position_ft=5,
                state=build_combatant_state(build_demo_fighter()),
            ) for i in range(3)
        ]
        setup = EncounterSetup(
            heroes=targets, monsters=[owner], ruleset="2014",
            hero_total_levels=3, monster_total_cr="1/4",
        )
        definition = SaveCapabilityDefinition(
            id="renamed-control", name="Control From Source",
            save_ability="wisdom", dc=15, range_ft=30,
            magical_effect=True, source_effect_immunity_on_success=True,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="charmed", duration_rounds=14400,
                source_target_limit=limit,
                source_effect_immunity_on_end=True,
            ),
        )
        return owner, targets, setup, _compile_save(definition)
    except Exception:
        logger.exception("Failed source-control capacity fixture.")
        raise


def _cast(owner, target, setup, action):
    try:
        return resolve_save_action(
            1, 1, owner, target, action, 5,
            FixedDiceProvider([1]), setup=setup, spend_action=False,
            check_resource=False, spend_resource=False,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
        )
    except Exception:
        logger.exception("Failed source-target control cast against %s.", target.combatant_id)
        raise


def _owned(target, owner, action):
    return [
        effect for effect in target.state.timed_effects
        if effect.effect_id == "charmed"
        and effect.source_id == owner.combatant_id
        and effect.source_effect_id == action.id
    ]


def test_second_successful_control_ends_first_and_grants_source_immunity():
    owner, (first, second, _), setup, action = _party()
    event = _cast(owner, first, setup, action)
    assert event.applied_condition_ids == ["charmed"]
    assert len(_owned(first, owner, action)) == 1
    _cast(owner, second, setup, action)
    assert not _owned(first, owner, action)
    assert len(_owned(second, owner, action)) == 1
    assert has_source_effect_immunity(first.state, action.id, owner.combatant_id)
    assert not has_source_effect_immunity(second.state, action.id, owner.combatant_id)


def test_capacity_two_discards_oldest_not_newest():
    owner, (first, second, third), setup, action = _party(limit=2)
    for target in (first, second, third):
        _cast(owner, target, setup, action)
    assert not _owned(first, owner, action)
    assert _owned(second, owner, action) and _owned(third, owner, action)


def test_other_sources_condition_does_not_block_release_immunity():
    owner, (first, second, _), setup, action = _party()
    _cast(owner, first, setup, action)
    apply_timed_condition(
        first.state, "charmed", "other-owner", source_effect_id="other-control",
        source_is_magical=False, use_default_poison_recovery=False,
    )
    _cast(owner, second, setup, action)
    assert not _owned(first, owner, action)
    assert any(effect.source_id == "other-owner" and effect.effect_id == "charmed"
               for effect in first.state.timed_effects)
    assert has_source_effect_immunity(first.state, action.id, owner.combatant_id)


def test_suppressed_new_control_does_not_evict_old_target():
    owner, (first, second, _), setup, action = _party()
    _cast(owner, first, setup, action)
    second.state.timed_effects.append(TimedEffect(
        effect_id="ward", source_id="protecting-ally",
        owned_debuff_counters=[DebuffCounter(
            debuff_id="charmed", source_scope="magical", mode="prevent",
        )],
    ))
    _cast(owner, second, setup, action)
    assert _owned(first, owner, action)
    assert not _owned(second, owner, action)


def test_reject_zero_source_capacity_before_casting():
    with pytest.raises(ValidationError):
        FailedSaveTimedEffect(effect_id="charmed", source_target_limit=0)
