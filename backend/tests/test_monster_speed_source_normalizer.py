from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_speed_source_normalizer import normalize_truncated_speed_parentheticals

logger = logging.getLogger(__name__)


def test_truncated_speed_parenthetical_repairs_from_matching_raw_source() -> None:
    try:
        row = {
            "name": "Moon Beast",
            "speed": "30 ft., 40 ft. (beast",
            "rawText": (
                "AC 12 Initiative +2 (12) HP 20 Speed 30 ft., 40 ft. (beast form only) "
                "MOD SAVE MOD SAVE MOD SAVE Str 10 +0 +0"
            ),
        }
        repaired = normalize_truncated_speed_parentheticals([row])[0]
        assert repaired["speed"] == "30 ft., 40 ft. (beast form only)"
    except Exception:
        logger.exception("Synthetic Speed normalization regression failed.")
        raise


def test_balanced_speed_source_is_not_rewritten() -> None:
    try:
        row = {
            "name": "Stable Beast",
            "speed": "30 ft., Swim 30 ft.",
            "rawText": "Speed 99 ft. MOD SAVE",
        }
        repaired = normalize_truncated_speed_parentheticals([row])[0]
        assert repaired["speed"] == "30 ft., Swim 30 ft."
    except Exception:
        logger.exception("Balanced Speed preservation regression failed.")
        raise


def test_canonical_werebear_speed_is_recovered_from_raw_text() -> None:
    try:
        werebear = next(row for row in load_monster_rows() if row["name"] == "Werebear")
        assert werebear["speed"] == "30 ft., 40 ft. (bear form only), Climb 30 ft. (bear form only)"
    except Exception:
        logger.exception("Werebear canonical Speed normalization regression failed.")
        raise
