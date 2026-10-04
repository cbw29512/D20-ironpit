from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.emanation_save_damage import resolve_emanation_hit
from app.combat.emanation_speed import sync_emanation_speed
from app.combat.hostile_condition_auras import resolve_hostile_condition_aura
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

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
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve enemy-turn-start and enter-or-start emanation damage from active timed effects."""
    try:
        events: list[BattleEvent] = []
        sync_emanation_speed(setup)
        active_turn = turn_key or f"{round_number}:{target.combatant_id}"
        for source in [*setup.heroes, *setup.monsters]:
            if not _opposing(source, target):
                continue
            for action in _active_emanations(source):
                distance = combatant_distance(source, target)
                aura_event, sequence = resolve_hostile_condition_aura(
                    sequence, round_number, source, target, action, distance,
                    [member.state for member in [*setup.heroes, *setup.monsters]], dice,
                )
                if aura_event is not None:
                    events.append(aura_event)
                emanation = action.start_turn_emanation_damage
                if emanation is None:
                    continue
                if emanation.trigger not in {"enemy_turn_start", "enter_or_start"}:
                    continue
                event, sequence = resolve_emanation_hit(
                    sequence, round_number, source, target, action, setup, dice, active_turn,
                )
                if event is not None:
                    events.append(event)
        return events, sequence
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Timed emanation turn-start resolution failed for %s.", target.combatant_id)
        raise RuntimeError("Timed emanation turn-start effects could not be resolved.") from exc
