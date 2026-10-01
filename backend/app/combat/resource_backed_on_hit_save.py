from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.modifier_stack import add_modifier
from app.combat.resources import resource_available, spend_resource
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent, DiceRoll
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.models import WeaponAttack
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResourceBackedOnHitSaveResolution:
    event: BattleEvent
    resource_remaining: int | None


def resolve_resource_backed_on_hit_save(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    dice,
    turn_key: str,
    *,
    affected_states=None,
) -> ResourceBackedOnHitSaveResolution | None:
    """Resolve one declarative optional on-hit save rider after a qualifying hit."""
    try:
        rider = attacker.state.template.progression_features.resource_backed_on_hit_save_rider
        if rider is None:
            return None
        if attack.id not in rider.trigger_attack_ids:
            return None
        if target.state.current_hp <= 0 or target.state.is_dead or not target.state.is_alive:
            return None
        if rider.once_per_turn and attacker.state.feature_last_turn_keys.get(rider.source_id) == turn_key:
            return None
        if not resource_available(attacker.state, rider.resource_id, rider.resource_cost):
            return None

        remaining = spend_resource(attacker.state, rider.resource_id, rider.resource_cost)
        if rider.once_per_turn:
            attacker.state.feature_last_turn_keys[rider.source_id] = turn_key

        save_roll, succeeded = resolve_saving_throw(
            target.state,
            rider.save_ability,
            rider.save_dc,
            dice,
            SavingThrowContext(condition_id=rider.failed_condition_id),
            round_number=round_number,
            encounter_roller=target,
        )

        applied_conditions: list[str] = []
        if not succeeded and rider.failed_condition_id is not None:
            applied = apply_timed_condition(
                target.state,
                rider.failed_condition_id,
                attacker.combatant_id,
                source_effect_id=rider.source_id,
                source_template=attacker.state.template,
                applied_round=round_number,
                expiry_timing=rider.failed_condition_expiry_timing,
                affected_states=affected_states,
                use_default_poison_recovery=False,
            )
            if applied is not None:
                applied_conditions.append(applied)

        if succeeded:
            if rider.successful_save_speed_multiplier is not None:
                add_modifier(target.state, CombatModifier(
                    id=f"{attacker.combatant_id}:{rider.source_id}:speed:{target.combatant_id}",
                    source_id=attacker.combatant_id,
                    source_effect_id=rider.source_id,
                    source_name=rider.source_name,
                    kind=ModifierKind.SPEED_MULTIPLIER,
                    multiplier=rider.successful_save_speed_multiplier,
                    expires_at_start_of_source_turn=True,
                ))
            if rider.successful_save_next_attack_advantage:
                add_modifier(target.state, CombatModifier(
                    id=f"{attacker.combatant_id}:{rider.source_id}:next-attack:{target.combatant_id}",
                    source_id=attacker.combatant_id,
                    source_effect_id=rider.source_id,
                    source_name=rider.source_name,
                    kind=ModifierKind.ATTACKS_AGAINST_ADVANTAGE,
                    consume_on_attack_against=True,
                    expires_at_start_of_source_turn=True,
                ))

        description = (
            f"{attacker.state.template.name} spends {rider.resource_cost} "
            f"{rider.resource_id.replace('-', ' ')} on {rider.source_name}; "
            f"{target.state.template.name} {'succeeds' if succeeded else 'fails'} "
            f"the DC {rider.save_dc} {rider.save_ability.title()} save."
        )
        if succeeded:
            effects: list[str] = []
            if rider.successful_save_speed_multiplier is not None:
                effects.append("Speed is reduced")
            if rider.successful_save_next_attack_advantage:
                effects.append("the next attack against the target has Advantage")
            if effects:
                description += " " + " and ".join(effects) + "."
        elif applied_conditions:
            description += f" {target.state.template.name} gains {', '.join(applied_conditions)}."

        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=attacker.combatant_id,
            actor_name=attacker.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=save_roll,
            save_ability=rider.save_ability,
            save_dc=rider.save_dc,
            save_succeeded=succeeded,
            applied_condition_ids=applied_conditions,
            feature_id=rider.source_id,
            resource_remaining=remaining,
            animation="stun",
            description=description,
        )
        return ResourceBackedOnHitSaveResolution(event=event, resource_remaining=remaining)
    except Exception as exc:
        logger.exception(
            "Resource-backed on-hit save failed: source=%s target=%s attack=%s.",
            attacker.combatant_id,
            target.combatant_id,
            attack.id,
        )
        raise RuntimeError("Resource-backed on-hit save could not be resolved.") from exc
