"""Source-neutral grouped failed-save condition lifecycle regressions."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.save_effects import FailedSaveTimedEffect


def _combatant(combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(build_demo_fighter()),
    )


def test_grouped_failed_save_conditions_share_one_lifecycle() -> None:
    definition = SaveCapabilityDefinition(
        id="renamed-group-control",
        name="Renamed Group Control",
        save_ability="wisdom",
        dc=16,
        range_ft=30,
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="charmed",
            additional_effect_ids=["incapacitated"],
            repeat_save_ability="wisdom",
            repeat_save_dc=16,
            repeat_save_timing="target_turn_end",
            source_effect_immunity_on_end=True,
        ),
    )
    action = _compile_save(definition)
    source = _combatant("source", "monsters", 0)
    target = _combatant("target", "heroes", 5)
    setup = EncounterSetup(
        heroes=[target],
        monsters=[source],
        ruleset="2014",
        hero_total_levels=1,
        monster_total_cr="1",
    )

    event = resolve_save_action(
        1, 1, source, target, action, 5, FixedDiceProvider([1]), setup=setup,
    )

    assert event.applied_condition_ids == ["charmed", "incapacitated"]
    assert {"charmed", "incapacitated"} <= set(target.state.active_effect_ids)
    primary = next(effect for effect in target.state.timed_effects if effect.effect_id == "charmed")
    secondary = next(
        effect for effect in target.state.timed_effects if effect.effect_id == "incapacitated"
    )
    assert primary.repeat_save_timing == "target_turn_end"
    assert secondary.repeat_save_timing is None
    assert primary.source_effect_id == secondary.source_effect_id == action.id
    assert remove_effect_group(target.state, primary) == ["charmed", "incapacitated"]
    assert action.failed_save_timed_effect.additional_effect_ids == ["incapacitated"]


def test_grouped_failed_save_condition_ids_must_be_distinct() -> None:
    with pytest.raises(ValidationError, match="must be distinct"):
        FailedSaveTimedEffect(
            effect_id="charmed",
            additional_effect_ids=["incapacitated", "charmed"],
        )
