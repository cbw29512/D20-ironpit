from __future__ import annotations

import logging

from app.content.monster_innate_source_2014 import (
    innate_spellcasting_source_2014,
    innate_spells_2014,
)
from app.content.monster_innate_support_2014 import (
    innate_spell_names_2014,
    supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _pit_fiend():
    try:
        return next(
            monster for monster in load_monster_source_2014()
            if monster.id == "pit-fiend"
        )
    except Exception:
        logger.exception("Pinned 2014 Pit Fiend source is missing.")
        raise


def test_reviewed_pit_fiend_innate_source_is_repaired_without_mutation() -> None:
    try:
        monster = _pit_fiend()
        snapshot = monster.model_dump_json()
        data = innate_spellcasting_source_2014(monster)

        assert data is not None
        assert data["ability"] == "charisma"
        assert data["save_dc"] == 21
        assert data["source_complete"] is True
        assert data["unsupported_text"] is None
        assert [
            (row["id"], row["usage"], row["uses_per_day"])
            for row in innate_spells_2014(monster)
        ] == [
            ("detect-magic", "at_will", None),
            ("fireball", "at_will", None),
            ("hold-monster", "per_day", 3),
            ("wall-of-fire", "per_day", 3),
        ]
        assert monster.model_dump_json() == snapshot
    except Exception:
        logger.exception("Pit Fiend innate source repair regression failed.")
        raise


def test_innate_spell_names_use_the_corrected_structured_view() -> None:
    try:
        monster = _pit_fiend()
        assert innate_spell_names_2014(monster) == {"fireball", "hold monster", "wall of fire"}
        assert supports_innate_spellcasting_2014(monster) is True
    except Exception:
        logger.exception("Pit Fiend corrected innate-name regression failed.")
        raise


def test_source_repair_fails_closed_when_damaged_fingerprint_drifts() -> None:
    try:
        monster = _pit_fiend()
        changed = monster.model_copy(update={
            "source_traits": monster.source_traits + " drift",
        })
        data = innate_spellcasting_source_2014(changed)

        assert data == changed.innate_spellcasting
        assert data is not None
        assert data["source_complete"] is False
        assert innate_spells_2014(changed) == []
    except Exception:
        logger.exception("Pit Fiend innate source-drift regression failed.")
        raise
