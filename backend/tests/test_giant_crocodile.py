from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster


def _monster():
    return next(item for item in build_arena_roster().monsters if item.name == "Giant Crocodile")


def _row() -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == "Giant Crocodile")


def test_giant_crocodile_reconciles_to_srd_5_2_1() -> None:
    assert audit_monster_source(_monster(), _row()) == []


def test_giant_crocodile_control_multiattack_is_exact() -> None:
    monster = _monster()
    assert (monster.challenge_rating, monster.armor_class, monster.max_hp, monster.speed_ft) == ("5", 14, 85, 30)
    assert monster.initiative_bonus == -1
    bite, tail = monster.weapon_attack, monster.alternate_weapon_attacks[0]
    assert (bite.attack_bonus, bite.weapon.dice_count, bite.weapon.dice_size, bite.damage_bonus) == (8, 3, 10, 5)
    assert bite.control_effect is not None
    assert bite.control_effect.max_target_size.value == "large"
    assert bite.control_effect.grapple_escape_dc == 15
    assert bite.control_effect.restrains_while_grappled is True
    assert (tail.attack_bonus, tail.weapon.dice_count, tail.weapon.dice_size, tail.damage_bonus) == (8, 3, 8, 5)
    assert tail.weapon.reach_ft == 10
    assert tail.knocks_prone_max_size.value == "large"
    assert tail.forbid_target_grappled_by_self is True
    assert [slot.attack_ids for slot in monster.attack_action.slots] == [[bite.id], [tail.id]]
