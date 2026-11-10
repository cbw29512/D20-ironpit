"""2014 source Enlarge composes generic timed size, save/check and weapon facts."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.combatants import ResourceDefinition
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.size import CreatureSize
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)
_HEADING = "Enlarge (Recharges after a Short or Long Rest)"
_PATTERN = re.compile(
    r"^For (?P<minutes>\d+) minute(?:s)?, the (?P<owner>[a-z-]+) magically "
    r"increases in size, along with anything it is wearing or carrying\. "
    r"While enlarged, the (?P=owner) is (?P<size>Large), doubles its damage "
    r"dice on Strength-based weapon attacks \(included in the attacks\), "
    r"and makes Strength checks and Strength saving throws with advantage\. "
    r"If the (?P=owner) lacks the room to become (?P=size), it attains the "
    r"maximum size possible in the space available\.$", re.IGNORECASE,
)


def source_enlarge_actions_2014(
    monster: SourceMonster2014,
) -> list[TimedSelfBuffAction]:
    """Prove every material printed clause before compiling universal actions."""
    try:
        if _HEADING not in monster.action_names:
            return []
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(_HEADING)
        match = _PATTERN.fullmatch(" ".join((printed or "").split()))
        if match is None or int(match.group("minutes")) != 1:
            return []
        return [TimedSelfBuffAction(
            id="enlarge", name="Enlarge", action_cost="action",
            resource_id="enlarge", resource_cost=1,
            duration_rounds=10, expiry_timing="source_turn_end",
            opening_eligible=False, magical_effect=True,
            size_override=CreatureSize.LARGE,
            ability_check_advantage_abilities=["strength"],
            saving_throw_advantage_grants=[SavingThrowAdvantageGrant(
                source_id="enlarge-strength-save", source_name="Enlarge",
                abilities=["strength"],
            )],
            priority=80, animation="buff",
        )]
    except Exception:
        logger.exception("Failed generic 2014 source Enlarge proof for %s.", monster.name)
        raise


def source_enlarge_resources_2014(
    monster: SourceMonster2014,
) -> list[ResourceDefinition]:
    """Short/long-rest recharges remain one-use resources within a fight."""
    try:
        return [ResourceDefinition(id="enlarge", name="Enlarge", max_uses=1)
                for _ in source_enlarge_actions_2014(monster)]
    except Exception:
        logger.exception("Failed source Enlarge resource for %s.", monster.name)
        raise
