"""Source-owned stacking ongoing HP loss, with no named-monster dispatch."""

import logging

from app.domain.models import CombatantState, TimedEffect

logger = logging.getLogger(__name__)


def apply_or_stack_hp_loss(
    state: CombatantState, effect_id: str, source_id: str,
    source_effect_id: str, *, dice_count: int, dice_size: int,
    ends_on_magical_healing: bool = False,
) -> int:
    """Return current stack size; each attacker/source action owns its own stack."""
    try:
        if not effect_id or not source_id or not source_effect_id:
            raise ValueError("Ongoing HP loss requires an effect and distinct source identity.")
        if dice_count < 1 or dice_size < 2:
            raise ValueError("Ongoing HP loss requires a positive dice pool.")
        if state.is_dead or not state.is_alive:
            return 0
        matched = next((
            item for item in state.timed_effects
            if item.effect_id == effect_id
            and item.source_id == source_id
            and item.source_effect_id == source_effect_id
        ), None)
        if matched is not None:
            if matched.start_of_turn_hp_loss_dice_count <= 0 or matched.start_of_turn_hp_loss_dice_size != dice_size:
                raise ValueError("An existing source wound has incompatible stack semantics.")
            if matched.ends_on_magical_healing != ends_on_magical_healing:
                raise ValueError("An existing source wound has incompatible healing-removal semantics.")
            new_count = matched.start_of_turn_hp_loss_dice_count + dice_count
            if new_count > 40:
                raise ValueError("Ongoing HP-loss stacks exceed the supported dice limit.")
            matched.start_of_turn_hp_loss_dice_count = new_count
            return new_count
        effect = TimedEffect(
            effect_id=effect_id, source_id=source_id,
            source_effect_id=source_effect_id,
            expires_at_start_of_source_turn=False,
            start_of_turn_hp_loss_dice_count=dice_count,
            start_of_turn_hp_loss_dice_size=dice_size,
            ends_on_magical_healing=ends_on_magical_healing,
        )
        state.timed_effects.append(effect)
        if effect_id not in state.active_effect_ids:
            state.active_effect_ids.append(effect_id)
        return dice_count
    except (ValueError, TypeError):
        raise
    except Exception:
        logger.exception("Ongoing HP-loss stack failed for %s.", state.template.name)
        raise
