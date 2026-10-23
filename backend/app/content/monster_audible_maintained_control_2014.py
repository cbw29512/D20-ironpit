from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)
_OPENING = re.compile(
    r"^the .+? sings a magical melody\. every (?P<types>[a-z]+ and [a-z]+) within "
    r"(?P<range>\d+) feet of the .+? that can hear the song must succeed on a dc "
    r"(?P<dc>\d+) (?P<ability>[a-z]+) saving throw or be charmed until the song ends\.",
    re.IGNORECASE,
)
_REQUIRED_CLAUSES = (
    "must take a bonus action on its subsequent turns to continue singing",
    "can stop singing at any time",
    "song ends if the",
    "is incapacitated",
    "while charmed by the",
    "a target is incapacitated",
    "ignores the songs of other",
    "more than 5 feet away",
    "must move on its turn toward the",
    "by the most direct route",
    "trying to get within 5 feet",
    "doesn't avoid opportunity attacks",
    "before moving into damaging terrain",
    "takes damage from a source other than the",
    "repeat the saving throw at the end of each of its turns",
    "successfully saves is immune to this",
    "for the next 24 hours",
)


def _normalized(text: str) -> str:
    return " ".join(text.replace("’", "'").casefold().split())


def semantic_audible_control_candidate_names_2014(
    monster: SourceMonster2014,
) -> tuple[str, ...]:
    """Find printed audible area control Actions before compatibility checks."""
    try:
        return tuple(
            name for name, body in source_sections_2014(monster.source_actions).items()
            if _OPENING.search(_normalized(body))
        )
    except Exception:
        logger.exception("Failed to classify audible control for %s.", monster.id)
        raise


def semantic_audible_maintained_control_names_2014(
    monster: SourceMonster2014,
) -> tuple[str, ...]:
    sections = source_sections_2014(monster.source_actions)
    return tuple(
        name for name in semantic_audible_control_candidate_names_2014(monster)
        if all(clause in _normalized(sections[name]) for clause in _REQUIRED_CLAUSES)
    )


def _compile(name: str, body: str) -> SaveCapabilityDefinition | None:
    text = _normalized(body)
    match = _OPENING.search(text)
    if match is None or not all(clause in text for clause in _REQUIRED_CLAUSES):
        return None
    target_types = [item.strip() for item in match["types"].split(" and ")]
    if target_types != ["humanoid", "giant"] or match["ability"].casefold() != "wisdom":
        return None
    radius, dc = int(match["range"]), int(match["dc"])
    action_id = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return SaveCapabilityDefinition(
        id=action_id,
        name=name,
        save_ability="wisdom",
        dc=dc,
        range_ft=radius,
        max_targets=20,
        target_scope="all-other-creatures",
        area=AreaTargeting(shape="emanation", origin="self", radius_ft=radius),
        requires_target_hearing=True,
        required_target_creature_types=target_types,
        prohibited_target_source_effect_ids=[action_id],
        magical_effect=True,
        effect_tags=["charmed"],
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="charmed",
            additional_effect_ids=["incapacitated"],
            repeat_save_ability="wisdom",
            repeat_save_dc=dc,
            repeat_save_timing="target_turn_end",
            damage_repeat_save_trigger="other_than_effect_source",
            repeat_save_before_damaging_terrain=True,
            source_maintenance_action_cost="bonus_action",
            turn_behavior="forced_approach_source",
            ends_if_source_incapacitated=True,
            ends_if_source_dead=True,
            source_effect_immunity_on_end=True,
        ),
        source_effect_immunity_on_success=True,
        animation="song",
    )


def source_proven_audible_maintained_controls_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    sections = source_sections_2014(monster.source_actions)
    return [
        action
        for name in semantic_audible_maintained_control_names_2014(monster)
        if (action := _compile(name, sections[name])) is not None
    ]


def supports_audible_maintained_controls_2014(monster: SourceMonster2014) -> bool:
    candidates = semantic_audible_control_candidate_names_2014(monster)
    if not candidates:
        return True
    actions = source_proven_audible_maintained_controls_2014(monster)
    return len(actions) == len(candidates) and len({action.id for action in actions}) == len(actions)
