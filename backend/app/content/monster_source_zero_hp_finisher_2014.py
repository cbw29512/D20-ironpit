"""2014 source-to-universal-save adapter for finishing living zero-HP targets.

No creature identity dispatch: only the complete printed clause permits
instant death, and only an actual death grants the owner printed healing.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_save_definitions import SaveCapabilityDefinition

logger = logging.getLogger(__name__)

_FINISHER = re.compile(
    r"^As a bonus action, the (?P<owner>[a-z][a-z'\\-]*) can target one "
    r"creature it can see within (?P<range>\\d+) feet of it that has 0 hit "
    r"points and is still alive\\. The target must succeed on a DC "
    r"(?P<dc>\\d+) (?P<save>Constitution) saving throw against this magic "
    r"or die\\. If the target dies, the (?P=owner) regains "
    r"(?P<average>\\d+) \\((?P<count>\\d+)d(?P<size>\\d+)\\) hit points\\.$",
    re.IGNORECASE,
)


def source_proven_zero_hp_finisher_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Only source-proven printed numbers produce a reusable Bonus Action save."""
    try:
        trait = "Consume Life"
        if trait not in monster.trait_names:
            return []
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get(trait)
        if not printed:
            return []
        match = _FINISHER.fullmatch(" ".join(printed.replace("’", "'").split()))
        if not match:
            return []
        data = match.groupdict()
        count, sides = int(data["count"]), int(data["size"])
        if int(data["average"]) != count * (sides + 1) // 2:
            return []
        return [SaveCapabilityDefinition(
            id="consume-life", name=trait, action_cost="bonus_action",
            save_ability="constitution", dc=int(data["dc"]),
            range_ft=int(data["range"]), requires_target_sight=True,
            target_scope="all-other-creatures", magical_effect=True,
            requires_target_zero_hp_alive=True,
            instant_death_on_failed_save=True,
            heal_source_on_kill_dice_count=count,
            heal_source_on_kill_dice_size=sides,
            animation="life-drain",
        )]
    except Exception:
        logger.exception("2014 zero-HP finisher source proof failed for %s.", monster.id)
        raise
