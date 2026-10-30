"""Generic on-hit delivery for Swallow actions embedded in an attack."""
from __future__ import annotations

import logging

from app.combat.swallow_state import swallow_after_bite
from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def apply_attack_hit_swallow(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    *,
    attacker_id: str,
    defender_id: str,
    pre_hit_grappled_by_attacker: bool,
) -> bool:
    """Apply only an attack-hit Swallow whose grapple existed before this hit."""
    try:
        if not pre_hit_grappled_by_attacker:
            return False
        rule = next(
            (
                item for item in attacker.template.swallow_actions
                if item.delivery_mode == "attack_hit"
                and item.attack_id == attack.id
            ),
            None,
        )
        if rule is None:
            return False
        return swallow_after_bite(
            attacker_id,
            attacker,
            defender_id,
            defender,
            rule,
            bite_hit=True,
        )
    except Exception:
        logger.exception(
            "Attack-hit Swallow delivery failed for %s with %s.",
            attacker.template.name,
            attack.id,
        )
        raise
