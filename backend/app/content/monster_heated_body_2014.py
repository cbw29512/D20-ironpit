from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

# Preserve printed parameters, not a per-monster identity table.
_SOURCE = re.compile(
    r"<strong>Heated Body\.</strong>.*?A creature that touches the .+? or hits it "
    r"with a melee attack while within (?P<reach>\d+) feet of it takes "
    r"\d+ \((?P<count>\d+)d(?P<size>\d+)\) fire damage",
    re.IGNORECASE | re.DOTALL,
)


def heated_body_retaliation_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind complete printed contact/melee retaliation to the universal passive effect."""
    try:
        if "Heated Body" not in monster.trait_names:
            return []
        source = monster.source_traits or ""
        match = _SOURCE.search(source)
        if match is None:
            return []
        return [TimedSelfBuffAction(
            id="heated-body", name="Heated Body", activation_timing="passive",
            melee_hit_retaliation=MeleeHitRetaliation(
                range_ft=int(match.group("reach")),
                dice_count=int(match.group("count")),
                dice_size=int(match.group("size")),
                damage_type=DamageType.FIRE,
                on_contact=True,
            ),
        )]
    except Exception:
        logger.exception("Failed 2014 heated-body source binding for %s.", monster.name)
        raise
