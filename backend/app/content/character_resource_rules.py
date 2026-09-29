from __future__ import annotations

from collections.abc import Callable

from app.content.character_resource_rules_2024 import (
    CLASS_RULES_2024,
    SPECIES_RULES_2024,
    SUBCLASS_RULES_2024,
)
from app.content.level_resources import (
    barbarian_2014_rage_uses,
    cleric_2014_channel_divinity_uses,
    cleric_2014_divine_intervention_uses,
    fighter_2014_action_surge_uses,
    fighter_2014_indomitable_uses,
    fighter_2014_second_wind_uses,
)
from app.content.ranger_2014_resource_audit import ranger_2014_spell_slot_resources
from app.content.spell_slot_progression import FULL_CASTER_CLASSES, spell_slot_resources
from app.content.warlock_2014_resource_audit import warlock_2014_resources
from app.domain.character_builds import CharacterBuildProfile

ResourceRule = tuple[str, str, Callable[[int], int]]

_PALADIN_2014_SLOTS = {
    1: (), 2: (2,), 3: (3,), 4: (3,), 5: (4, 2), 6: (4, 2), 7: (4, 3),
    8: (4, 3), 9: (4, 3, 2), 10: (4, 3, 2), 11: (4, 3, 3), 12: (4, 3, 3),
    13: (4, 3, 3, 1), 14: (4, 3, 3, 1), 15: (4, 3, 3, 2), 16: (4, 3, 3, 2),
    17: (4, 3, 3, 3, 1), 18: (4, 3, 3, 3, 1), 19: (4, 3, 3, 3, 2),
    20: (4, 3, 3, 3, 2),
}


def _monk_ki(level: int) -> int:
    return level if level >= 2 else 0


def _monk_wholeness(level: int) -> int:
    return 1 if level >= 6 else 0


def _paladin_channel(level: int) -> int:
    return 1 if level >= 3 else 0


def _rogue_stroke(level: int) -> int:
    return 1 if level >= 20 else 0


def _sorcery_points(level: int) -> int:
    return level if level >= 2 else 0


def _wild_shape(level: int) -> int:
    return 2 if 2 <= level < 20 else 0


def _finite_rage(level: int) -> int:
    return 0 if level >= 20 else barbarian_2014_rage_uses(level)


_2014_CLASS_RULES: dict[str, tuple[ResourceRule, ...]] = {
    "barbarian": (("rage", "Rage", _finite_rage),),
    "bard": (("bardic-inspiration", "Bardic Inspiration", lambda level: 3 if level < 4 else 4 if level < 8 else 5),),
    "cleric": (
        ("channel-divinity", "Channel Divinity", cleric_2014_channel_divinity_uses),
        ("divine-intervention", "Divine Intervention", cleric_2014_divine_intervention_uses),
    ),
    "druid": (("wild-shape", "Wild Shape", _wild_shape),),
    "fighter": (
        ("second-wind", "Second Wind", fighter_2014_second_wind_uses),
        ("action-surge", "Action Surge", fighter_2014_action_surge_uses),
        ("indomitable", "Indomitable", fighter_2014_indomitable_uses),
    ),
    "monk": (("ki", "Ki", _monk_ki), ("wholeness-of-body", "Wholeness of Body", _monk_wholeness)),
    "paladin": (
        ("lay-on-hands", "Lay on Hands", lambda level: 5 * level),
        ("channel-divinity", "Channel Divinity", _paladin_channel),
    ),
    "ranger": (),
    "rogue": (("stroke-of-luck", "Stroke of Luck", _rogue_stroke),),
    "sorcerer": (("sorcery-points", "Sorcery Points", _sorcery_points),),
    "warlock": (),
    "wizard": (),
}

_2014_UNLIMITED = {
    "barbarian": lambda level: ("rage",) if level >= 20 else (),
    "druid": lambda level: ("wild-shape",) if level >= 20 else (),
}


def class_resource_rules(profile: CharacterBuildProfile) -> dict[str, tuple[ResourceRule, ...]]:
    return _2014_CLASS_RULES if profile.ruleset == "2014" else CLASS_RULES_2024


def expected_resources(profile: CharacterBuildProfile) -> dict[str, int]:
    class_rules = class_resource_rules(profile)
    species_rules = {} if profile.ruleset == "2014" else SPECIES_RULES_2024
    subclass_rules = (
        SUBCLASS_RULES_2024.get(profile.subclass_id or "", ())
        if profile.ruleset == "2024"
        else ()
    )
    rules = [
        *class_rules.get(profile.class_id, ()),
        *subclass_rules,
        *species_rules.get(profile.species_id, ()),
    ]
    resolved = {resource_id: resolver(profile.level) for resource_id, _name, resolver in rules}
    if profile.ruleset == "2024" and profile.class_id in FULL_CASTER_CLASSES:
        resolved.update(spell_slot_resources(profile.class_id, profile.level))
    if profile.ruleset == "2014" and profile.class_id in {"bard", "cleric", "druid", "sorcerer", "wizard"}:
        resolved.update(spell_slot_resources(profile.class_id, profile.level))
    if profile.ruleset == "2014" and profile.class_id == "ranger":
        resolved.update(ranger_2014_spell_slot_resources(profile.level))
    if profile.ruleset == "2014" and profile.class_id == "warlock":
        resolved.update(warlock_2014_resources(profile.level))
    if profile.ruleset == "2014" and profile.class_id == "paladin":
        resolved.update({
            f"spell-slot-{spell_level}": uses
            for spell_level, uses in enumerate(_PALADIN_2014_SLOTS[profile.level], start=1)
        })
        if profile.level >= 14:
            resolved["cleansing-touch"] = profile.final_ability_scores.modifier("charisma")
        if profile.level >= 20:
            resolved["holy-nimbus"] = 1
    if profile.ruleset == "2014" and profile.class_id == "wizard" and profile.level >= 20:
        resolved.update({"signature-spell-fireball": 1, "signature-spell-lightning-bolt": 1})
    return {resource_id: uses for resource_id, uses in resolved.items() if uses > 0}


def expected_unlimited_resources(profile: CharacterBuildProfile) -> tuple[str, ...]:
    if profile.ruleset != "2014":
        return ()
    resolver = _2014_UNLIMITED.get(profile.class_id)
    return resolver(profile.level) if resolver else ()
