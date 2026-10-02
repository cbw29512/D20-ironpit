from app.content.spell_slot_progression import FULL_CASTER_CLASSES, HALF_CASTER_CLASSES, spell_slot_counts, spell_slot_resources


def test_full_caster_slot_progression_matches_2024_milestones() -> None:
    expected = {
        1: {1: 2},
        2: {1: 3},
        3: {1: 4, 2: 2},
        5: {1: 4, 2: 3, 3: 2},
        9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
        17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
        20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
    }
    for class_id in FULL_CASTER_CLASSES:
        for level, slots in expected.items():
            assert spell_slot_counts(class_id, level) == slots


def test_cleric_level_one_resources_use_exact_printed_slot_ids() -> None:
    assert spell_slot_resources("cleric", 1) == {"spell-slot-1": 2}


def test_half_caster_slot_progression_matches_2024_milestones() -> None:
    expected = {
        1: {1: 2},
        2: {1: 2},
        3: {1: 3},
        5: {1: 4, 2: 2},
        9: {1: 4, 2: 3, 3: 2},
        13: {1: 4, 2: 3, 3: 3, 4: 1},
        17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    }
    for class_id in HALF_CASTER_CLASSES:
        for level, slots in expected.items():
            assert spell_slot_counts(class_id, level) == slots


def test_spell_slot_progression_rejects_unaudited_pact_caster() -> None:
    try:
        spell_slot_counts("warlock", 1)
    except ValueError as exc:
        assert "not yet audited" in str(exc)
    else:
        raise AssertionError("warlock should remain fail-closed until its slot model is audited")
