from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_bonus_action_save_is_audited_against_bonus_action_source() -> None:
    try:
        issues = audit_monster_source(_monster("Basilisk"), _row("Basilisk"))
        assert not any("srd-basilisk-petrifying-gaze" in issue for issue in issues)
        assert "source-save-action-count-mismatch" not in issues
    except Exception:
        logger.exception("Bonus-action save source-section audit regression failed.")
        raise


def test_medusa_petrifying_gaze_uses_bonus_action_source_section() -> None:
    try:
        issues = audit_monster_source(_monster("Medusa"), _row("Medusa"))
        assert not any("srd-medusa-petrifying-gaze" in issue for issue in issues)
    except Exception:
        logger.exception("Medusa staged-save source-section audit regression failed.")
        raise


def test_centaur_trampling_charge_uses_shared_bonus_save_and_recharge() -> None:
    try:
        centaur = _monster("Centaur Trooper")
        action = next(item for item in centaur.saving_throw_actions if item.name == "Trampling Charge")
        resource = next(item for item in centaur.resources if item.id == action.resource_id)

        assert action.action_cost == "bonus_action"
        assert action.save_ability == "strength"
        assert action.dc == 14
        assert action.range_ft == 50
        assert (action.damage_dice_count, action.damage_dice_size, action.damage_bonus) == (1, 6, 4)
        assert action.damage_type == "bludgeoning"
        assert action.success_damage == "none"
        assert any(effect.kind == "prone" for effect in action.failure_effects)
        assert resource.max_uses == 1
        assert resource.recharge is not None
        assert resource.recharge.minimum_roll == 5
        assert audit_monster_source(centaur, _row("Centaur Trooper")) == []
    except Exception:
        logger.exception("Centaur Trampling Charge regression failed.")
        raise


def test_air_elemental_whirlwind_uses_contact_save_recharge_and_prone() -> None:
    try:
        elemental = _monster("Air Elemental")
        action = next(item for item in elemental.saving_throw_actions if item.name == "Whirlwind")
        resource = next(item for item in elemental.resources if item.id == action.resource_id)

        assert action.action_cost == "action"
        assert action.save_ability == "strength"
        assert action.dc == 13
        assert action.range_ft == 5
        assert (action.damage_dice_count, action.damage_dice_size, action.damage_bonus) == (4, 10, 2)
        assert action.damage_type == "thunder"
        assert action.success_damage == "half"
        assert action.push_target_away_ft == 20
        assert any(effect.kind == "prone" for effect in action.failure_effects)
        assert resource.max_uses == 1
        assert resource.recharge is not None
        assert resource.recharge.minimum_roll == 4
        assert audit_monster_source(elemental, _row("Air Elemental")) == []
    except Exception:
        logger.exception("Air Elemental Whirlwind regression failed.")
        raise
