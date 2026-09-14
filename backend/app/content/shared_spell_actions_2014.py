from __future__ import annotations

from app.domain.spells import SpellModifierEffect, SpellSaveAction
from app.domain.targeting import AreaTargeting


def build_faerie_fire(save_dc: int) -> SpellSaveAction:
    """Build the shared 2014 Faerie Fire effect with caster-provided save DC."""
    return SpellSaveAction(
        id="faerie-fire",
        name="Faerie Fire",
        level=1,
        range_ft=60,
        area=AreaTargeting(shape="cube", origin="point", length_ft=20),
        save_ability="dexterity",
        dc=save_dc,
        concentration=True,
        duration_minutes=1,
        failure_modifier_effects=[
            SpellModifierEffect(kind="attacks-against-advantage"),
            SpellModifierEffect(kind="invisibility-suppressed"),
        ],
        animation="faerie-fire",
    )
