"""Universal single-target spell group selection and geometry validation.

Source data optionally declares maximum distance BETWEEN all selected targets.
Fight state and target locations remain encounter-owned.
"""
from __future__ import annotations

from itertools import combinations
import logging
from typing import Sequence

from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def target_group_within_distance(
    targets: Sequence[EncounterCombatant], maximum_pair_distance_ft: int | None,
) -> bool:
    """Validate every pair, not just distance from the caster or first target."""
    try:
        if maximum_pair_distance_ft is None or len(targets) < 2:
            return True
        return all(
            combatant_distance(first, second) <= maximum_pair_distance_ft
            for first, second in combinations(targets, 2)
        )
    except Exception:
        logger.exception("Failed to validate the selected spell target group.")
        raise


def choose_spell_target_group(
    ranked: Sequence[EncounterCombatant],
    target_cap: int,
    maximum_pair_distance_ft: int | None,
) -> list[EncounterCombatant]:
    """Choose the largest legal group, preserving the current target ranking."""
    try:
        if target_cap < 1:
            raise ValueError("A spell target group must have a positive capacity.")
        if maximum_pair_distance_ft is None:
            return list(ranked[:target_cap])
        for group_size in range(min(target_cap, len(ranked)), 0, -1):
            for group in combinations(ranked, group_size):
                if target_group_within_distance(group, maximum_pair_distance_ft):
                    return list(group)
        return []
    except Exception:
        logger.exception("Failed to choose a constrained spell target group.")
        raise


def validate_spell_target_group(
    setup,
    target_ids: Sequence[str],
    maximum_pair_distance_ft: int | None,
) -> None:
    """Fail closed on invalid groups before any resource/action mutation."""
    try:
        if maximum_pair_distance_ft is None:
            return
        if len(set(target_ids)) != len(target_ids):
            raise ValueError("A spell target group cannot repeat a target.")
        members = {
            member.combatant_id: member
            for member in [*setup.heroes, *setup.monsters]
        }
        if any(target_id not in members for target_id in target_ids):
            raise ValueError("A spell target group contains an unknown target.")
        targets = [members[target_id] for target_id in target_ids]
        if not target_group_within_distance(targets, maximum_pair_distance_ft):
            raise ValueError("Spell targets exceed their declared pairwise distance.")
    except Exception:
        logger.exception("Spell target group is invalid.")
        raise
