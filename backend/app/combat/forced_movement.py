from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant
from app.domain.models import SavingThrowAction, WeaponAttack
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def _eligible(target: EncounterCombatant, maximum) -> bool:
    if not target.state.is_alive or target.state.is_dead:
        return False
    return maximum is None or size_at_most(target.state.template.size, maximum)


def _push_away(
    source: EncounterCombatant,
    target: EncounterCombatant,
    distance: int,
    maximum,
) -> int:
    if distance <= 0 or not _eligible(target, maximum):
        return 0
    direction = 1 if target.position_ft >= source.position_ft else -1
    destination = max(0, target.position_ft + direction * distance)
    moved = abs(destination - target.position_ft)
    target.position_ft = destination
    return moved


def apply_attack_push(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    *,
    hit: bool,
) -> int:
    """Apply declarative straight-away movement and return feet moved."""
    try:
        if not hit:
            return 0
        return _push_away(
            attacker, target, attack.push_target_away_ft, attack.push_target_max_size,
        )
    except Exception as exc:
        logger.exception("Forced push failed for %s.", attack.id)
        raise RuntimeError("Forced push resolution failed.") from exc


def apply_save_failure_push(
    source: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    *,
    save_failed: bool,
) -> int:
    """Apply a declarative straight-away push after a failed saving throw."""
    try:
        if not save_failed:
            return 0
        return _push_away(
            source, target, action.push_target_away_ft, action.push_target_max_size,
        )
    except Exception as exc:
        logger.exception("Failed-save push failed for %s.", action.id)
        raise RuntimeError("Failed-save forced push resolution failed.") from exc


def apply_attack_pull(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    *,
    hit: bool,
) -> int:
    """Apply declarative straight-toward movement and return feet moved."""
    try:
        distance = attack.pull_target_toward_ft
        if not hit or distance <= 0 or not _eligible(target, attack.pull_target_max_size):
            return 0
        separation = abs(target.position_ft - attacker.position_ft)
        moved = min(distance, separation)
        if moved <= 0:
            return 0
        direction = -1 if target.position_ft >= attacker.position_ft else 1
        target.position_ft = max(0, target.position_ft + direction * moved)
        return moved
    except Exception as exc:
        logger.exception("Forced pull failed for %s.", attack.id)
        raise RuntimeError("Forced pull resolution failed.") from exc
