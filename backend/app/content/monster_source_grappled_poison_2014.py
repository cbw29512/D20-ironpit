"""Source-proof a held-target Poisoned/Paralyzed save using universal effects.

The printed Action supplies DC, duration and a grappled-owner requirement.
The existing Grappled relation, save resolver and grouped condition lifecycle
supply all combat behavior, including the end-of-target-turn repeat save.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_grapple_capacity_2014 import source_completed_limited_grapple_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)
_HELD_POISON = re.compile(
    r"One creature grappled by the (?P<owner>[a-z][a-z '\-]*) must succeed "
    r"on a DC (?P<dc>\d+) Constitution saving throw or be poisoned for "
    r"(?P<minutes>\d+) minute(?:s)?\. Until this poison ends, the target "
    r"is paralyzed\. The target can repeat the saving throw at the end "
    r"of each of its turns, ending the effect on itself on a success\.",
    flags=re.IGNORECASE,
)


def source_proven_grappled_poison_saves_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Only complete source clauses may compose the existing timed conditions."""
    try:
        sections = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        matched = []
        for name, body in sections.items():
            match = _HELD_POISON.fullmatch(" ".join(body.replace("’", "'").split()))
            if match is None or name not in monster.action_names:
                continue
            owner = match["owner"].strip().casefold()
            if owner != monster.name.strip().casefold():
                # Identity may change, but the source's actor and card must agree.
                continue
            holders = [
                source_completed_limited_grapple_2014(monster, attack)
                for attack in monster.attacks
            ]
            holders = [
                attack for attack in holders
                if attack.source_complete
                and isinstance(attack.control_effect, dict)
                and attack.control_effect.get("grapple_escape_dc")
            ]
            if len(holders) != 1:
                continue
            reach = holders[0].reach_ft
            dc, minutes = int(match["dc"]), int(match["minutes"])
            if dc not in range(1, 41) or minutes not in range(1, 101):
                continue
            matched.append(SaveCapabilityDefinition(
                id=re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-"),
                name=name, save_ability="constitution", dc=dc,
                range_ft=reach, target_scope="all-other-creatures",
                requires_target_grappled_by_source=True,
                effect_tags=["poisoned", "paralyzed"],
                failed_save_timed_effect=FailedSaveTimedEffect(
                    effect_id="poisoned", additional_effect_ids=["paralyzed"],
                    duration_rounds=minutes * 10,
                    expiry_timing="target_turn_end",
                    repeat_save_ability="constitution", repeat_save_dc=dc,
                    repeat_save_timing="target_turn_end",
                ),
            ))
        return matched
    except Exception:
        logger.exception("2014 held-target Poisoned/Paralyzed source proof failed.")
        raise
