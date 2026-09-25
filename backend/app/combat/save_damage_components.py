from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.rogue_defenses import evasion_damage
from app.domain.models import DamageRollComponent, DamageType, SavingThrowAction
from app.domain.runtime import CombatantState
from app.domain.save_damage import SaveDamageComponent

logger = logging.getLogger(__name__)


def _damage_specs(action: SavingThrowAction) -> list[SaveDamageComponent]:
    try:
        if action.damage_components:
            if action.damage_dice_count or action.damage_type is not None or action.damage_bonus:
                raise ValueError(f"{action.name} mixes component and legacy save damage.")
            return list(action.damage_components)
        if action.damage_dice_count == 0:
            return []
        if action.damage_type is None:
            raise ValueError(f"{action.name} has damage dice but no damage type.")
        return [SaveDamageComponent(
            dice_count=action.damage_dice_count,
            dice_size=action.damage_dice_size,
            damage_bonus=action.damage_bonus,
            damage_type=action.damage_type,
        )]
    except Exception:
        logger.exception("Failed to derive save damage components for %s.", action.id)
        raise


def _shared_rolls(
    specs: list[SaveDamageComponent],
    shared: list[int] | list[list[int]] | None,
) -> list[list[int] | None]:
    if shared is None:
        return [None] * len(specs)
    if len(specs) == 1 and all(isinstance(item, int) for item in shared):
        return [list(shared)]
    if len(shared) != len(specs) or not all(isinstance(item, list) for item in shared):
        raise ValueError("Shared save damage rolls do not match the component count.")
    return [list(item) for item in shared]


def resolve_save_damage_components(
    state: CombatantState,
    action: SavingThrowAction,
    dice: DiceProvider,
    succeeded: bool,
    shared_damage_rolls: list[int] | list[list[int]] | None = None,
) -> tuple[int, list[DamageRollComponent], list[DamageRollComponent]]:
    try:
        specs = _damage_specs(action)
        if not specs or (succeeded and action.success_damage == "none"):
            return 0, [], []
        components: list[DamageRollComponent] = []
        for spec, shared in zip(specs, _shared_rolls(specs, shared_damage_rolls), strict=True):
            rolls = [dice.roll(spec.dice_size) for _ in range(spec.dice_count)] if shared is None else list(shared)
            if len(rolls) != spec.dice_count or any(not 1 <= roll <= spec.dice_size for roll in rolls):
                raise ValueError("Shared save damage rolls do not match the component dice.")
            raw_total = sum(rolls) + spec.damage_bonus
            total = evasion_damage(state, action.save_ability, succeeded, action.success_damage, raw_total)
            components.append(DamageRollComponent(
                source=action.name,
                notation=f"{spec.dice_count}d{spec.dice_size}+{spec.damage_bonus}",
                rolls=rolls,
                modifier=spec.damage_bonus,
                damage_type=DamageType(spec.damage_type),
                total=max(0, total),
            ))
        applied_total, applied_components = apply_damage_defenses(state, components)
        return applied_total, components, applied_components
    except Exception:
        logger.exception("Failed to resolve save damage components for %s.", action.id)
        raise
