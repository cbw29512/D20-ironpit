"""End-turn damage-threshold regurgitation for universal Swallow state."""
from __future__ import annotations

import logging

from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.swallow_state import release_swallowed
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_end_turn_swallow_regurgitation(
    sequence: int,
    round_number: int,
    swallowed: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    try:
        record = swallowed.state.swallowed
        if record is None or record.regurgitation_damage_threshold is None:
            return [], sequence

        members = {
            member.combatant_id: member
            for member in [*setup.heroes, *setup.monsters]
        }
        owner = members.get(record.source_id)
        if owner is None or owner.state.is_dead or not owner.state.is_alive:
            return [], sequence

        dealt = owner.state.damage_taken_this_turn_by_source.get(
            swallowed.combatant_id, 0,
        )
        if dealt < record.regurgitation_damage_threshold:
            return [], sequence
        if record.regurgitation_save_ability is None or record.regurgitation_save_dc is None:
            raise ValueError("Threshold regurgitation requires a save ability and DC.")

        roll, succeeded = resolve_saving_throw(
            owner.state,
            record.regurgitation_save_ability,
            record.regurgitation_save_dc,
            dice,
        )
        released: list[str] = []
        if not succeeded:
            targets = [
                member for member in members.values()
                if member.state.swallowed is not None
                and member.state.swallowed.source_id == owner.combatant_id
            ]
            if not record.regurgitation_all_swallowed:
                targets = [swallowed]
            for target in targets:
                if release_swallowed(
                    owner.state,
                    target.combatant_id,
                    target.state,
                    owner_id=owner.combatant_id,
                    exiting_prone=target.state.is_alive and not target.state.is_dead,
                ):
                    released.append(target.combatant_id)

        return [BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="saving_throw",
            actor_id=owner.combatant_id,
            actor_name=owner.state.template.name,
            target_id=swallowed.combatant_id,
            target_name=swallowed.state.template.name,
            saving_throw_roll=roll,
            save_ability=record.regurgitation_save_ability,
            save_dc=record.regurgitation_save_dc,
            save_succeeded=succeeded,
            feature_id=record.source_name,
            removed_condition_ids=["blinded", "restrained"] if released else [],
            animation="feature",
            description=(
                f"{owner.state.template.name} {'keeps' if succeeded else 'regurgitates'} "
                f"its swallowed creature after taking {dealt} damage from "
                f"{swallowed.state.template.name} during that turn."
            ),
        )], sequence + 1
    except Exception:
        logger.exception(
            "Threshold Swallow regurgitation failed for %s.",
            swallowed.combatant_id,
        )
        raise
