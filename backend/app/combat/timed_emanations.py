from __future__ import annotations

import logging

from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.encounter_targeting import combatant_distance
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
            (action, action.start_turn_emanation_damage)
            for action in source.state.template.timed_self_buff_actions
            if action.id in active_effect_ids and action.start_turn_emanation_damage is not None
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
            for action, emanation in _active_emanations(source):
                if emanation.trigger != "enemy_turn_start":
                    continue
                distance = combatant_distance(source, target)
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
