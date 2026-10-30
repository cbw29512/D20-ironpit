from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

_PATTERN = re.compile(
    r"^The .+? emits a .+?\. Each creature within (?P<radius>\d+) feet of it "
    r"that can hear it and that isn't a (?P<excluded>\w+) must succeed on a DC "
    r"(?P<dc>\d+) (?P<ability>\w+) saving throw or be (?P<condition>\w+) "
    r"until the end of the .+?'s next turn\.$",
    re.IGNORECASE,
)


def limited_audible_resource_uses_2014(monster: SourceMonster2014) -> dict[str, int]:
    try:
        result: dict[str, int] = {}
        for name, body in source_sections_2014(monster.source_actions).items():
            marker = re.search(r"\((\d+)\s*/\s*Day\)$", name, re.IGNORECASE)
            if marker is None or _PATTERN.fullmatch(" ".join(body.split())) is None:
                continue
            action_id = re.sub(
                r"[^a-z0-9]+", "-", name.split(" (", 1)[0].casefold()
            ).strip("-")
            result[action_id] = int(marker.group(1))
        return result
    except Exception:
        logger.exception("Failed to derive limited audible resources for %s.", monster.id)
        raise


def source_proven_limited_audible_conditions_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    try:
        sections = source_sections_2014(monster.source_actions)
        resource_uses = limited_audible_resource_uses_2014(monster)
        result: list[SaveCapabilityDefinition] = []
        for name, body in sections.items():
            action_id = re.sub(
                r"[^a-z0-9]+", "-", name.split(" (", 1)[0].casefold()
            ).strip("-")
            uses = resource_uses.get(action_id)
            if uses is None:
                continue
            match = _PATTERN.fullmatch(" ".join(body.split()))
            if match is None:
                continue
            result.append(SaveCapabilityDefinition(
                id=action_id,
                name=name.split(" (", 1)[0],
                save_ability=match["ability"].casefold(),
                dc=int(match["dc"]),
                range_ft=int(match["radius"]),
                max_targets=20,
                target_scope="all-other-creatures",
                area=AreaTargeting(
                    shape="emanation", origin="self", radius_ft=int(match["radius"]),
                ),
                requires_target_hearing=True,
                excluded_target_creature_types=[match["excluded"].casefold()],
                resource_id=action_id,
                resource_cost=1,
                effect_tags=[match["condition"].casefold()],
                failed_save_timed_effect=FailedSaveTimedEffect(
                    effect_id=match["condition"].casefold(),
                    duration_rounds=1,
                    expiry_timing="source_turn_end",
                ),
                animation="sound-wave",
            ))
        return result
    except Exception:
        logger.exception("Failed to bind limited audible conditions for %s.", monster.id)
        raise
