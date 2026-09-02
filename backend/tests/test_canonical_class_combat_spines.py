from app.content.canonical_class_combat_spines import (
    CANONICAL_CLASS_COMBAT_SPINES,
    canonical_class_combat_spine,
)
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.monk_combat_levels import MONK_COMBAT_LEVELS
from app.content.paladin_combat_levels import PALADIN_COMBAT_LEVELS
from app.content.ranger_combat_levels import RANGER_COMBAT_LEVELS
from app.content.rogue_combat_levels import ROGUE_COMBAT_LEVELS
from app.content.sorcerer_combat_levels import SORCERER_COMBAT_LEVELS
from app.content.warlock_combat_levels import WARLOCK_COMBAT_LEVELS
from app.content.wizard_combat_levels import WIZARD_COMBAT_LEVELS


def test_all_twelve_canonical_classes_have_exactly_twenty_contiguous_rows() -> None:
    assert set(CANONICAL_CLASS_COMBAT_SPINES) == set(HERO_BY_CLASS)
    assert len(CANONICAL_CLASS_COMBAT_SPINES) == 12
    for class_id, spine in CANONICAL_CLASS_COMBAT_SPINES.items():
        assert tuple(spine) == tuple(range(1, 21)), class_id
        assert canonical_class_combat_spine(class_id) is spine
        assert all(getattr(row, "level") == level for level, row in spine.items()), class_id


def test_monk_open_hand_numeric_progression_landmarks() -> None:
    assert (MONK_COMBAT_LEVELS[1].martial_arts_die, MONK_COMBAT_LEVELS[1].focus_points) == (6, 0)
    assert (MONK_COMBAT_LEVELS[5].martial_arts_die, MONK_COMBAT_LEVELS[5].focus_points) == (8, 5)
    assert MONK_COMBAT_LEVELS[11].martial_arts_die == 10
    assert (MONK_COMBAT_LEVELS[20].martial_arts_die, MONK_COMBAT_LEVELS[20].focus_points) == (12, 20)
    assert "quivering-palm" in MONK_COMBAT_LEVELS[17].features_added


def test_paladin_devotion_numeric_progression_landmarks() -> None:
    assert PALADIN_COMBAT_LEVELS[1].lay_on_hands_pool == 5
    assert PALADIN_COMBAT_LEVELS[20].lay_on_hands_pool == 100
    assert PALADIN_COMBAT_LEVELS[3].channel_divinity_uses == 2
    assert PALADIN_COMBAT_LEVELS[11].channel_divinity_uses == 3
    assert PALADIN_COMBAT_LEVELS[17].spell_slots == (4, 3, 3, 3, 1)
    assert "faithful-steed" in PALADIN_COMBAT_LEVELS[5].features_added


def test_ranger_hunter_numeric_progression_landmarks() -> None:
    assert RANGER_COMBAT_LEVELS[1].favored_enemy_uses == 2
    assert RANGER_COMBAT_LEVELS[5].favored_enemy_uses == 3
    assert RANGER_COMBAT_LEVELS[17].favored_enemy_uses == 6
    assert RANGER_COMBAT_LEVELS[20].spell_slots == (4, 3, 3, 3, 2)
    assert "hunter-prey-colossus-slayer" in RANGER_COMBAT_LEVELS[3].features_added
    assert "hunter-multiattack-defense" in RANGER_COMBAT_LEVELS[7].features_added


def test_rogue_thief_sneak_attack_progression_landmarks() -> None:
    assert ROGUE_COMBAT_LEVELS[1].sneak_attack_d6 == 1
    assert ROGUE_COMBAT_LEVELS[9].sneak_attack_d6 == 5
    assert ROGUE_COMBAT_LEVELS[20].sneak_attack_d6 == 10
    assert "thiefs-reflexes" in ROGUE_COMBAT_LEVELS[17].features_added


def test_full_caster_and_pact_magic_resource_landmarks() -> None:
    assert SORCERER_COMBAT_LEVELS[20].sorcery_points == 20
    assert SORCERER_COMBAT_LEVELS[20].spell_slots == (4, 3, 3, 3, 3, 2, 2, 1, 1)
    assert WARLOCK_COMBAT_LEVELS[1].pact_slots == 1
    assert (WARLOCK_COMBAT_LEVELS[17].pact_slots, WARLOCK_COMBAT_LEVELS[17].pact_slot_level) == (4, 5)
    assert WIZARD_COMBAT_LEVELS[20].prepared_spells == 25
    assert WIZARD_COMBAT_LEVELS[20].spell_slots == (4, 3, 3, 3, 3, 2, 2, 1, 1)
