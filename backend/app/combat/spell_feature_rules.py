from __future__ import annotations

import logging

from app.combat.spellcasting import legal_slot_levels
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.event_support import DamageRollComponent, DiceRoll
from app.domain.runtime import CombatantState
from app.domain.spell_features import SpellSpecificCastGrant
from app.domain.spells import SpellSaveAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


def available_cast_grant(
    state: CombatantState, spell_id: str, slot_level: int,
) -> SpellSpecificCastGrant | None:
    try:
        for grant in state.template.progression_features.spell_specific_cast_grants:
            if grant.spell_id != spell_id or grant.slot_level != slot_level:
                continue
            if grant.unlimited:
                return grant
            resource = next((item for item in state.resources if item.id == grant.resource_id), None)
            if resource is not None and resource.current_uses >= grant.resource_cost:
                return grant
        return None
    except Exception:
        logger.exception("Failed spell-specific cast grant lookup for %s.", state.template.name)
        raise


def legal_save_spell_levels(
    state: CombatantState, turn_key: str, action: SpellSaveAction,
) -> list[int]:
    try:
        levels = set(legal_slot_levels(
            state, turn_key, action.level,
            higher_slot_scaling=action.upcast_dice_per_level > 0,
        ))
        if action.level > 0 and available_cast_grant(state, action.id, action.level):
            levels.add(action.level)
        return sorted(levels)
    except Exception:
        logger.exception("Failed legal save-spell level lookup for %s.", action.id)
        raise


def spend_cast_grant(
    state: CombatantState, action: SpellSaveAction, slot_level: int,
) -> tuple[SpellSpecificCastGrant | None, int | None]:
    try:
        grant = available_cast_grant(state, action.id, slot_level)
        if grant is None or grant.unlimited:
            return grant, None
        resource = next(item for item in state.resources if item.id == grant.resource_id)
        resource.current_uses -= grant.resource_cost
        return grant, resource.current_uses
    except Exception:
        logger.exception("Failed to spend spell-specific cast grant for %s.", action.id)
        raise


def damage_maximizer_available(state: CombatantState, action: SpellSaveAction) -> bool:
    try:
        grant = state.template.progression_features.spell_damage_maximizer
        if grant is None or action.level == 0:
            return False
        if not grant.minimum_spell_level <= action.level <= grant.maximum_spell_level:
            return False
        return bool(action.damage_dice_count or action.damage_components)
    except Exception:
        logger.exception("Failed spell damage maximizer eligibility for %s.", action.id)
        raise


def should_auto_maximize_damage(state: CombatantState, action: SpellSaveAction) -> bool:
    try:
        if not damage_maximizer_available(state, action):
            return False
        grant = state.template.progression_features.spell_damage_maximizer
        if grant is None:
            return False
        return state.feature_use_counts.get(grant.source_id, 0) < grant.free_uses
    except Exception:
        logger.exception("Failed automatic spell damage maximizer policy for %s.", action.id)
        raise


def maximized_damage_rolls(action: SpellSaveAction) -> list[int] | list[list[int]]:
    try:
        if action.damage_components:
            return [[part.dice_size] * part.dice_count for part in action.damage_components]
        return [action.damage_dice_size] * action.damage_dice_count
    except Exception:
        logger.exception("Failed to build maximized damage rolls for %s.", action.id)
        raise


def apply_damage_maximizer_cost(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    action: SpellSaveAction,
    dice,
    affected_states: list[CombatantState],
) -> tuple[BattleEvent | None, int]:
    try:
        grant = caster.state.template.progression_features.spell_damage_maximizer
        if grant is None:
            return None, sequence
        uses = caster.state.feature_use_counts.get(grant.source_id, 0)
        caster.state.feature_use_counts[grant.source_id] = uses + 1
        if uses < grant.free_uses:
            return None, sequence

        repeat_index = uses - grant.free_uses
        dice_per_level = (
            grant.repeat_base_dice_per_spell_level
            + repeat_index * grant.repeat_increment_dice_per_spell_level
        )
        count = dice_per_level * action.level
        rolls = [dice.roll(grant.self_damage_die_size) for _ in range(count)]
        total = sum(rolls)
        hp_before = caster.state.current_hp
        temp_before = caster.state.temporary_hp
        apply_damage(
            caster.state, total, damage_types={DamageType(grant.self_damage_type)},
            dice=dice, affected_states=affected_states,
        )
        component = DamageRollComponent(
            source=grant.source_name,
            notation=f"{count}d{grant.self_damage_die_size}",
            rolls=rolls, modifier=0,
            damage_type=grant.self_damage_type,
            total=total, applied_total=total,
        )
        event = BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=caster.combatant_id, actor_name=caster.state.template.name,
            target_id=caster.combatant_id, target_name=caster.state.template.name,
            feature_id=grant.source_id,
            damage_roll=DiceRoll(
                notation=component.notation, rolls=rolls, modifier=0, total=total,
            ),
            damage_components=[component],
            hp_before=hp_before, hp_after=caster.state.current_hp,
            temporary_hp_before=temp_before, temporary_hp_after=caster.state.temporary_hp,
            animation="spell-overchannel",
            description=(
                f"{caster.state.template.name} suffers {total} {grant.self_damage_type} damage "
                f"from repeated use of {grant.source_name}."
            ),
        )
        return event, sequence + 1
    except Exception:
        logger.exception("Failed spell damage maximizer cost for %s.", caster.combatant_id)
        raise
