from __future__ import annotations

import logging

from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll
from app.domain.models import DamageType
from app.combat.dice import DiceProvider

logger = logging.getLogger(__name__)


def _opposing(source: EncounterCombatant, target: EncounterCombatant) -> bool:
    return source.side != target.side


def _active_emanations(source: EncounterCombatant):
    try:
        active_effect_ids = {
            effect.source_effect_id
            for effect in source.state.timed_effects
            if effect.source_id == source.combatant_id and effect.source_effect_id is not None
        }
        return [
            action
            for action in source.state.template.timed_self_buff_actions
            if action.id in active_effect_ids
            and (
                action.start_turn_emanation_damage is not None
                or action.hostile_start_turn_condition_aura is not None
            )
        ]
    except Exception as exc:
        logger.exception("Failed to discover timed emanations for %s.", source.combatant_id)
        raise RuntimeError("Timed emanation discovery failed.") from exc


def resolve_target_turn_start_emanations(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve fixed typed enemy-turn-start emanation damage from active timed effects."""
    try:
        events: list[BattleEvent] = []
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        for source in [*setup.heroes, *setup.monsters]:
            if not _opposing(source, target):
                continue
            for action in _active_emanations(source):
                distance = combatant_distance(source, target)
                aura = action.hostile_start_turn_condition_aura
                if aura is not None and aura.trigger == "enemy_turn_start" and distance <= aura.radius_ft:
                    immunity_id = f"{action.id}:success-immunity:{source.combatant_id}"
                    immune = any(
                        effect.effect_id == immunity_id
                        for effect in target.state.timed_effects
                    )
                    if not immune:
                        roll, succeeded = resolve_saving_throw(
                            target.state,
                            aura.save_ability,
                            aura.save_dc,
                            dice,
                            round_number=round_number,
                        )
                        applied = []
                        if succeeded:
                            if aura.success_immunity_rounds:
                                apply_timed_condition(
                                    target.state,
                                    immunity_id,
                                    source.combatant_id,
                                    source_effect_id=f"{action.id}:success-immunity",
                                    source_template=source.state.template,
                                    source_is_magical=aura.source_is_magical,
                                    applied_round=round_number,
                                    expires_round=round_number + aura.success_immunity_rounds,
                                    expiry_timing="source_turn_start",
                                    expires_at_start_of_source_turn=True,
                                    use_default_poison_recovery=False,
                                )
                        else:
                            condition = apply_timed_condition(
                                target.state,
                                aura.condition_id,
                                source.combatant_id,
                                source_effect_id=action.id,
                                source_template=source.state.template,
                                source_is_magical=aura.source_is_magical,
                                applied_round=round_number,
                                expires_round=round_number + action.duration_rounds,
                                expiry_timing=action.expiry_timing,
                                expires_at_start_of_source_turn=action.expiry_timing == "source_turn_start",
                                ends_if_source_incapacitated=action.ends_if_source_incapacitated,
                                ends_if_source_dead=action.ends_if_source_dead,
                                affected_states=affected_states,
                                use_default_poison_recovery=False,
                            )
                            if condition is not None:
                                applied.append(condition)
                        events.append(BattleEvent(
                            sequence=sequence,
                            round_number=round_number,
                            event_type="feature",
                            actor_id=source.combatant_id,
                            actor_name=source.state.template.name,
                            target_id=target.combatant_id,
                            target_name=target.state.template.name,
                            saving_throw_roll=roll,
                            save_ability=aura.save_ability,
                            save_dc=aura.save_dc,
                            save_succeeded=succeeded,
                            applied_condition_ids=applied,
                            distance_before_ft=distance,
                            feature_id=action.id,
                            animation=action.animation,
                            description=(
                                f"{target.state.template.name} starts its turn within {distance} feet of "
                                f"{source.state.template.name}'s {action.name} and "
                                f"{'resists' if succeeded else 'fails against'} its aura."
                            ),
                        ))
                        sequence += 1

                emanation = action.start_turn_emanation_damage
                if emanation is None or emanation.trigger != "enemy_turn_start":
                    continue
                if distance > emanation.radius_ft:
                    continue
                hp_before = target.state.current_hp
                temp_before = target.state.temporary_hp
                death_success_before = target.state.death_save_successes
                death_failure_before = target.state.death_save_failures
                applied = adjusted_damage_amount(
                    emanation.fixed_damage,
                    emanation.damage_type,
                    target.state,
                )
                if applied:
                    apply_damage(
                        target.state,
                        applied,
                        damage_types={emanation.damage_type},
                        dice=dice,
                        affected_states=affected_states,
                    )
                component = DamageRollComponent(
                    source=action.name,
                    notation=str(emanation.fixed_damage),
                    rolls=[],
                    modifier=0,
                    damage_type=emanation.damage_type,
                    total=emanation.fixed_damage,
                    applied_total=applied,
                )
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=round_number,
                    event_type="feature",
                    actor_id=source.combatant_id,
                    actor_name=source.state.template.name,
                    target_id=target.combatant_id,
                    target_name=target.state.template.name,
                    damage_roll=DiceRoll(
                        notation=str(emanation.fixed_damage),
                        rolls=[],
                        modifier=0,
                        total=applied,
                    ),
                    damage_components=[component],
                    hp_before=hp_before,
                    hp_after=target.state.current_hp,
                    temporary_hp_before=temp_before,
                    temporary_hp_after=target.state.temporary_hp,
                    death_save_successes_before=death_success_before,
                    death_save_failures_before=death_failure_before,
                    death_save_successes=target.state.death_save_successes,
                    death_save_failures=target.state.death_save_failures,
                    is_stable=target.state.is_stable,
                    is_dead=target.state.is_dead,
                    distance_before_ft=distance,
                    feature_id=action.id,
                    animation=action.animation,
                    description=(
                        f"{target.state.template.name} starts its turn within {distance} feet of "
                        f"{source.state.template.name}'s {action.name} and takes {applied} "
                        f"{emanation.damage_type.value} damage."
                    ),
                ))
                sequence += 1
        return events, sequence
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Timed emanation turn-start resolution failed for %s.", target.combatant_id)
        raise RuntimeError("Timed emanation turn-start effects could not be resolved.") from exc
