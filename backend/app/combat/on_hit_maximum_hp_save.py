from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.dice import DiceProvider
from app.combat.restoration_riders import apply_hit_point_maximum_reduction_state
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.models import CombatantState, DiceRoll, WeaponAttack
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnHitMaximumHpSaveResolution:
    save_roll: DiceRoll | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None
    reduction_applied: int = 0
    killed_by_zero_maximum: bool = False


def resolve_on_hit_maximum_hp_save(
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    damage_taken: int,
) -> OnHitMaximumHpSaveResolution:
    """Resolve a save that reduces maximum HP by an already-applied damage amount."""
    try:
        effect = attack.on_hit_maximum_hp_save
        if effect is None or defender.is_dead or not defender.is_alive:
            return OnHitMaximumHpSaveResolution()
        if damage_taken < 0:
            raise ValueError("Damage taken cannot be negative for a maximum-HP reduction rider.")
        save_roll, succeeded = resolve_saving_throw(
            defender,
            effect.save_ability,
            effect.dc,
            dice,
            SavingThrowContext(),
        )
        reduced = 0
        killed = False
        if not succeeded and effect.reduction == "damage_taken" and damage_taken:
            reduced = apply_hit_point_maximum_reduction_state(
                defender,
                damage_taken,
                zero_max_hp_kills=effect.zero_max_hp_kills,
            )
            killed = defender.is_dead
        return OnHitMaximumHpSaveResolution(
            save_roll=save_roll,
            save_ability=effect.save_ability,
            save_dc=effect.dc,
            save_succeeded=succeeded,
            reduction_applied=reduced,
            killed_by_zero_maximum=killed,
        )
    except Exception:
        logger.exception("Failed to resolve on-hit maximum-HP save for %s.", defender.template.name)
        raise
