from app.main import get_arena_roster
from app.domain.models import ArenaRoster, DamageType, WeaponAttackKind
from app.domain.traits import CombatTrait


def _by_id(items, item_id: str):
    return next(item for item in items if item.id == item_id)


def test_arena_roster_exposes_certified_batch() -> None:
    roster = get_arena_roster()

    assert isinstance(roster, ArenaRoster)
    assert [item.id for item in roster.characters] == [
        "karnok-stoneward-l1", "rokhan-stonefury-l1", "aldric-vane-l1",
        "brom-ironmark-l1", "selene-asharrow-l1", "mara-quickstep-l1",
    ]
    assert [item.id for item in roster.monsters] == [
        "srd-goblin-warrior", "srd-goblin-minion", "srd-hobgoblin-warrior", "srd-kobold-warrior",
        "srd-bandit", "srd-commoner", "srd-guard", "srd-giant-rat", "srd-giant-weasel",
        "srd-axe-beak", "srd-giant-lizard", "srd-wolf", "srd-dire-wolf", "srd-black-bear",
        "srd-brown-bear", "srd-baboon", "srd-camel", "srd-deer", "srd-draft-horse",
        "srd-giant-badger", "srd-jackal", "srd-boar", "srd-elk", "srd-giant-boar", "srd-hippogriff",
        "srd-awakened-shrub", "srd-badger", "srd-bat", "srd-cat", "srd-crab", "srd-frog",
        "srd-hawk", "srd-lizard", "srd-owl", "srd-rat", "srd-raven", "srd-weasel",
        "srd-eagle", "srd-panther", "srd-plesiosaurus", "srd-polar-bear", "srd-pony",
        "srd-pteranodon", "srd-riding-horse", "srd-tiger", "srd-vulture",
        "srd-giant-fire-beetle", "srd-giant-goat", "srd-giant-owl", "srd-hyena",
        "srd-giant-bat", "srd-mastiff", "srd-mule", "srd-rhinoceros", "srd-warhorse",
        "srd-ogre", "srd-owlbear", "srd-saber-toothed-tiger", "srd-scout", "srd-warrior-infantry",
        "srd-crocodile", "srd-giant-crab", "srd-constrictor-snake", "srd-giant-centipede",
        "srd-giant-venomous-snake", "srd-giant-wasp", "srd-giant-wolf-spider",
        "srd-archelon", "srd-ankylosaurus", "srd-giant-eagle", "srd-giant-elk", "srd-giant-crocodile",
        "srd-giant-constrictor-snake", "srd-tyrannosaurus-rex",
        "srd-animated-armor", "srd-animated-flying-sword", "srd-flying-snake", "srd-hippopotamus",
        "srd-killer-whale", "srd-manticore", "srd-pegasus", "srd-scorpion", "srd-skeleton", "srd-spider",
        "srd-tough", "srd-venomous-snake",
    ]


def test_brom_ironmark_matches_level_one_fighter_loadout() -> None:
    brom = _by_id(get_arena_roster().characters, "brom-ironmark-l1")
    assert (brom.level, brom.armor_class, brom.max_hp) == (1, 17, 12)
    assert brom.fighting_style == "Defense"
    assert len(brom.weapon_masteries) == 3
    assert (brom.weapon_attack.attack_bonus, brom.weapon_attack.damage_bonus) == (5, 3)
    assert brom.weapon_attack.weapon.name == "Greataxe"
    assert brom.weapon_attack.weapon.dice_size == 12
    assert brom.weapon_attack.weapon.mastery_property == "Cleave"
    assert brom.resources[0].max_uses == 2


def test_selene_asharrow_matches_archery_fighter_loadout() -> None:
    selene = _by_id(get_arena_roster().characters, "selene-asharrow-l1")
    assert (selene.level, selene.armor_class, selene.max_hp) == (1, 16, 12)
    assert selene.initiative_bonus == 3
    assert selene.fighting_style == "Archery"
    assert len(selene.weapon_masteries) == 3
    attack = selene.weapon_attack
    assert (attack.attack_bonus, attack.damage_bonus) == (7, 3)
    assert attack.weapon.name == "Longbow"
    assert attack.weapon.attack_kind is WeaponAttackKind.RANGED
    assert (attack.weapon.dice_size, attack.weapon.normal_range_ft, attack.weapon.long_range_ft) == (8, 150, 600)


def test_mara_quickstep_matches_level_one_rogue_loadout() -> None:
    mara = _by_id(get_arena_roster().characters, "mara-quickstep-l1")
    assert (mara.level, mara.armor_class, mara.max_hp) == (1, 14, 10)
    assert mara.archetype == "Rogue"
    assert mara.initiative_bonus == 3
    assert len(mara.weapon_masteries) == 2
    assert mara.weapon_attack.weapon.name == "Shortsword"
    assert mara.alternate_weapon_attacks[0].weapon.name == "Shortbow"
    assert (mara.weapon_attack.attack_bonus, mara.weapon_attack.damage_bonus) == (5, 3)
    assert mara.weapon_attack.conditional_damage[0].dice_size == 6
    assert mara.weapon_attack.conditional_damage[0].trigger == "attack_advantage"


