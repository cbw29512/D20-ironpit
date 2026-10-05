from app.combat.debuff_counters import difficult_terrain_multiplier
from app.combat.dice import FixedDiceProvider
from app.combat.flight_ground_immunity import combatant_is_flying
from app.combat.grapple import apply_grapple
from app.combat.grid_pathing import movement_step_cost_ft, plan_movement_toward
from app.combat.pit_engagement import voluntary_destination_leaves_melee
from app.combat.state import begin_turn, build_combatant_state
from app.combat.teleport_policy import choose_teleport_action
from app.combat.teleport_resolution import resolve_teleport
from app.combat.temporary_terrain import destination_is_difficult_terrain
from app.combat.timed_conditions import apply_timed_condition
from app.content.arena_map import build_standard_iron_pit_map
from app.content.demo import build_goblin_warrior
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.movement import MovementModes
from app.domain.runtime import TimedEffect
from app.domain.teleport_actions import TeleportAction
from app.domain.temporary_terrain import TemporaryTerrainZone


def _misty_step() -> TeleportAction:
    return TeleportAction(
        id="misty-step",
        name="Misty Step",
        level=2,
        action_cost="bonus_action",
        range_ft=30,
        resource_id="spell-slot-2",
        expends_spell_slot=True,
        animation="misty-step",
        source="SRD Misty Step mapped to the in-place pit teleport-cancel primitive",
    )


def _member(
    combatant_id: str,
    side: str,
    x: int,
    y: int,
    *,
    fly_ft: int = 0,
    teleport: bool = False,
) -> EncounterCombatant:
    updates: dict[str, object] = {
        "id": combatant_id,
        "name": combatant_id,
        "movement_modes": MovementModes(walk_ft=30, fly_ft=fly_ft),
    }
    if teleport:
        updates["teleport_actions"] = [_misty_step()]
        updates["resources"] = [
            ResourceDefinition(id="spell-slot-2", name="2nd-level Slot", max_uses=1),
        ]
    template = build_goblin_warrior().model_copy(update=updates)
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=state,
    )


def _setup(hero: EncounterCombatant, monster: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[hero],
        monsters=[monster],
        hero_total_levels=1,
        monster_total_cr="1/4",
        ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )


def test_flyer_ignores_ground_debuff_and_stays_in_melee() -> None:
    flyer = _member("flyer", "heroes", 7, 6, fly_ft=60)
    enemy = _member("enemy", "monsters", 8, 6)
    setup = _setup(flyer, enemy)
    zone = TemporaryTerrainZone(
        zone_id="thorns",
        source_id="enemy",
        action_id="thorns",
        action_name="Thorns",
        center=GridPosition(x=7, y=6),
        radius_ft=10,
        expires_round=3,
    )
    setup.temporary_terrain_zones.append(zone)

    assert combatant_is_flying(flyer.state) is True
    assert apply_timed_condition(
        flyer.state,
        "restrained",
        "enemy",
        source_effect_id="ground-snare",
        source_is_magical=True,
        ground_contact=True,
        use_default_poison_recovery=False,
    ) is None
    assert "restrained" not in flyer.state.active_effect_ids
    assert difficult_terrain_multiplier(flyer.state, source_is_magical=True) == 1
    assert destination_is_difficult_terrain(setup.temporary_terrain_zones, flyer, flyer.state.position) is False

    walker = _member("walker", "heroes", 7, 7)
    assert apply_timed_condition(
        walker.state,
        "restrained",
        "enemy",
        source_effect_id="ground-snare",
        source_is_magical=True,
        ground_contact=True,
        use_default_poison_recovery=False,
    ) == "restrained"
    assert destination_is_difficult_terrain(setup.temporary_terrain_zones, walker, GridPosition(x=7, y=7)) is True

    map_definition = BattleMapDefinition(id="melee-lock", width_squares=16, height_squares=16)
    members = [flyer, enemy]
    away = GridPosition(x=5, y=6)
    assert voluntary_destination_leaves_melee(flyer, members, away) is True
    assert movement_step_cost_ft(map_definition, flyer, away, members) == 5
    plan = plan_movement_toward(map_definition, flyer, enemy, members, 25, 60)
    assert plan.path == []
    assert flyer.state.position == GridPosition(x=7, y=6)


