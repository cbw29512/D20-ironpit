from __future__ import annotations

import logging

from app.combat.modifier_stack import add_modifier
from app.combat.weapon_mastery import weapon_mastery_active
from app.domain.models import CombatantState, WeaponAttack
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)
SLOW_EFFECT_ID = "weapon-mastery-slow"
SLOW_SPEED_PENALTY = -10


def weapon_slow_eligible(state: CombatantState, attack: WeaponAttack) -> bool:
    try:
        return weapon_mastery_active(state, attack, "Slow")
    except Exception:
        logger.exception("Slow mastery eligibility failed for %s.", state.template.name)
        raise


def apply_weapon_slow(
    attacker: CombatantState,
    attacker_id: str,
    target: CombatantState,
    attack: WeaponAttack,
    round_number: int,
) -> bool:
    """Hit with a mastered Slow weapon reduces the target's Speed by 10 feet until the attacker's next turn."""
    try:
        if target.is_dead or target.current_hp <= 0:
            return False
        if not weapon_slow_eligible(attacker, attack):
            return False
        add_modifier(target, CombatModifier(
            id=f"{attacker_id}:{SLOW_EFFECT_ID}:{target.template.id}",
            source_id=attacker_id,
            source_effect_id=SLOW_EFFECT_ID,
            source_name="Slow",
            kind=ModifierKind.SPEED,
            flat_bonus=SLOW_SPEED_PENALTY,
            expires_at_start_of_source_turn=True,
        ))
        return True
    except Exception:
        logger.exception("Slow mastery application failed for %s.", attacker.template.name)
        raise
