from app.content.fighter_combat_levels import (
    FIGHTER_COMBAT_LEVELS,
    fighter_arena_ignored,
    fighter_combat_features,
)
from app.content.fighter_progression import (
    build_karnok_stoneward_level,
    unsupported_fighter_engine_features,
)
from app.content.canonical_class_combat_spines import canonical_combat_features


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
    assert {"action-surge", "extra-attack", "indomitable", "tactical-master"} <= set(level_nine)
    assert "great-weapon-fighting" not in level_nine
    assert "great-weapon-fighting" in canonical_combat_features("fighter", 9, "champion")
    assert "tactical-master-sap" not in level_nine
    level_twenty = fighter_combat_features(20)
    assert {"improved-critical", "superior-critical", "heroic-warrior",
            "survivor-defy-death", "survivor-heroic-rally"}.isdisjoint(level_twenty)
    assert {"studied-attacks", "boon-combat-prowess"} <= set(level_twenty)
    champion_twenty = canonical_combat_features("fighter", 20, "champion")
    assert {"superior-critical", "heroic-warrior", "survivor-defy-death",
            "survivor-heroic-rally"} <= set(champion_twenty)
    assert fighter_arena_ignored(20) == ("tactical-master-push", "tactical-master-slow")


def test_fighter_runtime_levels_are_compiled_from_the_table() -> None:
    for level in range(1, 21):
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


def test_complete_fighter_table_is_supported_without_silent_feature_gaps() -> None:
    for level in range(1, 21):
        assert unsupported_fighter_engine_features(level) == ()
        assert build_karnok_stoneward_level(level).level == level
