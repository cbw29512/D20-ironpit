"""Source-verified 2014 source-turn grappler damage using universal typed damage."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.source_turn_relation_damage import SourceTurnRelationDamage
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)
_HEADING = re.compile(
    r"<strong>(?P<name>[^<]+)\.</strong>(?P<body>.*?)(?=<strong>|\Z)",
    re.DOTALL | re.IGNORECASE,
)
_GRAPPLER_DAMAGE = re.compile(
    r"At the start of each of its turns,\s+the\s+[\w\s'-]+\s+deals\s+"
    r"\d+\s+\((?P<count>\d+)d(?P<size>\d+)\)\s+"
    r"(?P<type>piercing|fire|cold|acid|bludgeoning|slashing|necrotic)\s+damage\s+"
    r"to any creature grappling it\.",
    re.IGNORECASE,
)


def source_turn_grappler_damage_2014(
    monster: SourceMonster2014,
) -> list[SourceTurnRelationDamage]:
    """Require the full printed trigger, relationship and dice before source binding."""
    try:
        source = monster.source_traits or ""
        found = []
        for section in _HEADING.finditer(source):
            name = section.group("name").strip()
            if name not in monster.trait_names:
                continue
            matches = list(_GRAPPLER_DAMAGE.finditer(section.group("body")))
            if not matches:
                continue
            if len(matches) != 1:
                raise ValueError(f"Ambiguous source-turn grappler damage for {monster.id}/{name}.")
            match = matches[0]
            found.append(SourceTurnRelationDamage(
                source_name=name, target_relation="creatures_grappling_source",
                dice_count=int(match.group("count")), dice_size=int(match.group("size")),
                damage_type=DamageType(match.group("type").lower()),
            ))
        return found
    except Exception:
        logger.exception("2014 source-turn grappler damage binding failed for %s.", monster.id)
        raise
