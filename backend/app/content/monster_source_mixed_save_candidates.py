from __future__ import annotations

import logging
import re

from app.content.monster_source_save_riders import common_failure_riders
from app.domain.actions import ActionCost
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.save_damage import SaveDamageComponent
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_MIXED_SAVE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    r"DC\s+(?P<dc>\d+),\s+(?P<target>[^.]+)\.\s+"
    r"Failure:\s+\d+\s+\((?P<count1>\d+)d(?P<size1>\d+)"
    r"(?:\s*(?P<sign1>[+-])\s*(?P<bonus1>\d+))?\)\s+"
    r"(?P<type1>[A-Za-z]+) damage plus\s+"
    r"\d+\s+\((?P<count2>\d+)d(?P<size2>\d+)"
    r"(?:\s*(?P<sign2>[+-])\s*(?P<bonus2>\d+))?\)\s+"
    r"(?P<type2>[A-Za-z]+) damage\.\s*"
    r"(?P<tail>The target[^.]+(?:\.\s*[^.]+)*)?",
    re.IGNORECASE,
)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to derive mixed-save id from %r.", value)
        raise RuntimeError("Mixed-save id could not be derived.") from exc


def _bonus(match: re.Match[str], suffix: str) -> int:
    try:
        value = int(match.group(f"bonus{suffix}") or 0)
        return -value if match.group(f"sign{suffix}") == "-" else value
    except Exception as exc:
        logger.exception("Failed to parse mixed-save damage bonus.")
        raise RuntimeError("Mixed-save damage bonus could not be parsed.") from exc


def mixed_save_candidates(
    monster: str,
    text: str,
    action_cost: ActionCost,
) -> list[SaveCapabilityDefinition]:
    """Compile failed saves with two independently typed damage components."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        for match in _MIXED_SAVE.finditer(text):
            name = match.group("name").strip()
            riders = common_failure_riders(
                match.group("target"),
                match.group("tail") or "",
            )
            actions.append(SaveCapabilityDefinition(
                id=f"srd-{_slug(monster)}-{_slug(name)}",
                name=name,
                action_cost=action_cost,
                save_ability=match.group("ability").lower(),
                dc=int(match.group("dc")),
                range_ft=int(
                    (re.search(r"within\s+(\d+)\s+feet", match.group("target"), re.I) or ["", "5"])[1]
                ),
                damage=DiceSpec(
                    count=int(match.group("count1")),
                    size=int(match.group("size1")),
                    bonus=_bonus(match, "1"),
                ),
                damage_type=DamageType(match.group("type1").lower()),
                additional_damage_components=[SaveDamageComponent(
                    dice_count=int(match.group("count2")),
                    dice_size=int(match.group("size2")),
                    damage_bonus=_bonus(match, "2"),
                    damage_type=DamageType(match.group("type2").lower()),
                )],
                success_damage="none",
                animation="save-effect",
                **riders,
            ))
        return actions
    except (TypeError, ValueError):
        logger.exception("Invalid mixed-save source data for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Mixed-save parsing failed for %s.", monster)
        raise RuntimeError(f"Mixed-save parsing failed for {monster}.") from exc