def test_srd_bandit_profile() -> None:
    bandit = _by_id(get_arena_roster().monsters, "srd-bandit")
    assert (bandit.challenge_rating, bandit.armor_class, bandit.max_hp) == ("1/8", 12, 11)
    assert bandit.initiative_bonus == 1
    assert (bandit.weapon_attack.attack_bonus, bandit.weapon_attack.damage_bonus) == (3, 1)
    crossbow = bandit.alternate_weapon_attacks[0]
    assert (crossbow.weapon.dice_size, crossbow.weapon.normal_range_ft, crossbow.weapon.long_range_ft) == (8, 80, 320)


def test_srd_commoner_profile() -> None:
    commoner = _by_id(get_arena_roster().monsters, "srd-commoner")
    assert (commoner.challenge_rating, commoner.armor_class, commoner.max_hp) == ("0", 10, 4)
    assert (commoner.weapon_attack.attack_bonus, commoner.weapon_attack.damage_bonus) == (2, 0)
    assert commoner.weapon_attack.weapon.dice_size == 4
    assert commoner.weapon_attack.weapon.damage_type is DamageType.BLUDGEONING


def test_srd_guard_profile() -> None:
    guard = _by_id(get_arena_roster().monsters, "srd-guard")
    assert (guard.challenge_rating, guard.armor_class, guard.max_hp) == ("1/8", 16, 11)
    assert guard.initiative_bonus == 1
    melee = guard.weapon_attack
    thrown = guard.alternate_weapon_attacks[0]
    assert (melee.attack_bonus, melee.damage_bonus, melee.weapon.dice_size) == (3, 1, 6)
    assert melee.weapon.attack_kind is WeaponAttackKind.MELEE
    assert thrown.weapon.attack_kind is WeaponAttackKind.RANGED
    assert (thrown.weapon.normal_range_ft, thrown.weapon.long_range_ft) == (20, 60)


def test_srd_giant_rat_profile() -> None:
    rat = _by_id(get_arena_roster().monsters, "srd-giant-rat")
    assert (rat.challenge_rating, rat.armor_class, rat.max_hp) == ("1/8", 13, 7)
    assert (rat.size.value, rat.speed_ft, rat.initiative_bonus) == ("small", 30, 3)
    assert (rat.weapon_attack.attack_bonus, rat.weapon_attack.damage_bonus) == (5, 3)
    assert rat.weapon_attack.weapon.dice_size == 4


def test_srd_giant_weasel_profile() -> None:
    weasel = _by_id(get_arena_roster().monsters, "srd-giant-weasel")
    assert (weasel.challenge_rating, weasel.armor_class, weasel.max_hp) == ("1/8", 13, 9)
    assert (weasel.speed_ft, weasel.initiative_bonus) == (40, 3)
    assert (weasel.weapon_attack.attack_bonus, weasel.weapon_attack.damage_bonus) == (5, 3)
    assert weasel.weapon_attack.weapon.dice_size == 4


def test_srd_axe_beak_profile() -> None:
    axe_beak = _by_id(get_arena_roster().monsters, "srd-axe-beak")
    assert (axe_beak.challenge_rating, axe_beak.armor_class, axe_beak.max_hp) == ("1/4", 11, 19)
    assert (axe_beak.size.value, axe_beak.speed_ft, axe_beak.initiative_bonus) == ("large", 50, 1)
    assert (axe_beak.weapon_attack.attack_bonus, axe_beak.weapon_attack.damage_bonus) == (4, 2)
    assert axe_beak.weapon_attack.weapon.dice_size == 8
    assert axe_beak.weapon_attack.weapon.damage_type is DamageType.SLASHING


def test_srd_giant_lizard_profile() -> None:
    lizard = _by_id(get_arena_roster().monsters, "srd-giant-lizard")
    assert (lizard.challenge_rating, lizard.armor_class, lizard.max_hp) == ("1/4", 12, 19)
    assert (lizard.size.value, lizard.speed_ft) == ("large", 40)
    assert (lizard.weapon_attack.attack_bonus, lizard.weapon_attack.damage_bonus) == (4, 2)
    assert lizard.weapon_attack.weapon.dice_size == 8
    assert lizard.weapon_attack.weapon.damage_type is DamageType.PIERCING


def test_srd_black_bear_profile_and_multiattack() -> None:
    bear = _by_id(get_arena_roster().monsters, "srd-black-bear")
    assert (bear.challenge_rating, bear.armor_class, bear.max_hp) == ("1/2", 11, 19)
    assert (bear.speed_ft, bear.initiative_bonus) == (30, 1)
    assert (bear.weapon_attack.attack_bonus, bear.weapon_attack.damage_bonus) == (4, 2)
    assert (bear.weapon_attack.weapon.dice_size, bear.weapon_attack.weapon.damage_type) == (6, DamageType.SLASHING)
    assert bear.attack_action is not None
    assert [slot.attack_ids for slot in bear.attack_action.slots] == [["black-bear-rend"], ["black-bear-rend"]]


