"""Source-proof 2014 Dreadful Glare through generic save-control primitives."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.failure_margin import FailureMarginEscalation
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)

_MUMMY_KEY = "2014-dreadful-glare-mummy"
_LORD_KEY = "2014-dreadful-glare-mummy-lord"

_SOURCE = re.compile(
    r"The (?P<source>mummy(?: lord)?) targets one creature it can see within "
    r"(?P<range>\d+) feet of it\. If the target can see the (?P=source), it must "
    r"succeed on a DC (?P<dc>\d+) Wisdom saving throw against this magic or "
    r"become frightened until the end of the (?P=source)'s next turn\. "
    r"If the target fails the saving throw by (?P<margin>\d+) or more, it is also "
    r"paralyzed for the same duration\. A target that succeeds on the saving throw "
    r"is immune to the Dreadful Glare of all mummies "
    r"(?P<scope>\(but not mummy lords\)|and mummy lords) for the next "
    r"(?P<hours>\d+) hours\.",
    flags=re.IGNORECASE,
)


def source_proven_dreadful_glare_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    try:
        name = "Dreadful Glare"
        if name not in monster.action_names:
            return []
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(name)
        if printed is None:
            return []
        normalized = " ".join(printed.replace("’", "'").split())
        match = _SOURCE.fullmatch(normalized)
        if match is None or int(match["hours"]) != 24:
            return []
        distance = int(match["range"])
        dc = int(match["dc"])
        margin = int(match["margin"])
        source_kind = match["source"].casefold()
        scope = match["scope"].casefold()
        if distance <= 0 or distance % 5 or not 1 <= dc <= 40 or margin != 5:
            return []
        if source_kind == "mummy" and scope == "(but not mummy lords)":
            blocking = [_MUMMY_KEY]
            grants = [_MUMMY_KEY]
        elif source_kind == "mummy lord" and scope == "and mummy lords":
            blocking = [_LORD_KEY]
            grants = [_MUMMY_KEY, _LORD_KEY]
        else:
            return []
        return [SaveCapabilityDefinition(
            id="dreadful-glare", name=name,
            save_ability="wisdom", dc=dc, range_ft=distance,
            requires_target_sight=True, requires_target_to_see_source=True,
            magical_effect=True, effect_tags=["frightened", "paralyzed"],
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="frightened", duration_rounds=1,
                expiry_timing="source_turn_end",
                failure_margin_escalation=FailureMarginEscalation(
                    margin=margin, additional_condition_ids=["paralyzed"],
                ),
            ),
            source_effect_immunity_keys_on_success=grants,
            source_effect_immunity_keys_blocking=blocking,
            animation="fear",
        )]
    except Exception:
        logger.exception("2014 Dreadful Glare source proof failed for %s.", monster.id)
        raise
