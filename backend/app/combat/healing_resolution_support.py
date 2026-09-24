from __future__ import annotations

from app.combat.defensive_modifier_rules import healing_is_maximized
from app.combat.dice import DiceProvider
from app.combat.hit_points import effective_max_hp
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, DiceRoll, HealingAction


def spend_healing_resource(
    healer: EncounterCombatant,
    action: HealingAction,
) -> int | None:
    if action.resource_id is None:
        return None
    resource = next(item for item in healer.state.resources if item.id == action.resource_id)
    resource.current_uses -= action.resource_cost
    return resource.current_uses


def resolve_percentile_healing_gate(
    sequence: int,
    round_number: int,
    healer: EncounterCombatant,
    target: EncounterCombatant,
    action: HealingAction,
    dice: DiceProvider,
    remaining: int | None,
) -> tuple[DiceRoll | None, BattleEvent | None]:
    if action.percentile_success_max is None:
        return None, None
    rolled = dice.roll(100)
    feature_roll = DiceRoll(
        notation="1d100",
        rolls=[rolled],
        selected_roll=rolled,
        total=rolled,
    )
    if rolled <= action.percentile_success_max:
        return feature_roll, None
    return feature_roll, BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=healer.combatant_id,
        actor_name=healer.state.template.name,
        target_id=target.combatant_id,
        target_name=target.state.template.name,
        feature_roll=feature_roll,
        hp_before=target.state.current_hp,
        hp_after=target.state.current_hp,
        death_save_successes=target.state.death_save_successes,
        death_save_failures=target.state.death_save_failures,
        is_stable=target.state.is_stable,
        is_dead=target.state.is_dead,
        feature_id=action.id,
        resource_remaining=remaining,
        animation=action.animation,
        description=(
            f"{healer.state.template.name} uses {action.name} and rolls {rolled} on d100; "
            f"the intervention fails (needed {action.percentile_success_max} or lower)."
        ),
    )


def resolve_healing_amount(
    target: EncounterCombatant,
    action: HealingAction,
    dice: DiceProvider,
) -> tuple[list[int], int, int, str, int]:
    if action.restore_to_effective_max:
        amount = effective_max_hp(target.state) - target.state.current_hp
        healed = restore_hit_points(target.state, amount)
        return [], healed, healed, "restore-to-effective-max", 0
    rolls = (
        [action.dice_size for _ in range(action.dice_count)]
        if healing_is_maximized(target.state)
        else [dice.roll(action.dice_size) for _ in range(action.dice_count)]
    )
    total = sum(rolls) + action.healing_bonus
    healed = restore_hit_points(target.state, total)
    notation = (
        f"{action.dice_count}d{action.dice_size}+{action.healing_bonus}"
        if action.dice_count else str(action.healing_bonus)
    )
    return rolls, total, healed, notation, action.healing_bonus
