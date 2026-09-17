from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DamageRollComponent, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def can_deflect_missiles(defender: CombatantState, attack: WeaponAttack) -> bool:
    try:
        return bool(
            defender.template.progression_features.deflect_missiles
            and attack.weapon.attack_kind is WeaponAttackKind.RANGED
            and is_available(defender, "reaction")
            and defender.current_hp > 0
        )
    except Exception:
        logger.exception("Failed Deflect Missiles eligibility check for %s", defender.template.id)
        raise


def apply_deflect_missiles(
    defender: CombatantState,
    attack: WeaponAttack,
    components: list[DamageRollComponent],
    dice: DiceProvider,
) -> tuple[list[DamageRollComponent], bool, int]:
    """Reduce ranged-weapon damage by 1d10 + Dexterity modifier + Monk level."""
    try:
        if not components or not can_deflect_missiles(defender, attack):
            return components, False, 0
        scores = defender.template.ability_scores
        if scores is None or defender.template.level is None:
            raise ValueError("Deflect Missiles requires character abilities and level.")
        reduction = dice.roll(10) + scores.modifier("dexterity") + defender.template.level
        spend(defender, "reaction")
        remaining = reduction
        reduced: list[DamageRollComponent] = []
        for component in components:
            applied_reduction = min(component.total, remaining)
            reduced.append(
                component.model_copy(update={"total": component.total - applied_reduction})
            )
            remaining -= applied_reduction
        return reduced, True, reduction
    except Exception:
        logger.exception("Failed Deflect Missiles resolution for %s", defender.template.id)
        raise
