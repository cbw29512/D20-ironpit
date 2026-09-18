from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.dice import FixedDiceProvider
from app.combat.recharge import resolve_recharge_checks
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition


def _source():
    return {monster.id: monster for monster in load_monster_source_2014()}


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
    )


def test_2014_hell_hound_binds_to_shared_area_save_and_recharge() -> None:
    source = _source()
    hell_hound = source["hell-hound"]
    assert basic_blockers_2014(hell_hound) == ()

    definition = adapt_basic_monster_2014(hell_hound)
    template = compile_combatant(definition)
    breath = next(action for action in template.saving_throw_actions if action.id == "fire-breath")
    assert breath.area is not None
    assert breath.area.shape == "cone"
    assert breath.area.length_ft == 15
    assert breath.resource_id == "fire-breath"
    assert template.resources[0].id == "fire-breath"
    assert template.recharge_rules[0].minimum_roll == 5


def test_shared_2014_area_save_spends_once_and_shares_damage_rolls() -> None:
    source = _source()
    actor = _member(
        compile_combatant(adapt_basic_monster_2014(source["hell-hound"])),
        "monster:hell-hound", "monsters", 1, 1,
    )
    commoner = compile_combatant(adapt_basic_monster_2014(source["commoner"]))
    first = _member(commoner, "hero:first", "heroes", 2, 1)
    second = _member(commoner, "hero:second", "heroes", 3, 1)
    setup = EncounterSetup(
        heroes=[first, second], monsters=[actor], hero_total_levels=2,
        monster_total_cr="3", ruleset="2014",
        map_definition=BattleMapDefinition(id="area-test", width_squares=10, height_squares=10),
    )

    selected = choose_area_save(actor, setup)
    assert selected is not None
    action, placement = selected
    assert action.id == "fire-breath"
    assert set(placement.target_ids) == {"hero:first", "hero:second"}

    events, sequence = resolve_area_save(
        1, 1, actor, setup, action, placement,
        FixedDiceProvider([1, 2, 3, 4, 5, 6, 1, 20]),
    )
    assert sequence == 3
    assert len(events) == 2
    assert actor.state.resources[0].current_uses == 0
    assert events[0].damage_components[0].rolls == [1, 2, 3, 4, 5, 6]
    assert events[1].damage_components[0].rolls == [1, 2, 3, 4, 5, 6]
    assert events[0].resource_remaining == 0
    assert events[1].resource_remaining == 0

    checks = resolve_recharge_checks(actor.state, FixedDiceProvider([5]))
    assert checks[0].restored is True
    assert actor.state.resources[0].current_uses == 1


def test_complex_2014_save_control_remains_fail_closed() -> None:
    gorgon = _source()["gorgon"]
    blockers = basic_blockers_2014(gorgon)
    assert "mechanic:save-action" in blockers
    assert "mechanic:recharge" in blockers
