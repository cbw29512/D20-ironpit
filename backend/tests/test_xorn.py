from app.content.monster_bonus_action_source_audit import complete_monster_bonus_action_fingerprints
from app.content.monster_catalog import load_monster_rows
from app.content.monster_saving_throws import with_source_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.models import DamageType


def test_xorn_source_profile_and_ordered_multiattack_are_exact() -> None:
    raw = next(template for template in build_zero_engine_monsters() if template.name == "Xorn")
    xorn = with_source_saving_throws(raw)
    xorn = complete_monster_trait_fingerprints([xorn])[0]
    xorn = complete_monster_bonus_action_fingerprints([xorn])[0]

    assert (xorn.armor_class, xorn.max_hp, xorn.speed_ft, xorn.initiative_bonus) == (19, 84, 20, 0)
    assert xorn.weapon_attack.weapon.name == "Bite"
    assert (
        xorn.weapon_attack.attack_bonus,
        xorn.weapon_attack.weapon.dice_count,
        xorn.weapon_attack.weapon.dice_size,
        xorn.weapon_attack.damage_bonus,
        xorn.weapon_attack.weapon.damage_type,
    ) == (6, 4, 6, 3, DamageType.PIERCING)

    claw = next(attack for attack in xorn.alternate_weapon_attacks if attack.weapon.name == "Claw")
    assert (
        claw.attack_bonus,
        claw.weapon.dice_count,
        claw.weapon.dice_size,
        claw.damage_bonus,
        claw.weapon.damage_type,
    ) == (6, 1, 10, 3, DamageType.SLASHING)

    assert xorn.attack_action is not None
    by_id = {attack.id: attack.weapon.name for attack in [xorn.weapon_attack, *xorn.alternate_weapon_attacks]}
    sequence = [by_id[slot.attack_ids[0]] for slot in xorn.attack_action.slots]
    assert sequence == ["Bite", "Claw", "Claw", "Claw"]
    assert all(len(slot.attack_ids) == 1 for slot in xorn.attack_action.slots)

    row = next(row for row in load_monster_rows() if row["name"] == "Xorn")
    assert audit_monster_source(xorn, row) == []
