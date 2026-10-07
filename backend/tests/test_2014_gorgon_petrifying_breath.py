from __future__ import annotations

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from scripts.browser_template_serializer import template_row


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def _compile(monster_id: str):
    return compile_combatant(adapt_basic_monster_2014(_source(monster_id)))


def _member(template, combatant_id: str, side: str, x: int) -> EncounterCombatant:
    state = build_combatant_state(template.model_copy(deep=True))
    state.position = GridPosition(x=x, y=0)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=state,
    )


def _encounter():
    gorgon = _member(_compile("gorgon"), "monster:gorgon", "monsters", 0)
    target = _member(_compile("commoner"), "hero:target", "heroes", 1)
    setup = EncounterSetup(
        heroes=[target],
        monsters=[gorgon],
        hero_total_levels=1,
        monster_total_cr="5",
        ruleset="2014",
        map_definition=BattleMapDefinition(
            id="gorgon-petrifying-breath",
            width_squares=12,
            height_squares=12,
        ),
    )
    action = next(
        item for item in gorgon.state.template.saving_throw_actions
        if item.id == "petrifying-breath"
    )
    return gorgon, target, setup, action


def test_gorgon_binds_existing_save_recharge_and_staged_petrification() -> None:
    source = _source("gorgon")
    assert basic_blockers_2014(source) == ()

    template = _compile("gorgon")
    action = next(
        item for item in template.saving_throw_actions
        if item.id == "petrifying-breath"
    )

    assert action.name == "Petrifying Breath"
    assert (action.save_ability, action.dc) == ("constitution", 13)
    assert action.area is not None
    assert (action.area.shape, action.area.length_ft) == ("cone", 30)
    assert action.resource_id == "petrifying-breath"

    rider = action.failed_save_timed_effect
    assert rider is not None
    assert rider.effect_id == "restrained"
    assert (
        rider.repeat_save_ability,
        rider.repeat_save_dc,
        rider.repeat_save_timing,
    ) == ("constitution", 13, "target_turn_end")
    assert rider.repeat_save_failure_condition_id == "petrified"

    recharge = next(
        rule for rule in template.recharge_rules
        if rule.resource_id == "petrifying-breath"
    )
    assert recharge.minimum_roll == 5

    browser = template_row(template)
    browser_action = next(
        item for item in browser["saving_throw_actions"]
        if item["id"] == "petrifying-breath"
    )
    assert browser_action["failedSaveTimedEffect"]["repeatSaveFailureConditionId"] == "petrified"


def test_gorgon_repeat_save_success_removes_restrained() -> None:
    gorgon, target, setup, action = _encounter()
    event = resolve_save_action(
        1,
        1,
        gorgon,
        target,
        action,
        10,
        FixedDiceProvider([1]),
        affected_states=[gorgon.state, target.state],
        setup=setup,
    )
    assert event.save_succeeded is False
    assert "restrained" in target.state.active_effect_ids
    assert target.state.is_dead is False

    lifecycle, _ = resolve_target_condition_timing(
        2,
        1,
        target,
        "target_turn_end",
        FixedDiceProvider([20]),
        setup,
    )
    assert lifecycle[0].save_succeeded is True
    assert "restrained" not in target.state.active_effect_ids
    assert "petrified" not in target.state.active_effect_ids
    assert target.state.is_dead is False


def test_gorgon_repeat_save_failure_escalates_through_universal_petrified_rule() -> None:
    gorgon, target, setup, action = _encounter()
    event = resolve_save_action(
        1,
        1,
        gorgon,
        target,
        action,
        10,
        FixedDiceProvider([1]),
        affected_states=[gorgon.state, target.state],
        setup=setup,
    )
    assert event.save_succeeded is False
    assert "restrained" in target.state.active_effect_ids
    assert target.state.is_dead is False

    lifecycle, _ = resolve_target_condition_timing(
        2,
        1,
        target,
        "target_turn_end",
        FixedDiceProvider([1]),
        setup,
    )
    assert lifecycle[0].save_succeeded is False
    assert "restrained" not in target.state.active_effect_ids
    assert "petrified" in target.state.active_effect_ids
    assert target.state.is_dead is True
    assert target.state.is_alive is False
    assert target.state.current_hp == 0
