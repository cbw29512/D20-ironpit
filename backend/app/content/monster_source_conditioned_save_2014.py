"""Source-proof 2014 save Actions requiring an existing target condition."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition

logger = logging.getLogger(__name__)

_DEATH_GLARE_SOURCE = re.compile(
    r"The hag targets one frightened creature she can see within (?P<range>\d+) feet of her\. "
    r"If the target can see the hag, it must succeed on a DC (?P<dc>\d+) "
    r"Wisdom saving throw against this magic or drop to 0 hit points\.",
    flags=re.IGNORECASE,
)


def source_proven_conditioned_saves_2014(monster: SourceMonster2014) -> list[SaveCapabilityDefinition]:
    """A renamed source Action uses universal save targeting and zero-HP resolution."""
    try:
        name = "Death Glare"
        if name not in monster.action_names:
            return []
        printed = source_sections_2014(monster.source_actions, include_continuations=True).get(name)
        if printed is None:
            return []
        match = _DEATH_GLARE_SOURCE.fullmatch(" ".join(printed.replace("’", "'").split()))
        if match is None:
            return []
        distance, dc = int(match["range"]), int(match["dc"])
        if distance <= 0 or distance % 5 or not (1 <= dc <= 40):
            return []
        return [SaveCapabilityDefinition(
            id="death-glare", name=name, save_ability="wisdom", dc=dc,
            range_ft=distance, requires_target_sight=True,
            requires_target_to_see_source=True,
            required_target_condition="frightened",
            failure_sets_zero_hp=True, magical_effect=True,
            animation="fear",
        )]
    except Exception:
        logger.exception("2014 source-conditioned save proof failed for %s", monster.id)
        raise
