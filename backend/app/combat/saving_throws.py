from __future__ import annotations

from app.combat.undead_fortitude import consume_survival_save_log
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log

from app.combat.action_economy import is_available, spend
from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.grapple import apply_grapple
from app.combat.failed_d20_test_override import source_name_for_roll
from app.combat.defensive_modifier_rules import saving_throw_advantage_source_names
from app.combat.rogue_defenses import evasion_damage
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll, EncounterCombatant, SavingThrowAction
from app.domain.runtime import CombatantState\nfrom app.domain.save_damage import SaveDamageComponent
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.size import size_at_most


def legal_save_action(action: SavingThrowAction, target: EncounterCombatant, distance_ft: int) -> bool:
    if distance_ft > action.range_ft: return False
    return action.target_max_size is None or size_at_most(target.state.template.size, action.target_max_size)


def _damage_specs(action: SavingThrowAction) -> list[SaveDamageComponent]:
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


def _shared_component_rolls(
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


def _damage_rolls(spec: SaveDamageComponent, dice: DiceProvider, shared: list[int] | None) -> list[int]:
    rolls = [dice.roll(spec.dice_size) for _ in range(spec.dice_count)] if shared is None else list(shared)
    if len(rolls) != spec.dice_count or any(not 1 <= roll <= spec.dice_size for roll in rolls):
        raise ValueError("Shared save damage rolls do not match the component dice.")
    return rolls


def _damage_components(
    state: CombatantState,
    action: SavingThrowAction,
    dice: DiceProvider,
    succeeded: bool,
    shared_damage_rolls: list[int] | list[list[int]] | None = None,
) -> list[DamageRollComponent]:
    specs = _damage_specs(action)
    if not specs or (succeeded and action.success_damage == "none"):
        return []
    shared = _shared_component_rolls(specs, shared_damage_rolls)
    components: list[DamageRollComponent] = []
    for spec, component_rolls in zip(specs, shared, strict=True):
        rolls = _damage_rolls(spec, dice, component_rolls)
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
    return components
