from __future__ import annotations

import logging

from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.catalog import CoverageStatus

logger = logging.getLogger(__name__)
_EXPECTED_IDS = {
    "Giant Shark": "srd-giant-shark",
    "Hunter Shark": "srd-hunter-shark",
    "Piranha": "srd-piranha",
    "Reef Shark": "srd-reef-shark",
    "Swarm of Piranhas": "srd-swarm-of-piranhas",
}
_NAMES = set(_EXPECTED_IDS)


def test_target_not_full_hp_monsters_are_source_complete() -> None:
    try:
        templates = {monster.name: monster for monster in build_legacy_monster_templates() if monster.name in _NAMES}
        rows = {str(row["name"]): row for row in load_monster_rows() if row["name"] in _NAMES}
        assert set(templates) == _NAMES
        assert set(rows) == _NAMES
        for name in sorted(_NAMES):
            assert audit_monster_source(templates[name], rows[name]) == []
        assert templates["Giant Shark"].speed_ft == 5
        assert templates["Giant Shark"].movement_modes.swim_ft == 60
        assert len(templates["Giant Shark"].attack_action.slots) == 2
        assert templates["Swarm of Piranhas"].weapon_attack.conditional_damage[0].trigger == "attacker_bloodied"
    except Exception:
        logger.exception("Target-not-full-HP monster source regression failed.")
        raise


def test_aquatic_monsters_certify_from_runtime_and_source_audit() -> None:
    try:
        cards = {card.name: card for card in build_monster_catalog() if card.name in _NAMES}
        assert set(cards) == _NAMES
        for name, expected_id in _EXPECTED_IDS.items():
            card = cards[name]
            assert card.coverage_status is CoverageStatus.RAW_READY
            assert card.runnable_template_id == expected_id
            assert card.blockers == []
    except Exception:
        logger.exception("Runtime-derived aquatic monster certification regression failed.")
        raise
