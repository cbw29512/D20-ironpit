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
from scripts.browser_template_serializer import template_row


def _source():
    return next(item for item in load_monster_source_2014() if item.id == "gorgon")


def _compile():
    return compile_combatant(adapt_basic_monster_2014(_source()))


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template.model_copy(deep=True)),
    )


def test_gorgon_petrifying_breath_source_and_browser_binding_are_exact() -> None:
    source = _source()
    action = next(item for item in source.saving_throw_actions if item["id"] == "petrifying-breath")
    control = action["failure_control_effect"]

    assert (action["save_ability"], action["dc"], action["range_ft"]) == ("constitution", 13, 30)
    assert action["area"] == {"shape": "cone", "origin": "self", "length_ft": 30}
    assert control == {
        "condition_id": "restrained",
        "repeat_save_ability": "constitution",
        "repeat_save_dc": 13,
        "repeat_save_timing": "target_turn_end",
        "repeat_save_failure_condition_id": "petrified",
    }
    assert source.action_recharges["petrifying-breath"] == 5
    assert basic_blockers_2014(source) == ()

    template = _compile()
    breath = next(item for item in template.saving_throw_actions if item.id == "petrifying-breath")
    rider = breath.failed_save_timed_effect
    assert rider is not None
    assert rider.effect_id == "restrained"
    assert (rider.repeat_save_ability, rider.repeat_save_dc, rider.repeat_save_timing) == (
        "constitution", 13, "target_turn_end",
    )
    assert rider.repeat_save_failure_condition_id == "petrified"

    browser = template_row(template)
    browser_breath = next(item for item in browser["saving_throw_actions"] if item["id"] == "petrifying-breath")
    assert browser_breath["failedSaveTimedEffect"]["repeatSaveFailureConditionId"] == "petrified"


def test_gorgon_failed_repeat_save_reuses_terminal_petrified_condition() -> None:
    gorgon = _member(_compile(), "monster:gorgon", "monsters", 0)
    target_template = compile_combatant(
        adapt_basic_monster_2014(
            next(item for item in load_monster_source_2014() if item.id == "commoner")
        )
    )
    target = _member(target_template, "hero:target", "heroes", 5)
    setup = EncounterSetup(
        heroes=[target],
        monsters=[gorgon],
        hero_total_levels=1,
        monster_total_cr="5",
        ruleset="2014",
    )
    action = next(item for item in gorgon.state.template.saving_throw_actions if item.id == "petrifying-breath")

    first = resolve_save_action(
        1, 1, gorgon, target, action, 5, FixedDiceProvider([1]), setup=setup,
    )
    assert first.save_succeeded is False
    assert "restrained" in target.state.active_effect_ids
    assert target.state.is_dead is False

    repeated, _ = resolve_target_condition_timing(
        2, 1, target, "target_turn_end", FixedDiceProvider([1]), setup,
    )
    assert repeated[0].save_succeeded is False
    assert "restrained" not in target.state.active_effect_ids
    assert "petrified" in target.state.active_effect_ids
    assert repeated[0].applied_condition_ids == ["petrified"]
    assert target.state.is_dead is True
    assert target.state.current_hp == 0
