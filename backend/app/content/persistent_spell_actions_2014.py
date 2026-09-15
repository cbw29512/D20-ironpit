from __future__ import annotations

from app.domain.spells import SpellAttackAction


def build_spiritual_weapon(attack_bonus: int, spellcasting_modifier: int) -> SpellAttackAction:
    """Build the reusable 2014 Spiritual Weapon combat action."""
    return SpellAttackAction(
        id="spiritual-weapon",
        name="Spiritual Weapon",
        level=2,
        action_cost="bonus_action",
        attack_kind="melee",
        range_ft=60,
        attack_bonus=attack_bonus,
        damage_dice_count=1,
        damage_dice_size=8,
        damage_bonus=spellcasting_modifier,
        damage_type="force",
        persistent_duration_rounds=10,
        animation="spiritual-weapon",
        source="SRD 5.1 / 2014 monster spell",
    )
