"""Universal damage from a live source-owned environment-context reaction."""
from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.environment_contexts import actor_inside_environment_context
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent

logger = logging.getLogger(__name__)


def resolve_environment_start_turn_damage(
    sequence: int, round_number: int,
    member: EncounterCombatant, setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    """Triggered, typed damage; no environment is assumed from trait names."""
    try:
        if member.state.is_dead or not member.state.is_alive:
            return [], sequence
        reactions = member.state.template.environment_context_reactions
        if not any(reaction.start_turn_damage_amount for reaction in reactions):
            return [], sequence
        events: list[BattleEvent] = []
        affected = [other.state for other in [*setup.heroes, *setup.monsters]]
        for reaction in reactions:
            amount = reaction.start_turn_damage_amount
            if not amount or not actor_inside_environment_context(
                member, setup, reaction.context_id,
            ):
                continue
            damage_type = reaction.start_turn_damage_type
            if damage_type is None:
                raise ValueError("Environmental start-turn damage has no type.")
            component = DamageRollComponent(
                source=reaction.source_name, notation=str(amount),
                rolls=[], modifier=0, damage_type=damage_type, total=amount,
            )
            before = member.state.current_hp
            applied, components = apply_damage_defenses(member.state, [component])
            apply_damage(
                member.state, applied, damage_types={damage_type},
                dice=dice, affected_states=affected, setup=setup,
                damage_components=components, source_id=member.combatant_id,
            )
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=member.combatant_id, actor_name=member.state.template.name,
                target_id=member.combatant_id, target_name=member.state.template.name,
                feature_id=reaction.source_name,
                hp_before=before, hp_after=member.state.current_hp,
                is_dead=member.state.is_dead, damage_components=components,
                animation="feature",
                description=(
                    f"{reaction.source_name}: {member.state.template.name} "
                    f"takes {applied} {damage_type.value} damage at the start "
                    f"of its turn in {reaction.context_id}."
                ),
            ))
            sequence += 1
            if member.state.is_dead:
                break
        return events, sequence
    except Exception:
        logger.exception("Failed source-owned environmental damage for %s.", member.combatant_id)
        raise
