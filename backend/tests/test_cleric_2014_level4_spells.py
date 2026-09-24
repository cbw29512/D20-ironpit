from app.content.cleric_2014_level4_spells import death_ward_2014


def test_2014_death_ward_is_data_bound_to_generic_survival_ward() -> None:
    spell = death_ward_2014()

    assert spell.id == "death-ward"
    assert spell.level == 4
    assert spell.action_cost == "action"
    assert spell.range_ft == 5
    assert spell.duration_minutes == 480
    assert spell.target_policy == "friendly"
    assert spell.concentration is False
    assert spell.survival_ward is not None
    assert spell.survival_ward.replacement_hp == 1
    assert spell.survival_ward.prevents_nondamage_instant_death is True
