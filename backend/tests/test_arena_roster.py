from app.main import get_arena_roster
from app.content.capability_registry import load_capability_definitions
from app.content.certified_heroes import build_certified_hero_templates
from app.content.pregens import build_brom_ironmark, build_mara_quickstep, build_selene_asharrow
from app.domain.models import ArenaRoster, WeaponAttackKind


def _by_id(items, item_id: str):
    return next(item for item in items if item.id == item_id)


def test_arena_roster_matches_merged_capability_registry() -> None:
    roster = get_arena_roster()
    assert isinstance(roster, ArenaRoster)
    assert [item.id for item in roster.characters] == [item.id for item in build_certified_hero_templates()]

    expected_monster_ids = [
        definition.id
        for definition in load_capability_definitions().values()
        if definition.kind == "monster"
    ]
    actual_monster_ids = [item.id for item in roster.monsters]
    assert actual_monster_ids == expected_monster_ids
    assert len(actual_monster_ids) == len(set(actual_monster_ids))


def test_brom_ironmark_matches_level_one_fighter_loadout() -> None:
    brom = build_brom_ironmark()
    assert (brom.level, brom.armor_class, brom.max_hp) == (1, 17, 12)
    assert brom.fighting_style == "Defense"
    assert len(brom.weapon_masteries) == 3
    assert (brom.weapon_attack.attack_bonus, brom.weapon_attack.damage_bonus) == (5, 3)
    assert brom.weapon_attack.weapon.name == "Greataxe"
    assert brom.weapon_attack.weapon.dice_size == 12
    assert brom.weapon_attack.weapon.mastery_property == "Cleave"
    assert brom.resources[0].max_uses == 2


def test_selene_asharrow_matches_archery_fighter_loadout() -> None:
    selene = build_selene_asharrow()
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
    mara = build_mara_quickstep()
    assert (mara.level, mara.armor_class, mara.max_hp) == (1, 14, 10)
    assert mara.archetype == "Rogue"
    assert mara.initiative_bonus == 3
    assert len(mara.weapon_masteries) == 2
    assert mara.weapon_attack.weapon.name == "Shortsword"
    assert mara.alternate_weapon_attacks[0].weapon.name == "Shortbow"
    assert (mara.weapon_attack.attack_bonus, mara.weapon_attack.damage_bonus) == (5, 3)
    assert mara.progression_features.sneak_attack_d6 == 1
    assert mara.weapon_attack.sneak_attack_eligible is True
    assert mara.alternate_weapon_attacks[0].sneak_attack_eligible is True
    assert not mara.weapon_attack.conditional_damage


def test_tyrannosaurus_rex_keeps_multiattack_target_restriction() -> None:
    rex = _by_id(get_arena_roster().monsters, "srd-tyrannosaurus-rex")
    bite, tail = rex.weapon_attack, rex.alternate_weapon_attacks[0]
    assert bite.control_effect is not None and bite.control_effect.restrains_while_grappled
    assert tail.forbid_target_grappled_by_self is True
    assert rex.attack_action is not None
    assert [slot.attack_ids for slot in rex.attack_action.slots] == [[bite.id], [tail.id]]
