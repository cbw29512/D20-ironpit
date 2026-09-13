from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_limited_use_source_audit import limited_use_issues
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_bonus_action_recharge_binding_satisfies_limited_use_audit() -> None:
    try:
        basilisk = _monster("Basilisk")
        gaze = next(action for action in basilisk.saving_throw_actions if action.name == "Petrifying Gaze")
        assert gaze.action_cost == "bonus_action"
        assert gaze.resource_id is not None
        assert limited_use_issues(basilisk, _row("Basilisk")) == []
    except Exception:
        logger.exception("Bonus-action Recharge audit regression failed.")
        raise


def test_recharge_binding_in_wrong_action_economy_section_fails_closed() -> None:
    try:
        basilisk = _monster("Basilisk")
        gaze = next(action for action in basilisk.saving_throw_actions if action.name == "Petrifying Gaze")
        wrong = gaze.model_copy(update={"action_cost": "action"})
        drifted = basilisk.model_copy(update={
            "saving_throw_actions": [
                wrong if action.id == gaze.id else action for action in basilisk.saving_throw_actions
            ],
        })
        issues = limited_use_issues(drifted, _row("Basilisk"))
        assert "uncertified-limited-use:bonusactions-petrifying-gaze-recharge-4-6" in issues
    except Exception:
        logger.exception("Recharge action-economy section fail-closed regression failed.")
        raise
