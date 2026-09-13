from __future__ import annotations

from app.domain.capability_effects import HitSavingThrowEffectDefinition
from app.domain.weapons import OnHitSavingThrow


def compile_hit_save(effect: HitSavingThrowEffectDefinition) -> OnHitSavingThrow:
    return OnHitSavingThrow(
        save_ability=effect.save_ability,
        dc=effect.dc,
        magical_effect=effect.magical_effect,
        target_filter=effect.target_filter,
        failure_effects=effect.failure_effects,
        severe_failure_margin=effect.severe_failure_margin,
        severe_failure_effects=effect.severe_failure_effects,
    )