def test_start_of_turn_flying_buff_clears_seeded_ground_debuff() -> None:
    flyer = _member("flyer", "heroes", 4, 4, fly_ft=40)
    assert apply_timed_condition(
        flyer.state,
        "poisoned",
        "seed",
        source_effect_id="toxin",
        use_default_poison_recovery=False,
    ) == "poisoned"
    flyer.state.timed_effects.append(TimedEffect(
        effect_id="restrained",
        source_id="seed",
        source_effect_id="ground-snare",
        ground_contact=True,
        ends_on_teleport=True,
    ))
    flyer.state.active_effect_ids.append("restrained")

    cleared = begin_turn(flyer.state)

    assert ("restrained", "seed", 0) in cleared
    assert "restrained" not in flyer.state.active_effect_ids
    assert "poisoned" in flyer.state.active_effect_ids


def test_misty_step_clears_teleport_cancelable_debuff_without_moving() -> None:
    caster = _member("caster", "heroes", 6, 6, teleport=True)
    enemy = _member("enemy", "monsters", 7, 6)
    setup = _setup(caster, enemy)
    origin = caster.state.position.model_copy(deep=True)
    assert apply_timed_condition(
        caster.state,
        "restrained",
        "enemy",
        source_effect_id="ground-snare",
        source_is_magical=True,
        ground_contact=True,
        ends_on_teleport=True,
        use_default_poison_recovery=False,
    ) == "restrained"
    apply_grapple(caster.state, "enemy", 12, 5, restrains=True)
    begin_turn(caster.state)
    choice = choose_teleport_action(caster, setup, "1:caster")
    assert choice is not None
    action, destination = choice
    assert action.id == "misty-step"
    assert destination == origin

    events, _ = resolve_teleport(
        1, 1, caster, setup, action, destination, FixedDiceProvider([1]), "1:caster",
    )

    assert caster.state.position == origin
    assert "restrained" not in caster.state.active_effect_ids
    assert caster.state.grapple_sources == []
    assert events[0].event_type == "feature"
    assert "restrained" in events[0].removed_condition_ids
    assert "without leaving its spot" in events[0].description


def test_creature_cannot_kite_out_of_melee_by_flying_or_running() -> None:
    map_definition = BattleMapDefinition(id="no-kite", width_squares=16, height_squares=16)
    runner = _member("runner", "heroes", 4, 4)
    flyer = _member("flyer", "monsters", 8, 4, fly_ft=60)
    enemy = _member("anchor", "monsters", 5, 4)
    hero_anchor = _member("hero-anchor", "heroes", 9, 4)

    assert voluntary_destination_leaves_melee(runner, [runner, enemy], GridPosition(x=2, y=4)) is True
    assert movement_step_cost_ft(map_definition, runner, GridPosition(x=2, y=4), [runner, enemy]) == 5
    run_plan = plan_movement_toward(map_definition, runner, enemy, [runner, enemy], 40, 60)
    assert run_plan.path == []
    assert runner.state.position == GridPosition(x=4, y=4)

    assert voluntary_destination_leaves_melee(flyer, [flyer, hero_anchor], GridPosition(x=12, y=4)) is True
    assert movement_step_cost_ft(map_definition, flyer, GridPosition(x=12, y=4), [flyer, hero_anchor]) == 5
    fly_plan = plan_movement_toward(map_definition, flyer, hero_anchor, [flyer, hero_anchor], 40, 60)
    assert fly_plan.path == []
    assert flyer.state.position == GridPosition(x=8, y=4)
    assert combatant_is_flying(flyer.state) is True

    closer = _member("closer", "monsters", 0, 4)
    close_plan = plan_movement_toward(
        map_definition, runner, closer, [runner, enemy, closer], 5, 30,
    )
    assert close_plan.path
    assert close_plan.final_distance_ft <= 5
    assert voluntary_destination_leaves_melee(runner, [runner, enemy, closer], close_plan.path[0]) is True
