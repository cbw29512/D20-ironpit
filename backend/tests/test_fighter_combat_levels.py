import pytest

from app.content.fighter_combat_levels import (
    FIGHTER_COMBAT_LEVELS,
    fighter_arena_ignored,
    fighter_combat_features,
)
from app.content.fighter_progression import (
    build_karnok_stoneward_level,
    unsupported_fighter_engine_features,
)


def _modifier(score: int) -> int:
    return (score - 10) // 2


def test_fighter_combat_table_covers_every_level_exactly_once() -> None:
    assert tuple(FIGHTER_COMBAT_LEVELS) == tuple(range(1, 21))
    assert FIGHTER_COMBAT_LEVELS[1].max_hp == 12
    assert FIGHTER_COMBAT_LEVELS[9].max_hp == 94
    assert FIGHTER_COMBAT_LEVELS[20].max_hp == 224
    assert FIGHTER_COMBAT_LEVELS[20].attack_count == 4
    assert FIGHTER_COMBAT_LEVELS[20].proficiency_bonus == 6


def test_fighter_table_encodes_logical_stat_progression_not_twenty_bespoke_builds() -> None:
    expected = {
        1: (17, 13, 15),
        4: (18, 13, 16),
        6: (20, 13, 16),
        8: (20, 13, 18),
        12: (20, 13, 20),
        14: (20, 15, 20),
        16: (20, 17, 20),
        19: (20, 18, 20),
    }
    for level, scores in expected.items():
        row = FIGHTER_COMBAT_LEVELS[level]
        assert (row.strength, row.dexterity, row.constitution) == scores


def test_fighter_features_accumulate_and_replacements_are_explicit() -> None:
    level_nine = fighter_combat_features(9)
    assert {"action-surge", "extra-attack", "great-weapon-fighting", "indomitable", "tactical-master"} <= set(level_nine)
    assert "tactical-master-sap" not in level_nine
    level_twenty = fighter_combat_features(20)
    assert "improved-critical" not in level_twenty
    assert {"superior-critical", "heroic-warrior", "studied-attacks", "survivor-defy-death",
            "survivor-heroic-rally", "boon-combat-prowess"} <= set(level_twenty)
    assert fighter_arena_ignored(20) == ("tactical-master-push", "tactical-master-slow")


def test_existing_fighter_runtime_levels_are_compiled_from_the_table() -> None:
    for level in range(1, 15):
        row = FIGHTER_COMBAT_LEVELS[level]
        template = build_karnok_stoneward_level(level)
        strength_mod = _modifier(row.strength)
        dexterity_mod = _modifier(row.dexterity)
        constitution_mod = _modifier(row.constitution)
        resources = {item.id: item.max_uses for item in template.resources}

        assert (template.max_hp, template.armor_class, template.initiative_bonus) == (
            row.max_hp, row.armor_class, dexterity_mod,
        )
        assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (
            row.proficiency_bonus + strength_mod, strength_mod,
        )
        assert template.saving_throw_bonuses["strength"] == row.proficiency_bonus + strength_mod
        assert template.saving_throw_bonuses["constitution"] == row.proficiency_bonus + constitution_mod
        assert template.weapon_masteries == list(row.weapon_masteries)
        assert resources["second-wind"] == row.second_wind_uses
        assert resources["adrenaline-rush"] == row.proficiency_bonus
        assert resources.get("action-surge", 0) == row.action_surge_uses
        assert resources.get("indomitable", 0) == row.indomitable_uses
        assert (len(template.attack_action.slots) if template.attack_action else 1) == row.attack_count


def test_complete_table_can_outrun_engine_without_silently_running_unsupported_rules() -> None:
    assert unsupported_fighter_engine_features(9) == ()
    assert unsupported_fighter_engine_features(10) == ()
    assert unsupported_fighter_engine_features(12) == ()
    assert unsupported_fighter_engine_features(13) == ()
    assert unsupported_fighter_engine_features(14) == ()
    assert unsupported_fighter_engine_features(15) == ("superior-critical",)
    assert FIGHTER_COMBAT_LEVELS[13].max_hp == 147
    assert FIGHTER_COMBAT_LEVELS[14].max_hp == 158
    with pytest.raises(ValueError, match="superior-critical"):
        build_karnok_stoneward_level(15)
