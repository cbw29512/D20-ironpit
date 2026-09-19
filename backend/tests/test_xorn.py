from __future__ import annotations

import logging

from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.catalog import CoverageStatus

logger = logging.getLogger(__name__)


def _xorn():
    try:
        return next(monster for monster in build_legacy_monster_templates() if monster.name == "Xorn")
    except Exception:
        logger.exception("Failed to resolve Xorn from the legacy authoring roster.")
        raise


def _source():
    try:
        return next(row for row in load_monster_rows() if row["name"] == "Xorn")
    except Exception:
        logger.exception("Failed to resolve the canonical Xorn source row.")
        raise


def test_xorn_source_contract_is_complete() -> None:
    try:
        xorn = _xorn()
        assert audit_monster_source(xorn, _source()) == []
        assert xorn.speed_ft == 20
        assert xorn.movement_modes.burrow_ft == 20
        assert xorn.source_trait_names == ["Earth Glide", "Treasure Sense"]
        assert xorn.source_bonus_action_names == ["Charge"]
        assert xorn.attack_action is not None
        assert [slot.attack_ids for slot in xorn.attack_action.slots] == [
            ["srd-xorn-bite"],
            ["srd-xorn-claw"],
            ["srd-xorn-claw"],
            ["srd-xorn-claw"],
        ]
    except Exception:
        logger.exception("Xorn source-contract regression failed.")
        raise


def test_xorn_is_raw_ready_in_production_roster() -> None:
    try:
        card = next(card for card in build_monster_catalog() if card.name == "Xorn")
        assert card.coverage_status is CoverageStatus.RAW_READY
        assert card.runnable_template_id == "srd-xorn"
        assert card.blockers == []
    except Exception:
        logger.exception("Xorn production-certification regression failed.")
        raise
