from __future__ import annotations

import logging

from app.content.monster_source_save_candidates import source_save_candidates
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _row(actions: str) -> dict[str, object]:
    return {"name": "Test Brute", "actions": actions}


def test_damage_save_derives_prone_rider_and_size_limit() -> None:
    try:
        actions, resources = source_save_candidates(_row(
            "Tail Slam. Strength Saving Throw: DC 14, one Large or smaller creature within 10 feet. "
            "Failure: 9 (2d6 + 2) Bludgeoning damage, and the target has the Prone condition. "
            "Success: Half damage."
        ))
        assert resources == []
        assert len(actions) == 1
        assert actions[0].success_damage == "half"
        assert len(actions[0].failure_effects) == 1
        assert actions[0].failure_effects[0].kind == "prone"
        assert actions[0].failure_effects[0].max_target_size is CreatureSize.LARGE
    except Exception:
        logger.exception("Shared Prone save-rider regression failed.")
        raise


def test_damage_save_derives_timed_condition_rider() -> None:
    try:
        actions, _ = source_save_candidates(_row(
            "Shock Wave. Constitution Saving Throw: DC 15, one creature within 30 feet. "
            "Failure: 12 (3d6 + 2) Thunder damage, and the target has the Stunned condition until the end of its next turn. "
            "Success: Half damage."
        ))
        effect = actions[0].failure_effects[0]
        assert effect.kind == "condition"
        assert effect.condition == "stunned"
        assert effect.expiry_timing == "target_turn_end"
    except Exception:
        logger.exception("Shared timed-condition save-rider regression failed.")
        raise


def test_pure_damage_save_remains_rider_free() -> None:
    try:
        actions, _ = source_save_candidates(_row(
            "Flame Burst. Dexterity Saving Throw: DC 13, each creature in a 15-foot Cone. "
            "Failure: 10 (3d6) Fire damage. Success: Half damage."
        ))
        assert len(actions) == 1
        assert actions[0].failure_effects == []
        assert actions[0].push_target_away_ft == 0
        assert actions[0].grapple is None
    except Exception:
        logger.exception("Pure-damage save regression failed.")
        raise
