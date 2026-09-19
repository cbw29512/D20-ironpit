import logging

from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_spellcasting_source_audit import spellcasting_issues
from app.domain.catalog import CoverageStatus

logger = logging.getLogger(__name__)


def _druid():
    return next(monster for monster in build_legacy_monster_templates() if monster.name == "Druid")


def _row():
    return next(row for row in load_monster_rows() if row["name"] == "Druid")


def test_druid_source_attacks_and_multiattack_are_exact() -> None:
    try:
        druid = _druid()
        attacks = [druid.weapon_attack, *druid.alternate_weapon_attacks]
        by_name = {attack.weapon.name: attack for attack in attacks}

        staff = by_name["Vine Staff"]
        assert (staff.attack_bonus, staff.weapon.dice_count, staff.weapon.dice_size, staff.damage_bonus) == (5, 1, 8, 3)
        assert staff.weapon.damage_type.value == "bludgeoning"
        assert len(staff.on_hit_damage) == 1
        assert (staff.on_hit_damage[0].dice_count, staff.on_hit_damage[0].dice_size) == (1, 4)
        assert staff.on_hit_damage[0].damage_type.value == "poison"

        wisp = by_name["Verdant Wisp"]
        assert (wisp.attack_bonus, wisp.weapon.dice_count, wisp.weapon.dice_size, wisp.damage_bonus) == (5, 3, 6, 0)
        assert wisp.weapon.damage_type.value == "radiant"
        assert (wisp.weapon.normal_range_ft, wisp.weapon.long_range_ft) == (90, 90)

        assert druid.attack_action is not None
        ids = {attack.id: attack.weapon.name for attack in attacks}
        assert [
            [ids[attack_id] for attack_id in slot.attack_ids]
            for slot in druid.attack_action.slots
        ] == [
            ["Vine Staff", "Verdant Wisp"],
            ["Vine Staff", "Verdant Wisp"],
        ]
    except Exception:
        logger.exception("Druid source attack regression failed.")
        raise


def test_druid_arena_spell_package_preserves_use_budget() -> None:
    try:
        druid = _druid()
        assert druid.source_spellcasting_fingerprint is not None
        assert druid.spell_attack_actions == []
        assert [spell.id for spell in druid.spell_save_actions] == [
            "inflict-wounds-l1-arena",
            "inflict-wounds-l2-arena",
        ]
        assert [spell.id for spell in druid.defensive_spell_actions] == ["longstrider"]

        level_one_sub = druid.spell_save_actions[0]
        assert (
            level_one_sub.level,
            level_one_sub.save_ability,
            level_one_sub.dc,
            level_one_sub.range_ft,
            level_one_sub.damage_dice_count,
            level_one_sub.damage_dice_size,
        ) == (1, "constitution", 13, 5, 2, 10)

        moonbeam_sub = druid.spell_save_actions[1]
        assert (
            moonbeam_sub.level,
            moonbeam_sub.save_ability,
            moonbeam_sub.dc,
            moonbeam_sub.range_ft,
        ) == (2, "constitution", 13, 5)
        assert (
            moonbeam_sub.damage_dice_count,
            moonbeam_sub.damage_dice_size,
            moonbeam_sub.damage_type,
            moonbeam_sub.upcast_dice_per_level,
        ) == (3, 10, "necrotic", 1)

        longstrider = druid.defensive_spell_actions[0]
        assert longstrider.level == 1
        assert [(effect.kind, effect.flat_bonus) for effect in longstrider.modifier_effects] == [("speed", 10)]

        resources = {resource.id: resource.max_uses for resource in druid.resources}
        assert resources == {"spell-slot-1": 5, "spell-slot-2": 1}
        assert audit_monster_source(druid, _row()) == []
    except Exception:
        logger.exception("Druid arena spell-package regression failed.")
        raise


def test_druid_spellcasting_audit_fails_closed_on_missing_substitution_or_uses() -> None:
    try:
        druid = _druid()
        row = _row()

        missing_substitution = druid.model_copy(update={"spell_save_actions": []})
        assert "monster-spell-package-mismatch" in spellcasting_issues(missing_substitution, row)

        wrong_uses = druid.model_copy(update={
            "resources": [
                resource.model_copy(update={"max_uses": 4})
                if resource.id == "spell-slot-1" else resource
                for resource in druid.resources
            ]
        })
        assert "monster-spell-resource-mismatch" in spellcasting_issues(wrong_uses, row)
    except Exception:
        logger.exception("Druid fail-closed spell audit regression failed.")
        raise


def test_druid_is_raw_ready_only_with_complete_arena_package() -> None:
    try:
        card = next(card for card in build_monster_catalog() if card.name == "Druid")
        assert card.coverage_status is CoverageStatus.RAW_READY
        assert card.runnable_template_id == "srd-druid"
        assert card.blockers == []
    except Exception:
        logger.exception("Druid catalog certification regression failed.")
        raise
