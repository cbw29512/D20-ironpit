"""Whole-clause 2014 Harpy Luring Song source binding."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

_LURING_SONG_SOURCE = re.compile(
    r"The harpy sings a magical melody\. Every humanoid and giant within "
    r"(?P<range>\d+) feet of the harpy that can hear the song must succeed "
    r"on a DC (?P<dc>\d+) Wisdom saving throw or be charmed until the song "
    r"ends\. The harpy must take a bonus action on its subsequent turns to "
    r"continue singing\. It can stop singing at any time\. The song ends if "
    r"the harpy is incapacitated\. While charmed by the harpy, a target is "
    r"incapacitated and ignores the songs of other harpies\. If the charmed "
    r"target is more than (?P<distance>\d+) feet away from the harpy, the "
    r"target must move on its turn toward the harpy by the most direct route, "
    r"trying to get within (?P=distance) feet\. It doesn't avoid opportunity "
    r"attacks, but before moving into damaging terrain, such as lava or a pit, "
    r"and whenever it takes damage from a source other than the harpy, the "
    r"target can repeat the saving throw\. A charmed target can also repeat "
    r"the saving throw at the end of each of its turns\. If the saving throw "
    r"is successful, the effect ends on it\. A target that successfully saves "
    r"is immune to this harpy's song for the next (?P<immunity>\d+) hours\.",
    flags=re.IGNORECASE,
)


def source_proven_luring_song_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Bind only an exact whole-clause printed Luring Song."""
    try:
        name = "Luring Song"
        if name not in monster.action_names:
            return []
        printed = source_sections_2014(monster.source_actions).get(name)
        if printed is None:
            return []
        normalized = " ".join(printed.replace("’", "'").split())
        match = _LURING_SONG_SOURCE.fullmatch(normalized)
        if match is None:
            return []
        range_ft = int(match["range"])
        dc = int(match["dc"])
        approach_ft = int(match["distance"])
        if range_ft != 300 or dc != 11 or approach_ft != 5:
            return []
        if int(match["immunity"]) != 24:
            return []
        return [SaveCapabilityDefinition(
            id="luring-song", name=name,
            save_ability="wisdom", dc=dc, range_ft=range_ft,
            max_targets=20, target_scope="all-other-creatures",
            area=AreaTargeting(
                shape="emanation", origin="self", radius_ft=range_ft,
            ),
            requires_target_hearing=True,
            required_target_creature_types=["humanoid", "giant"],
            magical_effect=True,
            effect_tags=["charmed", "incapacitated"],
            source_effect_immunity_on_success=True,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="charmed",
                additional_effect_ids=["incapacitated"],
                repeat_save_ability="wisdom", repeat_save_dc=dc,
                repeat_save_timing="target_turn_end",
                damage_repeat_save_trigger="other_than_effect_source",
                repeat_save_before_damaging_terrain=True,
                turn_behavior="forced_approach_source",
                ends_if_source_incapacitated=True,
                source_effect_immunity_on_repeat_save_success=True,
                source_maintenance_action_cost="bonus_action",
                exclusive_source_effect_group_id="audible-luring-song",
            ),
            animation="song",
        )]
    except Exception:
        logger.exception("2014 Luring Song source proof failed for %s.", monster.id)
        raise
