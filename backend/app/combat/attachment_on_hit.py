"""Apply source-provided linked attachment only after an ordinary successful hit."""
from __future__ import annotations

import logging

from app.combat.attachments import attach
from app.domain.attachments import Attachment

logger = logging.getLogger(__name__)


def apply_attack_hit_attachment(attack, attacker_id, target_id, target_state, setup) -> bool:
    """The hit resolver has already handled attack roll, piercing, and zero HP."""
    try:
        spec = attack.on_hit_attachment
        if spec is None:
            return False
        if setup is None:
            raise ValueError("On-hit attachment requires a live encounter setup.")
        if target_state.is_dead or not target_state.is_alive or target_state.current_hp <= 0:
            return False
        members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
        if attacker_id not in members or target_id not in members:
            raise ValueError("Attachment needs both source and target in the encounter.")
        row = Attachment(
            source_id=attacker_id, target_id=target_id,
            effect_id=spec.effect_id, source_name=spec.source_name,
            damage_dice_count=spec.dice_count,
            damage_dice_size=spec.dice_size, damage_bonus=spec.damage_bonus,
            damage_type=(spec.damage_type.value if spec.damage_type is not None else None),
            periodic_effect_kind=spec.periodic_effect_kind,
            damage_timing=spec.tick_timing,
            detach_after_hp_lost=spec.auto_end_after_hp_loss,
            blocks_source_attacks=spec.blocks_source_attacks,
            action_removable=spec.action_removable,
            action_removal_range_ft=spec.action_removal_range_ft,
            source_detach_movement_ft=spec.source_detach_movement_ft,
        )
        setup.attachments = list(attach(tuple(setup.attachments), row))
        return True
    except Exception:
        logger.exception("Failed to apply source-owned attachment %s to %s.",
                         attacker_id, target_id)
        raise
