from __future__ import annotations

import logging
import re

from app.content.basic_condition_actions import WAKE_SLEEPER_ID
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
_RECHARGE_LIMIT = r"Recharge\s+\d(?:\s*[-–]\s*\d)?"
_STAGED_CONDITION_SAVE = re.compile(
    rf"(?P<name>[A-Z][A-Za-z0-9’' -]*?)(?:\s+\((?P<limit>{_RECHARGE_LIMIT})\))?\.\s+"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    rf"DC\s+(?P<dc>\d+),\s+(?P<target>[^.]+)\.\s+"
    rf"(?:If\s+[^.]+\.\s+)?"
    rf"First Failure:\s+The target has the (?P<first>{_CONDITION}) condition and repeats the save "
    rf"at the end of its next turn if it is still (?P=first), ending the effect on itself on a success\.\s+"
    rf"Second Failure:\s+The target has the (?P<second>{_CONDITION}) condition instead of the (?P=first) condition\.",
    re.I,
)
_ESCALATING_REPEAT_SAVE = re.compile(
    rf"(?P<name>[A-Z][A-Za-z0-9’' -]*?)(?:\s+\((?P<limit>{_RECHARGE_LIMIT})\))?\.\s+"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    rf"DC\s+(?P<dc>\d+),\s+(?P<target>[^.]+)\.\s+"
    rf"First Failure:\s+The target has the (?P<first>{_CONDITION}) condition until the end of its next turn, "
    rf"(?:at which point|when) it repeats the save\.\s+"
    rf"Second Failure:\s+The target has the (?P<second>{_CONDITION}) condition, and it repeats the save at the end "
    rf"of each of its turns, ending the effect on itself on a success\.\s+After (?P<minutes>\d+) minute(?:s)?, it succeeds automatically\.",
    re.I,
)
_STAGED_TIMED_SLEEP = re.compile(
    rf"(?P<name>[A-Z][A-Za-z0-9’' -]*?)(?:\s+\((?P<limit>{_RECHARGE_LIMIT})\))?\.\s+"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    rf"DC\s+(?P<dc>\d+),\s+(?P<target>[^.]+)\.\s+"
    rf"First Failure:\s+The target has the (?P<first>{_CONDITION}) condition until the end of its next turn, "
    rf"at which point it repeats the save\.\s+Second Failure:\s+The target has the (?P<second>Unconscious) condition "
    rf"for (?P<sleep_minutes>\d+) minute(?:s)?\.\s+This effect ends for the target if it takes damage or a creature "
    rf"within 5 feet of it takes an action to wake it\.", re.I,
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _area(target: str) -> tuple[int, AreaTargeting | None]:
    cone = re.search(r"(\d+)-foot Cone", target, re.I)
    if cone:
        return 0, AreaTargeting(shape="cone", origin="self", length_ft=int(cone.group(1)))
    line = re.search(r"(\d+)-foot-long,\s*(\d+)-foot-wide Line", target, re.I)
    if line:
        return 0, AreaTargeting(shape="line", origin="self", length_ft=int(line.group(1)), width_ft=int(line.group(2)))
    within = re.search(r"within\s+(\d+)\s+feet", target, re.I)
    return (int(within.group(1)), None) if within else (0, None)


def _resource(monster: str, name: str, limit: str | None) -> ResourceDefinition | None:
    if not limit:
        return None
    recharge = re.fullmatch(r"Recharge\s+(\d)(?:\s*[-–]\s*(\d))?", limit, re.I)
    if recharge is None:
        return None
    return ResourceDefinition(
        id=f"srd-{_slug(monster)}-{_slug(name)}",
        name=name,
        max_uses=1,
        recharge=RechargeRule(minimum_roll=int(recharge.group(1))),
    )


def _candidate(monster: str, match: re.Match[str], action_cost: ActionCost) -> tuple[SaveCapabilityDefinition, ResourceDefinition | None]:
    name = match.group("name").strip(); ability = match.group("ability").lower(); dc = int(match.group("dc"))
    range_ft, area = _area(match.group("target")); resource = _resource(monster, name, match.groupdict().get("limit"))
    sleeping = "sleep_minutes" in match.re.groupindex
    effect = ConditionEffectDefinition(
        condition=match.group("first").lower(),
        repeat_save_ability=ability, repeat_save_dc=dc,
        repeat_save_timing="target_turn_end", repeat_save_failure_condition=match.group("second").lower(),
        repeat_save_failure_continues=not sleeping,
        repeat_save_failure_duration_rounds=int(match.group("sleep_minutes")) * 10 if sleeping else None,
        repeat_save_failure_ends_on_damage=sleeping,
        repeat_save_failure_allowed_removal_action_ids=[WAKE_SLEEPER_ID] if sleeping else [],
        automatic_success_after_rounds=(int(match.group("minutes")) * 10 if "minutes" in match.re.groupindex else None),
    )
    return SaveCapabilityDefinition(
        id=f"srd-{_slug(monster)}-{_slug(name)}", name=name, action_cost=action_cost,
        save_ability=ability, dc=dc, range_ft=range_ft, area=area, failure_effects=[effect],
        resource_id=resource.id if resource is not None else None, animation="save-effect",
    ), resource


def staged_condition_save_candidates(monster: str, text: str, action_cost: ActionCost) -> tuple[list[SaveCapabilityDefinition], list[ResourceDefinition]]:
    """Compile source-defined staged condition saves without monster-name branches."""
    try:
        actions: list[SaveCapabilityDefinition] = []; resources: list[ResourceDefinition] = []
        for pattern in (_STAGED_CONDITION_SAVE, _ESCALATING_REPEAT_SAVE, _STAGED_TIMED_SLEEP):
            for match in pattern.finditer(text):
                action, resource = _candidate(monster, match, action_cost)
                if all(existing.id != action.id for existing in actions): actions.append(action)
                if resource is not None and all(existing.id != resource.id for existing in resources): resources.append(resource)
        return actions, resources
    except (TypeError, ValueError):
        logger.exception("Invalid staged save source data for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Staged save parsing failed for %s.", monster)
        raise RuntimeError(f"Staged save parsing failed for {monster}.") from exc
