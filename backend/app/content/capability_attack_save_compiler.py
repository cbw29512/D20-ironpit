from __future__ import annotations

from app.domain.capability_effects import HitSavingThrowEffectDefinition
from app.domain.weapons import OnHitSavingThrow


def compile_hit_save(effect: HitSavingThrowEffectDefinition) -> OnHitSavingThrow:
    return OnHitSavingThrow(
        save_ability=effect.save_ability,
        dc=effect.dc,
        magical_effect=effect.magical_effect,
        failure_effects=effect.failure_effects,
    )
