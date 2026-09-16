from __future__ import annotations

import logging

from app.content.fighter_2014_levels import FIGHTER_2014_LEVELS
from app.content.fighter_2014_progression import build_karnok_stoneward_2014_level
from app.domain.models import CombatantTemplate
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
Hero2014Key = tuple[str, int, str]


def _resource_map(template: CombatantTemplate) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def _assert_fighter_level(template: CombatantTemplate, level: int) -> None:
    row = FIGHTER_2014_LEVELS[level]
    if template.ruleset != "2014" or template.kind != "character":
        raise ValueError(f"2014 Fighter {level} crossed the ruleset/kind boundary.")
    if template.level != level or template.id != f"karnok-stoneward-2014-l{level}":
        raise ValueError(f"2014 Fighter {level} identity drifted.")
    if template.weapon_masteries:
        raise ValueError(f"2014 Fighter {level} illegally contains 2024 Weapon Mastery.")
    if template.max_hp != row.max_hp or template.armor_class != 17:
        raise ValueError(f"2014 Fighter {level} HP/AC drifted from its audited level row.")
    if template.progression_features.critical_hit_minimum != row.critical_hit_minimum:
        raise ValueError(f"2014 Fighter {level} Champion critical threshold drifted.")
    if template.progression_features.indomitable_bonus != 0:
        raise ValueError(f"2014 Fighter {level} illegally contains the 2024 Indomitable level bonus.")
    if CombatTrait.SAVAGE_ATTACKER in template.combat_traits:
        raise ValueError(f"2014 Fighter {level} illegally contains the 2024 Savage Attacker feat.")
    expected_traits = {CombatTrait.SAVAGE_ATTACKS, CombatTrait.RELENTLESS_ENDURANCE}
    if set(template.combat_traits) != expected_traits:
        raise ValueError(f"2014 Fighter {level} Half-Orc trait set drifted.")
    resources = _resource_map(template)
    expected = {"second-wind": 1, "relentless-endurance": 1}
    if row.action_surge_uses:
        expected["action-surge"] = row.action_surge_uses
    if row.indomitable_uses:
        expected["indomitable"] = row.indomitable_uses
    if resources != expected:
        raise ValueError(f"2014 Fighter {level} resource counts drifted: {resources} != {expected}.")
    if level < 5 and template.attack_action is not None:
        raise ValueError(f"2014 Fighter {level} received Extra Attack too early.")
    if level >= 5 and len(template.attack_action.slots if template.attack_action else []) != 2:
        raise ValueError(f"2014 Fighter {level} must have exactly two Attack-action attacks.")
    if any(attack.weapon.mastery_property for attack in [template.weapon_attack, *template.alternate_weapon_attacks]):
        raise ValueError(f"2014 Fighter {level} exported a 2024 weapon mastery property.")


def build_certified_hero_entries_2014() -> list[tuple[Hero2014Key, CombatantTemplate]]:
    """Return the contiguous source-audited 2014 Fighter/Champion test progression."""
    try:
        entries: list[tuple[Hero2014Key, CombatantTemplate]] = []
        for level in range(1, 11):
            template = build_karnok_stoneward_2014_level(level)
            _assert_fighter_level(template, level)
            entries.append((("fighter", level, "canonical-2014"), template))
        return entries
    except Exception:
        logger.exception("2014 canonical hero certification failed.")
        raise
