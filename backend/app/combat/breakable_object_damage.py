"""Common fight-state damage resolver for breakable restraint or Grapple objects."""
from __future__ import annotations

import logging

from app.domain.breakable_restraints import BreakableObjectState

logger = logging.getLogger(__name__)

_VALID_DAMAGE = frozenset({
    "acid", "bludgeoning", "cold", "fire", "force", "lightning",
    "necrotic", "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
})


def damage_breakable_object_state(
    obj: BreakableObjectState,
    attack_total: int,
    rolled_damage: int,
    damage_type: str,
) -> tuple[int, bool]:
    """Consume object HP, never source HP, using declared immunity/vulnerability."""
    try:
        if attack_total < 0 or rolled_damage < 0:
            raise ValueError("Resolved attack/damage values must be nonnegative.")
        if attack_total < obj.armor_class:
            return 0, False
        if damage_type not in _VALID_DAMAGE:
            raise ValueError(f"Unknown breakable object damage type {damage_type!r}.")
        immunities = {part.value for part in obj.damage_immunities}
        vulnerabilities = {part.value for part in obj.damage_vulnerabilities}
        amount = 0 if damage_type in immunities else rolled_damage
        if amount and damage_type in vulnerabilities:
            amount *= 2
        applied = min(amount, obj.current_hp)
        obj.current_hp -= applied
        return applied, obj.current_hp == 0
    except Exception:
        logger.exception("Failed universal breakable object damage resolution.")
        raise
