from pydantic import ValidationError
import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.ongoing_spell_control import resolve_forced_approach
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_hazards import PersistentHazardState
from app.domain.save_effects import FailedSaveTimedEffect


def _member(identifier: str, side: str, x: int) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{identifier}"
    template.name = identifier
    member = EncounterCombatant(
        combatant_id=identifier, side=side, position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=6)
    member.state.movement_remaining_ft = 30
    return member


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    target = _member("renamed-target", "heroes", 5)
    singer = _member("renamed-source", "monsters", 8)
    setup = EncounterSetup(
        heroes=[target], monsters=[singer], hero_total_levels=1,
        monster_total_cr="1", ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )
    setup.persistent_hazards.append(PersistentHazardState(
        hazard_id="other-source:hazard", source_id="other-source",
        source_side="monsters", action_id="renamed-hazard",
        action_name="Renamed Hazard", position=GridPosition(x=6, y=6),
        footprint_size="medium", trigger_radius_ft=0,
        save_ability="dexterity", dc=10, failure_damage=5,
        success_damage=0, damage_type="fire", remaining_damage_capacity=20,
        expires_round=10,
    ))
    apply_timed_condition(
        target.state, "incapacitated", singer.combatant_id,
        source_effect_id="renamed-control", applied_round=1,
        expiry_timing="target_turn_end", repeat_save_ability="wisdom",
        repeat_save_dc=11, repeat_save_timing="target_turn_end",
        repeat_save_before_damaging_terrain=True,
        turn_behavior="forced_approach_source", use_default_poison_recovery=False,
    )
    apply_timed_condition(
        target.state, "charmed", singer.combatant_id,
        source_effect_id="renamed-control", applied_round=1,
        use_default_poison_recovery=False,
    )
    return target, singer, setup


def test_success_before_damaging_terrain_removes_group_without_moving() -> None:
    target, singer, setup = _setup()
    before = target.state.position.model_copy(deep=True)
    events, sequence = resolve_forced_approach(
        1, 1, target, setup, FixedDiceProvider([20]), "1:renamed-target",
    )
    assert sequence == 2
    assert [event.event_type for event in events] == ["saving_throw"]
    assert events[0].feature_id == "renamed-control"
    assert events[0].save_succeeded is True
    assert set(events[0].removed_condition_ids) == {"incapacitated", "charmed"}
    assert target.state.position == before
    assert target.state.movement_remaining_ft == 30
    assert singer.state.reaction_available is True


def test_failed_pre_entry_save_allows_step_and_hazard_resolution() -> None:
    target, _singer, setup = _setup()
    events, _ = resolve_forced_approach(
        1, 1, target, setup, FixedDiceProvider([1, 20]), "1:renamed-target",
    )
    assert events[0].event_type == "saving_throw"
    assert events[0].feature_id == "renamed-control"
    assert events[0].save_succeeded is False
    assert any(event.event_type == "movement" for event in events[1:])
    assert any(event.feature_id == "renamed-hazard" for event in events[1:])
    assert target.state.position != GridPosition(x=5, y=6)
    assert target.state.timed_effects[0].repeat_save_failure_count == 1


def test_damaging_terrain_trigger_requires_complete_repeat_save_data() -> None:
    with pytest.raises(ValidationError, match="Damaging-terrain repeat saves require"):
        FailedSaveTimedEffect(
            effect_id="renamed-control",
            repeat_save_before_damaging_terrain=True,
        )
