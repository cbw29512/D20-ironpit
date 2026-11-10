"""Source-neutral damage-trigger-only repeat saves never gain periodic turns."""
from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.damage_reaction_events import (
    applied_damage_total, resolve_damage_event_reactions,
)
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def _scenario():
    try:
        owner = EncounterCombatant(
            combatant_id="owner", side="monsters", position_ft=0,
            state=build_combatant_state(build_goblin_warrior()),
        )
        victim = EncounterCombatant(
            combatant_id="victim", side="heroes", position_ft=5,
            state=build_combatant_state(build_demo_fighter()),
        )
        setup = EncounterSetup(
            heroes=[victim], monsters=[owner], ruleset="2014",
            hero_total_levels=1, monster_total_cr="1/4",
        )
        ability = SaveCapabilityDefinition(
            id="renamed-control", name="Source-Owned Control",
            save_ability="wisdom", dc=10, range_ft=30,
            magical_effect=True, source_effect_immunity_on_success=True,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="charmed", duration_rounds=14400,
                repeat_save_ability="wisdom", repeat_save_dc=10,
                damage_repeat_save_trigger="any_damage_source",
                source_effect_immunity_on_end=True,
            ),
        )
        return owner, victim, setup, _compile_save(ability)
    except Exception:
        logger.exception("Failed to prepare event-only repeat-save fight.")
        raise


def test_damage_only_save_has_no_periodic_roll_but_reacts_to_real_damage():
    try:
        owner, victim, setup, ability = _scenario()
        event = resolve_save_action(
            1, 1, owner, victim, ability, 5,
            FixedDiceProvider([1]), setup=setup, spend_action=False,
        )
        assert event.applied_condition_ids == ["charmed"]
        effect = next(x for x in victim.state.timed_effects if x.effect_id == "charmed")
        assert effect.repeat_save_timing is None
        assert effect.repeat_save_ability == "wisdom"
        assert effect.damage_repeat_save_trigger == "any_damage_source"
        for timing in ("target_turn_start", "target_turn_end"):
            events, _ = resolve_target_condition_timing(
                2, 1, victim, timing, FixedDiceProvider([20]), setup,
            )
            assert not any(x.event_type == "saving_throw" for x in events)
        assert effect in victim.state.timed_effects
        hit = resolve_encounter_attack(
            3, 1, owner, victim, owner.state.template.weapon_attack, 5,
            FixedDiceProvider([19, 4]), setup, spend_action=False,
        )
        assert applied_damage_total(hit) > 0
        followups, _ = resolve_damage_event_reactions(
            4, 1, owner, hit, setup, FixedDiceProvider([20]),
        )
        assert len(followups) == 1
        assert followups[0].feature_id == "renamed-control"
        assert followups[0].save_succeeded
        assert "charmed" not in victim.state.active_effect_ids
    except Exception:
        logger.exception("Event-only damage-trigger save fight regression failed.")
        raise


@pytest.mark.parametrize("model", (FailedSaveTimedEffect, TimedEffect))
def test_event_only_requires_ability_and_dc_and_periodic_requires_timing(model):
    try:
        common = {"effect_id": "charmed"}
        if model is TimedEffect:
            common["source_id"] = "owner"
        valid = model(**common, repeat_save_ability="wisdom", repeat_save_dc=15,
                      damage_repeat_save_trigger="any_damage_source")
        assert valid.repeat_save_timing is None
        with pytest.raises(ValidationError):
            model(**common, repeat_save_ability="wisdom", repeat_save_dc=15)
        with pytest.raises(ValidationError):
            model(**common, repeat_save_dc=15,
                  damage_repeat_save_trigger="any_damage_source")
        with pytest.raises(ValidationError):
            model(**common, repeat_save_ability="wisdom",
                  damage_repeat_save_trigger="any_damage_source")
        with pytest.raises(ValidationError):
            model(**common, repeat_save_timing="target_turn_end")
        periodic = model(**common, repeat_save_ability="wisdom",
                         repeat_save_dc=15, repeat_save_timing="target_turn_end")
        assert periodic.repeat_save_timing == "target_turn_end"
    except Exception:
        logger.exception("Event-only vs periodic repeat-save validation failed.")
        raise
