"""Source-proof 2014 Frightful Presence through generic save-condition primitives."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)

_SOURCE = re.compile(
    r"Each creature of the (?P<source>\w+(?:'s)?) choice that is within "
    r"(?P<range>\d+) feet of the (?P=source) and aware of it must succeed on a "
    r"DC (?P<dc>\d+) Wisdom saving throw or become frightened for 1 minute\. "
    r"A creature can repeat the saving throw at the end of each of its turns, "
    r"ending the effect on itself on a success\. If a creature's saving throw "
    r"is successful or the effect ends for it, the creature is immune to the "
    r"(?P=source)'s Frightful Presence for the next 24 hours\.",
    flags=re.IGNORECASE,
)

def source_proven_frightful_presence_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    try:
        name = "Frightful Presence"
        if name not in monster.action_names:
            return []
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(name)
        if printed is None:
            return []
        normalized = " ".join(printed.replace("’", "'").split())
        match = _SOURCE.fullmatch(normalized)
        if match is None:
            return []
        distance = int(match["range"])
        dc = int(match["dc"])
        if distance <= 0 or distance % 5 or not 1 <= dc <= 40:
            return []
        return [SaveCapabilityDefinition(
            id="frightful-presence",
            name=name,
            save_ability="wisdom",
            dc=dc,
            range_ft=distance,
            effect_tags=["frightened"],
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="frightened",
                duration_rounds=10,
                expiry_timing="target_turn_end",
                repeat_save_ability="wisdom",
                repeat_save_dc=dc,
                repeat_save_timing="target_turn_end",
            ),
            source_effect_immunity_keys_on_success=["frightful-presence"],
            source_effect_immunity_keys_blocking=["frightful-presence"],
            animation="fear",
        )]
    except Exception:
        logger.exception(
            "2014 Frightful Presence source proof failed for %s.", monster.id
        )
        raise
