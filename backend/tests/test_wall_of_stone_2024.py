from __future__ import annotations

from app.combat.concentration import end_concentration
from app.combat.grid_barriers import barrier_blocks_transition
from app.combat.persistent_barrier_cast import cast_persistent_barrier
from app.combat.persistent_barrier_damage import apply_barrier_section_damage
from app.combat.persistent_barrier_lifecycle import cleanup_persistent_barriers
from app.combat.state import build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_barriers import GridBarrierEdge


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=state,
    )


def _setup() -> tuple[EncounterSetup, EncounterCombatant]:
    caster = _member(build_thalen_greenbough_level(9), "thalen", "heroes", 2, 7)
    target = _member(build_goblin_warrior(), "goblin", "monsters", 20, 7)
    setup = EncounterSetup(
        heroes=[caster],
        monsters=[target],
        hero_total_levels=9,
        monster_total_cr="1/4",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )
    return setup, caster


def _ten_panel_wall() -> list[list[GridBarrierEdge]]:
    """Ten contiguous 10-foot panels along one supported stone-floor boundary."""
    return [
        [
            GridBarrierEdge(
                first=GridPosition(x=x, y=4),
                second=GridPosition(x=x, y=5),
            ),
            GridBarrierEdge(
                first=GridPosition(x=x + 1, y=4),
                second=GridPosition(x=x + 1, y=5),
            ),
        ]
        for x in range(2, 22, 2)
    ]


def test_wall_of_stone_2024_source_data_and_slot_cast_are_exact() -> None:
    setup, caster = _setup()
    action = caster.state.template.persistent_barrier_actions[0]

    assert action.id == "wall-of-stone"
    assert action.level == 5
    assert action.cast_range_ft == 120
    assert action.concentration is True
    assert action.duration_rounds == 100
    assert action.permanent_after_full_duration is True
    assert (action.min_sections, action.max_sections) == (10, 10)
    assert action.sections_must_be_contiguous is True
    assert (action.section_length_ft, action.section_height_ft) == (10, 10)
    assert action.section_thickness_inches == 6
    assert action.armor_class == 15
    assert action.hit_points_per_section == 180
    assert action.damage_immunities == ["poison", "psychic"]
    assert action.required_support_material == "stone"

    event, sequence = cast_persistent_barrier(
        1, 1, caster, setup, action, _ten_panel_wall(), "1:thalen",
    )

    assert sequence == 2
    assert event.feature_id == "wall-of-stone"
    assert event.resource_remaining == 0
    assert len(setup.persistent_barriers) == 1
    barrier = setup.persistent_barriers[0]
    assert len(barrier.sections) == 10
    assert all(section.current_hp == 180 for section in barrier.sections)
    assert caster.state.concentration is not None
    assert caster.state.concentration.effect_id == "wall-of-stone"


def test_wall_section_immunity_and_destruction_reopen_its_edges() -> None:
    setup, caster = _setup()
    action = caster.state.template.persistent_barrier_actions[0]
    cast_persistent_barrier(1, 1, caster, setup, action, _ten_panel_wall(), "1:thalen")
    barrier = setup.persistent_barriers[0]
    section = barrier.sections[0]
    edge = section.edges[0]

    assert barrier_blocks_transition(edge.first, edge.second, setup.persistent_barriers)

    immune = apply_barrier_section_damage(
        setup, barrier.barrier_id, section.section_id, 999, "poison",
    )
    assert immune.immune is True
    assert immune.applied_damage == 0
    assert section.current_hp == 180

    destroyed = apply_barrier_section_damage(
        setup, barrier.barrier_id, section.section_id, 180, "slashing",
    )
    assert destroyed.destroyed is True
    assert destroyed.hp_after == 0
    assert not barrier_blocks_transition(edge.first, edge.second, setup.persistent_barriers)


def test_wall_supports_natural_recovery_drop_and_full_duration_permanence() -> None:
    setup, caster = _setup()
    action = caster.state.template.persistent_barrier_actions[0]
    grant = next(
        item for item in caster.state.template.progression_features.alternate_spell_cast_grants
        if item.spell_id == "wall-of-stone"
    )
    slot = caster.state.resources_by_id["spell-slot-5"]
    free = caster.state.resources_by_id["natural-recovery-free-cast"]

    cast_persistent_barrier(
        1, 1, caster, setup, action, _ten_panel_wall(), "1:thalen",
        alternate_cast=grant,
    )
    assert slot.current_uses == 1
    assert free.current_uses == 0

    end_concentration(
        caster.state,
        [member.state for member in [*setup.heroes, *setup.monsters]],
    )
    assert cleanup_persistent_barriers(setup, 1)
    assert setup.persistent_barriers == []

    setup, caster = _setup()
    action = caster.state.template.persistent_barrier_actions[0]
    cast_persistent_barrier(1, 1, caster, setup, action, _ten_panel_wall(), "1:thalen")
    removed = cleanup_persistent_barriers(setup, 101)

    assert removed == []
    assert len(setup.persistent_barriers) == 1
    assert setup.persistent_barriers[0].concentration is False
    assert setup.persistent_barriers[0].permanent_after_full_duration is False
