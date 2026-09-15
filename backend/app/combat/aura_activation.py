from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance
from app.combat.resources import resource_available, spend_resource
from app.domain.auras import StartTurnAura
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.runtime import ActiveAuraState, CombatantState

logger = logging.getLogger(__name__)


def aura_is_active(state: CombatantState, aura: StartTurnAura) -> bool:
    try:
        if aura.activation_cost is None:
            return True
        return any(active.aura_id == aura.id for active in state.active_auras)
    except Exception as exc:
        logger.exception("Failed active-aura check for %s / %s.", state.template.name, aura.id)
        raise RuntimeError("Aura active-state check failed.") from exc


def _enemy_in_aura(attacker: EncounterCombatant, setup: EncounterSetup, aura: StartTurnAura) -> bool:
    enemies = setup.monsters if attacker.side == "heroes" else setup.heroes
    return any(
        target.state.is_alive and not target.state.is_dead and target.state.current_hp > 0
        and combatant_distance(attacker, target) <= aura.range_ft
        for target in enemies
    )


def choose_activated_aura(attacker: EncounterCombatant, setup: EncounterSetup) -> StartTurnAura | None:
    try:
        for aura in attacker.state.template.start_turn_auras:
            if aura.activation_cost is None or aura.activation_duration_rounds is None:
                continue
            if aura_is_active(attacker.state, aura):
                continue
            if not is_available(attacker.state, aura.activation_cost):
                continue
            if not resource_available(attacker.state, aura.resource_id, aura.resource_cost):
                continue
            if _enemy_in_aura(attacker, setup, aura):
                return aura
        return None
    except Exception as exc:
        logger.exception("Failed activated-aura choice for %s.", attacker.combatant_id)
        raise RuntimeError("Activated aura could not be selected.") from exc


def activate_aura(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    aura: StartTurnAura,
) -> BattleEvent:
    try:
        if aura.activation_cost is None or aura.activation_duration_rounds is None:
            raise ValueError(f"Aura {aura.id!r} is passive and cannot be activated.")
        if aura_is_active(attacker.state, aura):
            raise ValueError(f"Aura {aura.id!r} is already active.")
        if not is_available(attacker.state, aura.activation_cost):
            raise ValueError(f"Aura {aura.id!r} activation cost is unavailable.")
        if not resource_available(attacker.state, aura.resource_id, aura.resource_cost):
            raise ValueError(f"Aura {aura.id!r} resource is unavailable.")
        spend(attacker.state, aura.activation_cost)
        remaining = spend_resource(attacker.state, aura.resource_id, aura.resource_cost)
        attacker.state.active_auras.append(ActiveAuraState(
            aura_id=aura.id,
            activated_round=round_number,
            expires_round=round_number + aura.activation_duration_rounds,
        ))
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=attacker.combatant_id,
            actor_name=attacker.state.template.name,
            feature_id=aura.id,
            resource_remaining=remaining,
            animation="aura",
            description=(
                f"{attacker.state.template.name} uses {aura.name}; its {aura.range_ft}-foot aura "
                f"is active for {aura.activation_duration_rounds} rounds."
            ),
        )
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Failed to activate aura %s for %s.", aura.id, attacker.combatant_id)
        raise RuntimeError("Aura activation failed.") from exc


def resolve_ready_activated_aura(sequence, round_number, attacker, setup):
    try:
        aura = choose_activated_aura(attacker, setup)
        if aura is None:
            return [], sequence, False
        return [activate_aura(sequence, round_number, attacker, aura)], sequence + 1, True
    except Exception:
        logger.exception("Failed activated-aura resolution for %s.", attacker.combatant_id)
        raise


def expire_active_auras(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
) -> tuple[list[BattleEvent], int]:
    try:
        expired = [aura for aura in source.state.active_auras if round_number >= aura.expires_round]
        if not expired:
            return [], sequence
        expired_ids = {aura.aura_id for aura in expired}
        source.state.active_auras = [aura for aura in source.state.active_auras if aura.aura_id not in expired_ids]
        definitions = {aura.id: aura for aura in source.state.template.start_turn_auras}
        events: list[BattleEvent] = []
        for active in expired:
            name = definitions.get(active.aura_id).name if active.aura_id in definitions else active.aura_id
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=source.combatant_id,
                actor_name=source.state.template.name,
                feature_id=active.aura_id,
                animation="aura-ended",
                description=f"{source.state.template.name}'s {name} ends.",
            ))
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Failed active-aura expiry for %s.", source.combatant_id)
        raise RuntimeError("Aura expiry failed.") from exc
