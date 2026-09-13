from __future__ import annotations

import logging

from app.combat.healing import restore_hit_points
from app.combat.max_hp import reduce_max_hp
from app.domain.event_support import DamageRollComponent
from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def resolve_max_hp_drain(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    damage_components: list[DamageRollComponent],
) -> tuple[int, int]:
    """Resolve fight-scoped max-HP drain from post-defense damage components."""
    try:
        effect = attack.max_hp_drain
        if effect is None:
            return 0, 0
        amount = sum(
            component.applied_total
            for component in damage_components
            if getattr(component.damage_type, "value", component.damage_type) == effect.damage_type
        )
        if amount <= 0:
            return 0, 0
        reduced = reduce_max_hp(defender, amount, kill_at_zero=effect.zero_max_hp_kills)
        healed = restore_hit_points(attacker, reduced) if effect.heal_attacker else 0
        return reduced, healed
    except Exception:
        logger.exception("Failed max-HP drain for %s using %s.", attacker.template.name, attack.id)
        raise
