from __future__ import annotations

import logging

from app.domain.post_hit_spell import PostHitSpellOption

logger = logging.getLogger(__name__)
_TRIGGERS = ("aurelia-longsword", "aurelia-javelin")


def build_paladin_2024_extra_smites(level: int, save_dc: int) -> list[PostHitSpellOption]:
    """Bind the printed 2024 extra smites that share the post-hit Bonus Action window."""
    try:
        options: list[PostHitSpellOption] = []
        if level >= 4:
            options.append(PostHitSpellOption(
                id="thunderous-smite",
                name="Thunderous Smite",
                level=1,
                trigger_attack_ids=list(_TRIGGERS),
                base_dice_count=2,
                dice_per_slot_above=1,
                dice_size=6,
                damage_type="thunder",
                save_ability="strength",
                save_dc=save_dc,
                failed_condition_id="prone",
                failed_push_ft=10,
            ))
        if level >= 5:
            options.append(PostHitSpellOption(
                id="shining-smite",
                name="Shining Smite",
                level=2,
                trigger_attack_ids=list(_TRIGGERS),
                base_dice_count=2,
                dice_per_slot_above=1,
                dice_size=6,
                damage_type="radiant",
                concentration=True,
                duration_rounds=10,
                attacks_against_advantage=True,
                suppress_invisible=True,
            ))
        if level >= 9:
            options.append(PostHitSpellOption(
                id="blinding-smite",
                name="Blinding Smite",
                level=3,
                trigger_attack_ids=list(_TRIGGERS),
                base_dice_count=3,
                dice_per_slot_above=1,
                dice_size=8,
                damage_type="radiant",
                save_ability="constitution",
                save_dc=save_dc,
                failed_condition_id="blinded",
                concentration=True,
                duration_rounds=10,
                repeat_save_ability="constitution",
                repeat_save_dc=save_dc,
                repeat_save_timing="target_turn_end",
            ))
        if level >= 13:
            options.append(PostHitSpellOption(
                id="staggering-smite",
                name="Staggering Smite",
                level=4,
                trigger_attack_ids=list(_TRIGGERS),
                base_dice_count=4,
                dice_per_slot_above=1,
                dice_size=6,
                damage_type="psychic",
                save_ability="wisdom",
                save_dc=save_dc,
                failed_condition_id="stunned",
                failed_condition_expiry_timing="source_turn_end",
            ))
        if level >= 19:
            options.append(PostHitSpellOption(
                id="banishing-smite",
                name="Banishing Smite",
                level=5,
                trigger_attack_ids=list(_TRIGGERS),
                base_dice_count=5,
                dice_per_slot_above=1,
                dice_size=10,
                damage_type="force",
                max_slot_level=5,
                concentration=True,
                duration_rounds=10,
                exile_if_hp_at_or_below=50,
            ))
        return options
    except Exception:
        logger.exception("Failed to build 2024 Paladin extra smites at level %s.", level)
        raise
