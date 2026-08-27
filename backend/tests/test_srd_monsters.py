from app.content.srd_monsters import build_ogre, build_skeleton
from app.domain.models import DamageType, WeaponAttackKind


def test_skeleton_srd_combat_record() -> None:
    skeleton = build_skeleton()

    assert skeleton.challenge_rating == "1/4"
    assert skeleton.armor_class == 14
    assert skeleton.max_hp == 13
    assert skeleton.speed_ft == 30
    assert skeleton.initiative_bonus == 3
    assert skeleton.damage_vulnerabilities == [DamageType.BLUDGEONING]
    assert skeleton.damage_immunities == [DamageType.POISON]
    assert skeleton.weapon_attack.attack_bonus == 5
    assert skeleton.weapon_attack.damage_bonus == 3
    assert skeleton.weapon_attack.weapon.dice_size == 6
    assert skeleton.alternate_weapon_attacks[0].weapon.normal_range_ft == 80
    assert skeleton.alternate_weapon_attacks[0].weapon.long_range_ft == 320


def test_ogre_srd_combat_record() -> None:
    ogre = build_ogre()

    assert ogre.challenge_rating == "2"
    assert ogre.armor_class == 11
    assert ogre.max_hp == 68
    assert ogre.speed_ft == 40
    assert ogre.initiative_bonus == -1
    assert ogre.weapon_attack.attack_bonus == 6
    assert ogre.weapon_attack.damage_dice is not None
    assert (ogre.weapon_attack.damage_dice.dice_count, ogre.weapon_attack.damage_dice.dice_size) == (2, 8)

    javelin = ogre.alternate_weapon_attacks[0]
    assert javelin.attack_bonus == 6
    assert javelin.weapon.attack_kind is WeaponAttackKind.THROWN
    assert javelin.weapon.normal_range_ft == 30
    assert javelin.weapon.long_range_ft == 120
    assert javelin.damage_dice is not None
    assert (javelin.damage_dice.dice_count, javelin.damage_dice.dice_size) == (2, 6)
