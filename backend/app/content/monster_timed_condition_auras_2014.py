from __future__ import annotations

import html
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.combatants import ResourceDefinition
from app.domain.timed_aura_components import TimedHostileConditionAura
from app.domain.timed_control_limits import TimedControlLimits
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_FETID_CLOUD = re.compile(
    r"(?P<name>Fetid Cloud) \(1/Day\)\. A (?P<radius>\d+)-foot radius .*?"
    r"It lasts for (?P<minutes>\d+) minute .*?"
    r"DC (?P<dc>\d+) Constitution saving throw or be poisoned until the start of its next turn\. "
    r"While poisoned in this way, the target can take either an action or a bonus action on its turn, "
    r"not both, and can['’]t take reactions",
    re.IGNORECASE | re.DOTALL,
)


def _match(monster: SourceMonster2014):
    text = html.unescape(monster.source_actions or "").replace("\u00ad", "")
    return _FETID_CLOUD.search(text)


def timed_condition_aura_action_names_2014(monster: SourceMonster2014) -> set[str]:
    """Return exact source Action labels consumed by the generic timed-aura binder."""
    try:
        if _match(monster) is None:
            return set()
        return {
            name.casefold()
            for name in monster.action_names
            if name.casefold().startswith("fetid cloud (1/day)")
        }
    except Exception:
        logger.exception("Failed to classify 2014 timed condition aura action for %s.", monster.name)
        raise


def timed_condition_aura_actions_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind source-declared timed save/condition emanations without runtime name dispatch."""
    try:
        match = _match(monster)
        if match is None:
            return []
        action_id = f"2014-{monster.id}-fetid-cloud"
        return [TimedSelfBuffAction(
            id=action_id,
            name=match.group("name"),
            action_cost="action",
            activation_timing="action",
            resource_id=f"{action_id}-use",
            duration_rounds=int(match.group("minutes")) * 10,
            expiry_timing="source_turn_start",
            hostile_start_turn_condition_aura=TimedHostileConditionAura(
                radius_ft=int(match.group("radius")),
                save_ability="constitution",
                save_dc=int(match.group("dc")),
                condition_id="poisoned",
                source_is_magical=False,
                condition_duration_rounds=1,
                condition_expiry_timing="target_turn_start",
                recipient_scope="all",
                suppress_reactions=True,
                control_limits=TimedControlLimits(action_bonus_exclusive=True),
                effect_tags=["poison"],
            ),
            priority=20,
            animation="poison",
        )]
    except Exception:
        logger.exception("Failed to bind 2014 timed condition aura action for %s.", monster.name)
        raise


def timed_condition_aura_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    """Create the printed once-per-day resource for each bound timed aura Action."""
    try:
        return [
            ResourceDefinition(id=action.resource_id, name=action.name, max_uses=1)
            for action in timed_condition_aura_actions_2014(monster)
            if action.resource_id is not None
        ]
    except Exception:
        logger.exception("Failed to bind 2014 timed condition aura resources for %s.", monster.name)
        raise
