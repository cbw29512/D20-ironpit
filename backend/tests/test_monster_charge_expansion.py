from app.combat.charge import charge_profile_for_attack_id
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from app.domain.traits import CombatTrait


def _monster(name: str):
    return next(item for item in build_arena_roster().monsters if item.name == name)


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_charge_expansion_reconciles_to_srd_source() -> None:
    for name in ("Minotaur Skeleton", "Triceratops"):
        assert audit_monster_source(_monster(name), _row(name)) == []


def test_minotaur_skeleton_charge_profile_matches_source() -> None:
    monster = _monster("Minotaur Skeleton")
    assert CombatTrait.CHARGE in monster.combat_traits
    assert [attack.id for attack in [monster.weapon_attack, *monster.alternate_weapon_attacks]] == [
        "minotaur-skeleton-gore", "minotaur-skeleton-slam",
    ]
    profile = charge_profile_for_attack_id("minotaur-skeleton-gore")
    assert profile is not None
    assert (profile.minimum_move_ft, profile.dice_count, profile.dice_size) == (20, 2, 8)
    assert profile.damage_type.value == "piercing"
    assert profile.max_target_size.value == "large"


def test_triceratops_charge_and_multiattack_match_source() -> None:
    monster = _monster("Triceratops")
    assert CombatTrait.CHARGE in monster.combat_traits
    assert [slot.attack_ids for slot in monster.attack_action.slots] == [
        ["triceratops-gore"], ["triceratops-gore"],
    ]
    profile = charge_profile_for_attack_id("triceratops-gore")
    assert profile is not None
    assert (profile.minimum_move_ft, profile.dice_count, profile.dice_size) == (20, 2, 8)
    assert profile.damage_type.value == "piercing"
    assert profile.max_target_size.value == "huge"


def test_charge_expansion_is_raw_ready() -> None:
    cards = {card.name: card for card in build_monster_catalog()}
    for name in ("Minotaur Skeleton", "Triceratops"):
        assert cards[name].coverage_status is CoverageStatus.RAW_READY
        assert cards[name].runnable_template_id is not None
        assert cards[name].blockers == []
