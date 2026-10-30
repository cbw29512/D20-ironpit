from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.domain.models import DamageRollComponent, DamageType, SavingThrowAction
from app.domain.runtime import CombatantState
from app.domain.save_damage import SaveDamageComponent
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _profiles(action: SavingThrowAction) -> list[SaveDamageComponent]:
    try:
        profiles: list[SaveDamageComponent] = []
        if action.damage_dice_count:
            if action.damage_type is None:
                raise ValueError(f"{action.name} has damage dice but no damage type.")
            profiles.append(SaveDamageComponent(
                dice_count=action.damage_dice_count,
                dice_size=action.damage_dice_size,
                damage_bonus=action.damage_bonus,
                damage_type=DamageType(action.damage_type),
            ))
        profiles.extend(action.additional_damage_components)
        return profiles
    except Exception:
        logger.exception("Failed save-damage profile preparation for %s.", action.id)
        raise


def _component_rolls(
    action: SavingThrowAction,
    profiles: list[SaveDamageComponent],
    dice: DiceProvider,
    shared_damage_rolls: list[int] | None,
) -> list[list[int]]:
    try:
        if shared_damage_rolls is None:
            return [
                [dice.roll(profile.dice_size) for _ in range(profile.dice_count)]
                for profile in profiles
            ]
        expected = sum(profile.dice_count for profile in profiles)
        if len(shared_damage_rolls) != expected:
            raise ValueError(f"{action.name} shared damage roll count does not match its damage dice.")
        groups: list[list[int]] = []
        offset = 0
        for profile in profiles:
            group = shared_damage_rolls[offset:offset + profile.dice_count]
            if any(not 1 <= roll <= profile.dice_size for roll in group):
                raise ValueError(f"{action.name} shared damage rolls contain an invalid die result.")
            groups.append(list(group))
            offset += profile.dice_count
        return groups
    except Exception:
        logger.exception("Failed damage-roll preparation for save action %s.", action.id)
        raise


def _evasion_applies(action: SavingThrowAction, target: CombatantState | None) -> bool:
    try:
        return bool(
            target is not None
            and CombatTrait.EVASION in target.template.combat_traits
            and action.save_ability == "dexterity"
            and action.success_damage == "half"
            and not is_incapacitated(target)
        )
    except Exception:
        logger.exception("Failed Evasion check for save action %s.", action.id)
        raise


def build_save_damage_components(
    action: SavingThrowAction,
    dice: DiceProvider,
    succeeded: bool,
    shared_damage_rolls: list[int] | None = None,
    capture_shared_damage_rolls: list[int] | None = None,
    target: CombatantState | None = None,
) -> list[DamageRollComponent]:
    try:
        profiles = _profiles(action)
        if not profiles:
            return []
        needs_shared_roll = capture_shared_damage_rolls is not None
        evasion = _evasion_applies(action, target)
        if succeeded and (action.success_damage == "none" or evasion) and not needs_shared_roll:
            return []
        roll_groups = _component_rolls(action, profiles, dice, shared_damage_rolls)
        if capture_shared_damage_rolls is not None:
            capture_shared_damage_rolls.clear()
            capture_shared_damage_rolls.extend(
                roll for group in roll_groups for roll in group
            )
        if succeeded and (action.success_damage == "none" or evasion):
            return []

        components: list[DamageRollComponent] = []
        for profile, rolls in zip(profiles, roll_groups, strict=True):
            total = sum(rolls) + profile.damage_bonus
            if (succeeded and action.success_damage == "half") or (evasion and not succeeded):
                total //= 2
            components.append(DamageRollComponent(
                source=action.name,
                notation=f"{profile.dice_count}d{profile.dice_size}+{profile.damage_bonus}",
                rolls=rolls,
                modifier=profile.damage_bonus,
                damage_type=profile.damage_type,
                total=max(0, total),
            ))
        return components
    except Exception:
        logger.exception("Failed damage-component preparation for save action %s.", action.id)
        raise
