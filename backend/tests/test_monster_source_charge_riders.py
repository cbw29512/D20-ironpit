from app.content.monster_source_charge_riders import parse_charge_replacement
from app.domain.size import CreatureSize


def test_movement_gated_prone_charge_is_source_driven() -> None:
    profile = parse_charge_replacement(
        "If the target is a Huge or smaller creature and the beast moved 20+ feet straight toward it "
        "immediately before the hit, the target has the Prone condition."
    )
    assert profile is not None
    assert profile.minimum_move_ft == 20
    assert profile.max_target_size == CreatureSize.HUGE
    assert profile.prone_max_target_size == CreatureSize.HUGE
    assert profile.replacement_damage is None


def test_movement_gated_prone_accepts_srd_comma_before_charge_clause() -> None:
    profile = parse_charge_replacement(
        "If the target is a Medium or smaller creature, and the boar moved 20+ feet straight toward it "
        "immediately before the hit, the target has the Prone condition."
    )
    assert profile is not None
    assert profile.minimum_move_ft == 20
    assert profile.max_target_size == CreatureSize.MEDIUM
    assert profile.prone_max_target_size == CreatureSize.MEDIUM
    assert profile.replacement_damage is None


def test_charge_total_with_same_damage_family_normalizes_to_bonus_delta() -> None:
    profile = parse_charge_replacement(
        " or 7 (2d6 + 1) Piercing damage if the boar moved 20+ feet straight toward the target "
        "immediately before the hit. If the target is a Medium or smaller creature, and the boar moved "
        "20+ feet straight toward it immediately before the hit, the target has the Prone condition.",
        base_dice_count=1,
        base_dice_size=6,
        base_damage_bonus=1,
        base_damage_type="Piercing",
    )
    assert profile is not None
    assert profile.minimum_move_ft == 20
    assert profile.max_target_size == CreatureSize.MEDIUM
    assert profile.prone_max_target_size == CreatureSize.MEDIUM
    assert profile.replacement_damage is None
    assert profile.bonus_damage is not None
    assert profile.bonus_damage.dice_count == 1
    assert profile.bonus_damage.dice_size == 6
    assert profile.bonus_damage.damage_bonus == 0
    assert profile.bonus_damage.damage_type == "piercing"


def test_charge_total_with_different_die_size_remains_replacement_damage() -> None:
    profile = parse_charge_replacement(
        " or 11 (2d8 + 2) Bludgeoning damage if the seahorse moved 20+ feet straight toward the target "
        "immediately before the hit",
        base_dice_count=2,
        base_dice_size=6,
        base_damage_bonus=2,
        base_damage_type="Bludgeoning",
    )
    assert profile is not None
    assert profile.bonus_damage is None
    assert profile.replacement_damage is not None
    assert profile.replacement_damage.dice_count == 2
    assert profile.replacement_damage.dice_size == 8
    assert profile.replacement_damage.damage_bonus == 2
    assert profile.replacement_damage.damage_type == "bludgeoning"