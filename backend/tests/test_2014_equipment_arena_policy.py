from app.content.monster_catalog_2014 import compile_monster_2014, load_catalog_2014, unsupported_mechanics_2014
from app.content.monster_catalog_2014_arena_policy import (
    is_arena_disabled_action_2014,
    is_arena_disabled_attack_detail_2014,
)


def _monster(name: str):
    try:
        return next(monster for monster in load_catalog_2014() if monster.name == name)
    except StopIteration as exc:
        raise AssertionError(f"Missing 2014 monster fixture: {name}") from exc


def test_equipment_only_actions_and_residuals_are_disabled() -> None:
    try:
        assert is_arena_disabled_action_2014("Antennae")
        assert is_arena_disabled_attack_detail_2014(
            "Nonmagical armor worn by the target is partly dissolved and takes a permanent cumulative -1 penalty to AC."
        )
        assert is_arena_disabled_attack_detail_2014(
            "A nonmagical weapon made of metal corrodes and takes a permanent cumulative -1 penalty to damage rolls."
        )
    except Exception as exc:
        raise AssertionError("Equipment-only arena policy classification failed.") from exc


def test_creature_damage_is_never_discarded_with_equipment_damage() -> None:
    try:
        residual = "The target takes 7 acid damage, and its nonmagical armor corrodes."
        assert not is_arena_disabled_attack_detail_2014(residual)
    except Exception as exc:
        raise AssertionError("Creature damage was incorrectly classified as equipment-only.") from exc


def test_rust_monster_equipment_mechanics_no_longer_block() -> None:
    try:
        blockers = unsupported_mechanics_2014(_monster("Rust Monster"))
        assert "action:Antennae" not in blockers
        assert "trait:Iron Scent" not in blockers
        assert "trait:Rust Metal" not in blockers
    except Exception as exc:
        raise AssertionError("Rust Monster still has arena-disabled equipment blockers.") from exc


def test_ooze_equipment_residuals_are_removed_without_losing_creature_reactive_damage() -> None:
    try:
        gray = unsupported_mechanics_2014(_monster("Gray Ooze"))
        black_source = _monster("Black Pudding")
        black = unsupported_mechanics_2014(black_source)
        assert "trait:Corrode Metal" not in gray
        assert "attack-detail:Pseudopod" not in gray
        assert "attack-detail:Pseudopod" not in black
        assert "trait:Corrosive Form" not in black

        compiled = compile_monster_2014(black_source)
        assert any(rule.id == "corrosive-form" for rule in compiled.melee_hit_reactive_damage)
    except Exception as exc:
        raise AssertionError("Ooze equipment policy lost or re-blocked creature-affecting mechanics.") from exc
