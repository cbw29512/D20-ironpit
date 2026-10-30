from __future__ import annotations

import logging
import re

from app.content.monster_source_save_riders import common_failure_riders, target_max_size
from app.domain.actions import ActionCost
from app.domain.capability_attacks import SaveCapabilityDefinition

logger = logging.getLogger(__name__)
_GRAPPLE_SAVE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    r"DC\s+(?P<dc>\d+),\s+(?P<target>[^.]+)\.\s+"
    r"Failure:\s+The target has the Grappled condition\s*"
    r"\(escape DC\s*(?P<escape>\d+)\)\.",
    re.IGNORECASE,
)
_WITHIN = re.compile(r"\bwithin\s+(\d+)\s+feet\b", re.IGNORECASE)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to slug grapple-save value %r.", value)
        raise RuntimeError("Grapple-save id could not be derived.") from exc


def grapple_save_candidates(
    monster: str,
    text: str,
    action_cost: ActionCost,
) -> list[SaveCapabilityDefinition]:
    """Compile source actions whose failed save applies an escapable grapple."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        for match in _GRAPPLE_SAVE.finditer(text):
            target = match.group("target")
            within = _WITHIN.search(target)
            range_ft = int(within.group(1)) if within else 5
            failure = (
                f"The target has the Grappled condition "
                f"(escape DC {match.group('escape')})"
            )
            riders = common_failure_riders(target, failure)
            action = SaveCapabilityDefinition(
                id=f"srd-{_slug(monster)}-{_slug(match.group('name'))}",
                name=match.group("name").strip(),
                action_cost=action_cost,
                save_ability=match.group("ability").lower(),
                dc=int(match.group("dc")),
                range_ft=range_ft,
                target_max_size=target_max_size(target),
                animation="grapple",
                **riders,
            )
            actions.append(action)
        return actions
    except (TypeError, ValueError):
        logger.exception("Invalid grapple-save source data for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Grapple-save parsing failed for %s.", monster)
        raise RuntimeError(f"Grapple-save parsing failed for {monster}.") from exc
