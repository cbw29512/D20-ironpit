from app.combat.persistent_hazards import cast_persistent_hazard, resolve_persistent_hazard_entries
from app.combat.state import build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import ResourceDefinition
from app.domain.persistent_hazards import PersistentHazardAction
from app.domain.size import CreatureSize
from app.combat.dice import FixedDiceProvider


def _member(template, combatant_id: str, side: str, x: int, y: int):
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def test_stationary_hazard_cast_and_first_entry_trigger_are_generic() -> None:
    base = build_seraphine_dawnshield_2014(6)
    caster_template = base.model_copy(update={
        "resources": [
            *base.resources,
            ResourceDefinition(id="spell-slot-4", name="Level 4 Spell Slot", max_uses=1),
        ],
    })
    goblin_template = next(
        item for item in build_arena_roster("2014").monsters
        if item.id == "2014-goblin"
    )
    caster = _member(caster_template, "cleric", "heroes", 2, 6)
    goblin = _member(goblin_template, "goblin", "monsters", 10, 6)
    setup = EncounterSetup(
        heroes=[caster],
        monsters=[goblin],
        hero_total_levels=6,
        monster_total_cr="1/4",
        ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )
    action = PersistentHazardAction(
        id="test-guardian",
        name="Test Guardian",
        level=4,
        cast_range_ft=30,
        duration_rounds=4800,
        footprint_size=CreatureSize.LARGE,
        trigger_radius_ft=10,
        save_ability="dexterity",
        dc=15,
        failure_damage=20,
        success_damage=10,
        damage_type="radiant",
        max_total_damage=60,
    )

    event, sequence = cast_persistent_hazard(
        1, 1, caster, setup, action, GridPosition(x=7, y=6), "1:cleric",
    )
    assert event.feature_id == "test-guardian"
    assert sequence == 2
    assert len(setup.persistent_hazards) == 1

    goblin.state.position = GridPosition(x=9, y=6)
    before = goblin.state.current_hp
    events, sequence = resolve_persistent_hazard_entries(
        sequence, 1, goblin, setup, FixedDiceProvider([1]), "1:goblin",
    )
    assert len(events) == 1
    assert events[0].save_succeeded is False
    assert events[0].damage_roll.total == 20
    assert goblin.state.current_hp == max(0, before - 20)
    assert setup.persistent_hazards[0].remaining_damage_capacity == 40

    again, sequence = resolve_persistent_hazard_entries(
        sequence, 1, goblin, setup, FixedDiceProvider([]), "1:goblin",
    )
    assert again == []


def test_hazard_disappears_after_actual_damage_capacity_is_spent() -> None:
    base = build_seraphine_dawnshield_2014(6)
    caster_template = base.model_copy(update={
        "resources": [
            *base.resources,
            ResourceDefinition(id="spell-slot-4", name="Level 4 Spell Slot", max_uses=1),
        ],
    })
    goblin_template = next(
        item for item in build_arena_roster("2014").monsters
        if item.id == "2014-goblin"
    ).model_copy(update={"max_hp": 100})
    caster = _member(caster_template, "cleric", "heroes", 2, 6)
    goblin = _member(goblin_template, "goblin", "monsters", 10, 6)
    setup = EncounterSetup(
        heroes=[caster], monsters=[goblin], hero_total_levels=6,
        monster_total_cr="1/4", ruleset="2014", map_definition=build_standard_iron_pit_map(),
    )
    action = PersistentHazardAction(
        id="test-guardian", name="Test Guardian", level=4, cast_range_ft=30,
        duration_rounds=4800, footprint_size=CreatureSize.LARGE, trigger_radius_ft=10,
        save_ability="dexterity", dc=15, failure_damage=20, success_damage=10,
        damage_type="radiant", max_total_damage=60,
    )
    _, sequence = cast_persistent_hazard(1, 1, caster, setup, action, GridPosition(x=7, y=6), "1:cleric")
    goblin.state.position = GridPosition(x=9, y=6)
    for round_number in (1, 2, 3):
        _, sequence = resolve_persistent_hazard_entries(
            sequence, round_number, goblin, setup, FixedDiceProvider([1]), f"{round_number}:goblin",
        )
    assert setup.persistent_hazards == []
