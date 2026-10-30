from __future__ import annotations

import logging
import re

from app.content.monster_source_limited_resources import source_limited_resource
from app.content.monster_source_save_riders import common_failure_riders
from app.domain.actions import ActionCost
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.combatants import ResourceDefinition
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_MOVEMENT_LED_SAVE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\s+"
    r"\((?P<limit>Recharge\s+\d(?:\s*[-–]\s*\d)?)\)\.\s+"
    r"(?P<lead>.*?moves up to .*?Speed.*?\.)\s+"
    r"(?P<target>Each creature whose space the [^.]+ enters is targeted once by the following effect)\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    r"DC\s+(?P<dc>\d+)\.\s+"
    r"Failure:\s+(?P<average>\d+)\s+\((?P<count>\d+)d(?P<size>\d+)"
    r"(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\)\s+"
    r"(?P<dtype>[A-Za-z]+) damage(?P<tail>[^.]*)\.",
    re.IGNORECASE,
)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to slug movement-led save value %r.", value)
        raise RuntimeError("Movement-led save id could not be derived.") from exc


def movement_led_save_candidates(
    monster: str,
    text: str,
    action_cost: ActionCost,
    *,
    abstract_range_ft: int,
) -> tuple[list[SaveCapabilityDefinition], list[ResourceDefinition]]:
    """Compile a save whose targets are defined by movement through creature spaces."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        resources: list[ResourceDefinition] = []
        for match in _MOVEMENT_LED_SAVE.finditer(text):
            name = match.group("name").strip()
            action_id = f"srd-{_slug(monster)}-{_slug(name)}"
            resource = source_limited_resource(action_id, name, match.group("limit"))
            if resource is None:
                raise ValueError(f"{name} requires a Recharge resource.")
            resources.append(resource)

            bonus = int(match.group("bonus") or 0)
            if match.group("sign") == "-":
                bonus *= -1
            riders = common_failure_riders("", match.group("tail") or "")
            actions.append(SaveCapabilityDefinition(
                id=action_id,
                name=name,
                action_cost=action_cost,
                save_ability=match.group("ability").lower(),
                dc=int(match.group("dc")),
                range_ft=abstract_range_ft,
                damage=DiceSpec(
                    count=int(match.group("count")),
                    size=int(match.group("size")),
                    bonus=bonus,
                ),
                damage_type=DamageType(match.group("dtype").lower()),
                success_damage="none",
                resource_id=resource.id,
                animation="charge",
                **riders,
            ))
        return actions, resources
    except (TypeError, ValueError):
        logger.exception("Invalid movement-led save source for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Movement-led save parsing failed for %s.", monster)
        raise RuntimeError(f"Movement-led save parsing failed for {monster}.") from exc
