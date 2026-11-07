"""Resolve source-owned swallowed acid damage at the *owner's* turn start."""
from __future__ import annotations

from app.combat.damage import roll_damage_component
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.saving_throw_context import SavingThrowContext
import logging

logger = logging.getLogger(__name__)
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.zero_hp import apply_damage
from app.combat.swallow_state import release_swallowed
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType

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
        # A source-defined successful save suppresses this turn's tick only.
        # Unconditional Swallow damage keeps its original behavior.
        save_roll, save_succeeded = None, False
        if record.turn_start_save_ability is not None:
            if record.turn_start_save_dc is None:
                raise ValueError("Turn-start damage save is missing its DC.")
            save_roll, save_succeeded = resolve_saving_throw(
                target.state, record.turn_start_save_ability,
                record.turn_start_save_dc, dice, SavingThrowContext(),
                round_number=round_number, encounter_roller=target, setup=setup,
            )
        if save_succeeded:
            component, adjusted, applied = None, [], 0
        else:
            component = roll_damage_component(
                dice, record.source_name,
                record.damage_dice_count, record.damage_dice_size,
                record.damage_bonus, damage_type, False,
            )
            applied, adjusted = apply_damage_defenses(target.state, [component])
        before = target.state.current_hp
        apply_damage(
            target.state, applied, damage_types={damage_type}, dice=dice,
            affected_states=affected, setup=setup, damage_components=adjusted,
            source_id=owner.combatant_id,
        )
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=owner.combatant_id, actor_name=owner.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=record.source_name, damage_components=adjusted,
            saving_throw_roll=save_roll, save_ability=record.turn_start_save_ability,
            save_dc=record.turn_start_save_dc, save_succeeded=(save_succeeded if save_roll is not None else None),
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
