from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn
from app.content.monsters_batch_three import build_monster_batch_three
from app.domain.models import EncounterSelection, WeaponAttackKind
from app.domain.traits import CombatTrait


def _by_id(monster_id: str):
    return next(item for item in build_monster_batch_three() if item.id == monster_id)


def test_batch_three_has_five_unique_templates() -> None:
    monsters = build_monster_batch_three()
    assert len(monsters) == 5
    assert len({monster.id for monster in monsters}) == 5


def test_ogre_has_greatclub_and_both_javelin_attack_modes() -> None:
    ogre = _by_id("srd-ogre")
    assert (ogre.armor_class, ogre.max_hp, ogre.speed_ft, ogre.initiative_bonus) == (11, 68, 40, -1)
    assert (ogre.weapon_attack.attack_bonus, ogre.weapon_attack.weapon.dice_count, ogre.weapon_attack.weapon.dice_size, ogre.weapon_attack.damage_bonus) == (6, 2, 8, 4)
    assert [attack.id for attack in ogre.alternate_weapon_attacks] == ["ogre-javelin-melee", "ogre-javelin"]
    melee_javelin, ranged_javelin = ogre.alternate_weapon_attacks
    assert melee_javelin.weapon.attack_kind is WeaponAttackKind.MELEE
    assert (melee_javelin.weapon.reach_ft, melee_javelin.attack_bonus, melee_javelin.weapon.dice_count, melee_javelin.weapon.dice_size, melee_javelin.damage_bonus) == (5, 6, 2, 6, 4)
    assert ranged_javelin.weapon.attack_kind is WeaponAttackKind.RANGED
    assert (ranged_javelin.attack_bonus, ranged_javelin.weapon.dice_count, ranged_javelin.weapon.dice_size, ranged_javelin.damage_bonus) == (6, 2, 6, 4)
    assert (ranged_javelin.weapon.normal_range_ft, ranged_javelin.weapon.long_range_ft) == (30, 120)


def test_owlbear_and_saber_tiger_make_two_rend_attacks() -> None:
    owlbear = _by_id("srd-owlbear")
    saber = _by_id("srd-saber-toothed-tiger")
    assert (owlbear.armor_class, owlbear.max_hp, owlbear.weapon_attack.attack_bonus) == (13, 59, 7)
    assert (owlbear.weapon_attack.weapon.dice_count, owlbear.weapon_attack.weapon.dice_size, owlbear.weapon_attack.damage_bonus) == (2, 8, 5)
    assert [slot.attack_ids for slot in owlbear.attack_action.slots] == [["owlbear-rend"], ["owlbear-rend"]]
    assert (saber.armor_class, saber.max_hp, saber.weapon_attack.attack_bonus) == (13, 52, 6)
    assert (saber.weapon_attack.weapon.dice_count, saber.weapon_attack.weapon.dice_size, saber.weapon_attack.damage_bonus) == (2, 6, 4)
    assert [slot.attack_ids for slot in saber.attack_action.slots] == [["saber-toothed-tiger-rend"], ["saber-toothed-tiger-rend"]]


def test_scout_and_infantry_match_srd_weapon_options() -> None:
    scout = _by_id("srd-scout")
    infantry = _by_id("srd-warrior-infantry")
    assert scout.weapon_attack.id == "scout-longbow"
    assert (scout.weapon_attack.weapon.normal_range_ft, scout.weapon_attack.weapon.long_range_ft) == (150, 600)
    assert scout.alternate_weapon_attacks[0].id == "scout-shortsword"
    assert [slot.attack_ids for slot in scout.attack_action.slots] == [
        ["scout-longbow", "scout-shortsword"],
        ["scout-longbow", "scout-shortsword"],
    ]
    assert infantry.combat_traits == [CombatTrait.PACK_TACTICS]
    assert infantry.weapon_attack.id == "warrior-infantry-spear-melee"
    assert (infantry.alternate_weapon_attacks[0].weapon.normal_range_ft, infantry.alternate_weapon_attacks[0].weapon.long_range_ft) == (20, 60)


def _scout_attack_ids(distance_ft: int) -> list[str]:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1"], monster_ids=["srd-scout"],
    ))
    hero, scout = setup.heroes[0], setup.monsters[0]
    hero.position_ft = 0
    scout.position_ft = distance_ft
    begin_turn(scout.state)
    events, _ = resolve_attack_action(1, 1, scout, setup, FixedDiceProvider([10, 4, 10, 4]))
    return [event.weapon_id for event in events if event.event_type == "attack"]


def test_scout_fires_at_range_and_switches_to_melee_when_engaged() -> None:
    assert _scout_attack_ids(30) == ["scout-longbow", "scout-longbow"]
    assert _scout_attack_ids(5) == ["scout-shortsword", "scout-shortsword"]
