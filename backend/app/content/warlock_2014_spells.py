from __future__ import annotations

from app.domain.spells import SpellAttackAction
from app.domain.targeted_concentration_damage import TargetedConcentrationDamageAction


def eldritch_blast_2014(attack_bonus: int, level: int, damage_bonus: int = 0, range_ft: int = 120) -> SpellAttackAction:
    """Build one 2014 Eldritch Blast beam from the universal spell-attack primitive.

    Levels 1-4 have one beam. Higher-level multi-beam resolution is intentionally
    certified separately rather than pretending one attack roll represents every beam.
    """
    if level not in range(1, 5):
        raise ValueError("Single-beam 2014 Eldritch Blast builder currently certifies levels 1 through 4.")
    if range_ft < 1:
        raise ValueError("Eldritch Blast range must be positive.")
    return SpellAttackAction(
        id="eldritch-blast",
        name="Eldritch Blast",
        level=0,
        action_cost="action",
        attack_kind="ranged",
        range_ft=range_ft,
        attack_bonus=attack_bonus,
        damage_dice_count=1,
        damage_dice_size=10,
        damage_bonus=damage_bonus,
        damage_type="force",
        animation="spell-attack",
        source="D&D Basic Rules 2014: Eldritch Blast",
    )


def hex_2014() -> TargetedConcentrationDamageAction:
    return TargetedConcentrationDamageAction(
        id="hex",
        name="Hex",
        level=1,
        action_cost="bonus_action",
        range_ft=90,
        dice_count=1,
        dice_size=6,
        damage_type="necrotic",
        duration_rounds_by_slot={1: 600, 3: 4800, 5: 14400},
        retarget_after_target_zero=True,
        priority=10,
        animation="targeted-concentration",
        source="D&D Basic Rules 2014: Hex",
    )
