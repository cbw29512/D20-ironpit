from __future__ import annotations

from app.domain.spells import SpellAttackAction, SpellModifierEffect


def build_guiding_bolt(attack_bonus: int) -> SpellAttackAction:
    return SpellAttackAction(
        id="guiding-bolt",
        name="Guiding Bolt",
        level=1,
        action_cost="action",
        range_ft=120,
        attack_bonus=attack_bonus,
        damage_dice_count=4,
        damage_dice_size=6,
        damage_type="radiant",
        on_hit_modifier_effects=[
            SpellModifierEffect(
                kind="attacks-against-advantage",
                consume_on_attack_against=True,
                expires_after_source_turns=1,
            ),
        ],
        animation="guiding-bolt",
        source="SRD 5.2.1 Guiding Bolt",
    )
