from __future__ import annotations

from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.modifier_stack import effective_armor_class, saving_throw_flat_bonus
from app.combat.persistent_beneficial_zone_cast import cast_persistent_beneficial_zone
from app.combat.persistent_beneficial_zone_effects import sync_persistent_beneficial_zones
from app.combat.persistent_beneficial_zone_move import move_persistent_beneficial_zone
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.models import DamageType
from app.domain.persistent_beneficial_zones import (
    PersistentBeneficialZoneAction,
    PersistentBeneficialZoneState,
)

MAP = BattleMapDefinition(id="beneficial-zone-test", width_squares=12, height_squares=12)


def _member(level: int, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_thalen_greenbough_level(level).model_copy(
        update={"id": combatant_id, "name": combatant_id},
    )
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=state,
    )


def _sanctuary_action() -> PersistentBeneficialZoneAction:
    return PersistentBeneficialZoneAction(
        id="test-sanctuary",
        name="Test Sanctuary",
        action_cost="action",
        resource_id="wild-shape",
        resource_cost=1,
        cast_range_ft=120,
        duration_rounds=10,
        shape="cube",
        length_ft=15,
        move_action_cost="bonus_action",
        move_distance_ft=60,
        move_range_ft=120,
        armor_class_bonus=2,
        saving_throw_bonus=2,
        saving_throw_abilities=["dexterity"],
        ally_damage_resistances=["fire"],
        include_source_for_defense=True,
        end_if_source_incapacitated=True,
        end_if_source_dead=True,
    )


def test_persistent_beneficial_zone_separates_source_data_from_runtime_state() -> None:
    action = _sanctuary_action()
    state = PersistentBeneficialZoneState(
        zone_id="druid:test-sanctuary:1",
        source_id="druid",
        source_side="heroes",
        action_id=action.id,
        action_name=action.name,
        position=GridPosition(x=4, y=4),
        applied_round=1,
        expires_round=11,
        length_ft=action.length_ft,
        armor_class_bonus=action.armor_class_bonus,
        saving_throw_bonus=action.saving_throw_bonus,
        saving_throw_abilities=action.saving_throw_abilities,
        ally_damage_resistances=action.ally_damage_resistances,
        include_source_for_defense=action.include_source_for_defense,
        end_if_source_incapacitated=action.end_if_source_incapacitated,
        end_if_source_dead=action.end_if_source_dead,
    )

    assert state.position == GridPosition(x=4, y=4)
    assert state.armor_class_bonus == 2
    assert state.saving_throw_bonus == 2
    assert state.saving_throw_abilities == ["dexterity"]
    assert state.ally_damage_resistances == ["fire"]


def test_zone_cast_spends_resource_and_composes_half_cover_and_ally_resistance() -> None:
    source = _member(14, "source", "heroes", 1, 1)
    ally = _member(9, "ally", "heroes", 2, 2)
    outside = _member(9, "outside", "heroes", 8, 8)
    enemy = _member(9, "enemy", "monsters", 10, 10)
    setup = EncounterSetup(
        heroes=[source, ally, outside],
        monsters=[enemy],
        hero_total_levels=32,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=MAP,
    )
    action = _sanctuary_action()
    wild_shape = next(item for item in source.state.resources if item.id == "wild-shape")

    event, sequence = cast_persistent_beneficial_zone(
        1, 1, source, setup, action, GridPosition(x=1, y=1),
    )

    assert sequence == 2
    assert event.feature_id == action.id
    assert source.state.action_available is False
    assert wild_shape.current_uses == 2
    assert len(setup.persistent_beneficial_zones) == 1

    assert effective_armor_class(source.state) == source.state.template.armor_class + 2
    assert effective_armor_class(ally.state) == ally.state.template.armor_class + 2
    assert effective_armor_class(outside.state) == outside.state.template.armor_class

    assert saving_throw_flat_bonus(source.state, "dexterity") == 2
    assert saving_throw_flat_bonus(ally.state, "dexterity") == 2
    assert saving_throw_flat_bonus(ally.state, "wisdom") == 0
    assert saving_throw_flat_bonus(outside.state, "dexterity") == 0

    assert adjusted_damage_amount(10, DamageType.FIRE, ally.state) == 5
    assert adjusted_damage_amount(10, DamageType.COLD, ally.state) == 10
    assert adjusted_damage_amount(10, DamageType.FIRE, outside.state) == 10


def test_zone_move_recomputes_owned_effects_without_leaking_old_position() -> None:
    source = _member(14, "source", "heroes", 1, 1)
    first = _member(9, "first", "heroes", 2, 2)
    second = _member(9, "second", "heroes", 6, 6)
    enemy = _member(9, "enemy", "monsters", 10, 10)
    setup = EncounterSetup(
        heroes=[source, first, second],
        monsters=[enemy],
        hero_total_levels=32,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=MAP,
    )
    action = _sanctuary_action()
    cast_persistent_beneficial_zone(
        1, 1, source, setup, action, GridPosition(x=1, y=1),
    )
    zone_id = setup.persistent_beneficial_zones[0].zone_id

    event, sequence = move_persistent_beneficial_zone(
        2, 1, source, setup, action, zone_id, GridPosition(x=5, y=5),
    )

    assert sequence == 3
    assert event.feature_id == action.id
    assert source.state.bonus_action_available is False
    assert saving_throw_flat_bonus(first.state, "dexterity") == 0
    assert adjusted_damage_amount(10, DamageType.FIRE, first.state) == 10
    assert saving_throw_flat_bonus(second.state, "dexterity") == 2
    assert adjusted_damage_amount(10, DamageType.FIRE, second.state) == 5


def test_zone_ends_when_source_becomes_incapacitated_and_cleans_owned_effects() -> None:
    source = _member(14, "source", "heroes", 1, 1)
    ally = _member(9, "ally", "heroes", 2, 2)
    enemy = _member(9, "enemy", "monsters", 10, 10)
    setup = EncounterSetup(
        heroes=[source, ally],
        monsters=[enemy],
        hero_total_levels=23,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=MAP,
    )
    action = _sanctuary_action()
    cast_persistent_beneficial_zone(
        1, 1, source, setup, action, GridPosition(x=1, y=1),
    )
    source.state.active_effect_ids.append("stunned")

    sync_persistent_beneficial_zones(setup, 1)

    assert setup.persistent_beneficial_zones == []
    assert saving_throw_flat_bonus(ally.state, "dexterity") == 0
    assert effective_armor_class(ally.state) == ally.state.template.armor_class
    assert adjusted_damage_amount(10, DamageType.FIRE, ally.state) == 10
