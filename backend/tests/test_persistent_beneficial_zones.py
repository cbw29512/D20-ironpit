from app.domain.grid import GridPosition
from app.domain.persistent_beneficial_zones import (
    PersistentBeneficialZoneAction,
    PersistentBeneficialZoneState,
)


def test_persistent_beneficial_zone_separates_source_data_from_runtime_state() -> None:
    action = PersistentBeneficialZoneAction(
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
