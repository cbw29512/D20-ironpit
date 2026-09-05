from __future__ import annotations

import logging

from app.content.monster_catalog import build_monster_catalog

logger = logging.getLogger(__name__)


def test_full_srd_monster_catalog_reaches_tarrasque_cr_30() -> None:
    try:
        monsters = build_monster_catalog()
        assert len(monsters) == 330

        tarrasque = next(monster for monster in monsters if monster.name == "Tarrasque")
        assert str(tarrasque.challenge_rating).startswith("30")
        assert tarrasque.monster_type
        assert "gargantuan" in tarrasque.size.lower()
        assert tarrasque.source_reference
    except Exception:
        logger.exception("Full SRD monster-range certification failed.")
        raise
