"""Source proof for form-qualified 2014 Charge and Pounce traits."""
from __future__ import annotations

import logging
import re

from app.content.monster_charge_profile_2014 import supports_charge_profile_2014
from app.content.monster_charge_source_corrections_2014 import corrected_charge_profile_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_HEADING = re.compile(r"^(?:Charge|Pounce) \([^()]+ or Hybrid Form Only\)$", re.I)


def _norm(value: str) -> str:
    return " ".join(value.casefold().replace("’", "'").split())


def _attack_base(value: str) -> str:
    return value.split(" (", 1)[0].strip().casefold()


def _matches_profile(monster: SourceMonster2014, heading: str, printed: str) -> bool:
    candidates = []
    for attack in monster.attacks:
        profile = corrected_charge_profile_2014(monster, attack)
        if profile is None or not supports_charge_profile_2014(profile):
            continue
        assert isinstance(profile, dict)
        text = _norm(printed)
        attack_name = _attack_base(attack.name)
        minimum = int(profile["minimum_move_ft"])
        opening = re.search(
            rf"moves at least {minimum} feet straight toward a (?:target|creature) "
            rf"and then hits it with (?:a |its )?{re.escape(attack_name)}(?: attack)? on the same turn",
            text,
        )
        if opening is None:
            continue
        damage = profile.get("bonus_damage")
        if isinstance(damage, dict):
            dice = f"{damage['dice_count']}d{damage['dice_size']}"
            if re.search(
                rf"extra \d+ \({re.escape(dice)}(?: \+ {int(damage['damage_bonus'])})?\) "
                rf"{re.escape(str(damage['damage_type']).casefold())} damage",
                text,
            ) is None:
                continue
        elif " takes an extra " in text:
            continue
        ability = profile.get("prone_save_ability")
        dc = profile.get("prone_save_dc")
        if ability is not None:
            if (
                f"dc {dc} {str(ability).casefold()} saving throw" not in text
                or "knocked prone" not in text
            ):
                continue
        follow_up = profile.get("follow_up_attack_id")
        if follow_up is not None:
            matches = [item for item in monster.attacks if item.id == follow_up]
            if len(matches) != 1:
                continue
            follow_name = _attack_base(matches[0].name)
            if (
                "if the target is prone" not in text
                or re.search(
                    rf"can make (?:one|another) (?:attack with (?:its )?)?"
                    rf"{re.escape(follow_name)}(?: attack)? against it as a bonus action",
                    text,
                ) is None
            ):
                continue
        elif " as a bonus action" in text:
            continue
        candidates.append(attack.id)
    return len(candidates) == 1 and heading in monster.trait_names


def source_proven_form_qualified_charge_traits_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Return qualifying source labels whose printed parameters compile exactly."""
    try:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        return frozenset(
            heading
            for heading, printed in sections.items()
            if _HEADING.fullmatch(heading) and _matches_profile(monster, heading, printed)
        )
    except Exception:
        logger.exception("Failed form-qualified Charge proof for %s.", monster.name)
        raise
