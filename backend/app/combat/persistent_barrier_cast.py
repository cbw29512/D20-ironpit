from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.alternate_spell_casts import spend_alternate_cast
from app.combat.concentration import start_concentration
from app.combat.persistent_barrier_geometry import validate_barrier_layout
from app.combat.persistent_barrier_lifecycle import cleanup_persistent_barriers
from app.combat.spellcasting import mark_slot_spell_cast
from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.persistent_barriers import (
    GridBarrierEdge,
    PersistentBarrierAction,
    PersistentBarrierSectionState,
    PersistentBarrierState,
)

logger = logging.getLogger(__name__)


def _slot_resource(caster: EncounterCombatant, level: int):
    try:
        resource_id = f"spell-slot-{level}"
        return next((item for item in caster.state.resources if item.id == resource_id), None)
    except Exception as exc:
        logger.exception("Failed to load barrier spell-slot resource level %s.", level)
        raise RuntimeError("Barrier spell-slot resource could not be loaded.") from exc


def cast_persistent_barrier(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: PersistentBarrierAction,
    section_edges: list[list[GridBarrierEdge]],
    turn_key: str,
    *,
    alternate_cast: AlternateSpellCastGrant | None = None,
) -> tuple[BattleEvent, int]:
    """Spend a legal cast and create one source-owned destructible barrier."""
    try:
        validate_barrier_layout(action, section_edges, caster, setup)
        if not is_available(caster.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")

        remaining = None
        if alternate_cast is not None:
            if alternate_cast.spell_id != action.id or alternate_cast.cast_level != action.level:
                raise ValueError("Alternate barrier cast does not match the barrier spell.")
            remaining = spend_alternate_cast(caster.state, alternate_cast)
        elif action.level > 0:
            resource = _slot_resource(caster, action.level)
            if resource is None or resource.current_uses < 1:
                raise ValueError(f"No level {action.level} spell slot remains.")
            mark_slot_spell_cast(caster.state, turn_key)
            resource.current_uses -= 1
            remaining = resource.current_uses

        spend(caster.state, action.action_cost)
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        if action.concentration:
            start_concentration(
                caster.state,
                caster.combatant_id,
                action.id,
                round_number,
                affected_states,
                expires_round=round_number + action.duration_rounds,
                slot_level=action.level if action.level > 0 else None,
            )
            cleanup_persistent_barriers(setup, round_number)

        barrier_id = (
            f"{caster.combatant_id}:{action.id}:{round_number}:"
            f"{len(setup.persistent_barriers) + 1}"
        )
        sections = [
            PersistentBarrierSectionState(
                section_id=f"{barrier_id}:section-{index}",
                edges=[edge.model_copy(deep=True) for edge in edges],
                current_hp=action.hit_points_per_section,
                armor_class=action.armor_class,
                damage_immunities=list(action.damage_immunities),
            )
            for index, edges in enumerate(section_edges, start=1)
        ]
        setup.persistent_barriers.append(PersistentBarrierState(
            barrier_id=barrier_id,
            source_id=caster.combatant_id,
            source_side=caster.side,
            action_id=action.id,
            action_name=action.name,
            concentration=action.concentration,
            applied_round=round_number,
            expires_round=round_number + action.duration_rounds,
            permanent_after_full_duration=action.permanent_after_full_duration,
            blocks_movement=action.blocks_movement,
            blocks_line_of_sight=action.blocks_line_of_sight,
            sections=sections,
            animation=action.animation,
        ))
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            feature_id=action.id,
            resource_remaining=remaining,
            animation=action.animation,
            description=(
                f"{caster.state.template.name} creates {action.name} "
                f"with {len(sections)} barrier sections."
            ),
        ), sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Persistent barrier cast failed for %s.", caster.combatant_id)
        raise RuntimeError("Persistent barrier could not be created.") from exc
