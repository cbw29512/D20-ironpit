from __future__ import annotations

import logging

from app.combat.offensive_range_profile import OffensiveRangeProfile
from app.combat.offensive_save_ranges import save_action_profiles
from app.combat.offensive_spell_ranges import spell_profiles
from app.combat.offensive_weapon_ranges import weapon_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)
OffensiveRange = tuple[str, int]
RankedOffensiveRange = tuple[int, str, int]


def ranked_offensive_range_profiles_for_target(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    turn_key: str,
    setup: EncounterSetup | None = None,
) -> list[OffensiveRangeProfile]:
    try:
        return [
            *weapon_profiles(attacker, target, setup),
            *spell_profiles(attacker, turn_key, target, setup),
            *save_action_profiles(attacker, target),
        ]
    except Exception:
        logger.exception(
            "Failed offensive-range profile inventory for %s against %s.",
            attacker.combatant_id,
            target.combatant_id,
        )
        raise


def ranked_offensive_ranges_for_target(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    turn_key: str,
) -> list[RankedOffensiveRange]:
    try:
        return [
            (profile.priority, profile.family, profile.max_range_ft)
            for profile in ranked_offensive_range_profiles_for_target(attacker, target, turn_key)
        ]
    except Exception:
        logger.exception(
            "Failed ranked offensive-range inventory for %s against %s.",
            attacker.combatant_id,
            target.combatant_id,
        )
        raise


def offensive_ranges_for_target(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    turn_key: str,
) -> list[OffensiveRange]:
    try:
        return [
            (family, distance)
            for _, family, distance in ranked_offensive_ranges_for_target(attacker, target, turn_key)
        ]
    except Exception:
        logger.exception(
            "Failed offensive-range inventory for %s against %s.",
            attacker.combatant_id,
            target.combatant_id,
        )
        raise
