from app.content.cleric_2014_level4_spells import death_ward_2014, guardian_of_faith_2014


def test_2014_death_ward_is_data_bound_to_generic_survival_ward() -> None:
    spell = death_ward_2014()

    assert spell.id == "death-ward"
    assert spell.level == 4
    assert spell.action_cost == "action"
    assert spell.range_ft == 5
    assert spell.duration_minutes == 480
    assert spell.target_policy == "friendly"
    assert spell.concentration is False
    assert len(spell.modifier_effects) == 1
    ward = spell.modifier_effects[0]
    assert ward.kind == "zero-hp-replacement"
    assert ward.replacement_hp == 1
    assert ward.prevents_instant_death is True


def test_2014_guardian_of_faith_is_data_bound_to_generic_hazard() -> None:
    action = guardian_of_faith_2014(15)

    assert action.id == "guardian-of-faith"
    assert action.level == 4
    assert action.cast_range_ft == 30
    assert action.duration_rounds == 4800
    assert action.footprint_size.value == "large"
    assert action.trigger_radius_ft == 10
    assert action.save_ability == "dexterity"
    assert action.dc == 15
    assert action.failure_damage == 20
    assert action.success_damage == 10
    assert action.damage_type == "radiant"
    assert action.max_total_damage == 60
