from __future__ import annotations

import logging

from app.combat.on_hit_condition_save import OnHitConditionSaveResolution
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
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
    affected_states: list[CombatantState] | None = None,
    setup=None,
) -> OnHitConditionSaveResolution:
    """Apply/stack a declared source-owned turn-start HP loss, not typed damage."""
    try:
        rule = attack.on_hit_ongoing_hp_loss
        if rule is None or defender.is_dead or not defender.is_alive:
            return OnHitConditionSaveResolution()
        if any(creature_matches_kind(defender.template, kind)
               for kind in rule.excluded_creature_types):
            return OnHitConditionSaveResolution()
        existing = next((
            effect for effect in defender.timed_effects
            if effect.effect_id == rule.effect_id and effect.source_id == source_id
            and effect.source_effect_id == attack.weapon.name
        ), None)
        if existing is not None:
            if not rule.stacks_on_reapply:
                return OnHitConditionSaveResolution()
            existing.start_of_turn_hp_loss_dice_count += rule.dice_count
            return OnHitConditionSaveResolution(applied_condition=rule.effect_id)
        roll, succeeded = resolve_saving_throw(
            defender, rule.save_ability, rule.dc, dice, SavingThrowContext()
        )
        applied = None
        if not succeeded:
            applied = apply_timed_condition(
                defender, rule.effect_id, source_id,
                source_effect_id=attack.weapon.name,
                applied_round=round_number, expires_at_start_of_source_turn=False,
                start_of_turn_hp_loss_dice_count=rule.dice_count,
                start_of_turn_hp_loss_dice_size=rule.dice_size,
                ends_on_magical_healing=rule.ends_on_magical_healing,
                affected_states=affected_states,
            )
        return OnHitConditionSaveResolution(
            roll, rule.save_ability, rule.dc, succeeded, applied
        )
    except Exception:
        logger.exception("On-hit ongoing HP loss failed for %s.", defender.template.name)
        raise
