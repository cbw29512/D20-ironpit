"""Source-proof rechargeable timed-control Actions from immutable 2014 cards."""
from __future__ import annotations

import logging
import re

from app.content.monster_arena_action_policy_2014 import action_label_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)
_RECHARGE = re.compile(r"^(?P<name>.+?) \\(Recharge (?P<minimum>[1-6])(?:-6)?\\)$", re.I)
_BLINDING_CONE = re.compile(
    r"The [^.]+? exhales a (?P<length>\d+)-foot cone of blinding dust\. "
    r"Each creature in that area must succeed on a DC (?P<dc>\d+) Dexterity saving throw "
    r"or be blinded for (?P<minutes>\d+) minute\. A creature can repeat the saving throw "
    r"at the end of each of its turns, ending the effect on itself on a success\.", re.I,
)
_POISON_SPORES = re.compile(
    r"A (?P<radius>\d+)-foot-radius cloud of toxic spores extends out from the [^.]+?\. "
    r"The spores spread around corners\. Each creature in that area must succeed on a DC "
    r"(?P<dc>\d+) Constitution saving throw or become poisoned\. While poisoned in this way, "
    r"a target takes (?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)\) poison damage at the "
    r"start of each of its turns\. A target can repeat the saving throw at the end of each of "
    r"its turns, ending the effect on itself on a success\. Emptying a vial of holy water on "
    r"the target also ends the effect on it\.", re.I,
)


def _normalize(text: str) -> str:
    try:
        normalized = " ".join(
            text.replace("\u00ad", "").replace("’", "'").replace("‑", "-").replace("‐", "-").replace("–", "-").split()
        )
        return re.sub(r"(?<=\d)-\s+(?=[A-Za-z])", "-", normalized)
    except Exception:
        logger.exception("Failed to normalize Recharge timed-control source text.")
        raise


def _recharge_identity(monster: SourceMonster2014, heading: str):
    try:
        match = _RECHARGE.fullmatch(_normalize(heading))
        if match is None:
            return None
        label = action_label_2014(heading)
        ids = [item for item in monster.action_recharges if item.replace("-", " ").casefold() == label]
        if len(ids) != 1:
            return None
        action_id, minimum = ids[0], int(match["minimum"])
        if monster.action_recharges.get(action_id) != minimum:
            return None
        return action_id, match["name"].strip()
    except Exception:
        logger.exception("Failed Recharge identity proof for %s / %s.", monster.id, heading)
        raise


def _blind_action(action_id: str, name: str, text: str) -> SaveCapabilityDefinition | None:
    try:
        match = _BLINDING_CONE.fullmatch(text)
        if match is None:
            return None
        length, dc, minutes = int(match["length"]), int(match["dc"]), int(match["minutes"])
        if length <= 0 or length % 5 or minutes <= 0:
            return None
        return SaveCapabilityDefinition(
            id=action_id, name=name, save_ability="dexterity", dc=dc, range_ft=length,
            max_targets=20, target_scope="all-other-creatures",
            area=AreaTargeting(shape="cone", origin="self", length_ft=length),
            effect_tags=["blinded"], resource_id=action_id, resource_cost=1,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="blinded", duration_rounds=minutes * 10,
                expiry_timing="target_turn_end", repeat_save_ability="dexterity",
                repeat_save_dc=dc, repeat_save_timing="target_turn_end",
            ), animation="blind",
        )
    except Exception:
        logger.exception("Failed Recharge blinding-cone compilation for %s.", action_id)
        raise


def _spore_action(action_id: str, name: str, text: str) -> SaveCapabilityDefinition | None:
    try:
        match = _POISON_SPORES.fullmatch(text)
        if match is None:
            return None
        radius, dc = int(match["radius"]), int(match["dc"])
        count, size, average = int(match["count"]), int(match["size"]), int(match["average"])
        if radius <= 0 or radius % 5 or average != count * (size + 1) // 2:
            return None
        return SaveCapabilityDefinition(
            id=action_id, name=name, save_ability="constitution", dc=dc, range_ft=radius,
            max_targets=20, target_scope="all-other-creatures",
            area=AreaTargeting(shape="emanation", origin="self", radius_ft=radius),
            effect_tags=["poisoned"], resource_id=action_id, resource_cost=1,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="poisoned", expiry_timing=None,
                repeat_save_ability="constitution", repeat_save_dc=dc,
                repeat_save_timing="target_turn_end", allowed_removal_action_ids=["holy-water"],
                start_of_turn_damage_dice_count=count, start_of_turn_damage_dice_size=size,
                start_of_turn_damage_type="poison",
            ), animation="poison",
        )
    except Exception:
        logger.exception("Failed Recharge spore compilation for %s.", action_id)
        raise


def source_proven_recharge_timed_controls_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    try:
        result: list[SaveCapabilityDefinition] = []
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        for heading, printed in sections.items():
            identity = _recharge_identity(monster, heading)
            if identity is None:
                continue
            action_id, name = identity
            text = _normalize(printed)
            action = _blind_action(action_id, name, text) or _spore_action(action_id, name, text)
            if action is not None:
                result.append(action)
        return result
    except Exception:
        logger.exception("Failed to bind Recharge timed controls for %s.", monster.name)
        raise
