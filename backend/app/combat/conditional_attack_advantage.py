from __future__ import annotations

import logging

from app.combat.hit_points import effective_max_hp
from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def conditional_attack_advantage_sources(attack: WeaponAttack, target: CombatantState) -> int:
    """Return declarative attack-roll Advantage sources satisfied by target state."""
    try:
        total = 0
        for spec in attack.conditional_attack_advantage:
            if spec.trigger == "target_not_full_hp":
                total += int(target.current_hp < effective_max_hp(target))
                continue
            raise ValueError(f"Unsupported conditional attack Advantage trigger: {spec.trigger!r}.")
        return total
    except Exception:
        logger.exception("Failed to evaluate conditional attack Advantage for %s.", attack.id)
        raise
