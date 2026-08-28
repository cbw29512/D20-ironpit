from __future__ import annotations

import logging

from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.monsters import build_axe_beak, build_bandit, build_commoner, build_giant_lizard
from app.content.pregens import build_brom_ironmark
from app.domain.models import ArenaRoster

logger = logging.getLogger(__name__)


def build_arena_roster() -> ArenaRoster:
    try:
        return ArenaRoster(
            characters=[
                build_demo_fighter(),
                build_brom_ironmark(),
            ],
            monsters=[
                build_goblin_warrior(),
                build_bandit(),
                build_commoner(),
                build_axe_beak(),
                build_giant_lizard(),
            ],
        )
    except Exception as exc:
        logger.exception("Failed to build Iron Pit arena roster.")
        raise RuntimeError("Arena roster could not be created.") from exc
