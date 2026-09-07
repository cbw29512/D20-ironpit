from app.content.barbarian_combat_levels import (
    BARBARIAN_COMBAT_LEVELS,
    barbarian_arena_ignored,
    barbarian_combat_features,
)
from app.content.barbarian_progression import (
    build_rokhan_stonefury_level,
    unsupported_barbarian_engine_features,
)


def _modifier(score: int) -> int:
    return (score - 10) // 2


def test_barbarian_combat_table_covers_every_level_exactly_once() -> None:
    assert tuple(BARBARIAN_COMBAT_LEVELS) == tuple(range(1, 21))
    assert (BARBARIAN_COMBAT_LEVELS[1].max_hp, BARBARIAN_COMBAT_LEVELS[7].max_hp) == (14, 75)
    level_twenty = BARBARIAN_COMBAT_LEVELS[20]
    assert (level_twenty.strength, level_twenty.constitution, level_twenty.armor_class, level_twenty.max_hp) == (25, 24, 18, 285)
    assert (level_twenty.rage_uses, level_twenty.rage_damage_bonus) == (6, 4)


def test_barbarian_table_encodes_one_logical_optimized_progression() -> None:
    expected = {
        1: (17, 15),
        4: (18, 16),
        8: (20, 16),
        12: (20, 18),
        16: (20, 20),
        19: (21, 20),
        20: (25, 24),
    }
    for level, scores in expected.items():
        row = BARBARIAN_COMBAT_LEVELS[level]
        assert (row.strength, row.constitution) == scores


def test_barbarian_features_accumulate_while_arena_neutral_movement_is_ignored() -> None:
    level_six = set(barbarian_combat_features(6))
    assert {"rage", "danger-sense", "reckless-attack", "frenzy", "extra-attack", "fast-movement", "mindless-rage"} <= level_six
    assert "primal-knowledge" not in level_six
    assert barbarian_arena_ignored(9) == ("primal-knowledge", "instinctive-pounce", "hamstring-blow")
    level_twenty = set(barbarian_combat_features(20))
    assert "brutal-strike" not in level_twenty
    assert {"brutal-strike-2d10", "retaliation", "relentless-rage", "intimidating-presence",
            "persistent-rage", "indomitable-might", "boon-irresistible-offense", "primal-champion"} <= level_twenty


def test_existing_barbarian_runtime_levels_are_compiled_from_the_table() -> None:
    for level in range(1, 9):
        row = BARBARIAN_COMBAT_LEVELS[level]
        template = build_rokhan_stonefury_level(level)
        strength_mod = _modifier(row.strength)
        constitution_mod = _modifier(row.constitution)
        resources = {item.id: item.max_uses for item in template.resources}

        assert (template.max_hp, template.armor_class, template.speed_ft) == (row.max_hp, row.armor_class, row.speed_ft)
        assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (
            row.proficiency_bonus + strength_mod, strength_mod,
        )
        assert template.saving_throw_bonuses["strength"] == row.proficiency_bonus + strength_mod
        assert template.saving_throw_bonuses["constitution"] == row.proficiency_bonus + constitution_mod
        assert template.skill_bonuses["athletics"] == row.proficiency_bonus + strength_mod
        assert template.weapon_masteries == list(row.weapon_masteries)
        assert resources["rage"] == row.rage_uses
        assert resources["adrenaline-rush"] == row.proficiency_bonus
        assert template.rage_damage_bonus == row.rage_damage_bonus
        assert (len(template.attack_action.slots) if template.attack_action else 1) == row.attack_count


def test_current_barbarian_frontier_blocks_only_on_missing_combat_engine_feature() -> None:
    assert unsupported_barbarian_engine_features(7) == ()
    assert unsupported_barbarian_engine_features(8) == ()
    assert unsupported_barbarian_engine_features(9) == ("brutal-strike",)
    assert BARBARIAN_COMBAT_LEVELS[7].max_hp == 75
    assert build_rokhan_stonefury_level(8).level == 8
