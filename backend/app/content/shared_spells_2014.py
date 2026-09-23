from __future__ import annotations

from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

_SOURCE = "D&D Basic Rules 2014: Sanctuary"


def sanctuary_2014(save_dc: int) -> DefensiveSpellAction:
    """Build the shared 2014 Sanctuary spell through the universal targeting-save gate."""
    return DefensiveSpellAction(
        id="sanctuary",
        name="Sanctuary",
        level=1,
        action_cost="bonus_action",
        range_ft=30,
        duration_minutes=1,
        target_policy="friendly",
        target_count=1,
        priority=32,
        modifier_effects=[
            SpellModifierEffect(
                kind="targeting-save-gate",
                save_ability="wisdom",
                save_dc=save_dc,
                ends_on_owner_attack=True,
            ),
        ],
        animation="sanctuary",
        source=_SOURCE,
    )
