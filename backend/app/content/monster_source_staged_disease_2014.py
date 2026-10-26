"""Semantic 2014 source binding for delayed disease-stage attack effects."""
from __future__ import annotations

import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

_ATTACK = re.compile(
    r"Melee Weapon Attack:\s*\+(?P<hit>\d+) to hit,\s*"
    r"reach (?P<reach>\d+) ft\.,\s*one target\.\s*Hit:\s*"
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)\s*\+\s*(?P<bonus>\d+)\)"
    r" (?P<damage_type>\w+) damage\.",
    re.IGNORECASE,
)
_SAVE = re.compile(r"DC (?P<dc>\d+) Constitution saving throw or become diseased", re.I)
_DELAY = re.compile(r"disease has no effect for (?P<minutes>\d+) minute", re.I)
_LEVEL = re.compile(r"disease-curing spell of (?P<level>\d+)(?:st|nd|rd|th) level", re.I)

_PERIODIC = re.compile(
    r"When the creature is outside a body of water, it takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)\) acid damage "
    r"every (?P<minutes>\d+) minutes unless moisture is applied to the skin "
    r"before (?P<moisture_minutes>\d+) minutes have passed\.",
    re.IGNORECASE,
)


def source_proven_arena_neutral_periodic_2014(section: str) -> dict | None:
    """Audit a long-interval environmental rider without putting it in fight state."""
    match = _PERIODIC.search(section)
    if match is None or section[match.end():].strip():
        return None  # Unknown later source riders must fail closed.
    values = {key: int(value) for key, value in match.groupdict().items()}
    if (values["average"] != values["count"] * (values["size"] + 1) // 2
            or values["minutes"] != values["moisture_minutes"]
            or values["minutes"] < 10):
        return None
    return {
        "interval_minutes": values["minutes"],
        "moisture_suppression_minutes": values["moisture_minutes"],
        "dice_count": values["count"],
        "dice_size": values["size"],
        "damage_type": "acid",
    }



def supported_staged_disease_effect_2014(row: object) -> bool:
    if not isinstance(row, dict):
        return False
    return set(row) == {
        "save_ability", "dc", "effect_id", "cannot_regain_hit_points",
        "removal_effect_tag", "minimum_removal_spell_level",
        "removal_action_exceptions", "delayed_transition",
    } and isinstance(row["delayed_transition"], dict)


def source_bound_staged_disease_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Bind all in-Pit stages; source-proven ten-minute habitat rider is neutral."""
    if attack.source_complete or attack.kind != "melee" or attack.on_hit_save_effect:
        return attack
    section = source_sections_2014(
        monster.source_actions, include_continuations=True,
    ).get(attack.name, "")
    folded = section.casefold()
    required = (
        "any magic that cures disease", "after 1 minute",
        "disease can be removed only by", "heal",
        "regain hit points unless it is underwater",
        "skin becomes translucent and slimy",
    )
    save, delay, level = _SAVE.search(section), _DELAY.search(section), _LEVEL.search(section)
    periodic = source_proven_arena_neutral_periodic_2014(section)
    if not all(token in folded for token in required) or not all((save, delay, level)) or periodic is None:
        return attack
    for match in _ATTACK.finditer(section):
        row = match.groupdict()
        damage = attack.damage
        if (int(row["hit"]) != attack.attack_bonus
                or int(row["reach"]) != attack.reach_ft
                or int(row["average"]) != damage.average
                or int(row["count"]) != damage.dice_count
                or int(row["size"]) != damage.dice_size
                or int(row["bonus"]) != damage.bonus
                or row["damage_type"].lower() != damage.type):
            continue
        turns = int(delay.group("minutes")) * 10
        effect = {
            "save_ability": "constitution", "dc": int(save.group("dc")),
            "effect_id": "diseased", "cannot_regain_hit_points": False,
            "removal_effect_tag": "disease", "minimum_removal_spell_level": 0,
            "removal_action_exceptions": [],
            "delayed_transition": {
                "target_turns": turns, "cannot_regain_hit_points": True,
                "removal_effect_tag": "disease",
                "minimum_removal_spell_level": int(level.group("level")),
                "removal_action_exceptions": ["heal"],
            },
        }
        return attack.model_copy(update={
            "on_hit_save_effect": effect, "source_complete": True,
        })
    return attack
