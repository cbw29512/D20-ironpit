from app.content.monsters_beast_batch_two import build_beast_batch_two
from app.domain.models import DamageType
from app.domain.traits import CombatTrait


def _by_id(monster_id: str):
    return next(item for item in build_beast_batch_two() if item.id == monster_id)


def test_second_beast_batch_has_eighteen_unique_templates() -> None:
    monsters = build_beast_batch_two()
    assert len(monsters) == 18
    assert len({monster.id for monster in monsters}) == 18


def test_polar_bear_multiattack_and_cold_resistance() -> None:
    bear = _by_id("srd-polar-bear")
    assert bear.damage_resistances == [DamageType.COLD]
    assert bear.attack_action is not None
    assert [slot.attack_ids for slot in bear.attack_action.slots] == [
        ["polar-bear-rend"], ["polar-bear-rend"],
    ]


def test_tiger_prone_vulture_pack_and_plesiosaurus_reach() -> None:
    tiger = _by_id("srd-tiger")
    vulture = _by_id("srd-vulture")
    plesiosaurus = _by_id("srd-plesiosaurus")
    assert tiger.weapon_attack.knocks_prone_max_size.value == "large"
    assert vulture.combat_traits == [CombatTrait.PACK_TACTICS]
    assert plesiosaurus.weapon_attack.weapon.reach_ft == 10


def test_first_expansion_uses_only_certified_combat_mechanics() -> None:
    beetle = _by_id("srd-giant-fire-beetle")
    goat = _by_id("srd-giant-goat")
    owl = _by_id("srd-giant-owl")
    hyena = _by_id("srd-hyena")

    assert beetle.weapon_attack.fixed_damage == 1
    assert beetle.weapon_attack.weapon.damage_type is DamageType.FIRE
    assert beetle.damage_resistances == [DamageType.FIRE]
    assert goat.combat_traits == [CombatTrait.CHARGE]
    assert goat.weapon_attack.id == "giant-goat-ram"
    assert owl.damage_resistances == [DamageType.NECROTIC, DamageType.RADIANT]
    assert owl.weapon_attack.weapon.dice_size == 10
    assert hyena.combat_traits == [CombatTrait.PACK_TACTICS]


def test_fifty_monster_expansion_matches_srd_attack_profiles() -> None:
    bat = _by_id("srd-giant-bat")
    mastiff = _by_id("srd-mastiff")
    mule = _by_id("srd-mule")
    rhino = _by_id("srd-rhinoceros")
    warhorse = _by_id("srd-warhorse")

    assert (bat.armor_class, bat.max_hp, bat.speed_ft, bat.initiative_bonus) == (13, 22, 60, 3)
    assert (bat.weapon_attack.attack_bonus, bat.weapon_attack.weapon.dice_size, bat.weapon_attack.damage_bonus) == (5, 6, 3)
    assert mastiff.weapon_attack.knocks_prone_max_size.value == "medium"
    assert (mastiff.weapon_attack.attack_bonus, mastiff.weapon_attack.damage_bonus) == (3, 1)
    assert (mule.weapon_attack.attack_bonus, mule.weapon_attack.weapon.dice_size, mule.weapon_attack.damage_bonus) == (4, 4, 2)
    assert rhino.combat_traits == [CombatTrait.CHARGE]
    assert (rhino.weapon_attack.attack_bonus, rhino.weapon_attack.weapon.dice_count, rhino.weapon_attack.weapon.dice_size, rhino.weapon_attack.damage_bonus) == (7, 2, 8, 5)
    assert warhorse.combat_traits == [CombatTrait.CHARGE]
    assert (warhorse.weapon_attack.attack_bonus, warhorse.weapon_attack.weapon.dice_count, warhorse.weapon_attack.weapon.dice_size, warhorse.weapon_attack.damage_bonus) == (6, 2, 4, 4)
