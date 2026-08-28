from app.main import get_arena_roster
from app.domain.models import ArenaRoster, DamageType


def _by_id(items, item_id: str):
    return next(item for item in items if item.id == item_id)


def test_arena_roster_exposes_certified_batch() -> None:
    roster = get_arena_roster()

    assert isinstance(roster, ArenaRoster)
    assert [item.id for item in roster.characters] == ["aldric-vane-l1", "brom-ironmark-l1"]
    assert [item.id for item in roster.monsters] == [
        "srd-goblin-warrior",
        "srd-bandit",
        "srd-commoner",
        "srd-axe-beak",
        "srd-giant-lizard",
    ]


def test_brom_ironmark_matches_level_one_fighter_loadout() -> None:
    brom = _by_id(get_arena_roster().characters, "brom-ironmark-l1")

    assert brom.level == 1
    assert brom.armor_class == 17
    assert brom.max_hp == 12
    assert brom.fighting_style == "Defense"
    assert len(brom.weapon_masteries) == 3
    assert brom.weapon_attack.attack_bonus == 5
    assert brom.weapon_attack.damage_bonus == 3
    assert brom.weapon_attack.weapon.name == "Greataxe"
    assert brom.weapon_attack.weapon.dice_size == 12
    assert brom.weapon_attack.weapon.mastery_property == "Cleave"
    assert brom.resources[0].id == "second-wind"
    assert brom.resources[0].max_uses == 2


def test_srd_bandit_profile() -> None:
    bandit = _by_id(get_arena_roster().monsters, "srd-bandit")

    assert (bandit.challenge_rating, bandit.armor_class, bandit.max_hp) == ("1/8", 12, 11)
    assert bandit.initiative_bonus == 1
    assert bandit.weapon_attack.weapon.name == "Scimitar"
    assert (bandit.weapon_attack.attack_bonus, bandit.weapon_attack.damage_bonus) == (3, 1)
    crossbow = bandit.alternate_weapon_attacks[0]
    assert crossbow.weapon.name == "Light Crossbow"
    assert (crossbow.weapon.dice_size, crossbow.weapon.normal_range_ft, crossbow.weapon.long_range_ft) == (8, 80, 320)


def test_srd_commoner_profile() -> None:
    commoner = _by_id(get_arena_roster().monsters, "srd-commoner")

    assert (commoner.challenge_rating, commoner.armor_class, commoner.max_hp) == ("0", 10, 4)
    assert commoner.weapon_attack.attack_bonus == 2
    assert commoner.weapon_attack.damage_bonus == 0
    assert commoner.weapon_attack.weapon.dice_size == 4
    assert commoner.weapon_attack.weapon.damage_type is DamageType.BLUDGEONING


def test_srd_axe_beak_profile() -> None:
    axe_beak = _by_id(get_arena_roster().monsters, "srd-axe-beak")

    assert (axe_beak.challenge_rating, axe_beak.armor_class, axe_beak.max_hp) == ("1/4", 11, 19)
    assert axe_beak.speed_ft == 50
    assert (axe_beak.weapon_attack.attack_bonus, axe_beak.weapon_attack.damage_bonus) == (4, 2)
    assert axe_beak.weapon_attack.weapon.dice_size == 8
    assert axe_beak.weapon_attack.weapon.damage_type is DamageType.SLASHING


def test_srd_giant_lizard_profile() -> None:
    lizard = _by_id(get_arena_roster().monsters, "srd-giant-lizard")

    assert (lizard.challenge_rating, lizard.armor_class, lizard.max_hp) == ("1/4", 12, 19)
    assert lizard.speed_ft == 40
    assert (lizard.weapon_attack.attack_bonus, lizard.weapon_attack.damage_bonus) == (4, 2)
    assert lizard.weapon_attack.weapon.dice_size == 8
    assert lizard.weapon_attack.weapon.damage_type is DamageType.PIERCING
