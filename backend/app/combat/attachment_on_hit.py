"""Apply source-provided linked attachment only after an ordinary successful hit."""
from __future__ import annotations

import logging

from app.combat.attachments import attach, sync_attachment_controls
from app.domain.models import RollMode
from app.domain.size import size_at_most
from app.domain.attachments import Attachment
from app.domain.attachment_receipts import AttachmentChange

logger = logging.getLogger(__name__)


def apply_attack_hit_attachment(attack, attacker_id, target_id, target_state, setup,
                                attack_mode: RollMode = RollMode.NORMAL) -> bool:
    """The hit resolver has already handled attack roll, piercing, and zero HP."""
    try:
        spec = attack.on_hit_attachment
        if spec is None:
            return False
        if setup is None:
            raise ValueError("On-hit attachment requires a live encounter setup.")
        # Zero-HP unconscious heroes remain living creatures and can be attached.
        if target_state.is_dead or not target_state.is_alive:
            return False
        members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
        if attacker_id not in members or target_id not in members:
            raise ValueError("Attachment needs both source and target in the encounter.")
        size = target_state.template.size
        if spec.attach_max_target_size is not None and not size_at_most(size, spec.attach_max_target_size):
            return False
        enhanced = (
            spec.enhanced_on_attack_advantage
            and attack_mode is RollMode.ADVANTAGE
            and (spec.enhanced_max_target_size is None
                 or size_at_most(size, spec.enhanced_max_target_size))
        )
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
            source_target_lock=spec.source_target_lock,
            source_advantage_against_target=spec.source_advantage_against_target,
            source_speed_zero=spec.source_speed_zero,
            moves_with_target=spec.moves_with_target,
            blinds_target=bool(enhanced and spec.enhanced_blinds_target),
            prevents_breathing=bool(enhanced and spec.enhanced_prevents_breathing),
            action_removal_check_ability=spec.action_removal_check_ability,
            action_removal_check_dc=spec.action_removal_check_dc,
        )
        setup.attachments = list(attach(tuple(setup.attachments), row))
        sync_attachment_controls(setup)
        return True
    except Exception:
        logger.exception("Failed to apply source-owned attachment %s to %s.",
                         attacker_id, target_id)
        raise


def attached_hit_receipts(attack, attacker_id, target_id, setup) -> list[AttachmentChange]:
    """Report a successful link without projecting it as Grappled."""
    try:
        spec = attack.on_hit_attachment
        if spec is None or setup is None:
            return []
        return [
            AttachmentChange(
                operation="attach", source_id=row.source_id, target_id=row.target_id,
                effect_id=row.effect_id, source_name=row.source_name,
            )
            for row in setup.attachments
            if row.source_id == attacker_id and row.target_id == target_id
            and row.effect_id == spec.effect_id
        ]
    except Exception:
        logger.exception("Failed to build hit attachment receipt for %s.", attacker_id)
        raise
