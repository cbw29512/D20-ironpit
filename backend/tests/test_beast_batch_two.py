from app.content.monsters_beast_batch_two import build_beast_batch_two
from app.domain.models import DamageType
from app.domain.traits import CombatTrait


def _by_id(monster_id: str):
    return next(item for item in build_beast_batch_two() if item.id == monster_id)


def test_second_beast_batch_has_thirteen_unique_templates() -> None:
    monsters = build_beast_batch_two()
    assert len(monsters) == 13
    assert len({monster.id for monster in monsters}) == 13


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


def test_new_beasts_use_only_certified_combat_mechanics() -> None:
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
    assert hyena.weapon_attack.weapon.dice_count == 1
    assert hyena.weapon_attack.weapon.dice_size == 6
