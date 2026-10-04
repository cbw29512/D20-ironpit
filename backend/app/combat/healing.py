from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.pooled_healing import bind_pool_healing_action
from app.combat.dice import DiceProvider
from app.combat.healing_policy import (
    choose_healing_action,
    choose_healing_target,
    resource_available,
    slot_heal,
    target_allowed,
)
from app.combat.healing_resolution_support import (
    apply_healing_riders,
    resolve_healing_amount,
    resolve_percentile_healing_gate,
    spend_healing_resource,
)
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.zero_hp_stabilization import stabilize_at_zero
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, DiceRoll, HealingAction


logger = logging.getLogger(__name__)


def resolve_healing(
    sequence: int,
    round_number: int,
    healer: EncounterCombatant,
    target: EncounterCombatant,
    action: HealingAction,
    dice: DiceProvider,
    turn_key: str | None = None,
) -> BattleEvent:
    try:
        if (not is_available(healer.state, action.action_cost)
            or not target_allowed(healer, target, action) or not resource_available(healer, action, turn_key)):
            raise ValueError("Healing action is not legal for this target or turn.")
        action = bind_pool_healing_action(healer, target, action)
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
        if action.stabilize_at_zero:
            stabilize_at_zero(target.state)
            rolls, roll_total, healed, notation, modifier = [], 0, 0, "stabilize", 0
            removed = []
            description = (
                f"{healer.state.template.name} uses {action.name} on {target.state.template.name} "
                f"and stabilizes them."
            )
        else:
            rolls, roll_total, healed, notation, modifier = resolve_healing_amount(healer, target, action, dice)
            removed = apply_healing_riders(target, action)
            rider_text = (
                " Conditions ended: " + ", ".join(item.replace("_", " ").title() for item in removed) + "."
                if removed else ""
            )
            restored = "Temporary HP" if action.grants_temporary_hp else "HP"
            description = (
                f"{healer.state.template.name} uses {action.name} on {target.state.template.name} "
                f"and restores {healed} {restored}." + rider_text
            )
        if feature_roll is not None:
            description = (
                f"{healer.state.template.name} uses {action.name} and rolls {feature_roll.total} on d100; "
                f"the intervention succeeds. {target.state.template.name} is restored for {healed} HP."
                + rider_text
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
            removed_condition_ids=removed,
            resource_remaining=remaining,
            animation=action.animation,
            description=description,
        )
    except Exception:
        logger.exception("Healing rejected or failed: %s -> %s (%s).", healer.combatant_id, target.combatant_id, action.id)
        raise
