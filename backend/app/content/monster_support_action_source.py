from __future__ import annotations

import logging
import re

from app.content.monster_source_limited_resources import source_limited_resource
from app.domain.combatants import ResourceDefinition
from app.domain.support_actions import CombatSupportAction

logger = logging.getLogger(__name__)
_SUPPORT = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\s+"
    r"\((?P<limit>Recharge\s+\d(?:\s*[-–]\s*\d)?)\)\.\s+"
    r"The [^.]+ or one creature of its choice that can see or hear it gains "
    r"\d+ \((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\) "
    r"Temporary Hit Points and has Advantage on attack rolls until the start of the [^.]+[’']s next turn\.",
    re.IGNORECASE,
)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to slug support-action value %r.", value)
        raise RuntimeError("Support-action id could not be derived.") from exc


def source_support_actions(
    monster: str,
    text: str,
    action_cost: str,
) -> tuple[list[CombatSupportAction], list[ResourceDefinition]]:
    try:
        actions: list[CombatSupportAction] = []
        resources: list[ResourceDefinition] = []
        for match in _SUPPORT.finditer(text):
            name = match.group("name").strip()
            action_id = f"srd-{_slug(monster)}-{_slug(name)}"
            resource = source_limited_resource(action_id, name, match.group("limit"))
            if resource is None:
                raise ValueError(f"{name} requires a Recharge resource.")
            bonus = int(match.group("bonus") or 0)
            if match.group("sign") == "-":
                bonus *= -1
            resources.append(resource)
            actions.append(CombatSupportAction(
                id=action_id,
                name=name,
                action_cost=action_cost,
                target_mode="self_or_ally",
                temporary_hp_dice_count=int(match.group("count")),
                temporary_hp_dice_size=int(match.group("size")),
                temporary_hp_bonus=bonus,
                attack_roll_advantage_until_source_turn_start=True,
                resource_id=resource.id,
                animation="war-cry",
            ))
        return actions, resources
    except (TypeError, ValueError):
        logger.exception("Invalid support-action source for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Support-action parsing failed for %s.", monster)
        raise RuntimeError(f"Support-action parsing failed for {monster}.") from exc
