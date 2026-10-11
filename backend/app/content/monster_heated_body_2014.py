from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

# A complete source clause is required. A trait label by itself cannot
# certify a retaliation. Stop at the next printed trait boundary.
_CONTACT = re.compile(
    r"A creature that touches the .+? or hits it with a melee attack "
    r"while within (?P<reach>\\d+) feet of it takes "
    r"\\d+ \\((?P<count>\\d+)d(?P<size>\\d+)\\) (?P<type>fire|acid) damage\\b",
    re.IGNORECASE | re.DOTALL,
)


def _source_retaliation_2014(
    monster: SourceMonster2014, label: str, damage_type: DamageType,
) -> list[TimedSelfBuffAction]:
    if label not in monster.trait_names:
        return []
    source = monster.source_traits or ""
    heading = re.compile(
        rf"<strong>{re.escape(label)}\\.</strong>(?P<body>.*?)(?=<strong>|\\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    section = heading.search(source)
    if section is None:
        return []
    match = _CONTACT.search(section.group("body"))
    if match is None or match.group("type").lower() != damage_type.value:
        return []
    return [TimedSelfBuffAction(
        id=label.lower().replace(" ", "-"), name=label, activation_timing="passive",
        melee_hit_retaliation=MeleeHitRetaliation(
            range_ft=int(match.group("reach")),
            dice_count=int(match.group("count")),
            dice_size=int(match.group("size")),
            damage_type=damage_type,
            on_contact=True,
        ),
    )]


def heated_body_retaliation_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Preserve 2014 fire parameters with a generic passive retaliation rule."""
    try:
        return _source_retaliation_2014(monster, "Heated Body", DamageType.FIRE)
    except Exception:
        logger.exception("Failed 2014 Heated Body binding for %s.", monster.name)
        raise


def corrosive_form_retaliation_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind the printed Acid hit/contact clause; equipment damage is Pit-neutral."""
    try:
        return _source_retaliation_2014(monster, "Corrosive Form", DamageType.ACID)
    except Exception:
        logger.exception("Failed 2014 Corrosive Form binding for %s.", monster.name)
        raise
