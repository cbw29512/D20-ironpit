from __future__ import annotations

from dataclasses import dataclass

from app.combat.defensive_modifier_rules import (
    remove_owner_attack_ending_modifiers,
    targeting_save_gate,
)
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent, DiceRoll
from app.domain.modifiers import CombatModifier


@dataclass(frozen=True)
class TargetingWardCheck:
    gate: CombatModifier
    roll: DiceRoll | None
    succeeded: bool


def check_targeting_ward(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    dice: DiceProvider,
) -> TargetingWardCheck | None:
    """End attack-breaking wards on the attacker, then test any ward protecting the target."""
    remove_owner_attack_ending_modifiers(attacker.state)
    gate = targeting_save_gate(target.state)
    if gate is None:
        return None
    roll, succeeded = resolve_saving_throw(
        attacker.state,
        gate.save_ability or "wisdom",
        gate.save_dc or 1,
        dice,
    )
    return TargetingWardCheck(gate, roll, succeeded)


def blocked_targeting_event(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    action_name: str,
    check: TargetingWardCheck,
) -> BattleEvent:
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="saving_throw",
        actor_id=attacker.combatant_id,
        actor_name=attacker.state.template.name,
        target_id=target.combatant_id,
        target_name=target.state.template.name,
        attack_name=action_name,
        saving_throw_roll=check.roll,
        save_ability=check.gate.save_ability,
        save_dc=check.gate.save_dc,
        save_succeeded=False,
        hit=False,
        feature_id=check.gate.source_effect_id,
        animation=check.gate.source_effect_id,
        description=(
            f"{attacker.state.template.name} fails the {check.gate.save_ability.title()} save against "
            f"{check.gate.source_effect_id}; the attack or spell targeting {target.state.template.name} is lost."
        ),
    )
