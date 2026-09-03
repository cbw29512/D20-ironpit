from app.content.bard_combat_levels import BARD_COMBAT_LEVELS, bard_arena_ignored, bard_combat_features
from app.content.subclass_combat_overlays import subclass_combat_features, subclass_ignored_ids_for_class


def test_bard_combat_table_covers_every_level_and_official_slot_progression() -> None:
    assert tuple(BARD_COMBAT_LEVELS) == tuple(range(1, 21))
    assert BARD_COMBAT_LEVELS[1].spell_slots == (2, 0, 0, 0, 0, 0, 0, 0, 0)
    assert BARD_COMBAT_LEVELS[10].spell_slots == (4, 3, 3, 3, 2, 0, 0, 0, 0)
    assert BARD_COMBAT_LEVELS[20].spell_slots == (4, 3, 3, 3, 3, 2, 2, 1, 1)
    assert (BARD_COMBAT_LEVELS[5].bardic_die_size, BARD_COMBAT_LEVELS[10].bardic_die_size,
            BARD_COMBAT_LEVELS[15].bardic_die_size) == (8, 10, 12)


def test_bard_uses_simple_caster_array_and_deterministic_mental_advancement() -> None:
    expected = {
        1: (13, 15, 17),
        4: (13, 15, 19),
        8: (13, 16, 20),
        12: (13, 18, 20),
        16: (13, 20, 20),
        19: (14, 20, 20),
    }
    for level, scores in expected.items():
        row = BARD_COMBAT_LEVELS[level]
        assert (row.intelligence, row.wisdom, row.charisma) == scores
        assert row.max_hp == 8 + 5 * (level - 1)
        assert row.armor_class == 12


def test_bard_base_table_and_lore_overlay_keep_only_arena_relevant_features() -> None:
    assert bard_arena_ignored(20) == ("expertise", "jack-of-all-trades", "expertise-2")
    assert "lore-bonus-proficiencies" in subclass_ignored_ids_for_class("bard")
    level_seven = set(bard_combat_features(7))
    assert {"bardic-inspiration", "font-of-inspiration", "countercharm"} <= level_seven
    assert {"cutting-words", "magical-discoveries"} <= set(subclass_combat_features("college-lore", 7))
    level_twenty = set(bard_combat_features(20))
    assert {"superior-inspiration", "boon-spell-recall", "words-of-creation"} <= level_twenty
    assert "peerless-skill" in subclass_combat_features("college-lore", 20)


def test_bardic_inspiration_uses_follow_charisma_modifier() -> None:
    assert BARD_COMBAT_LEVELS[1].bardic_inspiration_uses == 3
    assert BARD_COMBAT_LEVELS[4].bardic_inspiration_uses == 4
    assert BARD_COMBAT_LEVELS[8].bardic_inspiration_uses == 5
    assert BARD_COMBAT_LEVELS[20].bardic_inspiration_uses == 5
