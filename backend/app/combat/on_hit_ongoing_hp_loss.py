"""Resolve a source-driven on-hit saving throw and source-owned ongoing HP loss."""

from __future__ import annotations

import logging

from app.combat.on_hit_condition_save import OnHitConditionSaveResolution
from app.combat.ongoing_hp_loss import apply_or_stack_hp_loss
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.content.monster_creature_types import creature_matches_kind
from app.domain.models import CombatantState, WeaponAttack
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def resolve_on_hit_ongoing_hp_loss(
    defender: CombatantState,
    attack: WeaponAttack,
    dice,
    *,
    source_id: str,
    round_number: int,
) -> OnHitConditionSaveResolution:
    """Apply a failed-save wound; repeat hits from this source stack without a save."""
    try:
        rule = attack.on_hit_ongoing_hp_loss
        if rule is None or defender.is_dead or not defender.is_alive:
            return OnHitConditionSaveResolution()
        if any(
            creature_matches_kind(defender.template, kind)
            for kind in rule.excluded_creature_types
        ):
            return OnHitConditionSaveResolution()
        source_effect_id = attack.weapon.name
        existing = next((
            effect for effect in defender.timed_effects
            if effect.effect_id == rule.effect_id
            and effect.source_id == source_id
            and effect.source_effect_id == source_effect_id
        ), None)
        if existing is not None:
            if not rule.stacks_on_reapply:
                return OnHitConditionSaveResolution()
            apply_or_stack_hp_loss(
                defender, rule.effect_id, source_id, source_effect_id,
                dice_count=rule.dice_count, dice_size=rule.dice_size,
                ends_on_magical_healing=rule.ends_on_magical_healing,
            )
            return OnHitConditionSaveResolution(applied_condition=rule.effect_id)
        save_roll, succeeded = resolve_saving_throw(
            defender, rule.save_ability, rule.dc, dice, SavingThrowContext()
        )
        applied = None
        if not succeeded:
            apply_or_stack_hp_loss(
                defender, rule.effect_id, source_id, source_effect_id,
                dice_count=rule.dice_count, dice_size=rule.dice_size,
                ends_on_magical_healing=rule.ends_on_magical_healing,
            )
            applied = rule.effect_id
        return OnHitConditionSaveResolution(
            save_roll, rule.save_ability, rule.dc, succeeded, applied
        )
    except Exception:
        logger.exception(
            "Failed on-hit persistent HP loss for %s, source %s, round %d.",
            defender.template.name, source_id, round_number,
        )
        raise
