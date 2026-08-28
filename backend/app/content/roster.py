from __future__ import annotations

import logging

from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.monsters import build_axe_beak, build_bandit, build_commoner, build_giant_lizard
from app.content.monsters_low_cr import build_giant_rat, build_giant_weasel, build_guard
from app.content.pregens import build_brom_ironmark, build_selene_asharrow
from app.domain.models import ArenaRoster

logger = logging.getLogger(__name__)


def build_arena_roster() -> ArenaRoster:
    try:
        return ArenaRoster(
            characters=[
                build_demo_fighter(),
                build_brom_ironmark(),
                build_selene_asharrow(),
            ],
            monsters=[
                build_goblin_warrior(),
                build_bandit(),
                build_commoner(),
                build_guard(),
                build_giant_rat(),
                build_giant_weasel(),
                build_axe_beak(),
                build_giant_lizard(),
            ],
        )
    except Exception as exc:
        logger.exception("Failed to build Iron Pit arena roster.")
        raise RuntimeError("Arena roster could not be created.") from exc
