from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.models import DamageType
from app.domain.traits import CombatTrait


def _monster(name: str):
    return next(item for item in build_arena_roster().monsters if item.name == name)


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_expansion_four_reconciles_to_srd_source() -> None:
    for name in ("Archelon", "Ankylosaurus", "Giant Eagle", "Giant Elk"):
        assert audit_monster_source(_monster(name), _row(name)) == []


def test_archelon_and_ankylosaurus_multiattacks_are_exact() -> None:
    archelon = _monster("Archelon")
    ankylosaurus = _monster("Ankylosaurus")
    assert (archelon.armor_class, archelon.max_hp, archelon.speed_ft) == (17, 90, 20)
    assert [slot.attack_ids for slot in archelon.attack_action.slots] == [["archelon-bite"], ["archelon-bite"]]
    assert (ankylosaurus.armor_class, ankylosaurus.max_hp, ankylosaurus.speed_ft) == (15, 68, 30)
    assert ankylosaurus.weapon_attack.knocks_prone_max_size.value == "huge"
    assert [slot.attack_ids for slot in ankylosaurus.attack_action.slots] == [["ankylosaurus-tail"], ["ankylosaurus-tail"]]


def test_giant_eagle_and_elk_typed_damage_and_charge_are_exact() -> None:
    eagle = _monster("Giant Eagle")
    elk = _monster("Giant Elk")
    assert (eagle.speed_ft, eagle.weapon_attack.weapon.dice_size) == (80, 4)
    assert eagle.weapon_attack.on_hit_damage[0].damage_type is DamageType.RADIANT
    assert set(eagle.damage_resistances) == {DamageType.NECROTIC, DamageType.RADIANT}
    assert CombatTrait.CHARGE in elk.combat_traits
    assert elk.weapon_attack.weapon.reach_ft == 10
    assert elk.weapon_attack.on_hit_damage[0].damage_type is DamageType.RADIANT
    profile = elk.weapon_attack.charge
    assert profile is not None and profile.bonus_damage is not None
    assert profile.minimum_move_ft == 20
    assert (profile.bonus_damage.dice_count, profile.bonus_damage.dice_size) == (2, 4)
    assert profile.bonus_damage.damage_type is DamageType.BLUDGEONING
    assert profile.max_target_size.value == "huge"
