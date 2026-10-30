from __future__ import annotations

import logging
import re

from app.content.monster_source_limited_resources import source_limited_resource
from app.content.monster_source_save_riders import common_failure_riders
from app.content.movement_modes import parse_movement_profile
from app.domain.actions import ActionCost
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.combatants import ResourceDefinition
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_MOVEMENT_SAVE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\s+"
    r"\((?P<limit>Recharge\s+\d(?:\s*[-–]\s*\d)?)\)\.\s+"
    r"[^.]*?moves up to its Speed[^.]*\.\s+"
    r"[^.]*?targeted once by the following effect\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    r"DC\s+(?P<dc>\d+)\.\s+"
    r"Failure:\s+\d+\s+\((?P<count>\d+)d(?P<size>\d+)"
    r"(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\)\s+"
    r"(?P<dtype>[A-Za-z]+) damage(?P<tail>,\s+and\s+[^.]+)?\.",
    re.IGNORECASE,
)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to derive movement-save id from %r.", value)
        raise RuntimeError("Movement-save id could not be derived.") from exc


def movement_save_candidates(
    monster: str,
    source_speed: object,
    text: str,
    action_cost: ActionCost,
) -> tuple[list[SaveCapabilityDefinition], list[ResourceDefinition]]:
    """Compile save effects preceded by source movement that the Pit abstracts away."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        resources: list[ResourceDefinition] = []
        speed = parse_movement_profile(source_speed).walk_ft
        for match in _MOVEMENT_SAVE.finditer(text):
            if speed <= 0:
                raise ValueError(f"{match.group('name')} requires a positive source Speed.")
            name = match.group("name").strip()
            action_id = f"srd-{_slug(monster)}-{_slug(name)}"
            resource = source_limited_resource(action_id, name, match.group("limit"))
            if resource is None:
                raise ValueError(f"{name} Recharge marker did not compile to a resource.")
            bonus = int(match.group("bonus") or 0)
            if match.group("sign") == "-":
                bonus *= -1
            riders = common_failure_riders("one creature", match.group("tail") or "")
            actions.append(SaveCapabilityDefinition(
                id=action_id,
                name=name,
                action_cost=action_cost,
                save_ability=match.group("ability").lower(),
                dc=int(match.group("dc")),
                range_ft=speed,
                damage=DiceSpec(
                    count=int(match.group("count")),
                    size=int(match.group("size")),
                    bonus=bonus,
                ),
                damage_type=DamageType(match.group("dtype").lower()),
                success_damage="none",
                resource_id=resource.id,
                animation="charge-save",
                **riders,
            ))
            resources.append(resource)
        return actions, resources
    except (TypeError, ValueError):
        logger.exception("Invalid movement-save source data for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Movement-save parsing failed for %s.", monster)
        raise RuntimeError(f"Movement-save parsing failed for {monster}.") from exc
