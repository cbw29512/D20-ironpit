from __future__ import annotations

from app.domain.actions import SavingThrowAction
from app.domain.spells import SpellAttackAction
from app.domain.targeted_concentration_damage import TargetedConcentrationDamageAction
from app.domain.targeting import AreaTargeting


def eldritch_blast_2014(attack_bonus: int, level: int, damage_bonus: int = 0, range_ft: int = 120) -> SpellAttackAction:
    """Build 2014 Eldritch Blast using independent universal spell attacks."""
    if level not in range(1, 21):
        raise ValueError("2014 Eldritch Blast character level must be between 1 and 20.")
    if range_ft < 1:
        raise ValueError("Eldritch Blast range must be positive.")
    attack_count = 1 + int(level >= 5) + int(level >= 11) + int(level >= 17)
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
        attack_count=attack_count,
        animation="spell-attack",
        source="D&D Basic Rules 2014: Eldritch Blast",
    )


def scorching_ray_2014(attack_bonus: int) -> SpellAttackAction:
    """Three independent rays, plus one ray for each slot level above 2."""
    return SpellAttackAction(
        id="scorching-ray",
        name="Scorching Ray",
        level=2,
        action_cost="action",
        attack_kind="ranged",
        range_ft=120,
        attack_bonus=attack_bonus,
        damage_dice_count=2,
        damage_dice_size=6,
        damage_type="fire",
        attack_count=3,
        attacks_per_slot_above=1,
        animation="spell-attack",
        source="D&D Basic Rules 2014: Scorching Ray",
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



def circle_of_death_2014(save_dc: int) -> SavingThrowAction:
    """Build 2014 Circle of Death as a resource-backed universal area save."""
    return SavingThrowAction(
        id="circle-of-death",
        name="Circle of Death",
        save_ability="constitution",
        dc=save_dc,
        range_ft=150,
        area=AreaTargeting(shape="radius", origin="point", radius_ft=60),
        damage_dice_count=8,
        damage_dice_size=6,
        damage_type="necrotic",
        success_damage="half",
        resource_id="mystic-arcanum-6",
        resource_cost=1,
        magical_effect=True,
        animation="spell-save",
    )
