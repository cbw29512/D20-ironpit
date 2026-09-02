import pytest

from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.cleric_combat_levels import (
    CLERIC_COMBAT_LEVELS,
    cleric_arena_ignored,
    cleric_combat_features,
)
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features


def _modifier(score: int) -> int:
    return (score - 10) // 2


def test_cleric_combat_table_covers_every_level_and_official_slot_progression() -> None:
    assert tuple(CLERIC_COMBAT_LEVELS) == tuple(range(1, 21))
    assert CLERIC_COMBAT_LEVELS[1].spell_slots == (2, 0, 0, 0, 0, 0, 0, 0, 0)
    assert CLERIC_COMBAT_LEVELS[9].spell_slots == (4, 3, 3, 3, 1, 0, 0, 0, 0)
    assert CLERIC_COMBAT_LEVELS[20].spell_slots == (4, 3, 3, 3, 3, 2, 2, 1, 1)
    assert (CLERIC_COMBAT_LEVELS[18].channel_divinity_uses, CLERIC_COMBAT_LEVELS[18].divine_spark_dice) == (4, 4)


def test_cleric_table_encodes_one_logical_caster_stat_progression() -> None:
    expected = {
        1: (17, 14),
        4: (19, 14),
        8: (20, 15),
        12: (20, 17),
        16: (20, 19),
        19: (20, 20),
    }
    for level, scores in expected.items():
        row = CLERIC_COMBAT_LEVELS[level]
        assert (row.wisdom, row.charisma) == scores
        assert row.max_hp == 8 + 5 * (level - 1)


def test_cleric_features_only_track_combat_content_and_mending_is_ignored() -> None:
    level_four = set(cleric_combat_features(4))
    assert {"cleric-spellcasting", "divine-spark", "turn-undead", "disciple-of-life", "preserve-life"} <= level_four
    assert "mending" not in level_four
    assert cleric_arena_ignored(20) == ("mending",)
    assert {"supreme-healing", "boon-of-fate", "greater-divine-intervention"} <= set(cleric_combat_features(20))


def test_existing_cleric_runtime_levels_compile_from_table() -> None:
    for level in range(1, 5):
        row = CLERIC_COMBAT_LEVELS[level]
        template = build_seraphine_dawnshield_level(level)
        wisdom_mod = _modifier(row.wisdom)
        charisma_mod = _modifier(row.charisma)
        resources = {item.id: item.max_uses for item in template.resources}

        assert (template.max_hp, template.armor_class) == (row.max_hp, row.armor_class)
        assert template.weapon_attack.attack_bonus == row.proficiency_bonus
        assert template.saving_throw_bonuses["wisdom"] == row.proficiency_bonus + wisdom_mod
        assert template.saving_throw_bonuses["charisma"] == row.proficiency_bonus + charisma_mod
        assert resources.get("channel-divinity", 0) == row.channel_divinity_uses
        assert resources["adrenaline-rush"] == row.proficiency_bonus
        for spell_level, uses in enumerate(row.spell_slots, start=1):
            assert resources.get(f"spell-slot-{spell_level}", 0) == uses


def test_complete_cleric_table_fails_closed_at_first_new_combat_spell_tier() -> None:
    assert unsupported_hero_engine_features(cleric_combat_features(4)) == ()
    assert unsupported_hero_engine_features(cleric_combat_features(5)) == (
        "sear-undead", "cleric-combat-spells-3",
    )
    with pytest.raises(ValueError, match="sear-undead, cleric-combat-spells-3"):
        build_seraphine_dawnshield_level(5)
