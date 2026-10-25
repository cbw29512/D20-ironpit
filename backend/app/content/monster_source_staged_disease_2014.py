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
    """Bind the reachable stage; unresolved later clauses keep source incomplete."""
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
    )
    save, delay, level = _SAVE.search(section), _DELAY.search(section), _LEVEL.search(section)
    if not all(token in folded for token in required) or not all((save, delay, level)):
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
        return attack.model_copy(update={"on_hit_save_effect": effect})
    return attack
