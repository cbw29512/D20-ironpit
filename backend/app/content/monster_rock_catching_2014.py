from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.damage_sources import DamageSourceQualifier
from app.domain.reactions import AttackDamageReductionReaction

logger = logging.getLogger(__name__)


def supports_rock_catching_reaction_2014(monster: SourceMonster2014) -> bool:
    """Require pinned 2014 source evidence before binding a shared Reaction."""
    try:
        text = monster.source_reactions or ""
        return (
            monster.reaction_names == ["Rock Catching"]
            and "DC 10" in text
            and "Dexterity" in text
            and "bludgeoning damage" in text
        )
    except Exception:
        logger.exception("Failed to verify incoming-hit Reaction for %s.", monster.id)
        raise


def source_hurled_object_qualifiers_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> list[DamageSourceQualifier]:
    """Tag source-declared thrown rocks as objects; combat never checks names."""
    try:
        if attack.kind != "ranged" or attack.damage.type != "bludgeoning":
            return []
        # This is source-content classification, not a runtime ability-name branch.
        if attack.name.casefold() not in {"rock", "stone", "boulder"}:
            return []
        printed = source_sections_2014(monster.source_actions).get(attack.name, "")
        if "Ranged Weapon Attack:" not in printed:
            return []
        return [DamageSourceQualifier.HURLED_OBJECT]
    except Exception:
        logger.exception("Failed to verify hurled-object source for %s.", monster.id)
        raise
