from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.catalog import CoverageStatus
from app.domain.size import CreatureSize


def _hill_giant():
    return next(
        monster for monster in build_legacy_monster_templates()
        if monster.name == "Hill Giant"
    )


def test_hill_giant_source_attacks_and_control_riders() -> None:
    giant = _hill_giant()
    row = next(row for row in load_monster_rows() if row["name"] == "Hill Giant")
    attacks = {
        attack.weapon.name: attack
        for attack in [giant.weapon_attack, *giant.alternate_weapon_attacks]
    }

    tree_club = attacks["Tree Club"]
    trash_lob = attacks["Trash Lob"]

    assert (tree_club.attack_bonus, tree_club.weapon.dice_count, tree_club.weapon.dice_size, tree_club.damage_bonus) == (8, 3, 8, 5)
    assert tree_club.weapon.reach_ft == 10
    assert tree_club.knocks_prone_max_size is CreatureSize.LARGE

    assert (trash_lob.attack_bonus, trash_lob.weapon.dice_count, trash_lob.weapon.dice_size, trash_lob.damage_bonus) == (8, 2, 10, 5)
    assert (trash_lob.weapon.normal_range_ft, trash_lob.weapon.long_range_ft) == (60, 240)
    assert trash_lob.control_effect is not None
    assert trash_lob.control_effect.condition_id == "poisoned"
    assert trash_lob.control_effect.expiry_timing == "target_turn_end"

    assert giant.attack_action is not None
    assert len(giant.attack_action.slots) == 2
    for slot in giant.attack_action.slots:
        assert set(slot.attack_ids) == {tree_club.id, trash_lob.id}

    assert audit_monster_source(giant, row) == []


def test_hill_giant_is_raw_ready() -> None:
    card = next(card for card in build_monster_catalog() if card.name == "Hill Giant")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-hill-giant"
    assert card.blockers == []
