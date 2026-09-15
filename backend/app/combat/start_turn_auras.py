from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _immunity_key(source_id: str, aura_id: str) -> str:
    return f"{source_id}:{aura_id}"


def resolve_start_turn_save_condition_auras(
    sequence: int, round_number: int, target: EncounterCombatant,
    setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve nearby source-owned save/condition emanations when target starts its turn."""
    try:
        events: list[BattleEvent] = []
        sources = [*setup.heroes, *setup.monsters]
        affected_states = [member.state for member in sources]
        for source in sources:
            if source.combatant_id == target.combatant_id or source.state.is_dead or not source.state.is_alive:
                continue
            for aura in source.state.template.start_turn_save_condition_auras:
                if aura.disabled_while_incapacitated and is_incapacitated(source.state):
                    continue
                immunity_key = _immunity_key(source.combatant_id, aura.id)
                if immunity_key in target.state.source_effect_immunities:
                    continue
                if combatant_distance(source, target) > aura.radius_ft:
                    continue
                roll, succeeded = resolve_saving_throw(
                    target.state, aura.save_ability, aura.dc, dice,
                    magical_effect=aura.magical_effect,
                )
                applied: list[str] = []
                if succeeded and aura.success_grants_source_immunity:
                    target.state.source_effect_immunities.append(immunity_key)
                elif not succeeded:
                    condition = apply_timed_condition(
                        target.state, aura.condition, source.combatant_id,
                        source_effect_id=aura.id, applied_round=round_number,
                        expiry_timing=aura.expiry_timing, affected_states=affected_states,
                    )
                    if condition:
                        applied.append(condition)
                events.append(BattleEvent(
                    sequence=sequence, round_number=round_number, event_type="saving_throw",
                    actor_id=source.combatant_id, actor_name=source.state.template.name,
                    target_id=target.combatant_id, target_name=target.state.template.name,
                    saving_throw_roll=roll, save_ability=aura.save_ability, save_dc=aura.dc,
                    save_succeeded=succeeded, applied_condition_ids=applied, feature_id=aura.id,
                    animation="aura-condition",
                    description=(
                        f"{target.state.template.name} {'SUCCEEDS' if succeeded else 'FAILS'} a DC {aura.dc} "
                        f"{aura.save_ability.title()} save against {source.state.template.name}'s {aura.name}."
                    ),
                ))
                sequence += 1
        return events, sequence
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Start-turn aura resolution failed for %s.", target.combatant_id)
        raise RuntimeError("Start-turn aura resolution failed.") from exc
