from __future__ import annotations

import logging

from app.content.monster_catalog_2014_action_support import unresolved_actions_2014
from app.content.monster_catalog_2014_models import CatalogMonster2014

logger = logging.getLogger(__name__)


def _monster(action_name: str) -> CatalogMonster2014:
    try:
        return CatalogMonster2014(
            id="arena-environment-test",
            name="Arena Environment Test",
            ruleset="2014",
            size="medium",
            creature_type="monstrosity",
            armor_class=10,
            max_hp=10,
            speed={"walk": 30},
            abilities={"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10},
            action_names=[action_name],
        )
    except Exception:
        logger.exception("Failed to build arena environment test monster.")
        raise


def test_underwater_only_ink_cloud_is_nonblocking_in_standard_pit() -> None:
    try:
        assert unresolved_actions_2014(_monster("Ink Cloud (Recharges after a Short or Long Rest)")) == []
    except Exception:
        logger.exception("Ink Cloud arena-policy regression failed.")
        raise


def test_destructible_wall_creation_is_nonblocking_in_standard_pit() -> None:
    try:
        assert unresolved_actions_2014(_monster("Wall of Ice (Recharge 6)")) == []
    except Exception:
        logger.exception("Wall of Ice arena-policy regression failed.")
        raise
