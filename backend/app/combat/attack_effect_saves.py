from __future__ import annotations

from app.combat.conditions import apply_condition
from app.combat.d20_tests import resolve_saving_throw
from app.combat.dice import DiceProvider
from app.domain.models import AttackEffect, BattleEvent, CombatantState


def resolve_save_condition_effect(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    effect: AttackEffect,
    dice: DiceProvider,
) -> list[BattleEvent]:
    if effect.condition is None or effect.save_ability is None or effect.save_dc is None:
        raise ValueError("Save-gated condition effect is incomplete.")

    roll, success = resolve_saving_throw(
        defender, effect.save_ability, effect.save_dc, dice
    )
    result_text = "automatically fails" if roll is None else (
        "succeeds" if success else "fails"
    )
    events = [BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="saving_throw",
        actor_id=defender.instance_id,
        actor_name=defender.template.name,
        target_id=attacker.instance_id,
        target_name=attacker.template.name,
        saving_throw=roll,
        test_dc=effect.save_dc,
        test_ability=effect.save_ability,
        test_success=success,
        feature_id=effect.id,
        animation="saving-throw",
        description=(
            f"{defender.template.name} {result_text} a "
            f"{effect.save_ability.value.title()} save against {effect.id}."
        ),
    )]
    if success:
        return events

    applied = apply_condition(
        defender,
        effect.condition,
        attacker,
        expires_on=effect.expires_on,
    )
    if applied:
        events.append(BattleEvent(
            sequence=sequence + 1,
            round_number=round_number,
            event_type="condition",
            actor_id=attacker.instance_id,
            actor_name=attacker.template.name,
            target_id=defender.instance_id,
            target_name=defender.template.name,
            condition=effect.condition,
            condition_active=True,
            feature_id=effect.id,
            animation="condition",
            description=(
                f"{defender.template.name} gains the {effect.condition.value.title()} condition."
            ),
        ))
    return events
