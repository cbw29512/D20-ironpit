from __future__ import annotations

import re

from app.content.monster_source_save_riders import common_failure_riders, slowing_breath_rider
from app.domain.actions import ActionCost, ConditionName
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.combatants import RechargeRule, ResourceDefinition
from app.domain.save_effects import TimedPenaltyEffectDefinition
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
_RESTRICTION_SAVE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+(?P<ability>\w+) Saving Throw:\s+DC\s+(?P<dc>\d+),\s+"
    r"(?P<target>[^.]+)\.\s+Failure:\s+(?P<failure>The target can[’']t take Reactions;[^.]+\.\s+"
    r"This effect lasts until the end of its next turn)\.", re.I,
)
_PENALTY_SAVE = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+(?P<ability>\w+) Saving Throw:\s+DC\s+(?P<dc>\d+),\s+"
    r"(?P<target>[^.]+)\.\s+Failure:\s+The target has Disadvantage on (?P<penalty_ability>\w+)-based D20 Tests "
    r"and subtracts \d+ \((?P<count>\d+)d(?P<size>\d+)\) from its damage rolls\.\s+It repeats the save at the end "
    r"of each of its turns, ending the effect on itself on a success\.\s+After (?P<minutes>\d+) minute(?:s)?, it succeeds automatically\.", re.I,
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _breath_name(value: str) -> str:
    words = value.strip().split()
    return " ".join(words[-2:]) if words and words[-1].lower() == "breath" and len(words) >= 2 else value.strip()


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


def _required_condition(target: str) -> ConditionName | None:
    match = re.search(r"has the (Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Poisoned|Prone|Restrained|Stunned|Unconscious) condition", target, re.I)
    return match.group(1).lower() if match else None


def _resource(monster: str, name: str, limit: str | None) -> ResourceDefinition | None:
    if not limit:
        return None
    resource_id = f"srd-{_slug(monster)}-{_slug(name)}"
    recharge = re.fullmatch(r"Recharge\s+(\d)(?:-(\d))?", limit, re.I)
    if recharge:
        return ResourceDefinition(id=resource_id, name=name, max_uses=1, recharge=RechargeRule(minimum_roll=int(recharge.group(1))))
    per_day = re.fullmatch(r"(\d+)/Day", limit, re.I)
    return ResourceDefinition(id=resource_id, name=name, max_uses=int(per_day.group(1))) if per_day else None


def _base_control(monster: str, match: re.Match[str], effects: list[object], action_cost: ActionCost) -> SaveCapabilityDefinition:
    name = _breath_name(match.group("name")); target = match.group("target")
    range_ft, area = _area(target)
    return SaveCapabilityDefinition(
        id=f"srd-{_slug(monster)}-{_slug(name)}", name=name, action_cost=action_cost,
        save_ability=match.group("ability").lower(), dc=int(match.group("dc")), range_ft=range_ft, area=area,
        required_target_condition=_required_condition(target), failure_effects=effects, animation="save-effect",
    )


def _parse_text(monster: str, text: str, action_cost: ActionCost) -> tuple[list[SaveCapabilityDefinition], list[ResourceDefinition]]:
    actions: list[SaveCapabilityDefinition] = []; resources: list[ResourceDefinition] = []
    for match in _SAVE.finditer(text):
        name = match.group("name").strip(); target = match.group("target")
        bonus = int(match.group("mod") or 0) * (-1 if match.group("sign") == "-" else 1)
        range_ft, area = _area(target); resource = _resource(monster, name, match.group("limit"))
        if resource: resources.append(resource)
        success = "half" if (match.group("success") or "").lower() == "half damage" else "none"
        riders = common_failure_riders(target, match.group("failure_tail") or "")
        actions.append(SaveCapabilityDefinition(
            id=f"srd-{_slug(monster)}-{_slug(name)}", name=name, action_cost=action_cost,
            save_ability=match.group("ability").lower(), dc=int(match.group("dc")), range_ft=range_ft, area=area,
            required_target_condition=_required_condition(target),
            damage=DiceSpec(count=int(match.group("count")), size=int(match.group("size")), bonus=bonus),
            damage_type=DamageType(match.group("dtype").lower()), success_damage=success,
            resource_id=resource.id if resource else None, animation="save-effect", **riders,
        ))
    existing = {action.id for action in actions}
    for match in _CONTROL_SAVE.finditer(text):
        riders = common_failure_riders(match.group("target"), match.group("failure"))
        action = _base_control(monster, match, list(riders.pop("failure_effects")), action_cost).model_copy(update=riders)
        if action.id not in existing: actions.append(action); existing.add(action.id)
    for match in _RESTRICTION_SAVE.finditer(text):
        restriction = slowing_breath_rider(match.group("failure"))
        if restriction is None: continue
        action = _base_control(monster, match, [restriction], action_cost)
        if action.id not in existing: actions.append(action); existing.add(action.id)
    for match in _PENALTY_SAVE.finditer(text):
        name = _breath_name(match.group("name"))
        penalty = TimedPenaltyEffectDefinition(
            effect_family=f"{_slug(monster)}-{_slug(name)}", d20_disadvantage_ability=match.group("penalty_ability").lower(),
            damage_penalty_dice_count=int(match.group("count")), damage_penalty_dice_size=int(match.group("size")),
            repeat_save_ability=match.group("ability").lower(), repeat_save_dc=int(match.group("dc")),
            repeat_save_timing="target_turn_end", automatic_success_after_rounds=int(match.group("minutes")) * 10,
        )
        action = _base_control(monster, match, [penalty], action_cost).model_copy(update={"forbid_target_affected_by_action": True})
        if action.id not in existing: actions.append(action); existing.add(action.id)
    return actions, resources


def source_save_candidates(row: dict[str, object]) -> tuple[list[SaveCapabilityDefinition], list[ResourceDefinition]]:
    monster = str(row["name"]); actions: list[SaveCapabilityDefinition] = []; resources: list[ResourceDefinition] = []
    for field, cost in (("actions", "action"), ("bonusActions", "bonus_action")):
        parsed, parsed_resources = _parse_text(monster, str(row.get(field, "")), cost)
        actions.extend(parsed); resources.extend(parsed_resources)
    unique_actions = {action.id: action for action in actions}
    unique_resources = {resource.id: resource for resource in resources}
    return list(unique_actions.values()), list(unique_resources.values())
