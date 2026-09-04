from __future__ import annotations

from app.content.monster_bonus_action_source_audit import bonus_action_issues
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def _row() -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == "Spy")


def _spy():
    return next(monster for monster in build_arena_roster().monsters if monster.name == "Spy")


def test_spy_native_profile_matches_complete_srd_source() -> None:
    spy = _spy()
    row = _row()

    assert spy.id == "srd-spy"
    assert spy.size.value == "medium"
    assert spy.movement_modes.walk_ft == 30
    assert spy.movement_modes.climb_ft == 30
    assert spy.source_bonus_action_names == ["Cunning Action"]
    assert bonus_action_issues(spy, row) == []
    assert audit_monster_source(spy, row) == []


def test_spy_attacks_preserve_poison_damage_and_ranges() -> None:
    attacks = {attack.weapon.name: attack for attack in [_spy().weapon_attack, *_spy().alternate_weapon_attacks]}

    shortsword = attacks["Shortsword"]
    assert shortsword.attack_bonus == 4
    assert shortsword.weapon.reach_ft == 5
    assert [(part.dice_count, part.dice_size, part.damage_type.value) for part in shortsword.on_hit_damage] == [(2, 6, "poison")]

    crossbow = attacks["Hand Crossbow"]
    assert crossbow.attack_bonus == 4
    assert crossbow.weapon.normal_range_ft == 30
    assert crossbow.weapon.long_range_ft == 120
    assert [(part.dice_count, part.dice_size, part.damage_type.value) for part in crossbow.on_hit_damage] == [(2, 6, "poison")]
