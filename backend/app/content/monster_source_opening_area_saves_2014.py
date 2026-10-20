"""2014 source-proofed opening area save adapted to universal combat mechanics.

This module converts pinned printed parameters to a generic opening-only Action.
It does NOT resolve initiative, saving throws, damage, or conditions by monster ID.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_damage import SaveDamageComponent
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

_LEAP = re.compile(
    r"If the bulette jumps at least (?P<jump>\d+) feet as part of its movement, "
    r"it can then use this action to land on its feet in a space that contains one or more other creatures\. "
    r"Each of those creatures must succeed on a DC (?P<dc>\d+) Strength or Dexterity saving throw "
    r"\(target's choice\) or be knocked prone and take "
    r"(?P<b_average>\d+) \((?P<b_count>\d+)d(?P<b_size>\d+) \+ (?P<b_bonus>\d+)\) bludgeoning damage plus "
    r"(?P<s_average>\d+) \((?P<s_count>\d+)d(?P<s_size>\d+) \+ (?P<s_bonus>\d+)\) slashing damage\. "
    r"On a successful save, the creature takes only half the damage, isn't knocked prone, "
    r"and is pushed (?P<push>\d+) feet out of the bulette's space into an unoccupied space of the creature's choice\. "
    r"If no unoccupied space is within range, the creature instead falls prone in the bulette's space\.",
    re.IGNORECASE,
)
_STANDING = re.compile(
    r"Standing Leap\. The bulette's long jump is up to (?P<long>\d+) feet and its high jump "
    r"is up to (?P<high>\d+) feet, with or without a running start\.",
    re.IGNORECASE,
)


def source_proven_opening_area_saves_2014(monster: SourceMonster2014) -> list[SaveCapabilityDefinition]:
    """Fail closed if either printed Action or enabling trait has changed."""
    try:
        if "Deadly Leap" not in monster.action_names:
            return []
        if "Standing Leap" not in monster.trait_names:
            return []
        action = source_sections_2014(monster.source_actions).get("Deadly Leap")
        traits = source_sections_2014(monster.source_traits).get("Standing Leap")
        if not action or not traits:
            return []
        match = _LEAP.fullmatch(" ".join(action.replace("’", "'").split()))
        standing = _STANDING.fullmatch("Standing Leap. " + " ".join(traits.replace("’", "'").split()))
        if match is None or standing is None:
            return []
        n = {key: int(value) for key, value in match.groupdict().items()}
        jump_range = int(standing["long"])
        if (
            n["jump"] != 15 or jump_range != 30 or int(standing["high"]) != 15
            or n["push"] != 5 or n["dc"] != 16
            or (n["b_count"], n["b_size"], n["b_bonus"], n["b_average"]) != (3, 6, 4, 14)
            or (n["s_count"], n["s_size"], n["s_bonus"], n["s_average"]) != (3, 6, 4, 14)
        ):
            return []
        return [SaveCapabilityDefinition(
            id="deadly-leap", name="Deadly Leap",
            save_ability="strength", save_ability_choices=["strength", "dexterity"],
            dc=n["dc"], range_ft=jump_range,
            opening_initiative_only=True,
            area=AreaTargeting(shape="square", origin="point", length_ft=10),
            damage_components=[
                SaveDamageComponent(
                    dice_count=n["b_count"], dice_size=n["b_size"],
                    damage_bonus=n["b_bonus"], damage_type="bludgeoning",
                ),
                SaveDamageComponent(
                    dice_count=n["s_count"], dice_size=n["s_size"],
                    damage_bonus=n["s_bonus"], damage_type="slashing",
                ),
            ],
            success_damage="half",
            failed_save_timed_effect=FailedSaveTimedEffect(effect_id="prone"),
            effect_tags=["prone"], animation="leap",
        )]
    except Exception:
        logger.exception("Failed 2014 opening area save source binding for %s.", monster.id)
        raise
