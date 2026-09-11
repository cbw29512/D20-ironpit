from __future__ import annotations

import logging
import re

from app.domain.actions import ActionCost
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.combatants import RechargeRule, ResourceDefinition
from app.domain.save_effects import ConditionEffectDefinition
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

_CONDITION = (
    r"Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Poisoned|"
    r"Prone|Restrained|Stunned|Unconscious|Petrified"
)
_STAGED_CONDITION_SAVE = re.compile(
    rf"(?P<name>[A-Z][A-Za-z0-9’' -]*?)(?:\s+\((?P<limit>Recharge\s+\d(?:-\d)?)\))?\.\s+"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    rf"DC\s+(?P<dc>\d+),\s+(?P<target>[^.]+)\.\s+"
    rf"(?:If\s+[^.]+\.\s+)?"
    rf"First Failure:\s+The target has the (?P<first>{_CONDITION}) condition and repeats the save "
    rf"at the end of its next turn if it is still (?P=first), ending the effect on itself on a success\.\s+"
    rf"Second Failure:\s+The target has the (?P<second>{_CONDITION}) condition instead of the (?P=first) condition\.",
    re.I,
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _area(target: str) -> tuple[int, AreaTargeting | None]:
    cone = re.search(r"(\d+)-foot Cone", target, re.I)
    if cone:
        return 0, AreaTargeting(shape="cone", origin="self", length_ft=int(cone.group(1)))
    line = re.search(r"(\d+)-foot-long,\s*(\d+)-foot-wide Line", target, re.I)
    if line:
        return 0, AreaTargeting(
            shape="line", origin="self", length_ft=int(line.group(1)), width_ft=int(line.group(2)),
        )
    within = re.search(r"within\s+(\d+)\s+feet", target, re.I)
    return (int(within.group(1)), None) if within else (0, None)


def _resource(monster: str, name: str, limit: str | None) -> ResourceDefinition | None:
    if not limit:
        return None
    recharge = re.fullmatch(r"Recharge\s+(\d)(?:-(\d))?", limit, re.I)
    if recharge is None:
        return None
    return ResourceDefinition(
        id=f"srd-{_slug(monster)}-{_slug(name)}",
        name=name,
        max_uses=1,
        recharge=RechargeRule(minimum_roll=int(recharge.group(1))),
    )


def staged_condition_save_candidates(
    monster: str,
    text: str,
    action_cost: ActionCost,
) -> tuple[list[SaveCapabilityDefinition], list[ResourceDefinition]]:
    """Compile complete first-failure/repeat-save/second-failure condition ladders."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        resources: list[ResourceDefinition] = []
        for match in _STAGED_CONDITION_SAVE.finditer(text):
            name = match.group("name").strip()
            ability = match.group("ability").lower()
            dc = int(match.group("dc"))
            range_ft, area = _area(match.group("target"))
            resource = _resource(monster, name, match.group("limit"))
            if resource is not None:
                resources.append(resource)
            effect = ConditionEffectDefinition(
                condition=match.group("first").lower(),
                repeat_save_ability=ability,
                repeat_save_dc=dc,
                repeat_save_timing="target_turn_end",
                repeat_save_failure_condition=match.group("second").lower(),
            )
            actions.append(SaveCapabilityDefinition(
                id=f"srd-{_slug(monster)}-{_slug(name)}",
                name=name,
                action_cost=action_cost,
                save_ability=ability,
                dc=dc,
                range_ft=range_ft,
                area=area,
                failure_effects=[effect],
                resource_id=resource.id if resource is not None else None,
                animation="save-effect",
            ))
        return actions, resources
    except (TypeError, ValueError):
        logger.exception("Invalid staged save source data for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Staged save parsing failed for %s.", monster)
        raise RuntimeError(f"Staged save parsing failed for {monster}.") from exc
