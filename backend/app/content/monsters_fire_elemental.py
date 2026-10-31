from __future__ import annotations

from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType


def build_fire_elemental_fire_form() -> TimedSelfBuffAction:
    """Bind 2014 Fire Form contact damage so it resolves in combat.

    Printed: a creature that touches the elemental or hits it with a melee
    attack while within 5 feet takes 1d10 fire. Space-entry ignition remains
    a follow-up. Does not claim admission.
    """
    return TimedSelfBuffAction(
        id="srd-fire-elemental-fire-form-contact",
        name="Fire Form",
        activation_timing="passive",
        melee_hit_retaliation=MeleeHitRetaliation(
            range_ft=5,
            dice_count=1,
            dice_size=10,
            damage_type=DamageType.FIRE,
            on_contact=True,
        ),
    )
