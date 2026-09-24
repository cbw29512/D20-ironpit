from __future__ import annotations

import logging

from app.combat.damage import aggregate_damage_components, fixed_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.grid_geometry import footprint_distance_ft
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType
from app.combat.persistent_hazard_cast import cast_persistent_hazard

logger = logging.getLogger(__name__)


def resolve_persistent_hazard_entries(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve first movement-to-radius triggers after one authoritative position step."""
    try:
        if mover.state.position is None:
            return [], sequence
        events: list[BattleEvent] = []
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        expired = [h for h in setup.persistent_hazards if round_number >= h.expires_round or h.remaining_damage_capacity <= 0]
        for hazard in expired:
            setup.persistent_hazards.remove(hazard)

        for hazard in list(setup.persistent_hazards):
            if hazard.source_side == mover.side:
                continue
            if hazard.triggered_turn_keys.get(mover.combatant_id) == turn_key:
                continue
            distance = footprint_distance_ft(
                mover.state.position, mover.state.template.size,
                hazard.position, hazard.footprint_size,
            )
            if distance > hazard.trigger_radius_ft:
                continue

            hazard.triggered_turn_keys[mover.combatant_id] = turn_key
            roll, succeeded = resolve_saving_throw(
                mover.state, hazard.save_ability, hazard.dc, dice,
            )
            raw_damage = hazard.success_damage if succeeded else hazard.failure_damage
            component = fixed_damage_component(
                hazard.action_name, raw_damage, DamageType(hazard.damage_type),
            )
            applied_total, components = apply_damage_defenses(mover.state, [component])
            hp_before = mover.state.current_hp
            if applied_total:
                apply_damage(
                    mover.state,
                    applied_total,
                    damage_types={DamageType(hazard.damage_type)},
                    dice=dice,
                    affected_states=affected_states,
                )
            hazard.remaining_damage_capacity = max(
                0, hazard.remaining_damage_capacity - applied_total,
            )
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="saving_throw",
                actor_id=hazard.source_id, actor_name=hazard.action_name,
                target_id=mover.combatant_id, target_name=mover.state.template.name,
                saving_throw_roll=roll, save_ability=hazard.save_ability,
                save_dc=hazard.dc, save_succeeded=succeeded,
                damage_roll=aggregate_damage_components(components),
                damage_components=components,
                hp_before=hp_before, hp_after=mover.state.current_hp,
                is_dead=mover.state.is_dead,
                feature_id=hazard.action_id,
                animation=hazard.animation,
                description=(
                    f"{mover.state.template.name} {'succeeds' if succeeded else 'fails'} "
                    f"the save against {hazard.action_name} and takes {applied_total} "
                    f"{hazard.damage_type} damage."
                ),
            ))
            sequence += 1
            if hazard.remaining_damage_capacity <= 0:
                setup.persistent_hazards.remove(hazard)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Persistent hazard entry resolution failed for %s.", mover.combatant_id)
        raise RuntimeError("Persistent hazard entry could not be resolved.") from exc
