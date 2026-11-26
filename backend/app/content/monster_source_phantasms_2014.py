"""Exact 2014 source binding for finite self-duplicate defenses."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.combatants import ResourceDefinition
from app.domain.timed_self_buffs import IllusoryDuplicateDefense, TimedSelfBuffAction

logger = logging.getLogger(__name__)

_PRINTED = (
    "The cloaker magically creates three illusory duplicates of itself if it isn't in bright light. "
    "The duplicates move with it and mimic its actions, shifting position so as to make it impossible "
    "to track which cloaker is the real one. If the cloaker is ever in an area of bright light, the "
    "duplicates disappear. Whenever any creature targets the cloaker with an attack or a harmful spell "
    "while a duplicate remains, that creature rolls randomly to determine whether it targets the cloaker "
    "or one of the duplicates. A creature is unaffected by this magical effect if it can't see or if it "
    "relies on senses other than sight. A duplicate has the cloaker's AC and uses its saving throws. If an "
    "attack hits a duplicate, or if a duplicate fails a saving throw against an effect that deals damage, "
    "the duplicate disappears."
)


def source_phantasms_action_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Compile only the complete printed action; identity is not a binding input."""
    try:
        matches = [
            heading for heading, body in source_sections_2014(
                monster.source_actions, include_continuations=True,
            ).items()
            if " ".join(body.replace("’", "'").split()) == _PRINTED
        ]
        if len(matches) != 1:
            return []
        heading = matches[0]
        if heading not in monster.action_names or not heading.startswith("Phantasms ("):
            return []
        return [TimedSelfBuffAction(
            id="phantasms", name=heading.split(" (", 1)[0], action_cost="action",
            resource_id="phantasms", resource_cost=1, magical_effect=True,
            expiry_timing=None,
            illusory_duplicate_defense=IllusoryDuplicateDefense(
                initial_duplicates=3,
                redirection_mode="uniform_original_and_duplicates",
                armor_class_mode="source_armor_class",
            ),
            priority=85, animation="mirror-image",
        )]
    except Exception:
        logger.exception("2014 Phantasms source binding failed for %s.", monster.id)
        raise


def source_phantasms_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    return [ResourceDefinition(id="phantasms", name=action.name, max_uses=1)
            for action in source_phantasms_action_2014(monster)]
