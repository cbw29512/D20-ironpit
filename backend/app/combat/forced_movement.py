from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant
from app.domain.models import WeaponAttack
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def apply_attack_push(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    *,
    hit: bool,
) -> int:
    """Apply a declarative straight-away push and return feet moved."""
    try:
        distance = attack.push_target_away_ft
        if not hit or distance <= 0:
            return 0
        maximum = attack.push_target_max_size
        if maximum is not None and not size_at_most(target.state.template.size, maximum):
            return 0
        direction = 1 if target.position_ft >= attacker.position_ft else -1
        destination = max(0, target.position_ft + direction * distance)
        moved = abs(destination - target.position_ft)
        target.position_ft = destination
        return moved
    except Exception as exc:
        logger.exception(
            "Forced push failed: %s -> %s via %s.",
            attacker.state.template.name,
            target.state.template.name,
            attack.weapon.name,
        )
        raise RuntimeError("Forced movement resolution failed.") from exc
