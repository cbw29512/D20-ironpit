"""Strict 2014 source-data binding for generic non-Grappled attachment."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014
from app.domain.capability_effects import AttachmentEffectDefinition

logger = logging.getLogger(__name__)

_KEYS = frozenset({
    "id", "name", "dice_count", "dice_size", "damage_bonus",
    "tick_timing", "blocks_source_attacks", "action_removable",
    "action_removal_range_ft", "source_detach_movement_ft",
    "auto_end_after_hp_loss",
})

_CONTROL = re.compile(
    r"\battaches? to (?:it|the target)\b.*\badvantage\b.*"
    r"\battaches? (?:by engulfing|to) the target(?:'s)? head\b.*"
    r"\bblinded and unable to breathe\b",
    re.I,
)
_DC = re.compile(r"(?:successful|succeeding on a) DC (?P<dc>\d+) Strength check", re.I)


def _control_attachment_parameters(attack: SourceAttack2014) -> dict[str, object] | None:
    """Parse the complete shared conditional-control declaration, never identity-dispatch."""
    text = " ".join((attack.unsupported_text or "").split())
    if not text or not _CONTROL.search(text):
        return None
    required = (
        "blinded and unable to breathe", "has advantage on",
        "speed also becomes 0" if "moves with the target" in text.lower() else "make this attack only against the target",
        "5 feet", "movement", "Strength check",
    )
    if not all(fragment.lower() in text.lower() for fragment in required):
        return None
    dc = _DC.search(text)
    if dc is None:
        return None
    attach_size = "large" if text.lower().startswith("if the target is large or smaller") else None
    enhanced_size = "medium" if "target is medium or smaller" in text.lower() else None
    # Darkmantle prints the same target lock/Advantage/speed/movement clauses in
    # separate sentences; Cloaker omits speed-zero/move-with-target.
    return {
        "attach_max_target_size": attach_size,
        "enhanced_max_target_size": enhanced_size,
        "source_speed_zero": "speed also becomes 0" in text.lower(),
        "moves_with_target": "moves with the target" in text.lower(),
        "dc": int(dc.group("dc")),
    }


def supports_source_attachment_2014(attack: SourceAttack2014) -> bool:
    """Validate source shape and semantics, never attack/monster display names."""
    try:
        if _control_attachment_parameters(attack) is not None:
            return (
                attack.kind == "melee"
                and attack.on_hit_save_effect is None
                and attack.control_effect is None
                and attack.on_hit_contested_movement is None
                and attack.ongoing_damage_effect is None
            )
        row = attack.ongoing_damage_effect
        if not isinstance(row, dict) or set(row) != _KEYS:
            return False
        if attack.kind != "melee" or not attack.source_complete:
            return False
        if attack.on_hit_save_effect is not None or attack.control_effect is not None:
            return False
        if attack.on_hit_contested_movement is not None:
            return False
        if not isinstance(row["id"], str) or not row["id"]:
            return False
        if not isinstance(row["name"], str) or row["name"] != attack.name:
            return False
        if type(row["dice_count"]) is not int or not 1 <= row["dice_count"] <= 40:
            return False
        if type(row["dice_size"]) is not int or not 2 <= row["dice_size"] <= 100:
            return False
        if type(row["damage_bonus"]) is not int:
            return False
        if row["tick_timing"] != "source_turn_start":
            return False
        if row["blocks_source_attacks"] is not True or row["action_removable"] is not True:
            return False
        if type(row["action_removal_range_ft"]) is not int or row["action_removal_range_ft"] < 0:
            return False
        if type(row["source_detach_movement_ft"]) is not int or row["source_detach_movement_ft"] < 0:
            return False
        if type(row["auto_end_after_hp_loss"]) is not int or row["auto_end_after_hp_loss"] < 1:
            return False
        return row["source_detach_movement_ft"] % 5 == 0 and row["action_removal_range_ft"] % 5 == 0
    except (TypeError, ValueError, KeyError):
        logger.exception("Malformed source attachment parameters for %s.", attack.id)
        return False


def source_attachment_effect_2014(attack: SourceAttack2014) -> AttachmentEffectDefinition:
    """Map declared parameters to one universal capability, not a named resolver."""
    try:
        if not supports_source_attachment_2014(attack):
            raise ValueError(f"Unsupported or incomplete source attachment on {attack.id}.")
        control = _control_attachment_parameters(attack)
        if control is not None:
            return AttachmentEffectDefinition(
                effect_id=f"{attack.id}-attachment", source_name=attack.name,
                action_removable=True, action_removal_range_ft=5,
                source_detach_movement_ft=5,
                attach_max_target_size=control["attach_max_target_size"],
                enhanced_on_attack_advantage=True,
                enhanced_max_target_size=control["enhanced_max_target_size"],
                source_target_lock=True,
                source_advantage_against_target=True,
                source_speed_zero=control["source_speed_zero"],
                moves_with_target=control["moves_with_target"],
                enhanced_blinds_target=True,
                enhanced_prevents_breathing=True,
                action_removal_check_ability="strength",
                action_removal_check_dc=control["dc"],
            )
        row = attack.ongoing_damage_effect
        return AttachmentEffectDefinition(
            effect_id=row["id"], source_name=row["name"],
            periodic_effect_kind="direct_hp_loss", dice_count=row["dice_count"],
            dice_size=row["dice_size"], damage_bonus=row["damage_bonus"],
            tick_timing=row["tick_timing"],
            blocks_source_attacks=row["blocks_source_attacks"],
            action_removable=row["action_removable"],
            action_removal_range_ft=row["action_removal_range_ft"],
            source_detach_movement_ft=row["source_detach_movement_ft"],
            auto_end_after_hp_loss=row["auto_end_after_hp_loss"],
        )
    except Exception:
        logger.exception("Failed to bind source attachment for %s.", attack.id)
        raise
