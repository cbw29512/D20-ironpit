from __future__ import annotations

import logging

from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll
from app.domain.models import DamageType
from app.domain.spell_damage_maximizers import SpellDamageMaximizerGrant
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def safe_maximizer_for_spell(
    caster: EncounterCombatant,
    spell_id: str,
    spell_level: int,
) -> SpellDamageMaximizerGrant | None:
    """Return a maximizer only while using it has no self-damage cost."""
    try:
        grant = caster.state.template.progression_features.spell_damage_maximizer
        if grant is None:
            return None
        if spell_id not in grant.eligible_spell_ids:
            return None
        if not grant.minimum_spell_level <= spell_level <= grant.maximum_spell_level:
            return None
        uses = caster.state.feature_use_counts.get(grant.source_id, 0)
        return grant if uses < grant.safe_uses else None
    except Exception:
        logger.exception(
            "Failed to select spell damage maximizer for %s and %s.",
            caster.combatant_id,
            spell_id,
        )
        raise


def maximized_save_damage_rolls(action: SpellSaveAction) -> list[int] | list[list[int]]:
    try:
        if action.damage_components:
            return [
                [component.dice_size] * component.dice_count
                for component in action.damage_components
            ]
        return [action.damage_dice_size] * action.damage_dice_count
    except Exception:
        logger.exception("Failed to build maximized save damage rolls for %s.", action.id)
        raise


def maximized_auto_hit_rolls(
    dice_count: int,
    dice_size: int,
    projectile_count: int,
) -> list[list[int]]:
    try:
        return [[dice_size] * dice_count for _ in range(projectile_count)]
    except Exception:
        logger.exception("Failed to build maximized auto-hit damage rolls.")
        raise


def resolve_maximizer_after_cast(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    grant: SpellDamageMaximizerGrant,
    spell_level: int,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Record one maximizer use and resolve any source-defined self damage."""
    try:
        if not grant.minimum_spell_level <= spell_level <= grant.maximum_spell_level:
            raise ValueError("Spell level is outside the maximizer's declared range.")
        uses_before = caster.state.feature_use_counts.get(grant.source_id, 0)
        caster.state.feature_use_counts[grant.source_id] = uses_before + 1
        if uses_before < grant.safe_uses:
            return [], sequence

        dice_per_level = (
            grant.initial_self_damage_dice_per_spell_level
            + (uses_before - grant.safe_uses) * grant.self_damage_increment_per_spell_level
        )
        dice_count = dice_per_level * spell_level
        rolls = [dice.roll(grant.self_damage_dice_size) for _ in range(dice_count)]
        amount = sum(rolls)
        hp_before = caster.state.current_hp
        temp_before = caster.state.temporary_hp
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        apply_damage(
            caster.state,
            amount,
            damage_types={DamageType(grant.self_damage_type)},
            dice=dice,
            affected_states=affected_states,
        )
        component = DamageRollComponent(
            source=grant.source_name,
            notation=f"{dice_count}d{grant.self_damage_dice_size}",
            rolls=rolls,
            modifier=0,
            damage_type=DamageType(grant.self_damage_type),
            total=amount,
        )
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            target_id=caster.combatant_id,
            target_name=caster.state.template.name,
            feature_id=grant.source_id,
            damage_roll=DiceRoll(
                notation=component.notation,
                rolls=rolls,
                modifier=0,
                total=amount,
            ),
            damage_components=[component],
            hp_before=hp_before,
            hp_after=caster.state.current_hp,
            temporary_hp_before=temp_before,
            temporary_hp_after=caster.state.temporary_hp,
            animation="spell-overchannel",
            description=(
                f"{caster.state.template.name} suffers {grant.source_name} self-damage "
                f"after maximizing a level {spell_level} spell."
            ),
        )
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to resolve spell damage maximizer %s for %s.",
            grant.source_id,
            caster.combatant_id,
        )
        raise RuntimeError("Spell damage maximizer could not be resolved.") from exc
