from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition

_EXPECTED = {
    "bronze-dragon-wyrmling": (12, 30),
    "young-bronze-dragon": (15, 40),
    "adult-bronze-dragon": (19, 60),
    "ancient-bronze-dragon": (23, 60),
}


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


def test_bronze_repulsion_breath_family_binds_shared_failed_save_push() -> None:
    for monster_id, (dc, push_ft) in _EXPECTED.items():
        source = _source(monster_id)
        repulsion = next(
            action for action in save_capabilities_2014(source)
            if action.id == "repulsion-breath"
        )

        assert repulsion.name == "Repulsion Breath"
        assert (repulsion.save_ability, repulsion.dc) == ("strength", dc)
        assert repulsion.area is not None
        assert (repulsion.area.shape, repulsion.area.length_ft) == ("cone", 30)
        assert repulsion.failed_save_push_ft == push_ft
        assert repulsion.resource_id == "breath-weapons"

        blockers = basic_blockers_2014(source)
        assert "mechanic:save-action" not in blockers

    assert basic_blockers_2014(_source("bronze-dragon-wyrmling")) == ()
    assert basic_blockers_2014(_source("young-bronze-dragon")) == ()
    assert basic_blockers_2014(_source("adult-bronze-dragon")) == ("source:extra-action",)
    assert basic_blockers_2014(_source("ancient-bronze-dragon")) == ("source:extra-action",)


def test_bronze_wyrmling_repulsion_uses_universal_forced_movement() -> None:
    dragon = _member(
        _compile("bronze-dragon-wyrmling"),
        "monster:bronze-wyrmling",
        "monsters",
        1,
    )
    commoner = _compile("commoner")
    target = _member(commoner, "hero:target", "heroes", 2)
    setup = EncounterSetup(
        heroes=[target],
        monsters=[dragon],
        hero_total_levels=1,
        monster_total_cr="1",
        ruleset="2014",
        map_definition=BattleMapDefinition(
            id="bronze-repulsion",
            width_squares=20,
            height_squares=4,
        ),
    )

    action = next(
        item for item in dragon.state.template.saving_throw_actions
        if item.id == "repulsion-breath"
    )
    event = resolve_save_action(
        1,
        1,
        dragon,
        target,
        action,
        5,
        FixedDiceProvider([1]),
        setup=setup,
    )

    assert event.save_succeeded is False
    assert action.failed_save_push_ft == 30
    assert target.state.position == GridPosition(x=8, y=0)
    assert "pushed 30 feet away" in event.description
    assert dragon.state.resources["breath-weapons"] == 0
