"""Compile immutable 2014 source death actions into shared save capabilities."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capabilities import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)
_DEATH_SAVE_TRIGGER = re.compile(
    r"\bwhen\b.+?\bdies\b.*?\bsaving throw\b", re.IGNORECASE,
)
_DAMAGE_DEATH_TRIGGER = re.compile(
    r"^When the .+? dies, it explodes, and each creature within (?P<range>\d+) feet "
    r"of it must make a DC (?P<dc>\d+) (?P<ability>[A-Za-z]+) saving throw, "
    r"taking (?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)\) "
    r"(?P<damage_type>[a-z]+) damage on a failed save, or half as much damage "
    r"on a successful one\. (?P<trailing>.+)$",
    re.IGNORECASE,
)
_CONDITION_DEATH_TRIGGER = re.compile(
    r"^When the .+? dies, it explodes in a burst of dust\\. Each creature within "
    r"(?P<range>\\d+) feet of it must then succeed on a DC (?P<dc>\\d+) "
    r"(?P<ability>[A-Za-z]+) saving throw or be (?P<condition>[a-z]+) for "
    r"(?P<minutes>\\d+) minute(?:s)?\\. A (?P=condition) creature can repeat the "
    r"saving throw on each of its turns, ending the effect on itself on a success\\.$",
    re.IGNORECASE,
)
_IGNORED_OBJECT_AFTERMATH = re.compile(
    r"^The explosion ignites flammable objects in that area that aren't being worn "
    r"or carried, and it destroys the .+?'s weapons\.$",
    re.IGNORECASE,
)


def semantic_death_trigger_names_2014(monster: SourceMonster2014) -> tuple[str, ...]:
    """Find printed death-save effects by trigger/effect semantics, not labels."""
    sections = source_sections_2014(monster.source_traits)
    return tuple(name for name, body in sections.items() if _DEATH_SAVE_TRIGGER.search(body))


def _compile(raw: object) -> SaveCapabilityDefinition:
    if not isinstance(raw, dict):
        raise ValueError("Death Trigger action must be a structured source declaration.")
    required = {
        "id", "name", "save_ability", "dc", "range_ft", "damage_dice_count",
        "damage_dice_size", "damage_bonus", "damage_type", "success_damage", "area",
    }
    missing = sorted(required - set(raw))
    if missing:
        raise ValueError(f"Death Trigger action is missing fields: {', '.join(missing)}")
    expected_area = {
        "shape": "emanation", "origin": "self", "radius_ft": raw["range_ft"],
    }
    if raw["area"] != expected_area:
        raise ValueError(f"Unsupported Death Trigger geometry: {raw!r}")
    return SaveCapabilityDefinition(
        id=str(raw["id"]),
        name=str(raw["name"]),
        save_ability=raw["save_ability"],
        dc=raw["dc"],
        range_ft=raw["range_ft"],
        max_targets=20,
        target_scope="all-other-creatures",
        area=raw["area"],
        damage=DiceSpec(
            count=raw["damage_dice_count"],
            size=raw["damage_dice_size"],
            bonus=raw["damage_bonus"],
        ),
        damage_type=raw["damage_type"],
        success_damage=raw["success_damage"],
        animation=raw.get("animation", "death-trigger"),
    )


def _source_damage_action(name: str, body: str) -> SaveCapabilityDefinition | None:
    match = _DAMAGE_DEATH_TRIGGER.fullmatch(body)
    if match is None or _IGNORED_OBJECT_AFTERMATH.fullmatch(match["trailing"]) is None:
        return None
    count, size, average = int(match["count"]), int(match["size"]), int(match["average"])
    if count < 1 or size < 2 or average != count * (size + 1) // 2:
        return None
    radius = int(match["range"])
    effect_id = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return SaveCapabilityDefinition(
        id=effect_id, name=name, save_ability=match["ability"].casefold(),
        dc=int(match["dc"]), range_ft=radius, max_targets=20,
        target_scope="all-other-creatures",
        area={"shape": "emanation", "origin": "self", "radius_ft": radius},
        damage=DiceSpec(count=count, size=size),
        damage_type=match["damage_type"].casefold(), success_damage="half",
        animation="death-trigger",
    )


def _source_condition_action(name: str, body: str) -> SaveCapabilityDefinition | None:
    match = _CONDITION_DEATH_TRIGGER.fullmatch(body)
    if match is None:
        return None
    condition = match["condition"].casefold()
    if condition != "blinded":
        return None
    radius, dc = int(match["range"]), int(match["dc"])
    effect_id = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return SaveCapabilityDefinition(
        id=effect_id, name=name, save_ability=match["ability"].casefold(),
        dc=dc, range_ft=radius, max_targets=20,
        target_scope="all-other-creatures",
        area={"shape": "emanation", "origin": "self", "radius_ft": radius},
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id=condition,
            duration_rounds=int(match["minutes"]) * 10,
            expiry_timing="target_turn_end",
            repeat_save_ability=match["ability"].casefold(),
            repeat_save_dc=dc,
            repeat_save_timing="target_turn_end",
        ),
        animation="death-trigger",
    )


def death_trigger_actions_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Compile structured declarations or exact source-proven damage triggers."""
    if monster.death_trigger_actions:
        return [_compile(raw) for raw in monster.death_trigger_actions]
    sections = source_sections_2014(monster.source_traits)
    return [
        action for name in semantic_death_trigger_names_2014(monster)
        if (action := _source_damage_action(name, sections[name])
            or _source_condition_action(name, sections[name])) is not None
    ]


def supports_death_triggers_2014(monster: SourceMonster2014) -> bool:
    semantic_names = semantic_death_trigger_names_2014(monster)
    if not monster.death_trigger_actions and not semantic_names:
        return True
    try:
        actions = death_trigger_actions_2014(monster)
        return (
            len(actions) == len(semantic_names)
            and len({action.id for action in actions}) == len(actions)
        )
    except (KeyError, TypeError, ValueError):
        logger.info("Unsupported 2014 Death Trigger source shape for %s.", monster.id)
        return False
