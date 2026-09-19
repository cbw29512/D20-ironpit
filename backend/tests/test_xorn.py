from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_saving_throws import with_source_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.catalog import CoverageStatus


def _xorn_template():
    raw = next(template for template in build_zero_engine_monsters() if template.name == "Xorn")
    fingerprinted = complete_monster_trait_fingerprints([raw])[0]
    return with_source_saving_throws(fingerprinted)


def test_xorn_exact_multiattack_and_traits_match_source() -> None:
    xorn = _xorn_template()
    row = next(row for row in load_monster_rows() if row["name"] == "Xorn")

    assert xorn.movement_modes.burrow_ft == 20
    assert xorn.source_trait_names == ["Earth Glide", "Treasure Sense"]
    assert xorn.attack_action is not None

    by_id = {
        attack.id: attack.weapon.name
        for attack in [xorn.weapon_attack, *xorn.alternate_weapon_attacks]
    }
    slot_names = [by_id[slot.attack_ids[0]] for slot in xorn.attack_action.slots]
    assert slot_names == ["Bite", "Claw", "Claw", "Claw"]

    bite = xorn.weapon_attack
    claw = xorn.alternate_weapon_attacks[0]
    assert (bite.attack_bonus, bite.weapon.dice_count, bite.weapon.dice_size, bite.damage_bonus) == (6, 4, 6, 3)
    assert (claw.attack_bonus, claw.weapon.dice_count, claw.weapon.dice_size, claw.damage_bonus) == (6, 1, 10, 3)
    assert audit_monster_source(xorn, row) == []


def test_xorn_is_raw_ready() -> None:
    card = next(card for card in build_monster_catalog() if card.name == "Xorn")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-xorn"
    assert card.blockers == []
