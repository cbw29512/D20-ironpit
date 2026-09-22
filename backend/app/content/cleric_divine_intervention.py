from __future__ import annotations

import logging

from app.content.healing_spell_effects import build_mass_cure_wounds
from app.domain.actions import HealingAction, SavingThrowAction

logger = logging.getLogger(__name__)

_RESOURCE_ID = "divine-intervention"


def build_divine_intervention_damage(save_dc: int) -> SavingThrowAction:
    """Free once-per-rest cast of 5th-level Inflict Wounds through Divine Intervention."""
    try:
        return SavingThrowAction(
            id="divine-intervention-inflict-wounds",
            name="Divine Intervention: Inflict Wounds (5th-Level)",
            save_ability="constitution",
            dc=save_dc,
            range_ft=5,
            damage_dice_count=6,
            damage_dice_size=10,
            damage_type="necrotic",
            success_damage="half",
            resource_id=_RESOURCE_ID,
            resource_cost=1,
            magical_effect=True,
            animation="inflict-wounds",
        )
    except Exception:
        logger.exception("Failed to build Divine Intervention damage action.")
        raise


def build_divine_intervention_healing(
    spellcasting_modifier: int,
    extra_healing_bonus: int = 0,
) -> HealingAction:
    """Free once-per-rest cast of Mass Cure Wounds through Divine Intervention."""
    try:
        base = build_mass_cure_wounds(spellcasting_modifier, extra_healing_bonus)
        return base.model_copy(update={
            "id": "divine-intervention-mass-cure-wounds",
            "name": "Divine Intervention: Mass Cure Wounds",
            "resource_id": _RESOURCE_ID,
            "resource_cost": 1,
        })
    except Exception:
        logger.exception("Failed to build Divine Intervention healing action.")
        raise
