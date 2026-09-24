from app.combat.grid_pathing_support import movement_step_cost_ft
from app.combat.movement_defenses import ignores_difficult_terrain
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridPosition
from app.combat.timed_conditions import apply_timed_condition

MAP = BattleMapDefinition(id="terrain-bypass-test", width_squares=8, height_squares=8)


def _member(template, combatant_id: str, side: str, x: int, y: int, *, unconscious: bool = False):
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    state.is_unconscious = unconscious
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=0, state=state)


def _incapacitated_hostile():
    template = build_goblin_warrior().model_copy(update={"id": "terrain-hostile", "ruleset": "2014"})
    return _member(template, "terrain-hostile", "monsters", 1, 1, unconscious=True)


def test_land_stride_bypasses_nonmagical_creature_space_difficult_terrain() -> None:
    hostile = _incapacitated_hostile()
    destination = GridPosition(x=1, y=1)

    ranger7 = _member(build_rowan_ashtrail_2014(7), "ranger7", "heroes", 0, 0)
    ranger8 = _member(build_rowan_ashtrail_2014(8), "ranger8", "heroes", 0, 0)
    druid5 = _member(build_thalen_greenbough_2014(5), "druid5", "heroes", 0, 0)
    druid6 = _member(build_thalen_greenbough_2014(6), "druid6", "heroes", 0, 0)

    assert movement_step_cost_ft(MAP, ranger7, destination, [ranger7, hostile]) == 10
    assert movement_step_cost_ft(MAP, ranger8, destination, [ranger8, hostile]) == 5
    assert movement_step_cost_ft(MAP, druid5, destination, [druid5, hostile]) == 10
    assert movement_step_cost_ft(MAP, druid6, destination, [druid6, hostile]) == 5


def test_timed_all_scope_bypasses_magical_and_nonmagical_difficult_terrain() -> None:
    member = _member(build_rowan_ashtrail_2014(1), "warded", "heroes", 0, 0)
    apply_timed_condition(
        member.state,
        "movement-ward",
        "caster",
        source_effect_id="test-freedom",
        difficult_terrain_bypass_scope="all",
        use_default_poison_recovery=False,
    )

    assert ignores_difficult_terrain(member.state, magical=False) is True
    assert ignores_difficult_terrain(member.state, magical=True) is True


def test_nonmagical_scope_does_not_bypass_magical_difficult_terrain() -> None:
    member = _member(build_rowan_ashtrail_2014(8), "ranger8", "heroes", 0, 0)

    assert ignores_difficult_terrain(member.state, magical=False) is True
    assert ignores_difficult_terrain(member.state, magical=True) is False
