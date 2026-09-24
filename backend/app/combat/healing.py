from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.dice import DiceProvider
from app.combat.healing_policy import (
    choose_healing_action,
    choose_healing_target,
    resource_available,
    slot_heal,
    target_allowed,
)
from app.combat.healing_resolution_support import (
    resolve_healing_amount,
    resolve_percentile_healing_gate,
    spend_healing_resource,
)
from app.combat.spellcasting import mark_slot_spell_cast
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, DiceRoll, HealingAction


def resolve_healing(
    sequence: int,
    round_number: int,
    healer: EncounterCombatant,
    target: EncounterCombatant,
    action: HealingAction,
    dice: DiceProvider,
    turn_key: str | None = None,
) -> BattleEvent:
    if not target_allowed(healer, target, action) or not resource_available(healer, action, turn_key):
        raise ValueError("Healing action is not legal for this target or turn.")
    if slot_heal(action):
        if turn_key is None:
            raise ValueError("Spell-slot healing requires an active turn key.")
        mark_slot_spell_cast(healer.state, turn_key)

    spend(healer.state, action.action_cost)
    remaining = spend_healing_resource(healer, action)
    feature_roll, failure = resolve_percentile_healing_gate(
        sequence,
        round_number,
        healer,
        target,
        action,
        dice,
        remaining,
    )
    if failure is not None:
        return failure

    hp_before = target.state.current_hp
    rolls, roll_total, healed, notation, modifier = resolve_healing_amount(target, action, dice)
    description = (
        f"{healer.state.template.name} uses {action.name} on {target.state.template.name} "
        f"and restores {healed} HP."
    )
    if feature_roll is not None:
        description = (
            f"{healer.state.template.name} uses {action.name} and rolls {feature_roll.total} on d100; "
            f"the intervention succeeds. {target.state.template.name} is restored for {healed} HP."
        )

    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="healing",
        actor_id=healer.combatant_id,
        actor_name=healer.state.template.name,
        target_id=target.combatant_id,
        target_name=target.state.template.name,
        feature_roll=feature_roll,
        healing_roll=DiceRoll(
            notation=notation,
            rolls=rolls,
            modifier=modifier,
            total=roll_total,
        ),
        hp_before=hp_before,
        hp_after=target.state.current_hp,
        death_save_successes=target.state.death_save_successes,
        death_save_failures=target.state.death_save_failures,
        is_stable=target.state.is_stable,
        is_dead=target.state.is_dead,
        feature_id=action.id,
        resource_remaining=remaining,
        animation=action.animation,
        description=description,
    )