def test_srd_brown_bear_profile_multiattack_and_prone_claw() -> None:
    bear = _by_id(get_arena_roster().monsters, "srd-brown-bear")
    assert (bear.challenge_rating, bear.armor_class, bear.max_hp) == ("1", 11, 22)
    assert (bear.speed_ft, bear.initiative_bonus) == (40, 1)
    bite = bear.weapon_attack
    claw = bear.alternate_weapon_attacks[0]
    assert (bite.attack_bonus, bite.damage_bonus, bite.weapon.dice_size) == (5, 3, 8)
    assert (claw.attack_bonus, claw.damage_bonus, claw.weapon.dice_size) == (5, 3, 4)
    assert claw.knocks_prone_max_size.value == "large"
    assert bear.attack_action is not None
    assert [slot.attack_ids for slot in bear.attack_action.slots] == [["brown-bear-bite"], ["brown-bear-claw"]]


def test_charge_beast_stat_blocks() -> None:
    boar = _by_id(get_arena_roster().monsters, "srd-boar")
    elk = _by_id(get_arena_roster().monsters, "srd-elk")
    giant_boar = _by_id(get_arena_roster().monsters, "srd-giant-boar")
    assert (boar.armor_class, boar.max_hp, boar.speed_ft) == (11, 13, 40)
    assert (boar.weapon_attack.attack_bonus, boar.weapon_attack.weapon.dice_size, boar.weapon_attack.damage_bonus) == (3, 6, 1)
    assert (elk.armor_class, elk.max_hp, elk.speed_ft) == (10, 11, 50)
    assert (elk.weapon_attack.attack_bonus, elk.weapon_attack.weapon.dice_size, elk.weapon_attack.damage_bonus) == (5, 6, 3)
    assert (giant_boar.armor_class, giant_boar.max_hp, giant_boar.speed_ft) == (13, 42, 40)
    assert (giant_boar.weapon_attack.attack_bonus, giant_boar.weapon_attack.weapon.dice_count, giant_boar.weapon_attack.damage_bonus) == (5, 2, 3)


def test_humanoid_expansion_matches_srd_profiles() -> None:
    monsters = get_arena_roster().monsters
    goblin = _by_id(monsters, "srd-goblin-minion")
    kobold = _by_id(monsters, "srd-kobold-warrior")
    hobgoblin = _by_id(monsters, "srd-hobgoblin-warrior")

    assert (goblin.size.value, goblin.armor_class, goblin.max_hp, goblin.initiative_bonus) == ("small", 12, 7, 2)
    assert goblin.alternate_weapon_attacks[0].weapon.normal_range_ft == 20
    assert CombatTrait.PACK_TACTICS in kobold.combat_traits
    assert (kobold.size.value, kobold.armor_class, kobold.max_hp) == ("small", 14, 7)
    assert CombatTrait.PACK_TACTICS in hobgoblin.combat_traits
    assert (hobgoblin.armor_class, hobgoblin.max_hp, hobgoblin.initiative_bonus) == (18, 11, 3)
    poison = hobgoblin.alternate_weapon_attacks[0].on_hit_damage[0]
    assert (poison.dice_count, poison.dice_size, poison.damage_type) == (3, 4, DamageType.POISON)


def test_hippogriff_matches_srd_multiattack_and_arena_flight_speed() -> None:
    hippogriff = _by_id(get_arena_roster().monsters, "srd-hippogriff")
    assert (hippogriff.size.value, hippogriff.armor_class, hippogriff.max_hp) == ("large", 11, 26)
    assert (hippogriff.speed_ft, hippogriff.initiative_bonus) == (60, 1)
    assert (hippogriff.weapon_attack.attack_bonus, hippogriff.weapon_attack.weapon.dice_size) == (5, 8)
    assert hippogriff.attack_action is not None
    assert [slot.attack_ids for slot in hippogriff.attack_action.slots] == [["hippogriff-rend"], ["hippogriff-rend"]]


def test_tyrannosaurus_rex_matches_srd_and_tail_target_restriction() -> None:
    rex = _by_id(get_arena_roster().monsters, "srd-tyrannosaurus-rex")
    assert (rex.challenge_rating, rex.size.value, rex.armor_class, rex.max_hp) == ("8", "huge", 13, 136)
    assert (rex.speed_ft, rex.initiative_bonus) == (50, 3)
    bite, tail = rex.weapon_attack, rex.alternate_weapon_attacks[0]
    assert (bite.attack_bonus, bite.weapon.dice_count, bite.weapon.dice_size, bite.damage_bonus) == (10, 4, 12, 7)
    assert bite.control_effect is not None and bite.control_effect.restrains_while_grappled
    assert (tail.attack_bonus, tail.weapon.dice_count, tail.weapon.dice_size, tail.damage_bonus) == (10, 4, 8, 7)
    assert tail.knocks_prone_max_size.value == "huge"
    assert tail.forbid_target_grappled_by_self is True
    assert rex.attack_action is not None
    assert [slot.attack_ids for slot in rex.attack_action.slots] == [[bite.id], [tail.id]]
