from __future__ import annotations

from app.domain.spells import SpellAttackAction


def eldritch_blast_2014(attack_bonus: int, level: int, damage_bonus: int = 0) -> SpellAttackAction:
    """Build one 2014 Eldritch Blast beam from the universal spell-attack primitive.

    Levels 1-4 have one beam. Higher-level multi-beam resolution is intentionally
    certified separately rather than pretending one attack roll represents every beam.
    """
    if level not in range(1, 5):
        raise ValueError("Single-beam 2014 Eldritch Blast builder currently certifies levels 1 through 4.")
    return SpellAttackAction(
        id="eldritch-blast",
        name="Eldritch Blast",
        level=0,
        action_cost="action",
        attack_kind="ranged",
        range_ft=120,
        attack_bonus=attack_bonus,
        damage_dice_count=1,
        damage_dice_size=10,
        damage_bonus=damage_bonus,
        damage_type="force",
        animation="spell-attack",
        source="D&D Basic Rules 2014: Eldritch Blast",
    )
