from __future__ import annotations

import logging

from app.content.healing_spell_effects import build_mass_cure_wounds
from app.content.offensive_spell_effects import build_fireball_2024
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



def build_greater_divine_intervention_wish_fireball(save_dc: int) -> SavingThrowAction:
    """Wish duplicates printed-level 2024 Fireball through Greater Divine Intervention."""
    try:
        spell = build_fireball_2024(save_dc)
        return SavingThrowAction(
            id="greater-divine-intervention-wish-fireball",
            name="Greater Divine Intervention: Wish — Fireball",
            action_cost=spell.action_cost,
            save_ability=spell.save_ability,
            dc=spell.dc,
            range_ft=spell.range_ft,
            area=spell.area,
            damage_dice_count=spell.damage_dice_count,
            damage_dice_size=spell.damage_dice_size,
            damage_bonus=spell.damage_bonus,
            damage_type=spell.damage_type,
            success_damage=spell.success_damage,
            resource_id=_RESOURCE_ID,
            resource_cost=1,
            magical_effect=True,
            animation=spell.animation,
        )
    except Exception:
        logger.exception("Failed to build Greater Divine Intervention Wish/Fireball action.")
        raise
