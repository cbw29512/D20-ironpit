"""Resolve source-owned swallowed acid damage at the *owner's* turn start."""
from __future__ import annotations

import logging

from app.combat.damage import roll_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.zero_hp import apply_damage
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.swallow_state import release_swallowed
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType

logger = logging.getLogger(__name__)


def release_invalid_swallowed(setup: EncounterSetup) -> list[str]:
    """Clear swallowed ownership after death; never change immutable cards."""
    members = {m.combatant_id: m for m in [*setup.heroes, *setup.monsters]}
    released: list[str] = []
    for target in members.values():
        record = target.state.swallowed
        if record is None:
            continue
        owner = members.get(record.source_id)
        if owner is not None and owner.state.is_alive and not owner.state.is_dead:
            if target.state.is_alive and not target.state.is_dead:
                continue
        if owner is not None:
            release_swallowed(
                owner.state, target.combatant_id, target.state,
                owner_id=owner.combatant_id,
                exiting_prone=target.state.is_alive and not target.state.is_dead,
            )
        else:
            target.state.swallowed = None
            target.state.active_effect_ids = [
                c for c in target.state.active_effect_ids
                if c not in ("blinded", "restrained")
            ]
        released.append(target.combatant_id)
    return released


def resolve_end_turn_swallow_regurgitation(
    sequence: int,
    round_number: int,
    swallowed: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve damage-threshold regurgitation at the swallowed creature's turn end."""
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

        event = BattleEvent(
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
        )
        return [event], sequence + 1
    except Exception:
        logger.exception(
            "Threshold Swallow regurgitation failed for %s.",
            swallowed.combatant_id,
        )
        raise


def source_turn_swallowed_damage(
    sequence: int, round_number: int, owner: EncounterCombatant,
    setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    """Existing typed defense/zero-HP resolver handles owner-turn damage."""
    release_invalid_swallowed(setup)
    if owner.state.is_dead or not owner.state.is_alive or owner.state.current_hp <= 0:
        return [], sequence
    events: list[BattleEvent] = []
    members = [*setup.heroes, *setup.monsters]
    affected = [item.state for item in members]
    targets = [
        item for item in members
        if item.state.swallowed is not None
        and item.state.swallowed.source_id == owner.combatant_id
        and item.state.is_alive and not item.state.is_dead
    ]
    for target in targets:
        record = target.state.swallowed
        damage_type = DamageType(record.damage_type)
        component = roll_damage_component(
            dice, record.source_name,
            record.damage_dice_count, record.damage_dice_size,
            0, damage_type, False,
        )
        applied, adjusted = apply_damage_defenses(target.state, [component])
        before = target.state.current_hp
        apply_damage(
            target.state, applied, damage_types={damage_type}, dice=dice,
            affected_states=affected, setup=setup, damage_components=adjusted,
        )
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=owner.combatant_id, actor_name=owner.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=record.source_name, damage_components=adjusted,
            hp_before=before, hp_after=target.state.current_hp,
            is_dead=target.state.is_dead, animation="feature",
            description=(
                f"{owner.state.template.name}: {record.source_name} deals "
                f"{applied} {damage_type.value} damage to swallowed "
                f"{target.state.template.name} at the source's turn start."
            ),
        ))
        sequence += 1
    release_invalid_swallowed(setup)
    return events, sequence
