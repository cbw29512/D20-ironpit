from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting
from app.domain.timed_damage import TimedDamageEffect

logger = logging.getLogger(__name__)

_CONE = re.compile(
    r"^The .+? exhales a (?P<area>\d+)-\s*foot cone of .+?\. "
    r"Each creature in that area must succeed on a DC (?P<dc>\d+) "
    r"(?P<ability>\w+) saving throw or be (?P<condition>\w+) for "
    r"(?P<minutes>\d+) minute(?:s)?\. A creature can repeat the saving throw "
    r"at the end of each of its turns, ending the effect on itself on a success\.$",
    re.IGNORECASE,
)
_EMANATION_DOT = re.compile(
    r"^A (?P<area>\d+)[^0-9]*foot[^a-z]+radius cloud of .+? extends out from the .+?\. "
    r"The .+? spread around corners\. Each creature in that area must succeed on a DC "
    r"(?P<dc>\d+) (?P<ability>\w+) saving throw or become (?P<condition>\w+)\. "
    r"While (?P=condition) in this way, a target takes (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+)\) (?P<damage>\w+) damage at the start of each "
    r"of its turns\. A target can repeat the saving throw at the end of each of its turns, "
    r"ending the effect on itself on a success\. Emptying a vial of holy water on the target "
    r"also ends the effect on it\.$",
    re.IGNORECASE,
)


def _normalized(text: str) -> str:
    try:
        return " ".join(
            text.replace("­", "").replace("‑", "-").replace("–", "-").split()
        )
    except Exception:
        logger.exception("Failed to normalize Recharge area-control source text.")
        raise


def source_proven_recharge_area_conditions_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    try:
        sections = source_sections_2014(monster.source_actions)
        result: list[SaveCapabilityDefinition] = []
        for action_id, minimum in monster.action_recharges.items():
            expected_suffix = f"(Recharge {minimum})"
            matches = [
                (name, body)
                for name, body in sections.items()
                if name.casefold().endswith(expected_suffix.casefold())
                and re.sub(r"[^a-z0-9]+", "-", name.split(" (", 1)[0].casefold()).strip("-")
                == action_id
            ]
            if len(matches) != 1:
                continue
            name, body = matches[0]
            plain_name = name.split(" (", 1)[0]
            text = _normalized(body)
            cone = _CONE.fullmatch(text)
            if cone is not None:
                result.append(SaveCapabilityDefinition(
                    id=action_id,
                    name=plain_name,
                    save_ability=cone["ability"].casefold(),
                    dc=int(cone["dc"]),
                    range_ft=int(cone["area"]),
                    max_targets=20,
                    target_scope="all-other-creatures",
                    area=AreaTargeting(
                        shape="cone", origin="self", length_ft=int(cone["area"]),
                    ),
                    resource_id=action_id,
                    effect_tags=[cone["condition"].casefold()],
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id=cone["condition"].casefold(),
                        duration_rounds=int(cone["minutes"]) * 10,
                        expiry_timing="target_turn_end",
                        repeat_save_ability=cone["ability"].casefold(),
                        repeat_save_dc=int(cone["dc"]),
                        repeat_save_timing="target_turn_end",
                    ),
                    animation="breath",
                ))
                continue
            dot = _EMANATION_DOT.fullmatch(text)
            if dot is not None:
                if int(dot["average"]) != int(dot["count"]) * (int(dot["size"]) + 1) // 2:
                    continue
                result.append(SaveCapabilityDefinition(
                    id=action_id,
                    name=plain_name,
                    save_ability=dot["ability"].casefold(),
                    dc=int(dot["dc"]),
                    range_ft=int(dot["area"]),
                    max_targets=20,
                    target_scope="all-other-creatures",
                    area=AreaTargeting(
                        shape="emanation", origin="self", radius_ft=int(dot["area"]),
                    ),
                    resource_id=action_id,
                    effect_tags=[dot["condition"].casefold()],
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id=dot["condition"].casefold(),
                        repeat_save_ability=dot["ability"].casefold(),
                        repeat_save_dc=int(dot["dc"]),
                        repeat_save_timing="target_turn_end",
                        allowed_removal_action_ids=["holy-water"],
                        start_of_turn_damage=TimedDamageEffect(
                            dice_count=int(dot["count"]),
                            dice_size=int(dot["size"]),
                            damage_type=dot["damage"].casefold(),
                        ),
                    ),
                    animation="spores",
                ))
        return result
    except Exception:
        logger.exception("Failed to bind Recharge area conditions for %s.", monster.id)
        raise
