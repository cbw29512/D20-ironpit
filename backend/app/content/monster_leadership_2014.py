"""Source-proven 2014 nonspell ally bonus-die commands (printed Leadership text).

Combat semantics live in the universal TimedFriendlyRollBonusAura resolver;
this module only verifies the immutable card supplies every printed term.
Binding keys on printed clauses, never on the monster name.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.combatants import ResourceDefinition
from app.domain.timed_self_buffs import TimedFriendlyRollBonusAura, TimedSelfBuffAction

logger = logging.getLogger(__name__)
_HEADING = re.compile(r"^(?P<name>[^(]+?) \(Recharges after a Short or Long Rest\)$")
_REQUIRED = (
    "for 1 minute", "whenever a nonhostile creature that it can see within 30 feet of it",
    "makes an attack roll or a saving throw", "can add a d4 to its roll",
    "provided it can hear and understand", "can benefit from only one",
    "die at a time", "this effect ends if the", "is incapacitated",
)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip().casefold()


def leadership_actions_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    try:
        sections = source_sections_2014(monster.source_actions)
        actions = []
        for heading in monster.action_names:
            match = _HEADING.match(heading)
            if match is None:
                continue
            printed = _clean(sections.get(heading, ""))
            name = match.group("name").strip()
            if not all(fragment in printed for fragment in _REQUIRED) or f"one {name.casefold()} die" not in printed:
                continue
            slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
            actions.append(TimedSelfBuffAction(
                id=slug, name=name, action_cost="action", activation_timing="action",
                resource_id=slug, resource_cost=1, duration_rounds=10,
                friendly_roll_bonus_aura=TimedFriendlyRollBonusAura(
                    radius_ft=30, requires_hearing=True, requires_source_sight=True,
                    includes_source=False, stack_group=slug,
                    attack_dice_count=1, attack_dice_size=4, save_dice_count=1, save_dice_size=4,
                ),
                concentration=False, ends_if_source_incapacitated=True, ends_if_source_dead=True,
                animation="buff",
            ))
        return actions
    except Exception:
        logger.exception("Failed 2014 Leadership source binding for %s.", monster.name)
        raise


def leadership_labels_2014(monster: SourceMonster2014) -> set[str]:
    return {action.name.casefold() for action in leadership_actions_2014(monster)}


def leadership_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    # Short/Long Rest recharge: no rest occurs inside one Iron Pit fight -> one use.
    return [ResourceDefinition(id=a.resource_id, name=a.name, max_uses=1)
            for a in leadership_actions_2014(monster) if a.resource_id]
