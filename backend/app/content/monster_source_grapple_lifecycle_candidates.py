from __future__ import annotations

import logging
import re

from app.content.monster_source_save_riders import target_max_size
from app.domain.actions import ActionCost
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import GrappleEffectDefinition
from app.domain.save_effects import PeriodicDamageEffectDefinition
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_PATTERN = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    r"DC\s+(?P<dc>\d+),\s+(?P<target>[^.]+)\.\s+"
    r"Failure:\s+The target is pulled into [^.]+ space and has the Grappled condition "
    r"\(escape DC\s*(?P<escape>\d+)\)\.\s+"
    r"Until the grapple ends, the target has the (?P<linked>[A-Za-z]+(?: and [A-Za-z]+)*) conditions, "
    r"and it takes \d+ \((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\) "
    r"(?P<dtype>[A-Za-z]+) damage at the start of each of its turns\..*?"
    r"can have only (?P<max>one|\d+) creature Grappled by this action at a time\.",
    re.IGNORECASE,
)
_WITHIN = re.compile(r"within\s+(\d+)\s+feet", re.IGNORECASE)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed grapple-lifecycle slug for %r.", value)
        raise RuntimeError("Grapple-lifecycle id could not be derived.") from exc


def grapple_lifecycle_save_candidates(
    monster: str,
    text: str,
    action_cost: ActionCost,
) -> list[SaveCapabilityDefinition]:
    """Compile save-gated grapples with linked conditions and periodic damage."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        for match in _PATTERN.finditer(text):
            target = match.group("target")
            within = _WITHIN.search(target)
            range_ft = int(within.group(1)) if within else 5
            conditions = [
                item.strip().lower()
                for item in re.split(r"\s+and\s+", match.group("linked"))
            ]
            restrains = "restrained" in conditions
            linked = [item for item in conditions if item != "restrained"]
            bonus = int(match.group("bonus") or 0)
            if match.group("sign") == "-":
                bonus *= -1
            maximum = 1 if match.group("max").lower() == "one" else int(match.group("max"))
            actions.append(SaveCapabilityDefinition(
                id=f"srd-{_slug(monster)}-{_slug(match.group('name'))}",
                name=match.group("name").strip(),
                action_cost=action_cost,
                save_ability=match.group("ability").lower(),
                dc=int(match.group("dc")),
                range_ft=range_ft,
                target_max_size=target_max_size(target),
                grapple=GrappleEffectDefinition(
                    escape_dc=int(match.group("escape")),
                    max_target_size=target_max_size(target),
                    restrains=restrains,
                    linked_conditions=linked,
                    periodic_damage=PeriodicDamageEffectDefinition(
                        timing="target_turn_start",
                        dice_count=int(match.group("count")),
                        dice_size=int(match.group("size")),
                        damage_bonus=bonus,
                        damage_type=DamageType(match.group("dtype").lower()),
                    ),
                ),
                max_active_grapple_targets=maximum,
                animation="grapple",
            ))
        return actions
    except (TypeError, ValueError):
        logger.exception("Invalid grapple-lifecycle source for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Grapple-lifecycle parsing failed for %s.", monster)
        raise RuntimeError(f"Grapple-lifecycle parsing failed for {monster}.") from exc
