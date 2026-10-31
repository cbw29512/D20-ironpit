"""Full-source 2014 Scare compilation into generic Frightened save Action."""
from __future__ import annotations
import logging
import re
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
logger = logging.getLogger(__name__)

_SCARE = re.compile(
    r"One creature of the (?P<owner>\w+)'s choice within (?P<distance>\d+) feet of it "
    r"must succeed on a DC (?P<dc>\d+) Wisdom saving throw or be frightened for "
    r"(?P<duration>\d+) minute\. The target can repeat the saving throw at the end "
    r"of each of its turns, with disadvantage if the (?P=owner) is within line "
    r"of sight, ending the effect on itself on a success\.", re.IGNORECASE,
)

def source_scare_2014(monster: SourceMonster2014) -> list[SaveCapabilityDefinition]:
    try:
        heading = "Scare (1/Day)"
        if heading not in monster.action_names:
            return []
        section = source_sections_2014(monster.source_actions).get(heading, "")
        match = _SCARE.fullmatch(" ".join(section.split()))
        if match is None or int(match["duration"]) != 1:
            return []
        return [SaveCapabilityDefinition(
            id="scare", name="Scare", save_ability="wisdom",
            dc=int(match["dc"]), range_ft=int(match["distance"]), max_targets=1,
            resource_id="scare", resource_cost=1,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="frightened", duration_rounds=10,
                expiry_timing="target_turn_end",
                repeat_save_ability="wisdom", repeat_save_dc=int(match["dc"]),
                repeat_save_timing="target_turn_end",
                repeat_save_disadvantage_while_source_visible=True,
            ), animation="fear",
        )]
    except Exception:
        logger.exception("2014 full-source Scare validation failed for %s", monster.id)
        raise
