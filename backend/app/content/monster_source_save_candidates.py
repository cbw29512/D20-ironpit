from __future__ import annotations

import re

from app.content.monster_source_save_riders import common_failure_riders
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.combatants import RechargeRule, ResourceDefinition
from app.domain.targeting import AreaTargeting
from app.domain.weapons import DamageType

_SAVE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)(?:\s+\((?P<limit>Recharge\s+\d(?:-\d)?|\d+/Day)\))?\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+DC\s+(?P<dc>\d+),\s+"
    r"(?P<target>[^.]+)\.\s+Failure:\s+(?P<average>\d+)\s+\((?P<count>\d+)d(?P<size>\d+)"
    r"(?:\s*(?P<sign>[+-])\s*(?P<mod>\d+))?\)\s+(?P<dtype>[A-Za-z]+) damage"
    r"(?P<failure_tail>(?:,\s+and\s+[^.]+|\.\s+If\s+the\s+target\s+[^.]+)*)\."
    r"(?:\s+Success:\s+(?P<success>Half damage|No damage)(?:\s+only)?\.)?", re.I,
)
_CONTROL_SAVE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)(?:\s+\((?P<limit>Recharge\s+\d(?:-\d)?|\d+/Day)\))?\.\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+DC\s+(?P<dc>\d+),\s+"
    r"(?P<target>[^.]+)\.\s+Failure:\s+(?P<failure>The target has the "
    r"(?:Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Poisoned|Prone|Restrained|Stunned|Unconscious) condition "
    r"until the (?:start|end) of (?:its|the [^.]+?[’']s) next turn)\.", re.I,
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
    emanation = re.search(r"(\d+)-foot Emanation", target, re.I)
    if emanation:
        return 0, AreaTargeting(shape="emanation", origin="self", radius_ft=int(emanation.group(1)))
    radius = re.search(r"(\d+)-foot-radius Sphere", target, re.I)
    within = re.search(r"within\s+(\d+)\s+feet", target, re.I)
    if radius and within:
        return int(within.group(1)), AreaTargeting(shape="radius", origin="point", radius_ft=int(radius.group(1)))
    return int(within.group(1)) if within else 0, None


def _resource(monster: str, name: str, limit: str | None) -> ResourceDefinition | None:
    if not limit:
        return None
    resource_id = f"srd-{_slug(monster)}-{_slug(name)}"
    recharge = re.fullmatch(r"Recharge\s+(\d)(?:-(\d))?", limit, re.I)
    if recharge:
        return ResourceDefinition(id=resource_id, name=name, max_uses=1, recharge=RechargeRule(minimum_roll=int(recharge.group(1))))
    per_day = re.fullmatch(r"(\d+)/Day", limit, re.I)
    if per_day:
        return ResourceDefinition(id=resource_id, name=name, max_uses=int(per_day.group(1)))
    return None


def _control_action(monster: str, match: re.Match[str]) -> tuple[SaveCapabilityDefinition, ResourceDefinition | None]:
    name = match.group("name").strip()
    resource = _resource(monster, name, match.group("limit"))
    range_ft, area = _area(match.group("target"))
    riders = common_failure_riders(match.group("target"), match.group("failure"))
    return SaveCapabilityDefinition(
        id=f"srd-{_slug(monster)}-{_slug(name)}", name=name, save_ability=match.group("ability").lower(),
        dc=int(match.group("dc")), range_ft=range_ft, area=area,
        resource_id=resource.id if resource else None, animation="save-effect", **riders,
    ), resource


def source_save_candidates(row: dict[str, object]) -> tuple[list[SaveCapabilityDefinition], list[ResourceDefinition]]:
    actions: list[SaveCapabilityDefinition] = []
    resources: list[ResourceDefinition] = []
    monster = str(row["name"])
    text = str(row.get("actions", ""))
    for match in _SAVE.finditer(text):
        name = match.group("name").strip()
        bonus = int(match.group("mod") or 0) * (-1 if match.group("sign") == "-" else 1)
        range_ft, area = _area(match.group("target"))
        resource = _resource(monster, name, match.group("limit"))
        if resource:
            resources.append(resource)
        success = "half" if (match.group("success") or "").lower() == "half damage" else "none"
        riders = common_failure_riders(match.group("target"), match.group("failure_tail") or "")
        actions.append(SaveCapabilityDefinition(
            id=f"srd-{_slug(monster)}-{_slug(name)}", name=name, save_ability=match.group("ability").lower(), dc=int(match.group("dc")),
            range_ft=range_ft, area=area, damage=DiceSpec(count=int(match.group("count")), size=int(match.group("size")), bonus=bonus),
            damage_type=DamageType(match.group("dtype").lower()), success_damage=success,
            resource_id=resource.id if resource else None, animation="save-effect", **riders,
        ))
    existing = {action.id for action in actions}
    for match in _CONTROL_SAVE.finditer(text):
        action, resource = _control_action(monster, match)
        if action.id in existing:
            continue
        actions.append(action)
        if resource:
            resources.append(resource)
    return actions, resources
